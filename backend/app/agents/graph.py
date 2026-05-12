from langgraph.graph import StateGraph, END

from app.agents.state import AgentState
from app.agents.supervisor import node_supervisor, route_to_next_agent
from app.agents.synthesizer import node_synthesize
from app.agents.specialists.order_agent import node_order_agent
from app.agents.specialists.shipment_agent import node_shipment_agent
from app.agents.specialists.stock_agent import node_stock_agent
from app.agents.specialists.policy_agent import node_policy_agent
from app.agents.specialists.manager_agent import node_manager_agent
from app.agents.specialists.complaint_agent import node_complaint_agent

_AGENT_ROUTING = {
    "order_agent": "order_agent",
    "shipment_agent": "shipment_agent",
    "stock_agent": "stock_agent",
    "policy_agent": "policy_agent",
    "manager_agent": "manager_agent",
    "complaint_agent": "complaint_agent",
    "synthesizer": "synthesizer",
}


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("supervisor", node_supervisor)
    graph.add_node("order_agent", node_order_agent)
    graph.add_node("shipment_agent", node_shipment_agent)
    graph.add_node("stock_agent", node_stock_agent)
    graph.add_node("policy_agent", node_policy_agent)
    graph.add_node("manager_agent", node_manager_agent)
    graph.add_node("complaint_agent", node_complaint_agent)
    graph.add_node("synthesizer", node_synthesize)

    graph.set_entry_point("supervisor")

    for node in ("supervisor", "order_agent", "shipment_agent", "stock_agent",
                 "policy_agent", "manager_agent", "complaint_agent"):
        graph.add_conditional_edges(node, route_to_next_agent, _AGENT_ROUTING)

    graph.add_edge("synthesizer", END)

    return graph.compile()


agent_graph = build_graph()
