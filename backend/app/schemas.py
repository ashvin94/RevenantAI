"""Shared Pydantic API contracts."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field


class HealthResponse(BaseModel):
    """Public, secret-free health response frozen for Phase 1 integration."""

    model_config = ConfigDict(extra="forbid")

    status: Literal["ok", "degraded"]
    database: Literal["available", "unavailable"]
    ml: Literal["available", "unavailable"]
    ai_provider: Literal["gemini", "groq", "unavailable"]
    ai_configured: bool
    fault_injection_enabled: bool
    version: str


class OrderCreateRequest(BaseModel):
    """Request schema for creating a new order."""

    model_config = ConfigDict(extra="forbid")

    sku: str = Field(min_length=1, max_length=64)
    quantity: int = Field(gt=0)
    logical_event_id: str = Field(min_length=1, max_length=128)


class OrderResponse(BaseModel):
    """Public representation of an order."""

    model_config = ConfigDict(extra="forbid")

    id: str
    sku: str
    quantity: int
    status: str
    version: int
    created_at: datetime
    updated_at: datetime


class ReservationResponse(BaseModel):
    """Public representation of an inventory reservation."""

    model_config = ConfigDict(extra="forbid")

    id: str
    order_id: str
    logical_event_id: str
    attempt_id: str
    quantity: int
    status: str
    created_at: datetime


class InventoryResponse(BaseModel):
    """Public inventory view."""

    model_config = ConfigDict(extra="forbid")

    sku: str
    initial_stock: int
    available_stock: int
    version: int


class OrderDetailResponse(BaseModel):
    """Detailed order view including its reservations."""

    model_config = ConfigDict(extra="forbid")

    order: OrderResponse
    reservations: list[ReservationResponse]


class ErrorDetail(BaseModel):
    model_config = ConfigDict(extra="forbid")

    code: str
    message: str
    request_id: str | None = None
    incident_id: str | None = None
    details: dict[str, Any] = Field(default_factory=dict)


class ErrorEnvelope(BaseModel):
    model_config = ConfigDict(extra="forbid")

    error: ErrorDetail


class FaultInjectionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str
    logical_event_id: str
    injected_reservation_id: str
    active_reservation_count: int
    order_version: int
    message: str


class InvariantResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    passed: bool
    expected: int | str
    actual: int | str
    evidence_ids: list[str]


class IncidentResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    order_id: str
    source: str
    type: str
    status: str
    evidence: dict[str, Any]
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None


class InspectionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    order_id: str
    healthy: bool
    rules: list[InvariantResult]
    incident: IncidentResponse | None


class RecoveryCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: Literal["RELEASE_DUPLICATE"]
    reservation_id: str
    action: Literal["RELEASE_RESERVATION"] = "RELEASE_RESERVATION"


class SimulationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate: RecoveryCandidate


class SimulationResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    incident_id: str
    candidate: RecoveryCandidate
    safe: bool
    before_available_stock: int
    after_available_stock: int
    active_reservations_after: int
    expected_order_version: int


class RecoveryRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    candidate: RecoveryCandidate
    expected_order_version: int = Field(ge=1)
    idempotency_key: str = Field(min_length=8, max_length=200)
    approved: Literal[True]


class RecoveryResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    execution_id: str
    incident_id: str
    status: Literal["COMMITTED", "REPLAYED"]
    released_reservation_id: str
    available_stock: int
    active_reservations: int
    verified: bool


class RootCauseProposal(BaseModel):
    """Strictly typed, non-executable AI output."""

    model_config = ConfigDict(extra="forbid")

    root_cause: str = Field(min_length=1, max_length=500)
    confidence: float = Field(ge=0, le=1)
    candidate: RecoveryCandidate
    evidence_ids: list[str] = Field(min_length=1)


class AnalysisResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    incident_id: str
    provider: Literal["gemini", "groq"]
    proposal: RootCauseProposal

class MLScoreResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")
    order_id: str
    available: bool
    suspicious: bool | None = None
    score: float | None = None
    reason: str | None = None
    synthetic_metrics: dict[str, Any] | None = None
