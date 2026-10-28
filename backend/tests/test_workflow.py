"""Comprehensive tests for normal order workflow, idempotency, and inventory conservation."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_create_order_success(client: TestClient) -> None:
    """T01: Order with quantity 1 creates one active reservation and decrements available stock."""
    # Check initial stock
    inv_res = client.get("/api/inventory/LAPTOP-001")
    assert inv_res.status_code == 200
    initial_available = inv_res.json()["available_stock"]
    assert initial_available == 10

    # Place order
    order_payload = {
        "sku": "LAPTOP-001",
        "quantity": 1,
        "logical_event_id": "EVT-TEST-1001",
    }
    response = client.post("/api/orders", json=order_payload)
    assert response.status_code == 201
    order_data = response.json()
    assert order_data["sku"] == "LAPTOP-001"
    assert order_data["quantity"] == 1
    assert order_data["status"] == "INVENTORY_RESERVED"
    assert order_data["version"] == 1

    # Check order detail has exactly 1 active reservation
    detail_res = client.get(f"/api/orders/{order_data['id']}")
    assert detail_res.status_code == 200
    detail = detail_res.json()
    assert len(detail["reservations"]) == 1
    res = detail["reservations"][0]
    assert res["quantity"] == 1
    assert res["status"] == "ACTIVE"
    assert res["logical_event_id"] == "EVT-TEST-1001"

    # Verify inventory was decremented once
    inv_after = client.get("/api/inventory/LAPTOP-001").json()
    assert inv_after["available_stock"] == initial_available - 1


def test_order_idempotency_prevents_duplicate_reservations(client: TestClient) -> None:
    """Submitting the same logical_event_id returns the existing order with no second reservation or stock deduction."""
    order_payload = {
        "sku": "LAPTOP-001",
        "quantity": 1,
        "logical_event_id": "EVT-IDEMP-2001",
    }
    res1 = client.post("/api/orders", json=order_payload)
    assert res1.status_code == 201
    order_id = res1.json()["id"]

    inv_mid = client.get("/api/inventory/LAPTOP-001").json()
    available_mid = inv_mid["available_stock"]

    # Replay identical event
    res2 = client.post("/api/orders", json=order_payload)
    assert res2.status_code == 201
    assert res2.json()["id"] == order_id

    # Stock must not have changed
    inv_end = client.get("/api/inventory/LAPTOP-001").json()
    assert inv_end["available_stock"] == available_mid

    # Reservation count must still be exactly 1
    detail = client.get(f"/api/orders/{order_id}").json()
    assert len(detail["reservations"]) == 1


def test_reject_zero_or_negative_quantity(client: TestClient) -> None:
    """Quantity <= 0 must be rejected by schema validation without creating state."""
    res_zero = client.post(
        "/api/orders",
        json={"sku": "LAPTOP-001", "quantity": 0, "logical_event_id": "EVT-ZERO"},
    )
    assert res_zero.status_code == 422

    res_neg = client.post(
        "/api/orders",
        json={"sku": "LAPTOP-001", "quantity": -5, "logical_event_id": "EVT-NEG"},
    )
    assert res_neg.status_code == 422


def test_reject_unknown_sku(client: TestClient) -> None:
    """Unknown catalog SKU returns 404 without mutations."""
    res = client.post(
        "/api/orders",
        json={"sku": "NON-EXISTENT-SKU", "quantity": 1, "logical_event_id": "EVT-UNKNOWN"},
    )
    assert res.status_code == 404


def test_reject_insufficient_stock(client: TestClient) -> None:
    """Orders exceeding available stock fail with 400 and preserve stock."""
    inv = client.get("/api/inventory/LAPTOP-001").json()
    available = inv["available_stock"]

    res = client.post(
        "/api/orders",
        json={"sku": "LAPTOP-001", "quantity": available + 50, "logical_event_id": "EVT-OVER"},
    )
    assert res.status_code == 400

    inv_after = client.get("/api/inventory/LAPTOP-001").json()
    assert inv_after["available_stock"] == available
