"""Deterministic business invariants derived only from persisted state."""

from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass

from app.models import Inventory, InventoryReservation, Order


@dataclass(frozen=True)
class InvariantCheck:
    id: str
    passed: bool
    expected: int | str
    actual: int | str
    evidence_ids: list[str]

    def to_dict(self) -> dict:
        return asdict(self)


def inspect_order_state(
    *,
    order: Order,
    inventory: Inventory,
    reservations: list[InventoryReservation],
    all_sku_reservations: list[InventoryReservation],
) -> list[InvariantCheck]:
    active = [item for item in reservations if item.status == "ACTIVE"]
    active_qty = sum(item.qty for item in active)
    event_counts = Counter(item.logical_event_id for item in active)
    max_event_count = max(event_counts.values(), default=0)
    all_active_qty = sum(
        item.qty for item in all_sku_reservations if item.status == "ACTIVE"
    )

    return [
        InvariantCheck(
            id="RESERVATION_QUANTITY_MATCH",
            passed=active_qty == order.quantity,
            expected=order.quantity,
            actual=active_qty,
            evidence_ids=[item.id for item in active],
        ),
        InvariantCheck(
            id="NO_DUPLICATE_ACTIVE_EVENT",
            passed=max_event_count <= 1,
            expected="at_most_1_active_reservation_per_logical_event",
            actual=max_event_count,
            evidence_ids=[item.id for item in active],
        ),
        InvariantCheck(
            id="NON_NEGATIVE_AVAILABLE_STOCK",
            passed=inventory.available_stock >= 0,
            expected=">=0",
            actual=inventory.available_stock,
            evidence_ids=[inventory.sku],
        ),
        InvariantCheck(
            id="STOCK_CONSERVATION",
            passed=inventory.available_stock
            == inventory.initial_stock - all_active_qty,
            expected=inventory.initial_stock - all_active_qty,
            actual=inventory.available_stock,
            evidence_ids=[inventory.sku]
            + [item.id for item in all_sku_reservations if item.status == "ACTIVE"],
        ),
    ]
