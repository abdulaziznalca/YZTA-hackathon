import requests
import json
import re

from app.config import settings

_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
_HEADERS = {"Content-Type": "application/json"}


def _call_gemini(prompt: str) -> str:
    url = f"{_BASE_URL}?key={settings.GEMINI_API_KEY}"
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=_HEADERS, data=json.dumps(payload), timeout=30)
        if response.status_code == 200:
            return response.json()["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        pass
    return ""


def route_intents(message: str) -> dict:
    prompt = f"""Aşağıdaki kullanıcı mesajını analiz et ve SADECE şu JSON formatında yanıt ver, başka hiçbir şey yazma:
{{"intents": [...], "order_number": null, "product_name": null}}

Intent seçenekleri (birden fazla seçilebilir):
- shipment_status: kargo/teslimat/nerede/takip soruları
- order_status: sipariş durumu soruları
- cancel_order: sipariş iptal etme isteği
- stock_query: stok/mevcut mu/kaç adet soruları
- policy_question: iade/hasar/garanti/politika soruları
- complaint: şikayet/memnuniyetsizlik
- manager_summary: yönetici/özet/dashboard/rapor talepleri

Sipariş numarası varsa "order_number" alanına yaz (sadece rakamları: "128", "1001" gibi).
Ürün adı varsa "product_name" alanına yaz.
Hiçbir intent uymuyorsa "intents" listesini boş bırak: []

Mesaj: {message}"""

    raw = _call_gemini(prompt)
    clean = re.sub(r"```(?:json)?\s*\n?", "", raw).strip().rstrip("`").strip()
    try:
        result = json.loads(clean)
        intents = result.get("intents", [])
        if not isinstance(intents, list):
            intents = []
        return {
            "intents": intents,
            "order_number": result.get("order_number"),
            "product_name": result.get("product_name"),
        }
    except (json.JSONDecodeError, AttributeError):
        return {"intents": [], "order_number": None, "product_name": None}


def generate_response(context: str, message: str) -> str:
    context_section = f"\nMevcut veriler:\n{context}" if context else ""
    prompt = f"""Sen ShopPilot AI müşteri destek asistanısın. Sipariş, kargo, stok, iade ve şikayet konularında yardımcı olursun. Genel sohbet ve sistem hakkındaki sorulara da nazikçe yanıt verirsin.

Kurallar:
- Kısa, net ve nazik yanıt ver
- Türkçe yanıt ver
- Stok kritikse bunu vurgula
- Konuyla ilgisi olmayan sorulara nazikçe yanıt ver ve ne konularda yardımcı olabileceğini belirt
{context_section}

Kullanıcı sorusu: {message}"""

    response = _call_gemini(prompt)
    if response:
        return response
    return _fallback_response(context)


def generate_response_with_system(system_prompt: str, context: str, message: str) -> str:
    context_section = f"\nVeriler:\n{context}" if context else ""
    prompt = f"""{system_prompt}
{context_section}

Kullanıcı sorusu: {message}"""

    response = _call_gemini(prompt)
    return response if response else (context or "Bilgi alınamadı.")


def synthesize_responses(parts: str, user_message: str) -> str:
    prompt = f"""Birden fazla uzman ajanın cevaplarını tek tutarlı bir yanıta birleştir.

Kullanıcı sorusu: {user_message}

Uzman yanıtları:
{parts}

Kurallar:
- Tek akıcı Türkçe yanıt oluştur
- Tüm bilgileri koru, tekrarları önle
- Kısa, net ve nazik ol"""

    response = _call_gemini(prompt)
    return response if response else parts


def _fallback_response(context: str) -> str:
    if not context:
        return "Üzgünüm, şu anda yanıt veremiyorum. Lütfen daha sonra tekrar deneyin."

    try:
        data = json.loads(context)
    except json.JSONDecodeError:
        return context

    if isinstance(data, dict) and data.get("error"):
        return str(data["error"])

    if isinstance(data, dict) and "order_number" in data and "status" in data:
        return (
            f"{data['order_number']} numaralı siparişinizin durumu: {data['status']}. "
            f"Tahmini teslim: {data.get('estimated_delivery', 'Bilinmiyor')}."
        )

    if isinstance(data, dict) and "tracking_number" in data:
        return (
            f"{data.get('order_number', 'Sipariş')} için kargo durumu: {data.get('shipment_status', 'Bilinmiyor')}. "
            f"Kargo firması: {data.get('carrier', 'Bilinmiyor')}, takip no: {data.get('tracking_number', 'Bilinmiyor')}."
        )

    if isinstance(data, dict) and "urunler" in data and isinstance(data["urunler"], list):
        lines = []
        for item in data["urunler"]:
            lines.append(
                f"{item.get('isim', 'Ürün')}: stok {item.get('stok', 0)}, durum {item.get('durum', 'Bilinmiyor')}"
            )
        return "\n".join(lines) if lines else "Ürün bilgisi bulunamadı."

    return context
