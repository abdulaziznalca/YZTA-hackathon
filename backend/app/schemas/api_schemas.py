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


class OrderItemResponse(BaseModel):
    product_id: int
    product_name: str
    quantity: int
    unit_price: float


class OrderDetailResponse(BaseModel):
    id: int
    order_number: str
    customer_name: str
    city: Optional[str]
    status: str
    estimated_delivery: Optional[str]
    total_amount: float
    items: list[OrderItemResponse]

    class Config:
        from_attributes = True


class OrderCreateItem(BaseModel):
    product_name: str
    quantity: int


class OrderCreateRequest(BaseModel):
    customer_name: str
    city: str
    items: list[OrderCreateItem]


class OrderCancelRequest(BaseModel):
    customer_name: str
    order_number: str


class OrderUpdateItem(BaseModel):
    product_name: str
    quantity: int


class OrderUpdateRequest(BaseModel):
    order_number: str
    customer_name: str
    add_items: list[OrderUpdateItem] = []
    remove_items: list[OrderUpdateItem] = []


class StockUpdateRequest(BaseModel):
    product_name: str
    new_stock: int


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
