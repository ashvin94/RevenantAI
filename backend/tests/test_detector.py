"""Controlled duplicate fault and deterministic detector tests."""

from fastapi.testclient import TestClient
from sqlmodel import Session, func, select

from app.config import Settings
from app.main import create_app
from app.models import Incident, Inventory, InventoryReservation


def create_demo_order(client: TestClient, event_id: str) -> dict:
    response = client.post(
        "/api/orders",
        json={
            "sku": "LAPTOP-001",
            "quantity": 1,
            "logical_event_id": event_id,
        },
    )
    assert response.status_code == 201
    return response.json()


def test_normal_order_inspection_is_healthy(client: TestClient) -> None:
    order = create_demo_order(client, "EVT-HEALTHY-1")

    inspection = client.post(f"/api/orders/{order['id']}/inspect")

    assert inspection.status_code == 200
    payload = inspection.json()
    assert payload["healthy"] is True
    assert payload["incident"] is None
    assert all(rule["passed"] for rule in payload["rules"])
    assert client.get("/api/incidents").json() == []


def test_injected_duplicate_creates_evidence_backed_incident(
    client: TestClient,
) -> None:
    order = create_demo_order(client, "EVT-DUPLICATE-1")
    before = client.get("/api/inventory/LAPTOP-001").json()

    injected = client.post(f"/api/orders/{order['id']}/inject-duplicate")
    inspection = client.post(f"/api/orders/{order['id']}/inspect")

    assert injected.status_code == 200
    assert injected.json()["active_reservation_count"] == 2
    assert inspection.status_code == 200
    payload = inspection.json()
    assert payload["healthy"] is False
    assert payload["incident"]["source"] == "RULE"
    assert payload["incident"]["type"] == "DUPLICATE_RESERVATION"
    rules = {rule["id"]: rule for rule in payload["rules"]}
    assert rules["RESERVATION_QUANTITY_MATCH"]["expected"] == 1
    assert rules["RESERVATION_QUANTITY_MATCH"]["actual"] == 2
    assert rules["NO_DUPLICATE_ACTIVE_EVENT"]["passed"] is False
    assert rules["NON_NEGATIVE_AVAILABLE_STOCK"]["passed"] is True
    assert rules["STOCK_CONSERVATION"]["passed"] is True
    after = client.get("/api/inventory/LAPTOP-001").json()
    assert after["available_stock"] == before["available_stock"] - 1

    detail = client.get(f"/api/orders/{order['id']}").json()
    assert len(detail["reservations"]) == 2
    assert len(client.get("/api/incidents").json()) == 1


def test_repeated_inspection_reuses_incident(client: TestClient) -> None:
    order = create_demo_order(client, "EVT-INSPECT-IDEMPOTENT-1")
    assert client.post(f"/api/orders/{order['id']}/inject-duplicate").status_code == 200

    first = client.post(f"/api/orders/{order['id']}/inspect").json()
    second = client.post(f"/api/orders/{order['id']}/inspect").json()

    assert first["incident"]["id"] == second["incident"]["id"]
    with Session(client.app.state.engine) as session:
        assert session.exec(select(func.count()).select_from(Incident)).one() == 1


def test_duplicate_fault_can_only_be_injected_once(client: TestClient) -> None:
    order = create_demo_order(client, "EVT-FAULT-ONCE-1")
    assert client.post(f"/api/orders/{order['id']}/inject-duplicate").status_code == 200
    inventory_after_first = client.get("/api/inventory/LAPTOP-001").json()

    repeated = client.post(f"/api/orders/{order['id']}/inject-duplicate")

    assert repeated.status_code == 409
    assert client.get("/api/inventory/LAPTOP-001").json() == inventory_after_first
    with Session(client.app.state.engine) as session:
        reservations = session.exec(
            select(InventoryReservation).where(
                InventoryReservation.order_id == order["id"],
                InventoryReservation.status == "ACTIVE",
            )
        ).all()
        inventory = session.get(Inventory, "LAPTOP-001")
    assert len(reservations) == 2
    assert inventory is not None


def test_fault_injection_disabled_is_nonmutating(settings: Settings) -> None:
    app = create_app(settings.model_copy(update={"enable_fault_injection": False}))
    with TestClient(app) as client:
        order = create_demo_order(client, "EVT-DISABLED-1")
        before = client.get("/api/inventory/LAPTOP-001").json()
        response = client.post(f"/api/orders/{order['id']}/inject-duplicate")
        after = client.get("/api/inventory/LAPTOP-001").json()

    assert response.status_code == 403
    assert after == before
    app.state.engine.dispose()
