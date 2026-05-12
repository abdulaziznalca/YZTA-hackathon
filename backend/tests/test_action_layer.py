import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

os.environ["DATABASE_URL"] = "sqlite:///./test_action_layer.db"

from app.database import SessionLocal, create_tables, engine, run_migrations
from app.models.db_models import ActionLog, Product, SupportTicket
from app.seed.seed_data import seed
from app.tools.action_tools import (
    create_cancel_request,
    create_complaint,
    create_stock_alert,
    get_ticket,
)
from app.tools.stock_tools import update_product_stock


def _db_file() -> Path:
    database = engine.url.database
    if not database:
        raise RuntimeError("SQLite database path not found")
    return Path(database)


def _reset() -> None:
    engine.dispose()
    db_file = _db_file()
    if db_file.exists():
        db_file.unlink()
    create_tables()
    run_migrations()
    seed()


# ─── Test 1 ───────────────────────────────────────────────────────────────────
def test_create_complaint_creates_ticket():
    _reset()
    result = create_complaint(
        customer_name="Ayşe Kaya",
        subject="Ürün bozuk geldi",
        description="Siparişim kırık kutuda geldi.",
    )
    assert "ticket_no" in result
    assert result["type"] == "complaint"
    assert result["status"] == "open"

    db = SessionLocal()
    try:
        ticket = db.query(SupportTicket).filter(SupportTicket.ticket_no == result["ticket_no"]).first()
        assert ticket is not None
        assert ticket.type == "complaint"

        log = db.query(ActionLog).filter(ActionLog.ticket_id == ticket.id).first()
        assert log is not None
        assert log.result == "ok"
    finally:
        db.close()


# ─── Test 2 ───────────────────────────────────────────────────────────────────
def test_complaint_idempotent():
    _reset()
    desc = "Kargo çok geç geldi ve paket hasar görmüştü."
    r1 = create_complaint(customer_name="Mehmet Demir", subject="Geç teslimat", description=desc)
    r2 = create_complaint(customer_name="Mehmet Demir", subject="Geç teslimat", description=desc)
    assert "ticket_no" in r1
    assert r1["ticket_no"] == r2["ticket_no"]

    db = SessionLocal()
    try:
        count = (
            db.query(SupportTicket)
            .filter(SupportTicket.type == "complaint", SupportTicket.customer_name == "Mehmet Demir")
            .count()
        )
        assert count == 1
    finally:
        db.close()


# ─── Test 3 ───────────────────────────────────────────────────────────────────
def test_cancel_request_success():
    _reset()
    from app.tools.order_tools import create_order

    created = create_order(
        customer_name="Fatma Yıldız",
        city="Ankara",
        items=[{"product_name": "Lavanta Sabunu", "quantity": 1}],
    )
    assert "error" not in created

    result = create_cancel_request(
        order_number=created["order_number"],
        customer_name="Fatma Yıldız",
        reason="Ürüne ihtiyacım kalmadı",
    )
    assert "ticket_no" in result
    assert result["type"] == "cancel_request"
    assert result["status"] == "approved"

    db = SessionLocal()
    try:
        from app.models.db_models import Order
        order = db.query(Order).filter(Order.order_number == created["order_number"]).first()
        assert order is not None
        assert order.status == "İptal Edildi"
    finally:
        db.close()


# ─── Test 4 ───────────────────────────────────────────────────────────────────
def test_cancel_request_rejected_for_delivered():
    _reset()
    from app.tools.order_tools import create_order
    from app.models.db_models import Order

    created = create_order(
        customer_name="Ali Öztürk",
        city="İzmir",
        items=[{"product_name": "Lavanta Sabunu", "quantity": 1}],
    )
    assert "error" not in created

    # Manuel olarak siparişi "Teslim Edildi" yap
    db = SessionLocal()
    try:
        order = db.query(Order).filter(Order.order_number == created["order_number"]).first()
        order.status = "Teslim Edildi"
        db.commit()
    finally:
        db.close()

    result = create_cancel_request(
        order_number=created["order_number"],
        customer_name="Ali Öztürk",
        reason="İstemiyorum",
    )
    assert "ticket_no" in result
    assert result["status"] == "rejected"


# ─── Test 5 ───────────────────────────────────────────────────────────────────
def test_stock_alert_under_threshold():
    _reset()
    # Stoku 3'e düşür
    update_product_stock("Lavanta Sabunu", 3)

    result = create_stock_alert("Lavanta Sabunu", threshold=5)
    assert "ticket_no" in result
    assert result["type"] == "stock_alert"
    assert result["status"] == "open"

    db = SessionLocal()
    try:
        ticket = db.query(SupportTicket).filter(SupportTicket.ticket_no == result["ticket_no"]).first()
        assert ticket is not None
        assert ticket.type == "stock_alert"
    finally:
        db.close()


# ─── Test 6 ───────────────────────────────────────────────────────────────────
def test_stock_alert_above_threshold():
    _reset()
    update_product_stock("Lavanta Sabunu", 50)

    result = create_stock_alert("Lavanta Sabunu", threshold=5)
    assert "info" in result
    assert result["info"] == "stok yeterli"

    db = SessionLocal()
    try:
        count = db.query(SupportTicket).filter(SupportTicket.type == "stock_alert").count()
        assert count == 0
    finally:
        db.close()


# ─── Test 7 ───────────────────────────────────────────────────────────────────
def test_get_ticket_endpoint():
    _reset()
    created = create_complaint(
        customer_name="Test Kullanıcı",
        subject="Test şikayeti",
        description="Bu bir test şikayetidir.",
    )
    assert "ticket_no" in created

    from fastapi.testclient import TestClient
    from app.main import app

    client = TestClient(app)
    response = client.get(f"/api/tickets/{created['ticket_no']}")
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_no"] == created["ticket_no"]
    assert data["type"] == "complaint"
