from app.tools.order_tools import get_order_by_number
from app.agents.specialists.base import run_specialist

_SYSTEM_PROMPT = """Sen ShopPilot AI sipariş takip uzmanısın.
Sipariş bilgilerini (durum, tahmini teslim, toplam tutar) net ve özlü şekilde Türkçe açıkla.
Sadece verilen verileri kullan, ek bilgi uydurma."""


def node_order_agent(state: dict) -> dict:
    order_number = state["extracted_params"].get("order_number") or ""
    tool_result = get_order_by_number(order_number)
    return run_specialist(state, "order_agent", "order_status", _SYSTEM_PROMPT, tool_result)
