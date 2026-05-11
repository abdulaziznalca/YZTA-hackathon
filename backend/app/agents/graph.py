from langgraph.graph import StateGraph, END

from app.agents.nodes import (
    AgentState,
    node_detect_intent,
    node_execute_tool,
    node_generate_response,
    route_by_intent,
)


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("detect_intent", node_detect_intent)
    graph.add_node("execute_tool", node_execute_tool)
    graph.add_node("generate_response", node_generate_response)

    graph.set_entry_point("detect_intent")

    graph.add_conditional_edges(
        "detect_intent",
        route_by_intent,
        {
            "execute_tool": "execute_tool",
            "generate_response": "generate_response",
        },
    )

    graph.add_edge("execute_tool", "generate_response")
    graph.add_edge("generate_response", END)

    return graph.compile()


agent_graph = build_graph()
