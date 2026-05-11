import re

from app.database import SessionLocal
from app.models.db_models import Order


def _normalize(order_number: str) -> str | None:
    digits = re.sub(r"[^\d]", "", str(order_number))
    return f"ORD-{digits}" if digits else None


def get_order_by_number(order_number: str) -> dict:
    normalized = _normalize(order_number)
    if not normalized:
        return {"error": "Geçersiz sipariş numarası"}

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_number == normalized).first()
        if not order:
            return {"error": f"{order_number} numaralı sipariş bulunamadı"}
        return {
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "status": order.status,
            "estimated_delivery": order.estimated_delivery,
            "total_amount": order.total_amount,
        }
    finally:
        db.close()
