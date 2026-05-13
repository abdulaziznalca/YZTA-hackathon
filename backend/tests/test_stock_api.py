import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

os.environ["DATABASE_URL"] = "sqlite:///./test_stock_api.db"

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


def test_list_stock_orders_by_stock_ascending():
    _reset()
    client = TestClient(app)
    response = client.get("/api/stock")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    stocks = [p["stock"] for p in data]
    assert stocks == sorted(stocks)


def test_search_stock_returns_matching_products():
    _reset()
    client = TestClient(app)
    response = client.get("/api/stock/search", params={"q": "Lavanta"})
    assert response.status_code == 200
    data = response.json()
    assert any("Lavanta" in p["name"] for p in data)


def test_search_stock_no_match_returns_empty_list():
    _reset()
    client = TestClient(app)
    response = client.get("/api/stock/search", params={"q": "OlmayanUrunXYZ"})
    assert response.status_code == 200
    assert response.json() == []


def test_update_stock_validation_rejects_negative():
    _reset()
    client = TestClient(app)
    response = client.patch(
        "/api/stock/update",
        json={"product_name": "Lavanta Sabunu", "new_stock": -5},
    )
    assert response.status_code == 400
