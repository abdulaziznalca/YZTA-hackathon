import requests
import json
import re

from database import (
    get_order_by_id,
    get_product_by_name,
    cancel_order,
    get_low_stock_products,
)

from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"


def ask_gemini(user_query):

    context = ""

    #Düşük stok (işletme için)
    if "düşük stok" in user_query.lower():

        products = get_low_stock_products()

        if products:
            return f"Düşük stoklu ürünler: {products}"

        return "Düşük stoklu ürün bulunmuyor."

    # Sipariş iptal
    if "iptal" in user_query.lower():

        order_match = re.search(r'\d+', user_query)

        if order_match:

            order_id = int(order_match.group())

            success = cancel_order(order_id)

            if success:
                return f"{order_id} numaralı siparişiniz başarıyla iptal edildi."

            else:
                return "İptal edilecek sipariş bulunamadı."

    # Sipariş numarası arıyoruz
    order_match = re.search(r'\d+', user_query)

    if order_match:

        order_id = int(order_match.group())

        order = get_order_by_id(order_id)

        if order:

            context = f"""
            Sipariş No: {order[0]}
            Müşteri: {order[1]}
            Durum: {order[2]}
            Tahmini Teslim: {order[3]}
            """

        else:
            context = "Sipariş bulunamadı."

    else:

        products = get_product_by_name(user_query)

        if products:
            context = f"Ürün Bilgileri: {products}"
        else:
            context = "Ürün bulunamadı."



    prompt = f"""
    Sen bir KOBİ müşteri destek asistanısın.

    Kurallar:
    - Sadece verilen verileri kullan
    - Bilmediğin şeyler için yanlış cevap verme
    - Kısa ve net cevap ver
    - Nazik ol

    Veriler:
    {context}

    Kullanıcı Sorusu:
    {user_query}
    """

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt
                    }
                ]
            }
        ]
    }

    headers = {
        "Content-Type": "application/json"
    }

    response = requests.post(
        URL,
        headers=headers,
        data=json.dumps(payload)
    )

    if response.status_code == 200:

        result = response.json()

        return result['candidates'][0]['content']['parts'][0]['text']

    else:
        return f"Hata: {response.status_code} - {response.text}"


if __name__ == "__main__":

    print(
        ask_gemini(
            "1001 numaralı siparişim nerede?"
        )
    )