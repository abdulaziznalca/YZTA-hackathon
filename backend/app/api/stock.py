from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Product
from app.schemas.api_schemas import ProductResponse

router = APIRouter(prefix="/api/stock", tags=["stock"])


@router.get("", response_model=list[ProductResponse])
def list_stock(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.stock.asc()).all()


@router.get("/search", response_model=list[ProductResponse])
def search_stock(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.name.ilike(f"%{q}%")).all()
