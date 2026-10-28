"""Read-only inventory endpoint for real database verification."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db import get_session
from app.models import Inventory
from app.schemas import InventoryResponse


router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("/{sku}", response_model=InventoryResponse)
def get_inventory(
    sku: str,
    session: Session = Depends(get_session),
) -> InventoryResponse:
    inventory = session.get(Inventory, sku)
    if inventory is None:
        raise HTTPException(status_code=404, detail="Inventory SKU not found.")
    return InventoryResponse(
        sku=inventory.sku,
        initial_stock=inventory.initial_stock,
        available_stock=inventory.available_stock,
        version=inventory.version,
    )

