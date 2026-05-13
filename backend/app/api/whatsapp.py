"""WhatsApp webhook endpoints — supports Twilio Sandbox and Meta Cloud API."""
import logging
import time
from collections import defaultdict

from fastapi import APIRouter, BackgroundTasks, Depends, Form, Header, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import SessionLocal, get_db
from app.models.db_models import ChatLog
from app.schemas.whatsapp_schemas import NormalizedInbound
from app.services.channel_dispatcher import handle_inbound
from app.services.whatsapp_service import send_message, verify_twilio_signature

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/whatsapp", tags=["whatsapp"])

# Simple in-memory rate limiter: IP → list of timestamps
_rate_store: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT = 60   # requests per window
_RATE_WINDOW = 60  # seconds


def _check_rate_limit(ip: str) -> None:
    now = time.time()
    timestamps = [t for t in _rate_store[ip] if now - t < _RATE_WINDOW]
    if len(timestamps) >= _RATE_LIMIT:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    timestamps.append(now)
    _rate_store[ip] = timestamps


def _is_duplicate(external_message_id: str, db: Session) -> bool:
    """Idempotency check — return True if already processed."""
    return (
        db.query(ChatLog)
        .filter(ChatLog.external_message_id == external_message_id)
        .first()
        is not None
    )


# ---------------------------------------------------------------------------
# GET  /api/whatsapp/webhook — Meta Cloud API hub.verify_token handshake
# ---------------------------------------------------------------------------

@router.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge"),
):
    if hub_mode == "subscribe" and hub_verify_token == settings.WHATSAPP_VERIFY_TOKEN:
        return int(hub_challenge)
    raise HTTPException(status_code=403, detail="Forbidden")


# ---------------------------------------------------------------------------
# POST /api/whatsapp/webhook — Twilio inbound message
# ---------------------------------------------------------------------------

@router.post("/webhook")
async def twilio_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    MessageSid: str = Form(...),
    From: str = Form(...),
    Body: str = Form(...),
    x_twilio_signature: str = Header(default="", alias="X-Twilio-Signature"),
):
    client_ip = request.client.host if request.client else "unknown"
    _check_rate_limit(client_ip)

    # Signature verification (skip in sandbox/dev via TWILIO_SKIP_SIGNATURE=true)
    form_data = dict(await request.form())
    if not settings.TWILIO_SKIP_SIGNATURE:
        proto = request.headers.get("x-forwarded-proto", request.url.scheme)
        host = request.headers.get("x-forwarded-host", request.headers.get("host", request.url.netloc))
        webhook_url = f"{proto}://{host}{request.url.path}"
        if not verify_twilio_signature(webhook_url, form_data, x_twilio_signature):
            raise HTTPException(status_code=403, detail="Invalid Twilio signature")

    # Idempotency (checked before background task)
    if _is_duplicate(MessageSid, db):
        logger.info("Duplicate message %s ignored", MessageSid)
        return {"status": "duplicate"}

    inbound = NormalizedInbound(
        external_message_id=MessageSid,
        sender_phone=From,
        body=Body,
        provider="twilio",
    )

    # Respond 200 immediately; agent runs in background to avoid Twilio timeout.
    # Background task opens its own DB session — the request session closes after return.
    background_tasks.add_task(_process_and_reply, inbound)
    return {"status": "accepted"}


async def _process_and_reply(inbound: NormalizedInbound) -> None:
    """Run agent and send WhatsApp reply. Uses its own DB session."""
    db = SessionLocal()
    try:
        response_text = await handle_inbound(
            message=inbound.body,
            db=db,
            channel="whatsapp",
            sender_id=inbound.sender_phone,
            external_message_id=inbound.external_message_id,
        )
        to = (
            inbound.sender_phone
            if inbound.sender_phone.startswith("whatsapp:")
            else f"whatsapp:{inbound.sender_phone}"
        )
        send_message(to=to, body=response_text)
    except Exception:
        logger.exception("Failed to process WhatsApp message %s", inbound.external_message_id)
    finally:
        db.close()
