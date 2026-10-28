"""Health contract, CORS, database, and redaction tests."""

from __future__ import annotations

from collections.abc import Generator

from fastapi.testclient import TestClient
from pydantic import SecretStr

from app.config import Settings
from app.db import get_session
from app.main import create_app


EXPECTED_FIELDS = {
    "status",
    "database",
    "ml",
    "ai_provider",
    "ai_configured",
    "fault_injection_enabled",
    "version",
}


def test_health_returns_frozen_degraded_contract(client: TestClient) -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    payload = response.json()
    assert set(payload) == EXPECTED_FIELDS
    assert payload == {
        "status": "degraded",
        "database": "available",
        "ml": "unavailable",
        "ai_provider": "gemini",
        "ai_configured": False,
        "fault_injection_enabled": True,
        "version": "0.1.0",
    }


def test_health_reports_ok_when_all_dependencies_are_present(
    settings: Settings,
) -> None:
    artifact = settings.ml_artifact_path
    metadata = settings.ml_metadata_path
    artifact.write_bytes(b"test-only-artifact")
    metadata.write_text("{}", encoding="utf-8")
    configured = settings.model_copy(
        update={"gemini_api_key": SecretStr("test-secret-not-a-real-key")}
    )
    app = create_app(configured)

    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["ai_configured"] is True
    assert "test-secret-not-a-real-key" not in response.text
    app.state.engine.dispose()


def test_health_reports_database_unavailable_without_leaking_exception(
    settings: Settings,
) -> None:
    class BrokenSession:
        def exec(self, _statement) -> None:
            raise RuntimeError("database-path-and-secret-must-not-leak")

    def broken_session() -> Generator[BrokenSession, None, None]:
        yield BrokenSession()

    app = create_app(settings)
    app.dependency_overrides[get_session] = broken_session
    with TestClient(app) as client:
        response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json()["database"] == "unavailable"
    assert response.json()["status"] == "degraded"
    assert "database-path-and-secret-must-not-leak" not in response.text
    app.dependency_overrides.clear()
    app.state.engine.dispose()


def test_cors_allows_only_configured_origin(client: TestClient) -> None:
    allowed = client.options(
        "/api/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    rejected = client.options(
        "/api/health",
        headers={
            "Origin": "https://untrusted.example",
            "Access-Control-Request-Method": "GET",
        },
    )

    assert allowed.status_code == 200
    assert allowed.headers["access-control-allow-origin"] == "http://localhost:5173"
    assert "access-control-allow-origin" not in rejected.headers


def test_openapi_exposes_health_response_schema(client: TestClient) -> None:
    response = client.get("/openapi.json")

    assert response.status_code == 200
    schema = response.json()
    health_operation = schema["paths"]["/api/health"]["get"]
    response_schema = health_operation["responses"]["200"]["content"][
        "application/json"
    ]["schema"]
    assert response_schema["$ref"].endswith("/HealthResponse")
