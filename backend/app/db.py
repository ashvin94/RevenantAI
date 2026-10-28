"""Database engine and request-session helpers."""

from __future__ import annotations

from collections.abc import Generator

from fastapi import Request
from sqlalchemy import Engine, event
from sqlmodel import SQLModel, Session, create_engine


def create_db_engine(database_url: str) -> Engine:
    """Create an engine and enable SQLite referential integrity per connection."""

    is_sqlite = database_url.startswith("sqlite")
    connect_args = {"check_same_thread": False} if is_sqlite else {}
    engine = create_engine(database_url, connect_args=connect_args)

    if is_sqlite:

        @event.listens_for(engine, "connect")
        def enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("PRAGMA foreign_keys=ON")
            finally:
                cursor.close()

    return engine


def get_session(request: Request) -> Generator[Session, None, None]:
    """Yield a short-lived session bound to this application instance."""

    with Session(request.app.state.engine) as session:
        yield session


def initialize_database(engine: Engine, *, demo_sku: str, initial_stock: int) -> None:
    """Create the MVP schema and seed inventory only when the SKU is absent."""

    from app.models import Inventory

    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        inventory = session.get(Inventory, demo_sku)
        if inventory is None:
            session.add(
                Inventory(
                    sku=demo_sku,
                    initial_stock=initial_stock,
                    available_stock=initial_stock,
                    version=0,
                )
            )
            session.commit()
