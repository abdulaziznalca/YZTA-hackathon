from app.tools.shipment_tools import get_shipment_by_order_number
from app.agents.specialists.base import run_specialist

_SYSTEM_PROMPT = """Sen ShopPilot AI kargo takip uzmanısın.
Kargo bilgilerini (kargo firması, takip numarası, mevcut konum, durum, tahmini teslim) açık ve anlaşılır Türkçe ile aktar.
Sadece verilen verileri kullan, ek bilgi uydurma."""


def node_shipment_agent(state: dict) -> dict:
    order_number = state["extracted_params"].get("order_number") or ""
    tool_result = get_shipment_by_order_number(order_number)
    return run_specialist(state, "shipment_agent", "shipment_status", _SYSTEM_PROMPT, tool_result)
