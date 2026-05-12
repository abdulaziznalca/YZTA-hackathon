import json
from typing import TypedDict

from app.services.gemini_service import detect_intent, generate_response
from app.tools.order_tools import cancel_order, create_order, get_order_by_number, update_order_items
from app.tools.shipment_tools import get_shipment_by_order_number
from app.tools.stock_tools import check_product_stock, update_product_stock
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
            "customer_name": result.get("customer_name"),
            "city": result.get("city"),
            "quantity": result.get("quantity"),
            "update_action": result.get("update_action"),
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
        elif intent == "order_cancel":
            order_number = params.get("order_number")
            customer_name = params.get("customer_name")
            if not customer_name:
                result = {"ask": "Siparişi iptal edebilmem için ad soyad bilginizi yazar mısınız?"}
            elif not order_number:
                result = {"ask": "Sipariş numaranızı yazar mısınız? (Örn: 128 veya ORD-128)"}
            else:
                result = cancel_order(order_number=str(order_number), customer_name=str(customer_name))
        elif intent == "order_create":
            customer_name = params.get("customer_name")
            city = params.get("city")
            product_name = params.get("product_name")
            quantity = params.get("quantity")
            if not customer_name:
                result = {"ask": "Yeni sipariş oluşturmak için ad soyad bilginizi yazar mısınız?"}
            elif not city:
                result = {"ask": "Hangi şehir için sipariş oluşturayım?"}
            elif not product_name:
                result = {"ask": "Hangi ürünü eklemek istersiniz? Ürün adını yazar mısınız?"}
            elif not quantity:
                result = {"ask": "Kaç adet istersiniz? (Örn: 2)"}
            else:
                result = create_order(
                    customer_name=str(customer_name),
                    city=str(city),
                    items=[{"product_name": str(product_name), "quantity": int(quantity)}],
                )
        elif intent == "order_update":
            order_number = params.get("order_number")
            customer_name = params.get("customer_name")
            product_name = params.get("product_name")
            quantity = params.get("quantity")
            action = params.get("update_action")
            if not customer_name:
                result = {"ask": "Siparişi güncelleyebilmem için ad soyad bilginizi yazar mısınız?"}
            elif not order_number:
                result = {"ask": "Hangi siparişi güncelleyelim? Sipariş numaranızı yazar mısınız? (Örn: 129)"}
            elif not product_name:
                result = {"ask": "Hangi ürünü eklemek veya çıkarmak istersiniz? Ürün adını yazar mısınız?"}
            elif not quantity:
                result = {"ask": "Kaç adet ekleyelim/çıkaralım? (Örn: 1)"}
            elif action not in {"add", "remove"}:
                result = {"ask": "Bu ürünü siparişe ekleyeyim mi yoksa çıkarayım mı? (ekle/çıkar)"}
            else:
                add_items = [{"product_name": str(product_name), "quantity": int(quantity)}] if action == "add" else []
                remove_items = [{"product_name": str(product_name), "quantity": int(quantity)}] if action == "remove" else []
                result = update_order_items(
                    order_number=str(order_number),
                    customer_name=str(customer_name),
                    add_items=add_items,
                    remove_items=remove_items,
                )
        elif intent == "stock_update":
            product_name = params.get("product_name")
            quantity = params.get("quantity")
            if not product_name:
                result = {"ask": "Hangi ürünün stokunu güncelleyelim? Ürün adını yazar mısınız?"}
            elif quantity is None:
                result = {"ask": "Yeni stok adedini yazar mısınız? (Örn: 25)"}
            else:
                result = update_product_stock(product_name=str(product_name), new_stock=int(quantity))
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
    # Tool özel bir soru döndürdüyse, doğrudan kullanıcıya sor.
    try:
        parsed = json.loads(state.get("tool_result", "") or "{}")
        if isinstance(parsed, dict) and parsed.get("ask"):
            return {**state, "final_response": str(parsed["ask"])}
    except Exception:
        pass

    response = generate_response(state.get("tool_result", ""), state["user_message"])
    return {**state, "final_response": response}
