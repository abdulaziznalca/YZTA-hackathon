from datetime import datetime, timedelta
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.db_models import ChatLog, Product


def get_chat_stats(db: Session, hours: int = 24) -> dict:
    since = datetime.utcnow() - timedelta(hours=hours)
    
    total = db.query(ChatLog).filter(ChatLog.created_at >= since).count()
    
    intent_counts = (
        db.query(ChatLog.intent, func.count(ChatLog.id).label("count"))
        .filter(ChatLog.created_at >= since, ChatLog.intent.isnot(None))
        .group_by(ChatLog.intent)
        .all()
    )
    
    return {
        "total_interactions": total,
        "intent_distribution": [
            {"intent": intent, "count": count} for intent, count in intent_counts
        ],
    }


def get_top_queried_products(db: Session, hours: int = 24, limit: int = 5) -> list:
    since = datetime.utcnow() - timedelta(hours=hours)
    
    product_queries = (
        db.query(
            ChatLog.extracted_product,
            func.count(ChatLog.id).label("query_count")
        )
        .filter(
            ChatLog.created_at >= since,
            ChatLog.extracted_product.isnot(None),
            ChatLog.extracted_product != ""
        )
        .group_by(ChatLog.extracted_product)
        .order_by(func.count(ChatLog.id).desc())
        .limit(limit)
        .all()
    )
    
    results = []
    for product_name, query_count in product_queries:
        product = db.query(Product).filter(
            Product.name.ilike(f"%{product_name}%")
        ).first()
        
        stock = product.stock if product else None
        stock_status = "unknown"
        if stock is not None:
            if stock == 0:
                stock_status = "out_of_stock"
            elif stock <= 5:
                stock_status = "critical"
            elif stock <= 10:
                stock_status = "low"
            else:
                stock_status = "ok"
        
        results.append({
            "product_name": product_name,
            "query_count": query_count,
            "current_stock": stock,
            "stock_status": stock_status,
        })
    
    return results


def get_analytics_summary(db: Session, hours: int = 24) -> dict:
    stats = get_chat_stats(db, hours)
    top_products = get_top_queried_products(db, hours)
    
    alerts = []
    for product in top_products:
        if product["stock_status"] in ["out_of_stock", "critical"]:
            alerts.append({
                "type": "stock_warning",
                "message": f"'{product['product_name']}' icin {product['query_count']} sorgu geldi, stok: {product['current_stock'] or 0}",
                "severity": "high" if product["stock_status"] == "out_of_stock" else "medium",
            })
    
    return {
        "period_hours": hours,
        "stats": stats,
        "top_queried_products": top_products,
        "alerts": alerts,
    }