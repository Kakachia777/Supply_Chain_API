from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from core.deps import get_db
from schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    InventoryResponse,
    TransactionCreate,
    TransactionResponse,
    StockValueResponse
)
from services.inventory import InventoryService

router = APIRouter()

@router.post("/items/", response_model=InventoryResponse)
def create_item(
    *,
    db: Session = Depends(get_db),
    item: InventoryCreate
) -> InventoryResponse:
    """
    Create new inventory item.
    """
    service = InventoryService(db)
    return service.create_item(item)

@router.get("/items/", response_model=List[InventoryResponse])
def get_items(
    *,
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    warehouse_id: Optional[int] = None,
    category: Optional[str] = None
) -> List[InventoryResponse]:
    """
    Retrieve inventory items with optional filtering.
    """
    service = InventoryService(db)
    return service.get_items(
        skip=skip,
        limit=limit,
        warehouse_id=warehouse_id,
        category=category
    )

@router.get("/items/{item_id}", response_model=InventoryResponse)
def get_item(
    *,
    db: Session = Depends(get_db),
    item_id: int
) -> InventoryResponse:
    """
    Get specific inventory item by ID.
    """
    service = InventoryService(db)
    item = service.get_item(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@router.put("/items/{item_id}", response_model=InventoryResponse)
def update_item(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    item_update: InventoryUpdate
) -> InventoryResponse:
    """
    Update inventory item.
    """
    service = InventoryService(db)
    return service.update_item(item_id, item_update)

@router.post("/transactions/", response_model=TransactionResponse)
def create_transaction(
    *,
    db: Session = Depends(get_db),
    transaction: TransactionCreate
) -> TransactionResponse:
    """
    Create inventory transaction.
    """
    service = InventoryService(db)
    return service.create_transaction(transaction)

@router.get("/items/{item_id}/transactions/", response_model=List[TransactionResponse])
def get_item_transactions(
    *,
    db: Session = Depends(get_db),
    item_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100)
) -> List[TransactionResponse]:
    """
    Get transactions for specific item.
    """
    service = InventoryService(db)
    return service.get_item_transactions(
        item_id=item_id,
        skip=skip,
        limit=limit
    )

@router.get("/low-stock/", response_model=List[InventoryResponse])
def get_low_stock_items(
    *,
    db: Session = Depends(get_db)
) -> List[InventoryResponse]:
    """
    Get items with stock level at or below reorder point.
    """
    service = InventoryService(db)
    return service.get_low_stock_items()

@router.get("/stock-value/", response_model=StockValueResponse)
def get_stock_value(
    *,
    db: Session = Depends(get_db),
    warehouse_id: Optional[int] = None
) -> StockValueResponse:
    """
    Get total stock value with optional warehouse filter.
    """
    service = InventoryService(db)
    return service.get_stock_value(warehouse_id=warehouse_id)

@router.get("/metrics/")
def get_inventory_metrics(
    *,
    db: Session = Depends(get_db)
) -> dict:
    """
    Get inventory metrics for monitoring.
    """
    service = InventoryService(db)
    
    # Get various metrics
    total_items = len(service.get_items())
    low_stock_items = len(service.get_low_stock_items())
    stock_value = service.get_stock_value()
    
    return {
        "total_items": total_items,
        "low_stock_items": low_stock_items,
        "stock_value": stock_value,
        "low_stock_percentage": (low_stock_items / total_items * 100) if total_items > 0 else 0
    } 