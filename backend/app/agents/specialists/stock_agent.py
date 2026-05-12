from app.tools.stock_tools import check_product_stock
from app.agents.specialists.base import run_specialist

_SYSTEM_PROMPT = """Sen ShopPilot AI stok yönetim uzmanısın.
Ürün stok durumlarını (stok adedi, durum: Mevcut/Kritik Stok/Tükendi, fiyat) Türkçe bildir.
Kritik stok veya tükenmiş ürünleri özellikle vurgula.
Sadece verilen verileri kullan."""


def node_stock_agent(state: dict) -> dict:
    product_name = state["extracted_params"].get("product_name") or ""
    tool_result = check_product_stock(product_name)
    return run_specialist(state, "stock_agent", "stock_query", _SYSTEM_PROMPT, tool_result)
