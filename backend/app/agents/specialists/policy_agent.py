from app.tools.rag_tools import search_policy_document
from app.agents.specialists.base import run_specialist

_SYSTEM_PROMPT = """Sen ShopPilot AI müşteri hizmetleri politika uzmanısın.
İade, hasar, garanti ve politika sorularını belgelerden alınan bilgiye dayanarak Türkçe yanıtla.
Bilgi belgelerinde yoksa bunu açıkça belirt, uydurma."""


def node_policy_agent(state: dict) -> dict:
    tool_result = search_policy_document(state["user_message"])
    return run_specialist(state, "policy_agent", "policy_question", _SYSTEM_PROMPT, tool_result)
