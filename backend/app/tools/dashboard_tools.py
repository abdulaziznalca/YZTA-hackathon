from app.database import SessionLocal
from app.models.db_models import Order, Product


def generate_daily_summary() -> dict:
    db = SessionLocal()
    try:
        total_orders = db.query(Order).count()
        shipped_orders = db.query(Order).filter(Order.status == "Kargoya Verildi").count()
        delayed_orders = db.query(Order).filter(Order.status == "Gecikti").count()
        total_products = db.query(Product).count()
        critical_products = db.query(Product).filter(Product.stock <= 5).all()
        out_of_stock = db.query(Product).filter(Product.stock == 0).count()

        return {
            "toplam_siparis": total_orders,
            "kargodaki": shipped_orders,
            "geciken": delayed_orders,
            "toplam_urun": total_products,
            "stok_tukenen": out_of_stock,
            "kritik_stok": [{"isim": p.name, "stok": p.stock} for p in critical_products],
        }
    finally:
        db.close()
