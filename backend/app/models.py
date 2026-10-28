"""Persisted business entities for the simulated order workflow."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import CheckConstraint
from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    return datetime.now(UTC)


def new_id() -> str:
    return str(uuid4())


class Order(SQLModel, table=True):
    __tablename__ = "orders"
    __table_args__ = (CheckConstraint("quantity > 0", name="ck_orders_quantity_positive"),)

    id: str = Field(default_factory=new_id, primary_key=True)
    sku: str = Field(index=True, max_length=100)
    quantity: int
    status: str = Field(default="INVENTORY_RESERVED", max_length=40)
    version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)


class Inventory(SQLModel, table=True):
    __tablename__ = "inventory"
    __table_args__ = (
        CheckConstraint("initial_stock >= 0", name="ck_inventory_initial_nonnegative"),
        CheckConstraint("available_stock >= 0", name="ck_inventory_available_nonnegative"),
        CheckConstraint(
            "available_stock <= initial_stock",
            name="ck_inventory_available_not_above_initial",
        ),
    )

    sku: str = Field(primary_key=True, max_length=100)
    initial_stock: int
    available_stock: int
    version: int = Field(default=0, ge=0)
    updated_at: datetime = Field(default_factory=utc_now)


class InventoryReservation(SQLModel, table=True):
    __tablename__ = "inventory_reservations"
    __table_args__ = (
        CheckConstraint("qty > 0", name="ck_reservations_qty_positive"),
    )

    id: str = Field(default_factory=new_id, primary_key=True)
    order_id: str = Field(foreign_key="orders.id", index=True)
    logical_event_id: str = Field(index=True, max_length=100)
    attempt_id: str = Field(index=True, max_length=100)
    qty: int
    status: str = Field(default="ACTIVE", index=True, max_length=20)
    created_at: datetime = Field(default_factory=utc_now)
    committed_at: datetime | None = None
    released_at: datetime | None = None


class WorkflowEvent(SQLModel, table=True):
    __tablename__ = "workflow_events"
    __table_args__ = (
        CheckConstraint("duration_ms >= 0", name="ck_events_duration_nonnegative"),
        CheckConstraint("retry_no >= 0", name="ck_events_retry_nonnegative"),
    )

    id: str = Field(default_factory=new_id, primary_key=True)
    logical_event_id: str = Field(index=True, max_length=100)
    attempt_id: str = Field(index=True, max_length=100)
    order_id: str = Field(foreign_key="orders.id", index=True)
    step: str = Field(max_length=50)
    result: str = Field(max_length=50)
    duration_ms: int = 0
    retry_no: int = 0
    created_at: datetime = Field(default_factory=utc_now)


class ProcessedEvent(SQLModel, table=True):
    __tablename__ = "processed_events"

    logical_event_id: str = Field(primary_key=True, max_length=100)
    order_id: str = Field(foreign_key="orders.id", index=True)
    processed_at: datetime = Field(default_factory=utc_now)


class Incident(SQLModel, table=True):
    __tablename__ = "incidents"

    id: str = Field(default_factory=new_id, primary_key=True)
    order_id: str = Field(foreign_key="orders.id", index=True)
    fingerprint: str = Field(unique=True, index=True, max_length=200)
    source: str = Field(default="RULE", index=True, max_length=20)
    type: str = Field(default="DUPLICATE_RESERVATION", index=True, max_length=60)
    status: str = Field(default="OPEN", index=True, max_length=30)
    evidence_json: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    resolved_at: datetime | None = None


class RecoveryExecution(SQLModel, table=True):
    __tablename__ = "recovery_executions"

    id: str = Field(default_factory=new_id, primary_key=True)
    incident_id: str = Field(foreign_key="incidents.id", index=True)
    idempotency_key: str = Field(unique=True, index=True, max_length=200)
    candidate_id: str = Field(max_length=60)
    released_reservation_id: str = Field(max_length=100)
    expected_order_version: int
    status: str = Field(default="COMMITTED", max_length=30)
    result_json: str
    created_at: datetime = Field(default_factory=utc_now)
