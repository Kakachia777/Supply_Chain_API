from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from models.inventory import Inventory, InventoryTransaction, Warehouse
from schemas.inventory import (
    InventoryCreate,
    InventoryUpdate,
    TransactionCreate,
    WarehouseCreate
)

logger = logging.getLogger(__name__)

class InventoryService:
    """Service for inventory management operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_item(self, item: InventoryCreate) -> Inventory:
        """
        Create a new inventory item.
        
        Args:
            item: Inventory item data
            
        Returns:
            Created inventory item
            
        Raises:
            HTTPException: If item creation fails
        """
        try:
            db_item = Inventory(**item.dict())
            self.db.add(db_item)
            self.db.commit()
            self.db.refresh(db_item)
            
            logger.info(f"Created inventory item: {db_item.sku}")
            return db_item
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Failed to create inventory item: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Item with this SKU already exists"
            )
    
    def get_item(self, item_id: int) -> Optional[Inventory]:
        """
        Get inventory item by ID.
        
        Args:
            item_id: Item ID
            
        Returns:
            Inventory item if found, None otherwise
        """
        return self.db.query(Inventory).filter(Inventory.id == item_id).first()
    
    def get_items(
        self,
        skip: int = 0,
        limit: int = 100,
        warehouse_id: Optional[int] = None,
        category: Optional[str] = None
    ) -> List[Inventory]:
        """
        Get inventory items with optional filtering.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            warehouse_id: Optional warehouse filter
            category: Optional category filter
            
        Returns:
            List of inventory items
        """
        query = self.db.query(Inventory)
        
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        
        if category:
            query = query.filter(Inventory.category == category)
        
        return query.offset(skip).limit(limit).all()
    
    def update_item(self, item_id: int, item_update: InventoryUpdate) -> Optional[Inventory]:
        """
        Update inventory item.
        
        Args:
            item_id: Item ID
            item_update: Updated item data
            
        Returns:
            Updated inventory item
            
        Raises:
            HTTPException: If update fails
        """
        db_item = self.get_item(item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        for field, value in item_update.dict(exclude_unset=True).items():
            setattr(db_item, field, value)
        
        try:
            self.db.commit()
            self.db.refresh(db_item)
            logger.info(f"Updated inventory item: {db_item.sku}")
            return db_item
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Failed to update inventory item: {str(e)}")
            raise HTTPException(status_code=400, detail="Update failed")
    
    def create_transaction(self, transaction: TransactionCreate) -> InventoryTransaction:
        """
        Create inventory transaction and update item quantity.
        
        Args:
            transaction: Transaction data
            
        Returns:
            Created transaction
            
        Raises:
            HTTPException: If transaction creation fails
        """
        db_item = self.get_item(transaction.item_id)
        if not db_item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        # Calculate new quantity
        if transaction.transaction_type == "receive":
            new_quantity = db_item.quantity + transaction.quantity
        elif transaction.transaction_type == "issue":
            new_quantity = db_item.quantity - transaction.quantity
            if new_quantity < 0:
                raise HTTPException(
                    status_code=400,
                    detail="Insufficient stock"
                )
        else:
            new_quantity = transaction.quantity
        
        try:
            # Create transaction
            db_transaction = InventoryTransaction(**transaction.dict())
            self.db.add(db_transaction)
            
            # Update item quantity
            db_item.quantity = new_quantity
            db_item.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(db_transaction)
            
            logger.info(
                f"Created inventory transaction: {db_transaction.id}, "
                f"New quantity: {new_quantity}"
            )
            
            # Check reorder point
            if new_quantity <= db_item.reorder_point:
                logger.warning(
                    f"Item {db_item.sku} has reached reorder point. "
                    f"Current quantity: {new_quantity}"
                )
            
            return db_transaction
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to create transaction: {str(e)}")
            raise HTTPException(
                status_code=400,
                detail="Failed to create transaction"
            )
    
    def get_item_transactions(
        self,
        item_id: int,
        skip: int = 0,
        limit: int = 100
    ) -> List[InventoryTransaction]:
        """
        Get transactions for an item.
        
        Args:
            item_id: Item ID
            skip: Number of transactions to skip
            limit: Maximum number of transactions to return
            
        Returns:
            List of transactions
        """
        return (
            self.db.query(InventoryTransaction)
            .filter(InventoryTransaction.item_id == item_id)
            .order_by(InventoryTransaction.timestamp.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
    
    def get_low_stock_items(self) -> List[Inventory]:
        """
        Get items that have reached their reorder point.
        
        Returns:
            List of items with low stock
        """
        return (
            self.db.query(Inventory)
            .filter(Inventory.quantity <= Inventory.reorder_point)
            .all()
        )
    
    def get_stock_value(self, warehouse_id: Optional[int] = None) -> Dict[str, float]:
        """
        Calculate total stock value.
        
        Args:
            warehouse_id: Optional warehouse filter
            
        Returns:
            Dictionary with total value and currency breakdown
        """
        query = self.db.query(
            Inventory.currency,
            func.sum(Inventory.quantity * Inventory.unit_price).label("total_value")
        ).group_by(Inventory.currency)
        
        if warehouse_id:
            query = query.filter(Inventory.warehouse_id == warehouse_id)
        
        results = query.all()
        
        return {
            "total_value": sum(result.total_value for result in results),
            "by_currency": {
                result.currency: result.total_value
                for result in results
            }
        } 