from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Order, Product
from app.schemas.api_schemas import DashboardSummary, CriticalStockItem

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def get_summary(db: Session = Depends(get_db)):
    total_orders = db.query(Order).count()
    shipped_orders = db.query(Order).filter(Order.status == "Kargoya Verildi").count()
    delayed_orders = db.query(Order).filter(Order.status == "Gecikti").count()
    total_products = db.query(Product).count()
    critical_stock = db.query(Product).filter(Product.stock <= 5).all()

    return DashboardSummary(
        total_orders=total_orders,
        shipped_orders=shipped_orders,
        delayed_orders=delayed_orders,
        total_products=total_products,
        critical_stock=[CriticalStockItem(name=p.name, stock=p.stock) for p in critical_stock],
    )
