from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Order
from app.schemas.api_schemas import OrderResponse

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("", response_model=list[OrderResponse])
def list_orders(db: Session = Depends(get_db)):
    return db.query(Order).all()


@router.get("/by-number/{order_number}", response_model=OrderResponse)
def get_order_by_number(order_number: str, db: Session = Depends(get_db)):
    normalized = order_number if order_number.startswith("ORD-") else f"ORD-{order_number}"
    order = db.query(Order).filter(Order.order_number == normalized).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")
    return order


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Sipariş bulunamadı")
    return order
