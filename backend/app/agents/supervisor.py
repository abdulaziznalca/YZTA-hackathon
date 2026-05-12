from app.services.gemini_service import route_intents

_INTENT_TO_AGENT = {
    "order_status": "order_agent",
    "shipment_status": "shipment_agent",
    "stock_query": "stock_agent",
    "policy_question": "policy_agent",
    "manager_summary": "manager_agent",
    "complaint": "complaint_agent",
}


def node_supervisor(state: dict) -> dict:
    result = route_intents(state["user_message"])
    intents = result.get("intents", [])
    pending = [_INTENT_TO_AGENT[i] for i in intents if i in _INTENT_TO_AGENT]
    return {
        **state,
        "intents": intents,
        "extracted_params": {
            "order_number": result.get("order_number"),
            "product_name": result.get("product_name"),
        },
        "pending_agents": pending,
        "agent_results": [],
        "escalated_to": None,
    }


def route_to_next_agent(state: dict) -> str:
    pending = state.get("pending_agents", [])
    if not pending:
        return "synthesizer"
    return pending[0]
