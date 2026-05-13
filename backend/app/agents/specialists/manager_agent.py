from app.tools.dashboard_tools import generate_daily_summary
from app.agents.specialists.base import run_specialist

_SYSTEM_PROMPT = """Sen ShopPilot AI yönetici asistanısın.
Günlük özet raporunu (toplam sipariş, kargodaki, geciken, kritik stok) yöneticiye uygun profesyonel Türkçe ile sun.
Kritik durumları öne çıkar."""


def node_manager_agent(state: dict) -> dict:
    tool_result = generate_daily_summary()
    return run_specialist(state, "manager_agent", "manager_summary", _SYSTEM_PROMPT, tool_result)
