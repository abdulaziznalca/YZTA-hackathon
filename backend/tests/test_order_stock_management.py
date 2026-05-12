import os
import sqlite3
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

os.environ["DATABASE_URL"] = "sqlite:///./test_shoppilot.db"

from app.database import SessionLocal, create_tables, engine, run_migrations
from app.models.db_models import Product
from app.seed.seed_data import seed
from app.tools.order_tools import cancel_order, create_order
from app.tools.stock_tools import update_product_stock


def _db_file() -> Path:
    database = engine.url.database
    if not database:
        raise RuntimeError("SQLite database path not found")
    return Path(database)


def _reset_db_file() -> None:
    db_file = _db_file()
    engine.dispose()
    if db_file.exists():
        db_file.unlink()


def test_sqlite_migration_adds_city_column_for_legacy_orders_table():
    _reset_db_file()
    db_file = _db_file()
    conn = sqlite3.connect(db_file)
    try:
        conn.execute(
            """
            CREATE TABLE orders (
                id INTEGER NOT NULL,
                order_number VARCHAR NOT NULL,
                customer_name VARCHAR NOT NULL,
                status VARCHAR NOT NULL,
                estimated_delivery VARCHAR,
                total_amount FLOAT NOT NULL,
                PRIMARY KEY (id)
            );
            """
        )
        conn.commit()
    finally:
        conn.close()

    run_migrations()

    conn = sqlite3.connect(db_file)
    try:
        rows = conn.execute("PRAGMA table_info(orders);").fetchall()
        columns = {row[1] for row in rows}
    finally:
        conn.close()
    assert "city" in columns


def test_create_and_cancel_order_updates_stock_consistently():
    _reset_db_file()
    create_tables()
    run_migrations()
    seed()

    db = SessionLocal()
    try:
        before = db.query(Product).filter(Product.name == "Lavanta Sabunu").first()
        assert before is not None
        before_stock = before.stock
    finally:
        db.close()

    created = create_order(
        customer_name="Test User",
        city="Istanbul",
        items=[{"product_name": "Lavanta Sabunu", "quantity": 1}],
    )
    assert "error" not in created
    assert created["city"] == "Istanbul"
    assert created["items"][0]["quantity"] == 1

    db = SessionLocal()
    try:
        after_create = db.query(Product).filter(Product.name == "Lavanta Sabunu").first()
        assert after_create is not None
        assert after_create.stock == before_stock - 1
    finally:
        db.close()

    cancelled = cancel_order(created["order_number"], "Test User")
    assert cancelled["status"] == "İptal Edildi"

    db = SessionLocal()
    try:
        after_cancel = db.query(Product).filter(Product.name == "Lavanta Sabunu").first()
        assert after_cancel is not None
        assert after_cancel.stock == before_stock
    finally:
        db.close()


def test_stock_update_validation():
    _reset_db_file()
    create_tables()
    run_migrations()
    seed()

    bad = update_product_stock("Lavanta Sabunu", -1)
    assert bad["error"] == "Stok 0'dan küçük olamaz"

    good = update_product_stock("Lavanta Sabunu", 12)
    assert good["name"] == "Lavanta Sabunu"
    assert good["stock"] == 12
