from app.agents.specialists.base import run_specialist
from app.tools.action_tools import create_complaint

_SYSTEM_PROMPT = """Sen ShopPilot AI şikayet yöneticisisin.
Müşteri şikayetlerini empatiyle karşıla, şikayetin alındığını ve yöneticiye iletildiğini bildir.
Yanıtta mutlaka ticket_no referansını kullan (örnek: TCK-1001 takip numaranızla kaydedildi).
Özür dile ve çözüm sürecini açıkla. Türkçe yanıt ver."""


def node_complaint_agent(state: dict) -> dict:
    params = state.get("extracted_params", {})
    customer_name = params.get("customer_name") or "Müşteri"
    subject = params.get("subject") or "Şikayet"
    description = state.get("user_message", "")
    order_number = params.get("order_number")

    tool_result = create_complaint(
        customer_name=customer_name,
        subject=subject,
        description=description,
        order_number=order_number,
        source="web_chat",
    )

    updated = run_specialist(state, "complaint_agent", "complaint", _SYSTEM_PROMPT, tool_result)

    tickets = list(state.get("tickets", []))
    if "ticket_no" in tool_result:
        tickets.append(tool_result)

    return {**updated, "escalated_to": "manager_agent", "tickets": tickets}
