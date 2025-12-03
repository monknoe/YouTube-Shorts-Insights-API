from sqlmodel import SQLModel, Field, Session, select
from typing import Optional
from sqlmodel import Session, create_engine
from fastapi import FastAPI, HTTPException
import os
import signal

class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    price: float
    description: Optional[str] = None

class RequestBody(SQLModel):
    keyword: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None

DATABASE_URL = "sqlite:///./database.db"
engine = create_engine(DATABASE_URL, echo=True)

# 建立資料表
SQLModel.metadata.create_all(engine)

def create_item_db(item: Item):
    with Session(engine) as session:
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

def get_all_items():
    with Session(engine) as session:
        items = session.exec(select(Item)).all()
        return items

def get_item_by_id(item_id: int):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        return item

def update_item_db(item_id: int, new_data: dict):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if item:
            for key, value in new_data.items():
                setattr(item, key, value)
            session.add(item)
            session.commit()
            session.refresh(item)
        return item

def delete_item_db(item_id: int):
    with Session(engine) as session:
        item = session.get(Item, item_id)
        if item:
            session.delete(item)
            session.commit()
        return item

app = FastAPI()

@app.get("/")
def read_root():
    return {"day": 8, "message": "Welcome to Day 8!"}

def shutdown():
    os.kill(os.getpid(), signal.SIGTERM)
    return fastapi.Response(status_code=200, content='Server shutting down...')

@app.on_event('shutdown')
def on_shutdown():
    print('Server shutting down...')

@app.post("/items")
def create_item(item: Item):
    return create_item_db(item)

@app.get("/items")
def read_items():
    return get_all_items()

@app.get("/items/{item_id}")
def read_item(item_id: int):
    item = get_item_by_id(item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item

@app.get("/filter")
def filter(max_price: Optional[float] = None, min_price: Optional[float] = None):
    filtered_items = get_all_items()
    if max_price is not None:
        filtered_items = [item for item in filtered_items if item.price <= max_price]
    if min_price is not None:
        filtered_items = [item for item in filtered_items if item.price >= min_price]

    return filtered_items

@app.post("/items/search_body")
def search_items(body: RequestBody):
    results = get_all_items()

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