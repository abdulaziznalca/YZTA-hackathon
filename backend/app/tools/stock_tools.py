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


def update_product_stock(product_name: str, new_stock: int) -> dict:
    name = (product_name or "").strip()
    if not name:
        return {"error": "Ürün adı boş olamaz"}
    try:
        new_stock_int = int(new_stock)
    except Exception:
        return {"error": "Stok değeri geçersiz"}
    if new_stock_int < 0:
        return {"error": "Stok 0'dan küçük olamaz"}

    db = SessionLocal()
    try:
        product = db.query(Product).filter(Product.name.ilike(f"%{name}%")).order_by(Product.id.asc()).first()
        if not product:
            return {"error": f"'{name}' adında ürün bulunamadı"}
        product.stock = new_stock_int
        db.commit()
        return {"id": product.id, "name": product.name, "stock": product.stock, "price": product.price}
    finally:
        db.close()
