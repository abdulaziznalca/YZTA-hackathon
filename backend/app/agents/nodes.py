import json
from typing import TypedDict

from app.services.gemini_service import detect_intent, generate_response
from app.tools.order_tools import get_order_by_number
from app.tools.shipment_tools import get_shipment_by_order_number
from app.tools.stock_tools import check_product_stock
from app.tools.rag_tools import search_policy_document
from app.tools.dashboard_tools import generate_daily_summary


class AgentState(TypedDict):
    user_message: str
    intent: str
    extracted_params: dict
    tool_result: str
    final_response: str


def node_detect_intent(state: AgentState) -> AgentState:
    result = detect_intent(state["user_message"])
    return {
        **state,
        "intent": result.get("intent", "unknown"),
        "extracted_params": {
            "order_number": result.get("order_number"),
            "product_name": result.get("product_name"),
        },
    }


def route_by_intent(state: AgentState) -> str:
    if state["intent"] == "unknown":
        return "generate_response"
    return "execute_tool"


def node_execute_tool(state: AgentState) -> AgentState:
    intent = state["intent"]
    params = state["extracted_params"]

    try:
        if intent == "order_status":
            result = get_order_by_number(params.get("order_number") or "")
        elif intent == "shipment_status":
            result = get_shipment_by_order_number(params.get("order_number") or "")
        elif intent == "stock_query":
            result = check_product_stock(params.get("product_name") or "")
        elif intent == "policy_question":
            result = search_policy_document(state["user_message"])
        elif intent == "complaint":
            result = {"bilgi": "Şikayetiniz alındı ve yöneticiye iletildi. En kısa sürede dönüş yapılacak."}
        elif intent == "manager_summary":
            result = generate_daily_summary()
        else:
            result = {}
    except Exception as e:
        result = {"error": str(e)}

    tool_result = result if isinstance(result, str) else json.dumps(result, ensure_ascii=False)
    return {**state, "tool_result": tool_result}


def node_generate_response(state: AgentState) -> AgentState:
    response = generate_response(state.get("tool_result", ""), state["user_message"])
    return {**state, "final_response": response}
