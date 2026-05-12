from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.database import SessionLocal
from app.models.db_models import SupportTicket
from app.tools.action_tools import (
    create_cancel_request,
    create_complaint,
    create_stock_alert,
    get_ticket,
)

router = APIRouter(prefix="/api/tickets", tags=["tickets"])


class CancelRequest(BaseModel):
    order_number: str
    customer_name: str
    reason: Optional[str] = ""


class ComplaintRequest(BaseModel):
    customer_name: str
    subject: str
    description: str
    order_number: Optional[str] = None


class StockAlertRequest(BaseModel):
    product_name: str
    threshold: Optional[int] = 5


@router.post("/cancel")
def cancel_ticket(body: CancelRequest):
    result = create_cancel_request(
        order_number=body.order_number,
        customer_name=body.customer_name,
        reason=body.reason or "",
        source="api",
    )
    if "error" in result and result.get("status") not in ("rejected",):
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/complaint")
def complaint_ticket(body: ComplaintRequest):
    result = create_complaint(
        customer_name=body.customer_name,
        subject=body.subject,
        description=body.description,
        order_number=body.order_number,
        source="api",
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.post("/stock-alert")
def stock_alert_ticket(body: StockAlertRequest):
    result = create_stock_alert(
        product_name_or_id=body.product_name,
        threshold=body.threshold,
        source="api",
    )
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/{ticket_no}")
def get_ticket_detail(ticket_no: str):
    result = get_ticket(ticket_no)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result


@router.get("")
def list_tickets(type: Optional[str] = None, status: Optional[str] = None):
    db = SessionLocal()
    try:
        q = db.query(SupportTicket)
        if type:
            q = q.filter(SupportTicket.type == type)
        if status:
            q = q.filter(SupportTicket.status == status)
        tickets = q.order_by(SupportTicket.id.desc()).limit(100).all()
        return [
            {
                "ticket_no": t.ticket_no,
                "type": t.type,
                "status": t.status,
                "subject": t.subject,
                "customer_name": t.customer_name,
                "order_number": t.order_number,
                "created_at": t.created_at.isoformat() if t.created_at else None,
            }
            for t in tickets
        ]
    finally:
        db.close()
