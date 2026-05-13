"""Shared agent invocation pipeline used by both web chat and WhatsApp."""
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor

from sqlalchemy.orm import Session

from app.agents.graph import agent_graph
from app.models.db_models import ChatLog
from app.services.whatsapp_service import mask_phone

logger = logging.getLogger(__name__)
_executor = ThreadPoolExecutor(max_workers=4)


async def handle_inbound(
    message: str,
    db: Session,
    channel: str = "web",
    sender_id: str | None = None,
    external_message_id: str | None = None,
) -> str:
    """Invoke the agent graph and persist the conversation log.

    Returns the final response text.
    """
    initial_state = {
        "user_message": message,
        "intents": [],
        "extracted_params": {},
        "pending_agents": [],
        "agent_results": [],
        "final_response": "",
        "escalated_to": None,
        "tickets": [],
    }

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        _executor,
        lambda: agent_graph.invoke(initial_state),
    )

    intents_str = ",".join(result.get("intents", []))
    params = result.get("extracted_params", {})
    response_text = result["final_response"]

    masked_phone = mask_phone(sender_id) if sender_id else None

    log = ChatLog(
        user_message=message,
        ai_response=response_text,
        intent=intents_str or None,
        extracted_product=(params.get("product_name") or "").strip().title() or None,
        extracted_order=params.get("order_number"),
        channel=channel,
        external_message_id=external_message_id,
        sender_phone=masked_phone,
    )
    db.add(log)
    db.commit()

    return response_text
