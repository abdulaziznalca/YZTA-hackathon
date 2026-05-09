from fastapi import FastAPI
from pydantic import BaseModel

from ai_service import ask_gemini

app = FastAPI()


class Question(BaseModel):
    message: str


@app.post("/chat")
def chat(q: Question):

    answer = ask_gemini(q.message)

    return {
        "response": answer
    }