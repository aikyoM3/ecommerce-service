from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import os

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./payments.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy models
class Wallet(Base):
    __tablename__ = "wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, unique=True, index=True)
    balance = Column(Float, default=0.0)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class WalletBase(BaseModel):
    user_id: int
    balance: float

class WalletCreate(WalletBase):
    pass

class Wallet(WalletBase):
    id: int

    class Config:
        orm_mode = True

class AddBalanceRequest(BaseModel):
    user_id: int
    amount: float

app = FastAPI(title="Payment Service")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Payment Service"}

@app.post("/add_balance")
def add_balance(request: AddBalanceRequest):
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    
    db = SessionLocal()
    wallet = db.query(Wallet).filter(Wallet.user_id == request.user_id).first()
    
    if wallet is None:
        wallet = Wallet(user_id=request.user_id, balance=request.amount)
        db.add(wallet)
    else:
        wallet.balance += request.amount
    
    db.commit()
    db.refresh(wallet)
    db.close()
    
    return {"message": "Balance added successfully", "new_balance": wallet.balance}

@app.get("/get_balance/{user_id}")
def get_balance(user_id: int):
    db = SessionLocal()
    wallet = db.query(Wallet).filter(Wallet.user_id == user_id).first()
    db.close()
    
    if wallet is None:
        return {"balance": 0.0}
    
    return {"balance": wallet.balance} 