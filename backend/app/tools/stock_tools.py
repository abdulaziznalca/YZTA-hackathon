from app.database import SessionLocal
from app.models.db_models import Product


def check_product_stock(product_name: str) -> dict:
    db = SessionLocal()
    try:
        products = db.query(Product).filter(Product.name.ilike(f"%{product_name}%")).all()
        if not products:
            return {"error": f"'{product_name}' adında ürün bulunamadı"}

        results = []
        for p in products:
            if p.stock == 0:
                durum = "Tükendi"
            elif p.stock <= 5:
                durum = "Kritik Stok"
            else:
                durum = "Mevcut"
            results.append({"isim": p.name, "stok": p.stock, "fiyat": p.price, "durum": durum})

        return {"urunler": results}
    finally:
        db.close()
