from app.tools.order_tools import get_order_by_number
from app.tools.action_tools import create_cancel_request
from app.agents.specialists.base import run_specialist

_SYSTEM_PROMPT_STATUS = """Sen ShopPilot AI sipariş takip uzmanısın.
Sipariş bilgilerini (durum, tahmini teslim, toplam tutar) net ve özlü şekilde Türkçe açıkla.
Sadece verilen verileri kullan, ek bilgi uydurma."""

_SYSTEM_PROMPT_CANCEL = """Sen ShopPilot AI sipariş iptal uzmanısın.
İptal işleminin sonucunu kullanıcıya açıkla. Ticket numarası (TCK-xxxx) varsa mutlaka belirt.
Onaylanan iptallerde tebrik et, reddedilen iptallerde sebebi açıkla. Türkçe yanıt ver."""


def node_order_agent(state: dict) -> dict:
    params = state.get("extracted_params", {})
    order_number = params.get("order_number") or ""
    intents = state.get("intents", [])

    if "cancel_order" in intents:
        customer_name = params.get("customer_name") or ""
        tool_result = create_cancel_request(
            order_number=order_number,
            customer_name=customer_name,
            reason=state.get("user_message", ""),
            source="web_chat",
        )
        updated = run_specialist(state, "order_agent", "cancel_order", _SYSTEM_PROMPT_CANCEL, tool_result)

        tickets = list(state.get("tickets", []))
        if "ticket_no" in tool_result:
            tickets.append(tool_result)
        return {**updated, "tickets": tickets}

    tool_result = get_order_by_number(order_number)
    return run_specialist(state, "order_agent", "order_status", _SYSTEM_PROMPT_STATUS, tool_result)
