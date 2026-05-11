from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Shipment, Order
from app.schemas.api_schemas import ShipmentResponse

router = APIRouter(prefix="/api/shipments", tags=["shipments"])


@router.get("/by-order/{order_id}", response_model=ShipmentResponse)
def get_shipment_by_order(order_id: int, db: Session = Depends(get_db)):
    shipment = db.query(Shipment).filter(Shipment.order_id == order_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Kargo bilgisi bulunamadı")
    return shipment
