"""Normal order, controlled fault injection, and inspection API routes."""

from __future__ import annotations

import json
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.core.invariants import inspect_order_state
from app.core.ml import score_features
from app.core.workflow import (
    InventoryState,
    InsufficientStockError,
    LogicalEventConflictError,
    UnknownSkuError,
    create_normal_order,
    reserve_inventory,
)
from app.db import get_session
from app.models import (
    Incident,
    Inventory,
    InventoryReservation,
    Order,
    ProcessedEvent,
    WorkflowEvent,
    utc_now,
)
from app.schemas import (
    FaultInjectionResponse,
    IncidentResponse,
    InspectionResponse,
    InvariantResult,
    MLScoreResponse,
    OrderCreateRequest,
    OrderDetailResponse,
    OrderResponse,
    ReservationResponse,
)


router = APIRouter(prefix="/api/orders", tags=["orders"])


def incident_response(incident: Incident) -> IncidentResponse:
    return IncidentResponse(
        id=incident.id,
        order_id=incident.order_id,
        source=incident.source,
        type=incident.type,
        status=incident.status,
        evidence=json.loads(incident.evidence_json),
        created_at=incident.created_at,
        updated_at=incident.updated_at,
        resolved_at=incident.resolved_at,
    )


def order_response(order: Order) -> OrderResponse:
    return OrderResponse(
        id=order.id,
        sku=order.sku,
        quantity=order.quantity,
        status=order.status,
        version=order.version,
        created_at=order.created_at,
        updated_at=order.updated_at,
    )


def order_detail(session: Session, order: Order) -> OrderDetailResponse:
    reservations = session.exec(
        select(InventoryReservation)
        .where(InventoryReservation.order_id == order.id)
        .order_by(InventoryReservation.created_at, InventoryReservation.id)
    ).all()
    return OrderDetailResponse(
        order=order_response(order),
        reservations=[
            ReservationResponse(
                id=item.id,
                order_id=item.order_id,
                logical_event_id=item.logical_event_id,
                attempt_id=item.attempt_id,
                quantity=item.qty,
                status=item.status,
                created_at=item.created_at,
            )
            for item in reservations
        ],
    )


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: OrderCreateRequest,
    session: Session = Depends(get_session),
) -> OrderResponse:
    try:
        order, _deduplicated = create_normal_order(
            session,
            sku=payload.sku,
            quantity=payload.quantity,
            logical_event_id=payload.logical_event_id,
        )
        session.commit()
    except UnknownSkuError as exc:
        session.rollback()
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InsufficientStockError as exc:
        session.rollback()
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except LogicalEventConflictError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    except IntegrityError as exc:
        session.rollback()
        processed = session.get(ProcessedEvent, payload.logical_event_id)
        if processed is None:
            raise HTTPException(
                status_code=409,
                detail="Order could not be created because of a concurrent conflict.",
            ) from exc
        order = session.get(Order, processed.order_id)
        if order is None or order.sku != payload.sku or order.quantity != payload.quantity:
            raise HTTPException(
                status_code=409,
                detail="Logical event conflicts with another order.",
            ) from exc

    session.refresh(order)
    return order_response(order)


@router.get("/{order_id}", response_model=OrderDetailResponse)
def get_order(
    order_id: str,
    session: Session = Depends(get_session),
) -> OrderDetailResponse:
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")
    return order_detail(session, order)


@router.post("/{order_id}/inject-duplicate", response_model=FaultInjectionResponse)
def inject_duplicate(
    order_id: str,
    request: Request,
    session: Session = Depends(get_session),
) -> FaultInjectionResponse:
    if not request.app.state.settings.enable_fault_injection:
        raise HTTPException(status_code=403, detail="Demo fault injection is disabled.")

    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")
    if order.status != "INVENTORY_RESERVED":
        raise HTTPException(status_code=409, detail="Order cannot accept this demo fault.")

    active = session.exec(
        select(InventoryReservation).where(
            InventoryReservation.order_id == order.id,
            InventoryReservation.status == "ACTIVE",
        )
    ).all()
    if len(active) != 1:
        raise HTTPException(
            status_code=409,
            detail="Controlled duplicate fault can be injected exactly once.",
        )

    inventory = session.get(Inventory, order.sku)
    if inventory is None:
        raise HTTPException(status_code=409, detail="Order inventory is unavailable.")
    try:
        transition = reserve_inventory(
            InventoryState(
                sku=inventory.sku,
                available_stock=inventory.available_stock,
                version=inventory.version,
            ),
            order.quantity,
        )
    except InsufficientStockError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc

    now = utc_now()
    attempt_id = str(uuid4())
    duplicate = InventoryReservation(
        order_id=order.id,
        logical_event_id=active[0].logical_event_id,
        attempt_id=attempt_id,
        qty=order.quantity,
        status="ACTIVE",
        created_at=now,
    )
    event = WorkflowEvent(
        logical_event_id=active[0].logical_event_id,
        attempt_id=attempt_id,
        order_id=order.id,
        step="INVENTORY_RESERVED",
        result="SUCCESS_CONTROLLED_DUPLICATE_FAULT",
        duration_ms=0,
        retry_no=1,
        created_at=now,
    )
    inventory.available_stock = transition.current.available_stock
    inventory.version = transition.current.version
    inventory.updated_at = now
    order.version += 1
    order.updated_at = now
    session.add(inventory)
    session.add(order)
    session.add(duplicate)
    session.add(event)
    try:
        session.commit()
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Fault injection conflicted.") from exc

    return FaultInjectionResponse(
        order_id=order.id,
        logical_event_id=duplicate.logical_event_id,
        injected_reservation_id=duplicate.id,
        active_reservation_count=2,
        order_version=order.version,
        message="Controlled duplicate reservation fault injected successfully.",
    )


@router.post("/{order_id}/inspect", response_model=InspectionResponse)
def inspect_order(
    order_id: str,
    session: Session = Depends(get_session),
) -> InspectionResponse:
    order = session.get(Order, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found.")
    inventory = session.get(Inventory, order.sku)
    if inventory is None:
        raise HTTPException(status_code=409, detail="Order inventory is unavailable.")

    reservations = session.exec(
        select(InventoryReservation).where(
            InventoryReservation.order_id == order.id
        )
    ).all()
    all_sku_reservations = session.exec(
        select(InventoryReservation)
        .join(Order, InventoryReservation.order_id == Order.id)
        .where(Order.sku == order.sku)
    ).all()
    events = session.exec(
        select(WorkflowEvent).where(WorkflowEvent.order_id == order.id)
    ).all()
    checks = inspect_order_state(
        order=order,
        inventory=inventory,
        reservations=list(reservations),
        all_sku_reservations=list(all_sku_reservations),
    )
    healthy = all(check.passed for check in checks)
    incident = None

    if not healthy:
        fingerprint = f"DUPLICATE_RESERVATION:{order.id}"
        incident = session.exec(
            select(Incident).where(Incident.fingerprint == fingerprint)
        ).first()
        evidence = {
            "order": {
                "id": order.id,
                "sku": order.sku,
                "quantity": order.quantity,
                "version": order.version,
            },
            "inventory": {
                "sku": inventory.sku,
                "initial_stock": inventory.initial_stock,
                "available_stock": inventory.available_stock,
                "version": inventory.version,
            },
            "reservations": [
                {
                    "id": item.id,
                    "logical_event_id": item.logical_event_id,
                    "attempt_id": item.attempt_id,
                    "qty": item.qty,
                    "status": item.status,
                }
                for item in reservations
            ],
            "events": [
                {
                    "id": item.id,
                    "logical_event_id": item.logical_event_id,
                    "attempt_id": item.attempt_id,
                    "step": item.step,
                    "result": item.result,
                    "retry_no": item.retry_no,
                }
                for item in events
            ],
            "rules": [check.to_dict() for check in checks],
        }
        now = utc_now()
        if incident is None:
            incident = Incident(
                order_id=order.id,
                fingerprint=fingerprint,
                source="RULE",
                type="DUPLICATE_RESERVATION",
                status="OPEN",
                evidence_json=json.dumps(evidence, sort_keys=True),
                created_at=now,
                updated_at=now,
            )
        else:
            incident.evidence_json = json.dumps(evidence, sort_keys=True)
            incident.updated_at = now
        session.add(incident)
        session.commit()
        session.refresh(incident)

    return InspectionResponse(
        order_id=order.id,
        healthy=healthy,
        rules=[InvariantResult(**check.to_dict()) for check in checks],
        incident=incident_response(incident) if incident else None,
    )

@router.get("/{order_id}/ml-score", response_model=MLScoreResponse)
def ml_score(order_id: str, request: Request, session: Session = Depends(get_session)) -> MLScoreResponse:
    order = session.get(Order, order_id)
    if order is None: raise HTTPException(404, "Order not found.")
    reservations = session.exec(select(InventoryReservation).where(InventoryReservation.order_id == order.id, InventoryReservation.status == "ACTIVE")).all()
    events = session.exec(select(WorkflowEvent).where(WorkflowEvent.order_id == order.id)).all()
    settings = request.app.state.settings
    scored = score_features(settings.resolve_backend_path(settings.ml_artifact_path), settings.resolve_backend_path(settings.ml_metadata_path), [max((e.duration_ms for e in events), default=0), max((e.retry_no for e in events), default=0), len(reservations), order.quantity * len(reservations)])
    return MLScoreResponse(order_id=order.id, available=scored.available, suspicious=scored.suspicious, score=scored.score, reason=scored.reason, synthetic_metrics=scored.metadata)
