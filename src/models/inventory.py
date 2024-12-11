from typing import Optional
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum

from db.base_class import Base

class ItemCategory(str, enum.Enum):
    RAW_MATERIAL = "raw_material"
    FINISHED_GOOD = "finished_good"
    PACKAGING = "packaging"
    SPARE_PART = "spare_part"

class UnitOfMeasure(str, enum.Enum):
    PIECE = "piece"
    KILOGRAM = "kg"
    LITER = "liter"
    METER = "meter"
    BOX = "box"

class Inventory(Base):
    """Model for inventory items."""
    
    __tablename__ = "inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    sku = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    category = Column(Enum(ItemCategory), nullable=False)
    unit = Column(Enum(UnitOfMeasure), nullable=False)
    
    # Stock information
    quantity = Column(Float, nullable=False, default=0)
    reorder_point = Column(Float, nullable=False)
    reorder_quantity = Column(Float, nullable=False)
    
    # Location information
    warehouse_id = Column(Integer, ForeignKey("warehouse.id"), nullable=False)
    location = Column(String)  # Specific location within warehouse
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Price information
    unit_price = Column(Float)
    currency = Column(String, default="USD")
    
    # Relationships
    warehouse = relationship("Warehouse", back_populates="inventory_items")
    transactions = relationship("InventoryTransaction", back_populates="item")
    
    def __repr__(self):
        return f"<Inventory(sku={self.sku}, name={self.name}, quantity={self.quantity})>"

class InventoryTransaction(Base):
    """Model for inventory transactions."""
    
    __tablename__ = "inventory_transaction"
    
    id = Column(Integer, primary_key=True, index=True)
    item_id = Column(Integer, ForeignKey("inventory.id"), nullable=False)
    transaction_type = Column(String, nullable=False)  # receive, issue, adjust
    quantity = Column(Float, nullable=False)
    reference = Column(String)  # PO number, SO number, etc.
    
    # Tracking
    timestamp = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String, nullable=False)
    notes = Column(String)
    
    # Relationships
    item = relationship("Inventory", back_populates="transactions")
    
    def __repr__(self):
        return f"<InventoryTransaction(item_id={self.item_id}, type={self.transaction_type}, quantity={self.quantity})>"

class Warehouse(Base):
    """Model for warehouses."""
    
    __tablename__ = "warehouse"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    address = Column(String, nullable=False)
    
    # Contact information
    contact_person = Column(String)
    contact_email = Column(String)
    contact_phone = Column(String)
    
    # Capacity information
    total_capacity = Column(Float)  # in cubic meters
    used_capacity = Column(Float, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Tracking
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    inventory_items = relationship("Inventory", back_populates="warehouse")
    
    def __repr__(self):
        return f"<Warehouse(code={self.code}, name={self.name})>" 