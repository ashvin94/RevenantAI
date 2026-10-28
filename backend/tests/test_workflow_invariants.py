"""Additional persistence, rollback, and pure-transition checks for Phase 2."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, func, select

from app.core.workflow import InventoryState, reserve_inventory
from app.models import (
    Inventory,
    InventoryReservation,
    Order,
    ProcessedEvent,
    WorkflowEvent,
)


def row_count(session: Session, model: type) -> int:
    return session.exec(select(func.count()).select_from(model)).one()


def test_create_order_persists_event_and_processed_guard(client: TestClient) -> None:
    response = client.post(
        "/api/orders",
        json={
            "sku": "LAPTOP-001",
            "quantity": 2,
            "logical_event_id": "EVT-PERSIST-1",
        },
    )

    assert response.status_code == 201
    order_id = response.json()["id"]
    with Session(client.app.state.engine) as session:
        processed = session.get(ProcessedEvent, "EVT-PERSIST-1")
        events = session.exec(
            select(WorkflowEvent).where(WorkflowEvent.order_id == order_id)
        ).all()

    assert processed is not None
    assert processed.order_id == order_id
    assert len(events) == 1
    assert events[0].result == "SUCCESS_SIMULATED_PAYMENT_CONFIRMED"


def test_reused_event_with_different_payload_is_conflict_and_nonmutating(
    client: TestClient,
) -> None:
    original = {
        "sku": "LAPTOP-001",
        "quantity": 1,
        "logical_event_id": "EVT-CONFLICT-1",
    }
    assert client.post("/api/orders", json=original).status_code == 201
    before_inventory = client.get("/api/inventory/LAPTOP-001").json()

    conflict = client.post(
        "/api/orders",
        json={**original, "quantity": 2},
    )

    assert conflict.status_code == 409
    assert client.get("/api/inventory/LAPTOP-001").json() == before_inventory
    with Session(client.app.state.engine) as session:
        assert row_count(session, Order) == 1
        assert row_count(session, InventoryReservation) == 1
        assert row_count(session, ProcessedEvent) == 1


def test_insufficient_stock_rolls_back_every_business_row(client: TestClient) -> None:
    with Session(client.app.state.engine) as session:
        before = {
            "orders": row_count(session, Order),
            "reservations": row_count(session, InventoryReservation),
            "events": row_count(session, WorkflowEvent),
            "processed": row_count(session, ProcessedEvent),
        }
        inventory_before = session.get(Inventory, "LAPTOP-001")
        assert inventory_before is not None
        available_before = inventory_before.available_stock
        version_before = inventory_before.version

    response = client.post(
        "/api/orders",
        json={
            "sku": "LAPTOP-001",
            "quantity": available_before + 1,
            "logical_event_id": "EVT-ROLLBACK-1",
        },
    )

    assert response.status_code == 400
    with Session(client.app.state.engine) as session:
        after = {
            "orders": row_count(session, Order),
            "reservations": row_count(session, InventoryReservation),
            "events": row_count(session, WorkflowEvent),
            "processed": row_count(session, ProcessedEvent),
        }
        inventory_after = session.get(Inventory, "LAPTOP-001")
        assert inventory_after is not None
        assert inventory_after.available_stock == available_before
        assert inventory_after.version == version_before
    assert after == before


def test_database_rejects_negative_inventory(client: TestClient) -> None:
    with Session(client.app.state.engine) as session:
        inventory = session.get(Inventory, "LAPTOP-001")
        assert inventory is not None
        inventory.available_stock = -1
        session.add(inventory)
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()

    assert client.get("/api/inventory/LAPTOP-001").json()["available_stock"] == 10


def test_reserve_inventory_transition_is_pure() -> None:
    before = InventoryState(sku="LAPTOP-001", available_stock=10, version=4)

    transition = reserve_inventory(before, 3)

    assert before.available_stock == 10
    assert before.version == 4
    assert transition.previous is before
    assert transition.current.available_stock == 7
    assert transition.current.version == 5
