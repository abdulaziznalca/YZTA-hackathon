from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.db_models import Base

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_tables():
    Base.metadata.create_all(bind=engine)


def run_migrations():
    """Apply lightweight schema migrations for legacy local SQLite databases."""
    if engine.dialect.name != "sqlite":
        return

    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())

    if "orders" in table_names:
        columns = {col["name"] for col in inspector.get_columns("orders")}
        if "city" not in columns:
            with engine.begin() as conn:
                conn.execute(text("ALTER TABLE orders ADD COLUMN city VARCHAR"))

    if "chat_logs" in table_names:
        columns = {col["name"] for col in inspector.get_columns("chat_logs")}
        with engine.begin() as conn:
            if "channel" not in columns:
                conn.execute(text("ALTER TABLE chat_logs ADD COLUMN channel VARCHAR NOT NULL DEFAULT 'web'"))
            if "external_message_id" not in columns:
                conn.execute(text("ALTER TABLE chat_logs ADD COLUMN external_message_id VARCHAR"))
            if "sender_phone" not in columns:
                conn.execute(text("ALTER TABLE chat_logs ADD COLUMN sender_phone VARCHAR"))


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
