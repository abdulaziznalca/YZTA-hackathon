import hashlib
import json
from datetime import datetime, timedelta

from app.database import SessionLocal
from app.models.db_models import ActionLog, Product, SupportTicket
from app.tools.order_tools import cancel_order


def _generate_ticket_no(db) -> str:
    last = db.query(SupportTicket).order_by(SupportTicket.id.desc()).first()
    if last and last.ticket_no:
        try:
            num = int(last.ticket_no.replace("TCK-", "")) + 1
        except ValueError:
            num = 1000
    else:
        num = 1000
    return f"TCK-{num}"


def _log(db, action: str, ticket_id=None, payload=None, result="ok", error_message=None):
    db.add(
        ActionLog(
            ticket_id=ticket_id,
            action=action,
            actor="agent",
            payload_json=json.dumps(payload, ensure_ascii=False) if payload else None,
            result=result,
            error_message=error_message,
        )
    )


def _ticket_to_dict(t: SupportTicket) -> dict:
    return {
        "ticket_no": t.ticket_no,
        "type": t.type,
        "status": t.status,
        "subject": t.subject,
        "customer_name": t.customer_name,
        "order_number": t.order_number,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "message": f"Talebiniz alındı. Takip numaranız: {t.ticket_no}",
    }


def create_cancel_request(
    order_number: str,
    customer_name: str,
    reason: str = "",
    source: str = "web_chat",
) -> dict:
    db = SessionLocal()
    try:
        # Idempotency: same order + customer with active ticket
        existing = (
            db.query(SupportTicket)
            .filter(
                SupportTicket.type == "cancel_request",
                SupportTicket.order_number == order_number,
                SupportTicket.customer_name.ilike(customer_name.strip()),
                SupportTicket.status.in_(["open", "approved"]),
            )
            .first()
        )
        if existing:
            _log(db, "create_cancel_request_idempotent", ticket_id=existing.id,
                 payload={"order_number": order_number})
            db.commit()
            return _ticket_to_dict(existing)

        result = cancel_order(order_number, customer_name)

        ticket_no = _generate_ticket_no(db)
        if "error" in result:
            ticket = SupportTicket(
                ticket_no=ticket_no,
                type="cancel_request",
                status="rejected",
                source=source,
                customer_name=customer_name.strip(),
                order_number=order_number,
                subject=f"İptal Talebi – {order_number}",
                description=reason or "Müşteri iptal isteği",
                meta_json=json.dumps({"cancel_result": result}, ensure_ascii=False),
            )
            db.add(ticket)
            db.flush()
            _log(db, "create_cancel_request", ticket_id=ticket.id,
                 payload={"order_number": order_number, "reason": reason},
                 result="error", error_message=result["error"])
            db.commit()
            return {**_ticket_to_dict(ticket), "message": result["error"]}

        ticket = SupportTicket(
            ticket_no=ticket_no,
            type="cancel_request",
            status="approved",
            source=source,
            customer_name=customer_name.strip(),
            order_number=order_number,
            subject=f"İptal Talebi – {order_number}",
            description=reason or "Müşteri iptal isteği",
            meta_json=json.dumps({"cancel_result": result}, ensure_ascii=False),
        )
        db.add(ticket)
        db.flush()
        _log(db, "create_cancel_request", ticket_id=ticket.id,
             payload={"order_number": order_number, "reason": reason})
        db.commit()
        return _ticket_to_dict(ticket)
    except Exception as exc:
        db.rollback()
        try:
            _log(db, "create_cancel_request", payload={"order_number": order_number},
                 result="error", error_message=str(exc))
            db.commit()
        except Exception:
            pass
        return {"error": str(exc)}
    finally:
        db.close()


def create_complaint(
    customer_name: str,
    subject: str,
    description: str,
    order_number: str = None,
    source: str = "web_chat",
) -> dict:
    db = SessionLocal()
    try:
        desc_hash = hashlib.md5(description[:80].encode()).hexdigest()
        window = datetime.utcnow() - timedelta(minutes=5)
        existing = (
            db.query(SupportTicket)
            .filter(
                SupportTicket.type == "complaint",
                SupportTicket.customer_name.ilike(customer_name.strip()),
                SupportTicket.created_at >= window,
            )
            .all()
        )
        for t in existing:
            if t.meta_json:
                try:
                    meta = json.loads(t.meta_json)
                    if meta.get("desc_hash") == desc_hash:
                        _log(db, "create_complaint_idempotent", ticket_id=t.id,
                             payload={"customer_name": customer_name})
                        db.commit()
                        return _ticket_to_dict(t)
                except Exception:
                    pass

        ticket_no = _generate_ticket_no(db)
        ticket = SupportTicket(
            ticket_no=ticket_no,
            type="complaint",
            status="open",
            source=source,
            customer_name=customer_name.strip(),
            order_number=order_number,
            subject=subject,
            description=description,
            meta_json=json.dumps({"desc_hash": desc_hash}, ensure_ascii=False),
        )
        db.add(ticket)
        db.flush()
        _log(db, "create_complaint", ticket_id=ticket.id,
             payload={"customer_name": customer_name, "subject": subject})
        db.commit()
        return _ticket_to_dict(ticket)
    except Exception as exc:
        db.rollback()
        try:
            _log(db, "create_complaint", payload={"customer_name": customer_name},
                 result="error", error_message=str(exc))
            db.commit()
        except Exception:
            pass
        return {"error": str(exc)}
    finally:
        db.close()


def create_stock_alert(
    product_name_or_id,
    threshold: int = 5,
    source: str = "agent",
) -> dict:
    db = SessionLocal()
    try:
        if isinstance(product_name_or_id, int):
            product = db.query(Product).filter(Product.id == product_name_or_id).first()
        else:
            product = (
                db.query(Product)
                .filter(Product.name.ilike(f"%{product_name_or_id}%"))
                .order_by(Product.id.asc())
                .first()
            )

        if not product:
            return {"error": f"'{product_name_or_id}' adında ürün bulunamadı"}

        if product.stock > threshold:
            return {"info": "stok yeterli", "product": product.name, "stock": product.stock}

        # Idempotency: same product, open alert in last 24h
        window = datetime.utcnow() - timedelta(hours=24)
        existing = (
            db.query(SupportTicket)
            .filter(
                SupportTicket.type == "stock_alert",
                SupportTicket.product_id == product.id,
                SupportTicket.status == "open",
                SupportTicket.created_at >= window,
            )
            .first()
        )
        if existing:
            _log(db, "create_stock_alert_idempotent", ticket_id=existing.id,
                 payload={"product_id": product.id})
            db.commit()
            return _ticket_to_dict(existing)

        ticket_no = _generate_ticket_no(db)
        ticket = SupportTicket(
            ticket_no=ticket_no,
            type="stock_alert",
            status="open",
            source=source,
            product_id=product.id,
            subject=f"Kritik Stok Uyarısı – {product.name}",
            description=f"{product.name} stoğu kritik seviyede: {product.stock} adet (eşik: {threshold})",
            meta_json=json.dumps({"product_id": product.id, "stock": product.stock, "threshold": threshold},
                                  ensure_ascii=False),
        )
        db.add(ticket)
        db.flush()
        _log(db, "create_stock_alert", ticket_id=ticket.id,
             payload={"product_id": product.id, "stock": product.stock})
        db.commit()
        return _ticket_to_dict(ticket)
    except Exception as exc:
        db.rollback()
        try:
            _log(db, "create_stock_alert",
                 payload={"product_name_or_id": str(product_name_or_id)},
                 result="error", error_message=str(exc))
            db.commit()
        except Exception:
            pass
        return {"error": str(exc)}
    finally:
        db.close()


def get_ticket(ticket_no: str) -> dict:
    db = SessionLocal()
    try:
        ticket = db.query(SupportTicket).filter(SupportTicket.ticket_no == ticket_no).first()
        if not ticket:
            return {"error": f"{ticket_no} numaralı ticket bulunamadı"}
        return _ticket_to_dict(ticket)
    finally:
        db.close()
