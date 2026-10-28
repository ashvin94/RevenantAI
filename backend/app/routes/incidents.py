"""Incident inspection, simulation, and approved recovery endpoints."""

import json

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session, select

from app.core.ai import AIUnavailableError, propose_recovery
from app.core.recovery import RecoverySnapshot, ReservationSnapshot, release_duplicate, snapshot_is_recovered
from app.db import get_session
from app.models import Incident, Inventory, InventoryReservation, Order, RecoveryExecution, utc_now
from app.schemas import AnalysisResponse, IncidentResponse, RecoveryRequest, RecoveryResponse, SimulationRequest, SimulationResponse


router = APIRouter(prefix="/api/incidents", tags=["incidents"])


def _state(session: Session, incident: Incident):
    order = session.get(Order, incident.order_id)
    if order is None:
        raise HTTPException(409, "Incident order is missing.")
    inventory = session.get(Inventory, order.sku)
    reservations = session.exec(select(InventoryReservation).where(InventoryReservation.order_id == order.id)).all()
    if inventory is None:
        raise HTTPException(409, "Incident inventory is missing.")
    snapshot = RecoverySnapshot(
        available_stock=inventory.available_stock,
        inventory_version=inventory.version,
        order_version=order.version,
        reservations=[ReservationSnapshot(id=r.id, qty=r.qty, status=r.status) for r in reservations],
    )
    return order, inventory, reservations, snapshot


def to_response(incident: Incident) -> IncidentResponse:
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


@router.get("", response_model=list[IncidentResponse])
def list_incidents(session: Session = Depends(get_session)) -> list[IncidentResponse]:
    incidents = session.exec(
        select(Incident).order_by(Incident.created_at.desc())
    ).all()
    return [to_response(item) for item in incidents]


@router.get("/{incident_id}", response_model=IncidentResponse)
def get_incident(
    incident_id: str,
    session: Session = Depends(get_session),
) -> IncidentResponse:
    incident = session.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found.")
    return to_response(incident)


@router.post("/{incident_id}/analyze", response_model=AnalysisResponse)
def analyze_incident(incident_id: str, request: Request, session: Session = Depends(get_session)) -> AnalysisResponse:
    incident = session.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(404, "Incident not found.")
    try:
        proposal = propose_recovery(request.app.state.settings, json.loads(incident.evidence_json))
    except AIUnavailableError as exc:
        raise HTTPException(503, str(exc)) from exc
    except Exception as exc:
        # Provider failures are unavailable, never an internal server crash or fake plan.
        raise HTTPException(503, f"AI provider request failed: {type(exc).__name__}") from exc
    active_ids = {
        r.id for r in session.exec(select(InventoryReservation).where(
            InventoryReservation.order_id == incident.order_id,
            InventoryReservation.status == "ACTIVE",
        )).all()
    }
    if proposal.candidate.reservation_id not in active_ids:
        raise HTTPException(422, "AI proposal target is not supported by current evidence.")
    evidence_ids = set(active_ids) | {incident.order_id, incident.id}
    if not set(proposal.evidence_ids).issubset(evidence_ids):
        raise HTTPException(422, "AI proposal cites unknown evidence.")
    return AnalysisResponse(incident_id=incident.id, provider=request.app.state.settings.ai_provider, proposal=proposal)


@router.post("/{incident_id}/simulate", response_model=SimulationResponse)
def simulate_recovery(incident_id: str, payload: SimulationRequest, session: Session = Depends(get_session)) -> SimulationResponse:
    incident = session.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(404, "Incident not found.")
    if incident.status != "OPEN":
        raise HTTPException(409, "Incident is not open.")
    order, _inventory, _reservations, before = _state(session, incident)
    try:
        after = release_duplicate(before, payload.candidate.reservation_id)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    return SimulationResponse(
        incident_id=incident.id, candidate=payload.candidate,
        safe=snapshot_is_recovered(after, order.quantity),
        before_available_stock=before.available_stock,
        after_available_stock=after.available_stock,
        active_reservations_after=sum(r.status == "ACTIVE" for r in after.reservations),
        expected_order_version=before.order_version,
    )


@router.post("/{incident_id}/recover", response_model=RecoveryResponse)
def recover_incident(incident_id: str, payload: RecoveryRequest, session: Session = Depends(get_session)) -> RecoveryResponse:
    replay = session.exec(select(RecoveryExecution).where(RecoveryExecution.idempotency_key == payload.idempotency_key)).first()
    if replay is not None:
        return RecoveryResponse(**json.loads(replay.result_json), status="REPLAYED")
    incident = session.get(Incident, incident_id)
    if incident is None:
        raise HTTPException(404, "Incident not found.")
    if incident.status != "OPEN":
        raise HTTPException(409, "Incident is not open.")
    order, inventory, reservations, before = _state(session, incident)
    if order.version != payload.expected_order_version:
        raise HTTPException(409, "Order version changed; simulate again.")
    try:
        simulated = release_duplicate(before, payload.candidate.reservation_id)
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    if not snapshot_is_recovered(simulated, order.quantity):
        raise HTTPException(409, "Candidate failed independent verification.")
    target = next((r for r in reservations if r.id == payload.candidate.reservation_id), None)
    if target is None or target.status != "ACTIVE":
        raise HTTPException(409, "Exact target is no longer active.")
    now = utc_now()
    target.status, target.released_at = "RELEASED", now
    inventory.available_stock += target.qty
    inventory.version += 1
    inventory.updated_at = now
    order.version += 1
    order.updated_at = now
    incident.status, incident.updated_at, incident.resolved_at = "RECOVERED", now, now
    execution = RecoveryExecution(
        incident_id=incident.id, idempotency_key=payload.idempotency_key,
        candidate_id=payload.candidate.id, released_reservation_id=target.id,
        expected_order_version=payload.expected_order_version, result_json="{}",
    )
    session.add(execution)
    session.flush()
    active_after = session.exec(select(InventoryReservation).where(InventoryReservation.order_id == order.id, InventoryReservation.status == "ACTIVE")).all()
    verified = len(active_after) == 1 and sum(r.qty for r in active_after) == order.quantity
    if not verified or inventory.available_stock != simulated.available_stock:
        session.rollback()
        raise HTTPException(409, "Post-change verification failed; transaction rolled back.")
    result = {"execution_id": execution.id, "incident_id": incident.id, "released_reservation_id": target.id, "available_stock": inventory.available_stock, "active_reservations": 1, "verified": True}
    execution.result_json = json.dumps(result, sort_keys=True)
    session.add(execution)
    session.commit()
    return RecoveryResponse(**result, status="COMMITTED")
