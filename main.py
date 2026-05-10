from fastapi import FastAPI
from pydantic import BaseModel

from ai_service import ask_gemini
from database import (
    get_order_by_id,
    get_product_by_name
)

app = FastAPI()


class Question(BaseModel):
    message: str


@app.get("/")
def root():
    return {
        "message": "KOBI AI Backend Calisiyor"
    }


@app.post("/chat")
def chat(q: Question):

    answer = ask_gemini(q.message)

    return {
        "response": answer
    }


@app.get("/orders/{order_id}")
def get_order(order_id: int):

    order = get_order_by_id(order_id)

    if order:

        return {
            "id": order[0],
            "customer": order[1],
            "status": order[2],
            "delivery_date": order[3]
        }

    return {
        "error": "Sipariş bulunamadı"
    }


@app.get("/products/{product_name}")
def get_product(product_name: str):

    products = get_product_by_name(product_name)

    return {
        "products": products
    }