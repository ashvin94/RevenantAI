"""Normal order processing built around a reusable pure stock transition."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from sqlmodel import Session

from app.models import (
    Inventory,
    InventoryReservation,
    Order,
    ProcessedEvent,
    WorkflowEvent,
    utc_now,
)


class WorkflowError(Exception):
    """Base error for expected business-rule failures."""


class UnknownSkuError(WorkflowError):
    pass


class InsufficientStockError(WorkflowError):
    pass


class LogicalEventConflictError(WorkflowError):
    pass


@dataclass(frozen=True)
class InventoryState:
    sku: str
    available_stock: int
    version: int


@dataclass(frozen=True)
class ReservationTransition:
    previous: InventoryState
    current: InventoryState
    quantity: int


def reserve_inventory(state: InventoryState, quantity: int) -> ReservationTransition:
    """Calculate a reservation without accessing or mutating the database."""

    if quantity <= 0:
        raise ValueError("Reservation quantity must be positive.")
    if state.available_stock < quantity:
        raise InsufficientStockError(
            f"Insufficient stock for {state.sku}: requested {quantity}, "
            f"available {state.available_stock}."
        )
    return ReservationTransition(
        previous=state,
        current=InventoryState(
            sku=state.sku,
            available_stock=state.available_stock - quantity,
            version=state.version + 1,
        ),
        quantity=quantity,
    )


def create_normal_order(
    session: Session,
    *,
    sku: str,
    quantity: int,
    logical_event_id: str,
) -> tuple[Order, bool]:
    """Stage one correct order transaction, returning whether it was deduplicated."""

    processed = session.get(ProcessedEvent, logical_event_id)
    if processed is not None:
        order = session.get(Order, processed.order_id)
        if order is None:
            raise LogicalEventConflictError("Processed event references a missing order.")
        if order.sku != sku or order.quantity != quantity:
            raise LogicalEventConflictError(
                "Logical event already belongs to a different order payload."
            )
        return order, True

    inventory = session.get(Inventory, sku)
    if inventory is None:
        raise UnknownSkuError(f"Unknown SKU: {sku}")

    transition = reserve_inventory(
        InventoryState(
            sku=inventory.sku,
            available_stock=inventory.available_stock,
            version=inventory.version,
        ),
        quantity,
    )
    attempt_id = str(uuid4())
    now = utc_now()
    order = Order(
        sku=sku,
        quantity=quantity,
        status="INVENTORY_RESERVED",
        version=1,
        created_at=now,
        updated_at=now,
    )
    # Establish the parent row before dependent records. This remains inside
    # the caller's transaction, so any later failure rolls the order back too.
    session.add(order)
    session.flush()
    reservation = InventoryReservation(
        order_id=order.id,
        logical_event_id=logical_event_id,
        attempt_id=attempt_id,
        qty=quantity,
        status="ACTIVE",
        created_at=now,
    )
    event = WorkflowEvent(
        logical_event_id=logical_event_id,
        attempt_id=attempt_id,
        order_id=order.id,
        step="INVENTORY_RESERVED",
        result="SUCCESS_SIMULATED_PAYMENT_CONFIRMED",
        duration_ms=0,
        retry_no=0,
        created_at=now,
    )
    processed_event = ProcessedEvent(
        logical_event_id=logical_event_id,
        order_id=order.id,
        processed_at=now,
    )

    inventory.available_stock = transition.current.available_stock
    inventory.version = transition.current.version
    inventory.updated_at = now
    session.add(inventory)
    session.add(reservation)
    session.add(event)
    session.add(processed_event)
    session.flush()
    return order, False
