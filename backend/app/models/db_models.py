from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    stock = Column(Integer, nullable=False, default=0)
    price = Column(Float, nullable=False)

    items = relationship("OrderItem", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    order_number = Column(String, unique=True, nullable=False, index=True)
    customer_name = Column(String, nullable=False)
    city = Column(String, nullable=True)
    status = Column(String, nullable=False, default="Hazırlanıyor")
    estimated_delivery = Column(String, nullable=True)
    total_amount = Column(Float, nullable=False, default=0.0)

    shipment = relationship("Shipment", back_populates="order", uselist=False)
    items = relationship("OrderItem", back_populates="order", cascade="all, delete-orphan")


class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False, default=0.0)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="items")


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
    extracted_product = Column(String, nullable=True)
    extracted_order = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # WhatsApp channel fields
    channel = Column(String, nullable=False, default="web")  # "web" | "whatsapp"
    external_message_id = Column(String, nullable=True, index=True)
    sender_phone = Column(String, nullable=True)  # masked: +90****1234


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    ticket_no = Column(String, unique=True, nullable=False, index=True)
    type = Column(String, nullable=False)        # cancel_request | complaint | stock_alert
    status = Column(String, nullable=False, default="open")  # open | approved | rejected | resolved
    source = Column(String, nullable=False, default="web_chat")  # web_chat | api | whatsapp
    customer_name = Column(String, nullable=True)
    order_number = Column(String, nullable=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    meta_json = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    action_logs = relationship("ActionLog", back_populates="ticket")


class ActionLog(Base):
    __tablename__ = "action_logs"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("support_tickets.id"), nullable=True)
    action = Column(String, nullable=False)
    actor = Column(String, nullable=False, default="agent")  # agent | system | user
    payload_json = Column(Text, nullable=True)
    result = Column(String, nullable=False, default="ok")    # ok | error
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    ticket = relationship("SupportTicket", back_populates="action_logs")