import re

from app.database import SessionLocal
from datetime import datetime, timedelta

from app.models.db_models import Order, OrderItem, Product


def _normalize(order_number: str) -> str | None:
    digits = re.sub(r"[^\d]", "", str(order_number))
    return f"ORD-{digits}" if digits else None


def get_order_by_number(order_number: str) -> dict:
    normalized = _normalize(order_number)
    if not normalized:
        return {"error": "Geçersiz sipariş numarası"}

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_number == normalized).first()
        if not order:
            return {"error": f"{order_number} numaralı sipariş bulunamadı"}
        return {
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "status": order.status,
            "estimated_delivery": order.estimated_delivery,
            "total_amount": order.total_amount,
        }
    finally:
        db.close()


def cancel_order(order_number: str, customer_name: str) -> dict:
    normalized = _normalize(order_number)
    if not normalized:
        return {"error": "Geçersiz sipariş numarası"}
    if not (customer_name or "").strip():
        return {"error": "Müşteri adı boş olamaz"}

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_number == normalized).first()
        if not order:
            return {"error": f"{order_number} numaralı sipariş bulunamadı"}
        if order.customer_name.strip().lower() != customer_name.strip().lower():
            return {"error": "Müşteri adı eşleşmedi"}
        if order.status in {"Teslim Edildi", "İptal Edildi"}:
            return {"error": f"Bu siparişin durumu '{order.status}', iptal edilemez"}

        # Stok iadesi (siparişte item varsa)
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        for it in items:
            product = db.query(Product).filter(Product.id == it.product_id).first()
            if product:
                product.stock += max(int(it.quantity), 0)

        order.status = "İptal Edildi"
        db.commit()
        return {"order_number": order.order_number, "status": order.status}
    finally:
        db.close()


def create_order(customer_name: str, city: str, items: list[dict]) -> dict:
    if not (customer_name or "").strip():
        return {"error": "Ad soyad bilgisi gerekli"}
    if not (city or "").strip():
        return {"error": "Şehir bilgisi gerekli"}
    if not items:
        return {"error": "En az 1 ürün gerekli"}

    db = SessionLocal()
    try:
        # yeni sıra no: ORD-(max+1)
        last = db.query(Order).order_by(Order.id.desc()).first()
        next_num = 1000
        if last and last.order_number:
            digits = re.sub(r"[^\d]", "", last.order_number)
            if digits.isdigit():
                next_num = int(digits) + 1
        order_number = f"ORD-{next_num}"

        order = Order(
            order_number=order_number,
            customer_name=customer_name.strip(),
            city=city.strip(),
            status="Hazırlanıyor",
            estimated_delivery=(datetime.utcnow() + timedelta(days=3)).strftime("%d %B %Y"),
            total_amount=0.0,
        )
        db.add(order)
        db.flush()

        total = 0.0
        created_items: list[dict] = []
        for it in items:
            name = (it.get("product_name") or "").strip()
            qty = int(it.get("quantity") or 0)
            if not name or qty <= 0:
                continue
            product = db.query(Product).filter(Product.name.ilike(f"%{name}%")).order_by(Product.id.asc()).first()
            if not product:
                return {"error": f"'{name}' adında ürün bulunamadı"}
            if product.stock < qty:
                return {"error": f"'{product.name}' için stok yetersiz (stok: {product.stock})"}

            product.stock -= qty
            unit_price = float(product.price or 0.0)
            total += unit_price * qty
            db.add(
                OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=qty,
                    unit_price=unit_price,
                )
            )
            created_items.append(
                {"product_id": product.id, "product_name": product.name, "quantity": qty, "unit_price": unit_price}
            )

        order.total_amount = float(total)
        db.commit()
        return {
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "city": order.city,
            "status": order.status,
            "estimated_delivery": order.estimated_delivery,
            "total_amount": order.total_amount,
            "items": created_items,
        }
    finally:
        db.close()


def update_order_items(
    order_number: str,
    customer_name: str,
    add_items: list[dict] | None = None,
    remove_items: list[dict] | None = None,
) -> dict:
    normalized = _normalize(order_number)
    if not normalized:
        return {"error": "Geçersiz sipariş numarası"}
    if not (customer_name or "").strip():
        return {"error": "Müşteri adı boş olamaz"}

    add_items = add_items or []
    remove_items = remove_items or []
    if not add_items and not remove_items:
        return {"error": "Eklenecek veya çıkarılacak ürün bulunamadı"}

    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_number == normalized).first()
        if not order:
            return {"error": f"{order_number} numaralı sipariş bulunamadı"}
        if order.customer_name.strip().lower() != customer_name.strip().lower():
            return {"error": "Müşteri adı eşleşmedi"}
        if order.status in {"Teslim Edildi", "İptal Edildi"}:
            return {"error": f"Bu siparişin durumu '{order.status}', güncellenemez"}

        # ürün çıkar: önce siparişteki item’dan düş, sonra stok iade et
        for it in remove_items:
            name = (it.get("product_name") or "").strip()
            qty = int(it.get("quantity") or 0)
            if not name or qty <= 0:
                continue
            product = db.query(Product).filter(Product.name.ilike(f"%{name}%")).order_by(Product.id.asc()).first()
            if not product:
                return {"error": f"'{name}' adında ürün bulunamadı"}
            oi = (
                db.query(OrderItem)
                .filter(OrderItem.order_id == order.id, OrderItem.product_id == product.id)
                .first()
            )
            if not oi or oi.quantity < qty:
                mevcut = oi.quantity if oi else 0
                return {"error": f"'{product.name}' siparişte yeterli değil (siparişte: {mevcut})"}
            oi.quantity -= qty
            product.stock += qty
            if oi.quantity == 0:
                db.delete(oi)

        # ürün ekle: stok düş, item’a ekle
        for it in add_items:
            name = (it.get("product_name") or "").strip()
            qty = int(it.get("quantity") or 0)
            if not name or qty <= 0:
                continue
            product = db.query(Product).filter(Product.name.ilike(f"%{name}%")).order_by(Product.id.asc()).first()
            if not product:
                return {"error": f"'{name}' adında ürün bulunamadı"}
            if product.stock < qty:
                return {"error": f"'{product.name}' için stok yetersiz (stok: {product.stock})"}
            product.stock -= qty
            oi = (
                db.query(OrderItem)
                .filter(OrderItem.order_id == order.id, OrderItem.product_id == product.id)
                .first()
            )
            if oi:
                oi.quantity += qty
            else:
                db.add(
                    OrderItem(
                        order_id=order.id,
                        product_id=product.id,
                        quantity=qty,
                        unit_price=float(product.price or 0.0),
                    )
                )

        # total hesapla
        items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
        total = 0.0
        result_items: list[dict] = []
        for oi in items:
            product = db.query(Product).filter(Product.id == oi.product_id).first()
            pname = product.name if product else f"Ürün-{oi.product_id}"
            total += float(oi.unit_price or 0.0) * int(oi.quantity or 0)
            result_items.append(
                {
                    "product_id": oi.product_id,
                    "product_name": pname,
                    "quantity": int(oi.quantity or 0),
                    "unit_price": float(oi.unit_price or 0.0),
                }
            )
        order.total_amount = float(total)
        db.commit()

        return {
            "order_number": order.order_number,
            "customer_name": order.customer_name,
            "status": order.status,
            "estimated_delivery": order.estimated_delivery,
            "total_amount": order.total_amount,
            "items": result_items,
        }
    finally:
        db.close()
