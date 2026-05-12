import asyncio
from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.api_schemas import ChatRequest, ChatResponse
from app.agents.graph import agent_graph
from app.database import get_db
from app.models.db_models import ChatLog

router = APIRouter(prefix="/api/chat", tags=["chat"])
_executor = ThreadPoolExecutor(max_workers=4)


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    initial_state = {
        "user_message": request.message,
        "intents": [],
        "extracted_params": {},
        "pending_agents": [],
        "agent_results": [],
        "final_response": "",
        "escalated_to": None,
    }

    loop = asyncio.get_running_loop()
    result = await loop.run_in_executor(
        _executor,
        lambda: agent_graph.invoke(initial_state),
    )

    intents_str = ",".join(result.get("intents", []))
    params = result.get("extracted_params", {})

    log = ChatLog(
        user_message=request.message,
        ai_response=result["final_response"],
        intent=intents_str or None,
        extracted_product=(params.get("product_name") or "").strip().title() or None,
        extracted_order=params.get("order_number"),
    )
    db.add(log)
    db.commit()

    return ChatResponse(
        response=result["final_response"],
        intent=intents_str,
    )
