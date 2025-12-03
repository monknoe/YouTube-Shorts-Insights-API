from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from fastapi import Query
import os
import signal

app = FastAPI()

@app.get("/")
def read_root():
    return {"day": 7, "message": "Welcome to Day 7!"}

def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return fastapi.Response(status_code=200, content='Server shutting down...')

@app.on_event('shutdown')
def on_shutdown():
    print('Server shutting down...')

class Item(BaseModel):
    name: str
    price: float=Query(..., ge=0)
    description: Optional[str] = None

class RequestBody(BaseModel):
    keyword: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

# 假資料庫
items =[Item(name="Apple", price=10, description="Fresh red apple"),
        Item(name="Banana", price=5, description="Yellow ripe banana"),
        Item(name="Milk", price=25, description="Whole milk 1L"),]

@app.post("/items")
def create_item(item: Item):
    items.append(item)
    return {
        "message": "Item created!",
        "item": item
    }

@app.post("/items/search_body")
def search_items(body: RequestBody):
    results = items

    if body.keyword:
        kw = body.keyword.lower()
        results = [
            item for item in results
            if kw in item.name.lower() or kw in (item.description or "").lower()
        ]

    if body.min_price is not None:
        results = [item for item in results if item.price >= body.min_price]

    if body.max_price is not None:
        results = [item for item in results if item.price <= body.max_price]

    return results