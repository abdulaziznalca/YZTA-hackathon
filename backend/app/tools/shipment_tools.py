import re

from app.database import SessionLocal
from app.models.db_models import Order, Shipment


def _normalize(order_number: str) -> str | None:
    digits = re.sub(r"[^\d]", "", str(order_number))
    return f"ORD-{digits}" if digits else None


def get_shipment_by_order_number(order_number: str) -> dict:
    normalized = _normalize(order_number)
    if not normalized:
        return {"error": "Geçersiz sipariş numarası"}

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_number == normalized).first()
        if not order:
            return {"error": f"{order_number} numaralı sipariş bulunamadı"}

        shipment = db.query(Shipment).filter(Shipment.order_id == order.id).first()
        if not shipment:
            return {"error": "Bu sipariş için henüz kargo bilgisi yok"}

        return {
            "order_number": order.order_number,
            "carrier": shipment.carrier,
            "tracking_number": shipment.tracking_number,
            "current_location": shipment.current_location,
            "shipment_status": shipment.status,
            "estimated_delivery": order.estimated_delivery,
        }
    finally:
        db.close()
