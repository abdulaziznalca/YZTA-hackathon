from datetime import datetime, timedelta
from app.database import SessionLocal
from app.models.db_models import Product, Order, Shipment, ChatLog


def seed():
    db = SessionLocal()
    try:
        if db.query(Order).count() > 0:
            return

        orders_data = [
            {"order_number": "ORD-128", "customer_name": "Ahmet Yılmaz", "status": "Kargoya Verildi", "estimated_delivery": "13 Mayıs 2026", "total_amount": 450.0},
            {"order_number": "ORD-129", "customer_name": "Beyza Kaya", "status": "Hazırlanıyor", "estimated_delivery": "15 Mayıs 2026", "total_amount": 750.0},
            {"order_number": "ORD-130", "customer_name": "Mehmet Çelik", "status": "Gecikti", "estimated_delivery": "10 Mayıs 2026", "total_amount": 320.0},
            {"order_number": "ORD-131", "customer_name": "Fatma Demir", "status": "Kargoya Verildi", "estimated_delivery": "14 Mayıs 2026", "total_amount": 980.0},
            {"order_number": "ORD-132", "customer_name": "Ali Şahin", "status": "Teslim Edildi", "estimated_delivery": "9 Mayıs 2026", "total_amount": 260.0},
            {"order_number": "ORD-133", "customer_name": "Zeynep Arslan", "status": "Gecikti", "estimated_delivery": "8 Mayıs 2026", "total_amount": 540.0},
            {"order_number": "ORD-134", "customer_name": "Hasan Yıldız", "status": "Hazırlanıyor", "estimated_delivery": "16 Mayıs 2026", "total_amount": 1200.0},
            {"order_number": "ORD-135", "customer_name": "Ayşe Öztürk", "status": "Kargoya Verildi", "estimated_delivery": "13 Mayıs 2026", "total_amount": 870.0},
            {"order_number": "ORD-136", "customer_name": "İbrahim Kurt", "status": "Teslim Edildi", "estimated_delivery": "8 Mayıs 2026", "total_amount": 390.0},
            {"order_number": "ORD-137", "customer_name": "Selin Polat", "status": "Gecikti", "estimated_delivery": "7 Mayıs 2026", "total_amount": 620.0},
        ]

        orders = []
        for data in orders_data:
            order = Order(**data)
            db.add(order)
            orders.append(order)
        db.flush()

        shipments_data = [
            {"order_idx": 0, "carrier": "Aras Kargo", "tracking_number": "TRK789456", "current_location": "İstanbul Dağıtım Merkezi", "status": "Dağıtımda"},
            {"order_idx": 3, "carrier": "Yurtiçi Kargo", "tracking_number": "YK123456", "current_location": "Ankara Şubesi", "status": "Yolda"},
            {"order_idx": 4, "carrier": "MNG Kargo", "tracking_number": "MNG789", "current_location": "Teslim Edildi", "status": "Teslim Edildi"},
            {"order_idx": 5, "carrier": "PTT Kargo", "tracking_number": "PTT456789", "current_location": "İzmir Depo", "status": "Gecikti"},
            {"order_idx": 7, "carrier": "Sürat Kargo", "tracking_number": "SK321654", "current_location": "Bursa Şubesi", "status": "Yolda"},
            {"order_idx": 8, "carrier": "Aras Kargo", "tracking_number": "TRK111222", "current_location": "Teslim Edildi", "status": "Teslim Edildi"},
            {"order_idx": 9, "carrier": "Yurtiçi Kargo", "tracking_number": "YK999888", "current_location": "Antalya Depo", "status": "Gecikti"},
        ]

        for sd in shipments_data:
            shipment = Shipment(
                order_id=orders[sd["order_idx"]].id,
                carrier=sd["carrier"],
                tracking_number=sd["tracking_number"],
                current_location=sd["current_location"],
                status=sd["status"],
            )
            db.add(shipment)

        products_data = [
            ("Lavanta Sabunu", 2, 120.0),
            ("Zeytinyağı 1L", 50, 450.0),
            ("Biber Salçası 500gr", 20, 150.0),
            ("Biber Salçası 1kg", 15, 300.0),
            ("Biber Salçası 5kg", 30, 1400.0),
            ("Domates Salçası 500gr", 20, 160.0),
            ("Domates Salçası 1kg", 15, 300.0),
            ("Süzme Çiçek Balı", 15, 300.0),
            ("El Yapımı Erişte", 0, 85.0),
            ("Kurutulmuş Patlıcan", 4, 150.0),
            ("Kurutulmuş Domates", 100, 200.0),
            ("Salamur Köy Peyniri", 50, 300.0),
            ("Köy Tereyağı", 70, 800.0),
            ("Asma Yaprak", 100, 1500.0),
            ("Üzüm Sirkesi", 80, 200.0),
            ("Elma Sirkesi", 3, 180.0),
            ("Kara Dut Reçeli", 50, 300.0),
            ("Kayısı Reçeli", 80, 300.0),
            ("Dut Pekmezi", 60, 400.0),
            ("Nar Ekşisi", 70, 270.0),
        ]

        for name, stock, price in products_data:
            db.add(Product(name=name, stock=stock, price=price))

        chat_logs_data = [
            {"user_message": "Lavanta sabunu stokta var mı?", "ai_response": "Lavanta Sabunu stokta mevcut, ancak sadece 2 adet kaldı.", "intent": "stock_query", "extracted_product": "Lavanta Sabunu", "hours_ago": 2},
            {"user_message": "Zeytinyağı fiyatı ne kadar?", "ai_response": "Zeytinyağı 1L fiyatı 450 TL'dir.", "intent": "stock_query", "extracted_product": "Zeytinyağı", "hours_ago": 3},
            {"user_message": "128 numaralı siparişim nerede?", "ai_response": "ORD-128 numaralı siparişiniz kargoya verildi.", "intent": "shipment_status", "extracted_order": "128", "hours_ago": 4},
            {"user_message": "Kargom ne zaman gelir?", "ai_response": "Tahmini teslimat tarihiniz 13 Mayıs 2026.", "intent": "shipment_status", "extracted_order": "128", "hours_ago": 5},
            {"user_message": "El yapımı erişte var mı?", "ai_response": "Üzgünüm, El Yapımı Erişte şu anda stokta yok.", "intent": "stock_query", "extracted_product": "El Yapımı Erişte", "hours_ago": 6},
            {"user_message": "İade politikanız nedir?", "ai_response": "14 gün içinde iade yapabilirsiniz.", "intent": "policy_question", "hours_ago": 7},
            {"user_message": "Siparişimi iptal etmek istiyorum", "ai_response": "İptal talebiniz alındı.", "intent": "policy_question", "hours_ago": 8},
            {"user_message": "Ürün hasarlı geldi", "ai_response": "Şikayetiniz kaydedildi, en kısa sürede dönüş yapılacak.", "intent": "complaint", "hours_ago": 9},
            {"user_message": "Lavanta sabunu almak istiyorum", "ai_response": "Lavanta Sabunu stokta, 120 TL.", "intent": "stock_query", "extracted_product": "Lavanta Sabunu", "hours_ago": 10},
            {"user_message": "130 sipariş durumu", "ai_response": "ORD-130 numaralı siparişiniz gecikti.", "intent": "order_status", "extracted_order": "130", "hours_ago": 11},
            {"user_message": "Elma sirkesi kaç adet kaldı?", "ai_response": "Elma Sirkesi stokta 3 adet kaldı, kritik seviyede.", "intent": "stock_query", "extracted_product": "Elma Sirkesi", "hours_ago": 12},
            {"user_message": "Bugünkü özet rapor", "ai_response": "Bugün 10 sipariş, 3 geciken var.", "intent": "manager_summary", "hours_ago": 1},
        ]

        now = datetime.utcnow()
        for log_data in chat_logs_data:
            hours_ago = log_data.pop("hours_ago")
            log = ChatLog(
                user_message=log_data["user_message"],
                ai_response=log_data["ai_response"],
                intent=log_data["intent"],
                extracted_product=log_data.get("extracted_product"),
                extracted_order=log_data.get("extracted_order"),
                created_at=now - timedelta(hours=hours_ago),
            )
            db.add(log)

        db.commit()
    finally:
        db.close()