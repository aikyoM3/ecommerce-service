from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pydantic import BaseModel
import os
from datetime import datetime
from typing import Dict, Any

# Database setup
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./analytics.db")
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy models
class OrderEvent(Base):
    __tablename__ = "order_events"

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)
    data = Column(String)  # JSON string
    created_at = Column(String, default=lambda: datetime.now().isoformat())

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic models
class EventBase(BaseModel):
    type: str
    data: Dict[str, Any]

class EventCreate(EventBase):
    pass

class Event(EventBase):
    id: int
    created_at: str

    class Config:
        orm_mode = True

app = FastAPI(title="Analytics Service")

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def read_root():
    return {"message": "Welcome to Analytics Service"}

@app.post("/analytics/event")
def log_event(event: EventCreate):
    db = SessionLocal()
    db_event = OrderEvent(
        event_type=event.type,
        data=str(event.data)  # Convert dict to string for storage
    )
    db.add(db_event)
    db.commit()
    db.refresh(db_event)
    db.close()
    return {"message": "Event logged successfully"}

@app.get("/analytics/summary")
def get_summary():
    db = SessionLocal()
    events = db.query(OrderEvent).filter(OrderEvent.event_type == "order_placed").all()
    
    total_orders = len(events)
    total_revenue = 0
    
    for event in events:
        try:
            data = eval(event.data)  # Convert string back to dict
            total_revenue += data.get("total_amount", 0)
        except:
            continue
    
    db.close()
    
    return {
        "total_orders": total_orders,
        "total_revenue": total_revenue,
        "average_order_value": total_revenue / total_orders if total_orders > 0 else 0
    } 