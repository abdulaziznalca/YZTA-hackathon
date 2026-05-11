from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    stock = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, nullable=False, index=True)
    customer_name = Column(String, nullable=False)
    status = Column(String, nullable=False, default="Hazırlanıyor")
    estimated_delivery = Column(String, nullable=True)
    total_amount = Column(Float, nullable=False, default=0.0)

    shipment = relationship("Shipment", back_populates="order", uselist=False)


class Shipment(Base):
    __tablename__ = "shipments"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    carrier = Column(String, nullable=False)
    tracking_number = Column(String, nullable=False)
    current_location = Column(String, nullable=True)
    status = Column(String, nullable=False, default="Yolda")

    order = relationship("Order", back_populates="shipment")


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_message = Column(Text, nullable=False)
    ai_response = Column(Text, nullable=False)
    intent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
