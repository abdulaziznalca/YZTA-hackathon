from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.api_schemas import ChatRequest, ChatResponse
from app.database import get_db
from app.services.channel_dispatcher import handle_inbound

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    response_text = await handle_inbound(
        message=request.message,
        db=db,
        channel="web",
    )
    return ChatResponse(response=response_text, intent="")
