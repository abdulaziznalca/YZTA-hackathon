import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

os.environ["DATABASE_URL"] = "sqlite:///./test_orders_api.db"

from fastapi.testclient import TestClient

from app.database import create_tables, engine, run_migrations
from app.main import app
from app.seed.seed_data import seed


def _reset() -> None:
    engine.dispose()
    db_file = Path(engine.url.database)
    if db_file.exists():
        db_file.unlink()
    create_tables()
    run_migrations()
    seed()


def test_list_orders_returns_seeded_data():
    _reset()
    client = TestClient(app)
    response = client.get("/api/orders")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 10
    order_numbers = {o["order_number"] for o in data}
    assert "ORD-128" in order_numbers


def test_get_order_by_number_with_prefix():
    _reset()
    client = TestClient(app)
    response = client.get("/api/orders/by-number/ORD-128")
    assert response.status_code == 200
    assert response.json()["order_number"] == "ORD-128"


def test_get_order_by_number_without_prefix_normalizes():
    _reset()
    client = TestClient(app)
    response = client.get("/api/orders/by-number/129")
    assert response.status_code == 200
    assert response.json()["order_number"] == "ORD-129"


def test_get_order_by_number_404():
    _reset()
    client = TestClient(app)
    response = client.get("/api/orders/by-number/ORD-9999")
    assert response.status_code == 404
