from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Order
from app.schemas.api_schemas import (
    OrderCancelRequest,
    OrderCreateRequest,
    OrderDetailResponse,
    OrderResponse,
    OrderUpdateRequest,
)
from app.tools.order_tools import cancel_order, create_order, update_order_items

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


@router.post("/create", response_model=OrderDetailResponse)
def create_new_order(request: OrderCreateRequest):
    result = create_order(
        customer_name=request.customer_name,
        city=request.city,
        items=[{"product_name": i.product_name, "quantity": i.quantity} for i in request.items],
    )
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/cancel")
def cancel_existing_order(request: OrderCancelRequest):
    result = cancel_order(order_number=request.order_number, customer_name=request.customer_name)
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.patch("/update-items", response_model=OrderDetailResponse)
def update_existing_order_items(request: OrderUpdateRequest):
    result = update_order_items(
        order_number=request.order_number,
        customer_name=request.customer_name,
        add_items=[{"product_name": i.product_name, "quantity": i.quantity} for i in (request.add_items or [])],
        remove_items=[{"product_name": i.product_name, "quantity": i.quantity} for i in (request.remove_items or [])],
    )
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result
