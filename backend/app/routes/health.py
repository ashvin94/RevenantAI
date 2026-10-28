"""Public health endpoint with no secret-bearing fields."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text
from sqlmodel import Session

from app.config import Settings
from app.db import get_session
from app.schemas import HealthResponse


router = APIRouter(prefix="/api", tags=["health"])


def settings_from_request(request: Request) -> Settings:
    return request.app.state.settings


@router.get("/health", response_model=HealthResponse)
def health(
    settings: Settings = Depends(settings_from_request),
    session: Session = Depends(get_session),
) -> HealthResponse:
    database_status = "available"
    try:
        session.exec(text("SELECT 1")).one()
    except Exception:
        database_status = "unavailable"

    artifact_exists = settings.resolve_backend_path(
        settings.ml_artifact_path
    ).is_file()
    metadata_exists = settings.resolve_backend_path(
        settings.ml_metadata_path
    ).is_file()
    ml_status = "available" if artifact_exists and metadata_exists else "unavailable"
    ai_configured = settings.provider_is_configured()

    overall_status = (
        "ok"
        if database_status == "available"
        and ml_status == "available"
        and ai_configured
        else "degraded"
    )

    return HealthResponse(
        status=overall_status,
        database=database_status,
        ml=ml_status,
        ai_provider=settings.ai_provider,
        ai_configured=ai_configured,
        fault_injection_enabled=settings.enable_fault_injection,
        version=settings.app_version,
    )

