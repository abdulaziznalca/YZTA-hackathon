from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.analytics_service import get_analytics_summary, get_chat_stats, get_top_queried_products

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.get("/summary")
def analytics_summary(
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    return get_analytics_summary(db, hours)


@router.get("/stats")
def chat_stats(
    hours: int = Query(default=24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    return get_chat_stats(db, hours)


@router.get("/top-products")
def top_products(
    hours: int = Query(default=24, ge=1, le=168),
    limit: int = Query(default=5, ge=1, le=20),
    db: Session = Depends(get_db)
):
    return get_top_queried_products(db, hours, limit)