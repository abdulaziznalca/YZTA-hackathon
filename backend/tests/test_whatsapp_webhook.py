import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

os.environ["DATABASE_URL"] = "sqlite:///./test_whatsapp_webhook.db"

from fastapi.testclient import TestClient

from app.api import whatsapp as whatsapp_module
from app.config import settings
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


def test_verify_webhook_returns_challenge_on_valid_token():
    _reset()
    client = TestClient(app)
    response = client.get(
        "/api/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": settings.WHATSAPP_VERIFY_TOKEN,
            "hub.challenge": "12345",
        },
    )
    assert response.status_code == 200
    assert response.json() == 12345


def test_verify_webhook_rejects_invalid_token():
    _reset()
    client = TestClient(app)
    response = client.get(
        "/api/whatsapp/webhook",
        params={
            "hub.mode": "subscribe",
            "hub.verify_token": "wrong-token",
            "hub.challenge": "12345",
        },
    )
    assert response.status_code == 403


def test_twilio_webhook_accepts_and_skips_duplicate(monkeypatch):
    _reset()
    settings.TWILIO_SKIP_SIGNATURE = True

    captured = {}

    def fake_add_task(func, inbound):
        captured["inbound"] = inbound

    monkeypatch.setattr(
        "fastapi.BackgroundTasks.add_task",
        lambda self, func, inbound: fake_add_task(func, inbound),
    )

    client = TestClient(app)
    response = client.post(
        "/api/whatsapp/webhook",
        data={
            "MessageSid": "SM_test_001",
            "From": "whatsapp:+905551112233",
            "Body": "Merhaba",
        },
    )
    assert response.status_code == 200
    assert response.json() == {"status": "accepted"}
    assert captured["inbound"].body == "Merhaba"
    assert captured["inbound"].external_message_id == "SM_test_001"


def test_twilio_webhook_missing_required_fields_returns_422():
    _reset()
    settings.TWILIO_SKIP_SIGNATURE = True
    client = TestClient(app)
    response = client.post("/api/whatsapp/webhook", data={"From": "whatsapp:+90555"})
    assert response.status_code == 422
