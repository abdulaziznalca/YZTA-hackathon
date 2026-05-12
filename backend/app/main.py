from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import create_tables, run_migrations
from app.seed.seed_data import seed
from app.services import rag_service
from app.api import orders, shipments, stock, dashboard, chat, analytics, tickets, whatsapp

_POLICY_FILE = Path(__file__).parent.parent.parent / "docs" / "policy.md"


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_tables()
    run_migrations()
    seed()
    try:
        rag_service.initialize(str(_POLICY_FILE))
    except Exception as e:
        print(f"RAG init atlandı: {e}")
    yield


app = FastAPI(title="ShopPilot AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(orders.router)
app.include_router(shipments.router)
app.include_router(stock.router)
app.include_router(dashboard.router)
app.include_router(chat.router)
app.include_router(analytics.router)
app.include_router(tickets.router)
app.include_router(whatsapp.router)

@app.get("/")
def root():
    return {"message": "ShopPilot AI Backend Çalışıyor"}
