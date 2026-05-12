from app.tools.stock_tools import check_product_stock
from app.tools.action_tools import create_stock_alert
from app.agents.specialists.base import run_specialist

_SYSTEM_PROMPT = """Sen ShopPilot AI stok yönetim uzmanısın.
Ürün stok durumlarını (stok adedi, durum: Mevcut/Kritik Stok/Tükendi, fiyat) Türkçe bildir.
Kritik stok veya tükenmiş ürünleri özellikle vurgula.
Stok uyarısı oluşturulduysa yanıtta ticket numarasını (TCK-xxxx) mutlaka belirt.
Sadece verilen verileri kullan."""

_CRITICAL_THRESHOLD = 5


def node_stock_agent(state: dict) -> dict:
    product_name = state["extracted_params"].get("product_name") or ""
    stock_result = check_product_stock(product_name)

    alert_tickets: list[dict] = []
    if "urunler" in stock_result:
        for item in stock_result["urunler"]:
            if item.get("stok", 999) <= _CRITICAL_THRESHOLD:
                alert = create_stock_alert(
                    product_name_or_id=item["isim"],
                    threshold=_CRITICAL_THRESHOLD,
                    source="agent",
                )
                if "ticket_no" in alert:
                    alert_tickets.append(alert)

    tool_result = {**stock_result}
    if alert_tickets:
        tool_result["stock_alerts"] = alert_tickets

    updated = run_specialist(state, "stock_agent", "stock_query", _SYSTEM_PROMPT, tool_result)

    tickets = list(state.get("tickets", []))
    tickets.extend(alert_tickets)
    return {**updated, "tickets": tickets}
