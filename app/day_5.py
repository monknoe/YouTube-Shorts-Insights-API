from fastapi import FastAPI
from pydantic import BaseModel
import os
import signal

app = FastAPI()

@app.get("/")
def read_root():
    return {"day": 5, "message": "Welcome to Day 5!"}

def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return fastapi.Response(status_code=200, content='Server shutting down...')

@app.on_event('shutdown')
def on_shutdown():
    print('Server shutting down...')

class Item(BaseModel):
    name: str
    price: float
    description: str = None

# °²¸ê®Æ®w
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
@app.get("/items")
def get_items():
    return items

@app.get("/items/{item_id}")
def get_item(item_id: int):
    if item_id < 0 or item_id >= len(items):
        return {"error": "Item not found"}
    return items[item_id]

@app.put("/items/{item_id}")
def update_item(item_id: int, item: Item):
    if item_id<0 or item_id>=len(items):
        return {"error": "Item not found"}
    items[item_id] = item
    return{
        "message":"Item updated!",
        "item": item
    }

@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    if item_id < 0 or item_id >= len(items):
        return {"error": "Item not found"}
    
    deleted = items.pop(item_id)
    return {"message": "Item deleted", "item": deleted}

@app.get("/filter")
def filter(max_price: float):
    filtered_items = [item for item in items if item.price <= max_price]
    return filtered_items

@app.get("/search")
def search(keyword: str):
    keyword_lower = keyword.lower()
    result = [
        item for item in items
        if keyword_lower in item.name.lower() or keyword_lower in item.description.lower()
    ]
    return result

@app.get("/items/search")
def advanced_search(
    keyword: Optional[str] = None,
    min_price: Optional[float] = Query(None, ge=0),
    max_price: Optional[float] = Query(None, ge=0)
):
    results = items
    if keyword:
        keyword_lower = keyword.lower()
        results = [
            item for item in results
            if keyword_lower in item.name.lower() or keyword_lower in (item.description or "").lower()
        ]
    if min_price is not None:
        results = [item for item in results if item.price >= min_price]
    if max_price is not None:
        results = [item for item in results if item.price <= max_price]

    return results
