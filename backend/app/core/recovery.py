"""Pure repair transitions shared by simulation and live recovery."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass


@dataclass
class ReservationSnapshot:
    id: str
    qty: int
    status: str


@dataclass
class RecoverySnapshot:
    available_stock: int
    inventory_version: int
    order_version: int
    reservations: list[ReservationSnapshot]


def release_duplicate(
    state: RecoverySnapshot, reservation_id: str
) -> RecoverySnapshot:
    """Return an independent repaired copy; never mutates the input."""
    repaired = deepcopy(state)
    matches = [r for r in repaired.reservations if r.id == reservation_id]
    if len(matches) != 1 or matches[0].status != "ACTIVE":
        raise ValueError("Target reservation is not uniquely active.")
    if sum(r.status == "ACTIVE" for r in repaired.reservations) != 2:
        raise ValueError("Expected exactly two active reservations before repair.")
    target = matches[0]
    target.status = "RELEASED"
    repaired.available_stock += target.qty
    repaired.inventory_version += 1
    repaired.order_version += 1
    return repaired


def snapshot_is_recovered(state: RecoverySnapshot, order_quantity: int) -> bool:
    active = [r for r in state.reservations if r.status == "ACTIVE"]
    return len(active) == 1 and sum(r.qty for r in active) == order_quantity
