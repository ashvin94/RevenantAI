"""FastAPI application factory and development entry point."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import Settings, get_settings
from app.db import create_db_engine, initialize_database
from app.routes.health import router as health_router
from app.routes.incidents import router as incidents_router
from app.routes.inventory import router as inventory_router
from app.routes.orders import router as orders_router


def create_app(settings: Settings | None = None) -> FastAPI:
    """Create an isolated application instance for runtime or tests."""

    resolved_settings = settings or get_settings()
    app = FastAPI(
        title=resolved_settings.app_name,
        version=resolved_settings.app_version,
    )
    app.state.settings = resolved_settings
    engine = create_db_engine(resolved_settings.database_url)
    app.state.engine = engine
    initialize_database(
        engine,
        demo_sku=resolved_settings.demo_sku,
        initial_stock=resolved_settings.demo_initial_stock,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=[resolved_settings.allowed_origin],
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type", "Idempotency-Key"],
    )
    app.include_router(health_router)
    app.include_router(inventory_router)
    app.include_router(orders_router)
    app.include_router(incidents_router)
    return app


app = create_app()
