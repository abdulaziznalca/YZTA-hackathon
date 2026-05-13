from pydantic import BaseModel
from typing import Optional


class TwilioInboundMessage(BaseModel):
    """Twilio WhatsApp webhook POST body (form-encoded, parsed by FastAPI Form)."""
    MessageSid: str
    From: str          # e.g. "whatsapp:+905xxxxxxxx"
    To: str            # Twilio sandbox number
    Body: str
    NumMedia: Optional[str] = "0"


class MetaInboundMessage(BaseModel):
    """Normalized message from Meta Cloud API webhook payload."""
    id: str
    from_: str
    body: str

    class Config:
        populate_by_name = True
        fields = {"from_": "from"}


class NormalizedInbound(BaseModel):
    """Provider-agnostic inbound message handed to channel_dispatcher."""
    external_message_id: str
    sender_phone: str       # raw phone, masking happens at DB layer
    body: str
    provider: str           # "twilio" | "meta"
