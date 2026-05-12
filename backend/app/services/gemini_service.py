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


def detect_intent(message: str) -> dict:
    prompt = f"""Aşağıdaki kullanıcı mesajını analiz et ve SADECE şu JSON formatında yanıt ver, başka hiçbir şey yazma:
{{"intent": "...", "order_number": null, "product_name": null, "customer_name": null, "city": null, "quantity": null, "update_action": null}}

Intent seçenekleri:
- shipment_status: kargo/teslimat/nerede/takip soruları
- order_status: sipariş durumu soruları
- stock_query: stok/mevcut mu/kaç adet soruları
- order_cancel: sipariş iptal etme talebi
- order_create: yeni sipariş oluşturma talebi
- order_update: siparişi güncelleme (ürün ekle/çıkar) talebi
- stock_update: stok güncelleme (işletmeci) talebi
- policy_question: iade/hasar/garanti/politika soruları
- complaint: şikayet/memnuniyetsizlik
- manager_summary: yönetici/özet/dashboard/rapor talepleri
- unknown: diğer tüm sorular

Sipariş numarası varsa "order_number" alanına yaz (sadece rakamları: "128", "1001" gibi).
Ürün adı varsa "product_name" alanına yaz.
Müşteri adı/soyadı (varsa) "customer_name" alanına yaz.
Şehir bilgisi (varsa) "city" alanına yaz.
Miktar (varsa) "quantity" alanına sayı yaz.
"update_action": sadece "add" veya "remove" olabilir (sipariş güncellemede ürün ekle/çıkar niyeti varsa).

Mesaj: {message}"""

    raw = _call_gemini(prompt)
    clean = re.sub(r"```(?:json)?\s*\n?", "", raw).strip().rstrip("`").strip()
    try:
        result = json.loads(clean)
        return {
            "intent": result.get("intent", "unknown"),
            "order_number": result.get("order_number"),
            "product_name": result.get("product_name"),
            "customer_name": result.get("customer_name"),
            "city": result.get("city"),
            "quantity": result.get("quantity"),
            "update_action": result.get("update_action"),
        }
    except (json.JSONDecodeError, AttributeError):
        return {
            "intent": "unknown",
            "order_number": None,
            "product_name": None,
            "customer_name": None,
            "city": None,
            "quantity": None,
            "update_action": None,
        }


def generate_response(context: str, message: str) -> str:
    context_section = f"\nMevcut veriler:\n{context}" if context else ""
    prompt = f"""Sen ShopPilot AI müşteri destek asistanısın.

Kurallar:
- Sadece verilen verileri kullan, ek bilgi uydurma
- Kısa, net ve nazik yanıt ver
- Türkçe yanıt ver
- Stok kritikse bunu vurgula
{context_section}

Kullanıcı sorusu: {message}"""

    response = _call_gemini(prompt)
    if response:
        return response
    return _fallback_response(context)


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
