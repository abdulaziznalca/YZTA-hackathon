import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

os.environ["DATABASE_URL"] = "sqlite:///./test_chat_endpoint.db"

from fastapi.testclient import TestClient

from app.api import chat as chat_module
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


def test_chat_endpoint_returns_handle_inbound_response(monkeypatch):
    _reset()

    async def fake_handle_inbound(message, db, channel="web", **kwargs):
        assert channel == "web"
        assert message == "Lavanta sabunu stokta var mı?"
        return "Lavanta Sabunu stokta mevcut, 12 adet."

    monkeypatch.setattr(chat_module, "handle_inbound", fake_handle_inbound)

    client = TestClient(app)
    response = client.post("/api/chat", json={"message": "Lavanta sabunu stokta var mı?"})
    assert response.status_code == 200
    data = response.json()
    assert data["response"] == "Lavanta Sabunu stokta mevcut, 12 adet."
    assert "intent" in data


def test_chat_endpoint_missing_message_returns_422():
    _reset()
    client = TestClient(app)
    response = client.post("/api/chat", json={})
    assert response.status_code == 422
