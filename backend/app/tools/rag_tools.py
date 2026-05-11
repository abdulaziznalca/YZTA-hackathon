from app.services import rag_service


def search_policy_document(question: str) -> str:
    return rag_service.search(question)
