from typing import TypedDict, Optional


class AgentState(TypedDict):
    user_message: str
    intents: list[str]
    extracted_params: dict
    pending_agents: list[str]
    agent_results: list[dict]
    final_response: str
    escalated_to: Optional[str]
    tickets: list[dict]
