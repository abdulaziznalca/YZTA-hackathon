import os
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

os.environ["DATABASE_URL"] = "sqlite:///./test_supervisor_routing.db"

from app.agents import supervisor


def test_supervisor_maps_intents_to_agents(monkeypatch):
    def fake_route(_msg):
        return {
            "intents": ["order_status", "shipment_status"],
            "order_number": "128",
            "product_name": None,
            "customer_name": None,
        }

    monkeypatch.setattr(supervisor, "route_intents", fake_route)

    state = {"user_message": "128 numaralı siparişim nerede?"}
    result = supervisor.node_supervisor(state)

    assert result["intents"] == ["order_status", "shipment_status"]
    assert result["pending_agents"] == ["order_agent", "shipment_agent"]
    assert result["extracted_params"]["order_number"] == "128"


def test_supervisor_unknown_intent_yields_empty_pending(monkeypatch):
    monkeypatch.setattr(
        supervisor,
        "route_intents",
        lambda _m: {"intents": ["unknown_intent"], "order_number": None, "product_name": None, "customer_name": None},
    )

    result = supervisor.node_supervisor({"user_message": "merhaba"})
    assert result["pending_agents"] == []


def test_route_to_next_agent_returns_synthesizer_when_no_pending():
    assert supervisor.route_to_next_agent({"pending_agents": []}) == "synthesizer"


def test_route_to_next_agent_returns_first_pending():
    assert supervisor.route_to_next_agent({"pending_agents": ["stock_agent", "policy_agent"]}) == "stock_agent"
