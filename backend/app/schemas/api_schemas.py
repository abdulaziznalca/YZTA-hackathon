from pydantic import BaseModel
from typing import Optional


class ProductResponse(BaseModel):
    id: int
    name: str
    stock: int
    price: float

    class Config:
        from_attributes = True


class OrderResponse(BaseModel):
    id: int
    order_number: str
    customer_name: str
    status: str
    estimated_delivery: Optional[str]
    total_amount: float

    class Config:
        from_attributes = True


class ShipmentResponse(BaseModel):
    id: int
    order_id: int
    carrier: str
    tracking_number: str
    current_location: Optional[str]
    status: str

    class Config:
        from_attributes = True


class CriticalStockItem(BaseModel):
    name: str
    stock: int


class DashboardSummary(BaseModel):
    total_orders: int
    shipped_orders: int
    delayed_orders: int
    total_products: int
    critical_stock: list[CriticalStockItem]


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    response: str
    intent: str
