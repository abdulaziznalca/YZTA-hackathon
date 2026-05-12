import json

from app.services.gemini_service import generate_response_with_system


def run_specialist(state: dict, agent_name: str, intent: str, system_prompt: str, tool_result) -> dict:
    tool_result_str = tool_result if isinstance(tool_result, str) else json.dumps(tool_result, ensure_ascii=False)
    draft = generate_response_with_system(system_prompt, tool_result_str, state["user_message"])
    result_entry = {
        "agent": agent_name,
        "intent": intent,
        "tool_result": tool_result_str,
        "draft_response": draft,
    }
    return {
        **state,
        "agent_results": state["agent_results"] + [result_entry],
        "pending_agents": state["pending_agents"][1:],
    }
