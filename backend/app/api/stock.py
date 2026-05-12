from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.db_models import Product
from app.schemas.api_schemas import ProductResponse, StockUpdateRequest
from app.tools.stock_tools import update_product_stock

router = APIRouter(prefix="/api/stock", tags=["stock"])


@router.get("", response_model=list[ProductResponse])
def list_stock(db: Session = Depends(get_db)):
    return db.query(Product).order_by(Product.stock.asc()).all()


@router.get("/search", response_model=list[ProductResponse])
def search_stock(q: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    return db.query(Product).filter(Product.name.ilike(f"%{q}%")).all()


@router.patch("/update", response_model=ProductResponse)
def update_stock(request: StockUpdateRequest):
    result = update_product_stock(product_name=request.product_name, new_stock=request.new_stock)
    if isinstance(result, dict) and result.get("error"):
        raise HTTPException(status_code=400, detail=result["error"])
    return result
