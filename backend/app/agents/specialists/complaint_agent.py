from app.agents.specialists.base import run_specialist

_SYSTEM_PROMPT = """Sen ShopPilot AI şikayet yöneticisisin.
Müşteri şikayetlerini empatiyle karşıla, şikayetin alındığını ve yöneticiye iletildiğini bildir.
Özür dile ve çözüm sürecini açıkla. Türkçe yanıt ver."""


def node_complaint_agent(state: dict) -> dict:
    tool_result = {
        "bilgi": "Şikayetiniz kaydedildi ve yöneticimize iletildi.",
        "durum": "İşleme alındı",
        "beklenti": "En kısa sürede size dönüş yapılacak.",
    }
    updated = run_specialist(state, "complaint_agent", "complaint", _SYSTEM_PROMPT, tool_result)
    return {**updated, "escalated_to": "manager_agent"}
