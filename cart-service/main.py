from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from pydantic import BaseModel
import os
import httpx

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./cart.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy models
class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    product_id = Column(Integer, index=True)
    quantity = Column(Integer)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class CartItemBase(BaseModel):
    user_id: int
    product_id: int
    quantity: int

class CartItemCreate(CartItemBase):
    pass

class CartItem(CartItemBase):
    id: int

    class Config:
        orm_mode = True

app = FastAPI(title="Cart Service")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

async def validate_product(product_id: int) -> bool:
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"http://product-service:8000/products/{product_id}")
            return response.status_code == 200
        except:
            return False

@app.get("/")
def read_root():
    return {"message": "Welcome to Cart Service"}

@app.get("/cart/{user_id}", response_model=list[CartItem])
def read_cart(user_id: int):
    db = SessionLocal()
    cart_items = db.query(CartItem).filter(CartItem.user_id == user_id).all()
    db.close()
    return cart_items

@app.post("/cart/add", response_model=CartItem)
async def add_to_cart(item: CartItemCreate):
    # Validate product exists
    if not await validate_product(item.product_id):
        raise HTTPException(status_code=404, detail="Product not found")
    
    db = SessionLocal()
    # Check if item already exists in cart
    existing_item = db.query(CartItem).filter(
        CartItem.user_id == item.user_id,
        CartItem.product_id == item.product_id
    ).first()
    
    if existing_item:
        existing_item.quantity += item.quantity
        db.commit()
        db.refresh(existing_item)
        db.close()
        return existing_item
    
    db_item = CartItem(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    db.close()
    return db_item

@app.delete("/cart/{user_id}/item/{product_id}")
def remove_item_from_cart(user_id: int, product_id: int):
    db = SessionLocal()
    db_item = db.query(CartItem).filter(
        CartItem.user_id == user_id,
        CartItem.product_id == product_id
    ).first()
    
    if db_item is None:
        db.close()
        raise HTTPException(status_code=404, detail="Cart item not found")
    
    db.delete(db_item)
    db.commit()
    db.close()
    return {"message": "Item removed from cart successfully"}

@app.delete("/cart/{user_id}")
def clear_cart(user_id: int):
    db = SessionLocal()
    db.query(CartItem).filter(CartItem.user_id == user_id).delete()
    db.commit()
    db.close()
    return {"message": "Cart cleared successfully"} 