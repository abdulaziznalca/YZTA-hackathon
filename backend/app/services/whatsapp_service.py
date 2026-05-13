import hashlib
import hmac
import re
import time
import logging
from urllib.parse import urlencode

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_TWILIO_API = "https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
_MAX_RETRIES = 3


def mask_phone(phone: str) -> str:
    """Return masked phone number: +90****1234 (last 4 digits visible)."""
    digits = re.sub(r"[^\d+]", "", phone)
    if len(digits) > 8:
        return digits[:3] + "****" + digits[-4:]
    return "****"


def verify_twilio_signature(url: str, post_params: dict, x_twilio_signature: str) -> bool:
    """Validate X-Twilio-Signature HMAC-SHA1."""
    if not settings.TWILIO_AUTH_TOKEN:
        logger.warning("TWILIO_AUTH_TOKEN not set — skipping signature check")
        return True

    sorted_params = "".join(f"{k}{v}" for k, v in sorted(post_params.items()))
    message = url + sorted_params
    expected = hmac.new(
        settings.TWILIO_AUTH_TOKEN.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha1,
    ).digest()

    import base64
    expected_b64 = base64.b64encode(expected).decode()
    return hmac.compare_digest(expected_b64, x_twilio_signature)


def send_message(to: str, body: str) -> bool:
    """Send a WhatsApp message via Twilio with exponential-backoff retry."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.error("Twilio credentials not configured")
        return False

    url = _TWILIO_API.format(sid=settings.TWILIO_ACCOUNT_SID)
    payload = {
        "From": settings.TWILIO_WHATSAPP_FROM,
        "To": to if to.startswith("whatsapp:") else f"whatsapp:{to}",
        "Body": body,
    }

    for attempt in range(1, _MAX_RETRIES + 1):
        try:
            with httpx.Client(timeout=10) as client:
                resp = client.post(
                    url,
                    data=payload,
                    auth=(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN),
                )
            if resp.status_code in (200, 201):
                logger.info("WhatsApp message sent to %s", mask_phone(to))
                return True
            logger.warning("Twilio returned %s on attempt %d", resp.status_code, attempt)
        except Exception as exc:
            logger.warning("send_message attempt %d failed: %s", attempt, exc)

        if attempt < _MAX_RETRIES:
            time.sleep(2 ** attempt)

    logger.error("Failed to send WhatsApp message to %s after %d attempts", mask_phone(to), _MAX_RETRIES)
    return False
