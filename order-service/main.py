from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
import os
import httpx
from datetime import datetime
from typing import List, Dict

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./orders.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy models
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    items = Column(JSON)  # List of {product_id, quantity, price}
    total_amount = Column(Float)
    status = Column(String, default="pending")
    created_at = Column(String, default=lambda: datetime.now().isoformat())

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class OrderItem(BaseModel):
    product_id: int
    quantity: int

class OrderCreate(BaseModel):
    user_id: int
    items: List[OrderItem]

class Order(BaseModel):
    id: int
    user_id: int
    items: List[Dict]
    total_amount: float
    status: str
    created_at: str

    class Config:
        orm_mode = True

app = FastAPI(title="Order Service")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def check_inventory(items: List[OrderItem]) -> bool:
    async with httpx.AsyncClient() as client:
        for item in items:
            try:
                response = await client.get(f"http://inventory-service:8000/inventory/{item.product_id}")
                if response.status_code != 200:
                    return False
                inventory = response.json()
                if inventory["stock"] < item.quantity:
                    return False
            except:
                return False
    return True

async def deduct_inventory(items: List[OrderItem]) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "http://inventory-service:8000/inventory/deduct",
                json={"items": [{"product_id": item.product_id, "quantity": item.quantity} for item in items]}
            )
            return response.status_code == 200
        except:
            return False

async def notify_analytics(order_data: dict):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://analytics-service:8000/analytics/event",
                json={"type": "order_placed", "data": order_data}
            )
        except:
            pass  # Analytics notification is not critical

@app.get("/")
def read_root():
    return {"message": "Welcome to Order Service"}

@app.post("/orders", response_model=Order)
async def create_order(order: OrderCreate):
    # Check inventory
    if not await check_inventory(order.items):
        raise HTTPException(status_code=400, detail="Insufficient inventory")
    
    # Get product prices and calculate total
    total_amount = 0
    order_items = []
    
    async with httpx.AsyncClient() as client:
        for item in order.items:
            try:
                response = await client.get(f"http://product-service:8000/products/{item.product_id}")
                if response.status_code != 200:
                    raise HTTPException(status_code=404, detail=f"Product {item.product_id} not found")
                product = response.json()
                total_amount += product["price"] * item.quantity
                order_items.append({
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": product["price"]
                })
            except:
                raise HTTPException(status_code=500, detail="Error fetching product information")
    
    # Deduct inventory
    if not await deduct_inventory(order.items):
        raise HTTPException(status_code=500, detail="Failed to update inventory")
    
    # Create order
    db = SessionLocal()
    db_order = Order(
        user_id=order.user_id,
        items=order_items,
        total_amount=total_amount,
        status="completed"
    )
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    
    # Notify analytics
    await notify_analytics({
        "order_id": db_order.id,
        "user_id": order.user_id,
        "total_amount": total_amount,
        "items": order_items
    })
    
    db.close()
    return db_order

@app.get("/orders/{user_id}", response_model=List[Order])
def get_user_orders(user_id: int):
    db = SessionLocal()
    orders = db.query(Order).filter(Order.user_id == user_id).all()
    db.close()
    return orders 