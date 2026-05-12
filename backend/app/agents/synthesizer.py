from app.services.gemini_service import synthesize_responses, generate_response


def node_synthesize(state: dict) -> dict:
    results = state.get("agent_results", [])

    if not results:
        response = generate_response("", state["user_message"])
    elif len(results) == 1:
        response = results[0]["draft_response"]
    else:
        parts = "\n\n".join(f"[{r['agent']}]: {r['draft_response']}" for r in results)
        response = synthesize_responses(parts, state["user_message"])

    return {**state, "final_response": response}
