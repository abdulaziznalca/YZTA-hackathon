from app.services.gemini_service import synthesize_responses, generate_response


def node_synthesize(state: dict) -> dict:
    results = state.get("agent_results", [])
    tickets = state.get("tickets", [])

    if not results:
        response = generate_response("", state["user_message"])
    elif len(results) == 1:
        response = results[0]["draft_response"]
    else:
        parts = "\n\n".join(f"[{r['agent']}]: {r['draft_response']}" for r in results)
        response = synthesize_responses(parts, state["user_message"])

    if tickets:
        ticket_refs = ", ".join(t["ticket_no"] for t in tickets if "ticket_no" in t)
        if ticket_refs and ticket_refs not in response:
            response = f"{response}\n\n📋 Takip numaranız: **{ticket_refs}**"

    return {**state, "final_response": response}
