from app.database import SessionLocal
from app.models.db_models import Product, Order, Shipment


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

        db.commit()
    finally:
        db.close()
