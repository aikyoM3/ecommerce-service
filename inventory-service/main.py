from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import os
from typing import List

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./inventory.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy models
class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, unique=True, index=True)
    stock = Column(Integer, default=0)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class InventoryBase(BaseModel):
    product_id: int
    stock: int

class InventoryCreate(InventoryBase):
    pass

class Inventory(InventoryBase):
    id: int

    class Config:
        orm_mode = True

class DeductRequest(BaseModel):
    items: List[dict]

app = FastAPI(title="Inventory Service")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Seed data
def seed_data():
    db = SessionLocal()
    if db.query(Inventory).first() is None:
        inventory_items = [
            Inventory(product_id=1, stock=10),
            Inventory(product_id=2, stock=20),
            Inventory(product_id=3, stock=15)
        ]
        db.add_all(inventory_items)
        db.commit()
    db.close()

# Seed data on startup
seed_data()

@app.get("/")
def read_root():
    return {"message": "Welcome to Inventory Service"}

@app.get("/inventory/{product_id}")
def get_inventory(product_id: int):
    db = SessionLocal()
    inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
    db.close()
    
    if inventory is None:
        raise HTTPException(status_code=404, detail="Product not found in inventory")
    
    return {"product_id": inventory.product_id, "stock": inventory.stock}

@app.post("/inventory/deduct")
def deduct_inventory(request: DeductRequest):
    db = SessionLocal()
    
    for item in request.items:
        inventory = db.query(Inventory).filter(Inventory.product_id == item["product_id"]).first()
        if inventory is None:
            db.close()
            raise HTTPException(status_code=404, detail=f"Product {item['product_id']} not found in inventory")
        
        if inventory.stock < item["quantity"]:
            db.close()
            raise HTTPException(status_code=400, detail=f"Insufficient stock for product {item['product_id']}")
        
        inventory.stock -= item["quantity"]
    
    db.commit()
    db.close()
    return {"message": "Inventory updated successfully"} 