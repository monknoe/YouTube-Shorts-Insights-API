from sqlmodel import Session, select
from app.models.item import Item
from app.schemas.item import RequestBody
from typing import List

def create_item(session: Session, item_data):
    item = Item(**item_data.dict())
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

def get_items(session: Session) -> List[Item]:
    return session.exec(select(Item)).all()

def get_item_by_id(session: Session, item_id: int) -> Item:
    return session.get(Item, item_id)

def delete_item_db(session: Session, item_id: int):
    item = session.get(Item, item_id)
    if item:
        session.delete(item)
        session.commit()
    return item

def update_item_db(session: Session, item_id: int, new_data:dict):
    item = session.get(Item, item_id)
    if item:
        for key, value in new_data.items():
            setattr(item, key, value)
        session.add(item)
        session.commit()
        session.refresh(item)
    return item

def search_items_db(session: Session, body: RequestBody):
    results = get_items(session)
    if body.keyword:
        kw= body.keyword.lower()
        results=[item for item in results 
        if kw in item.name.lower() or kw in (item.description or "").lower()]
    
    if body.min_price is not None:
        results=[item for item in results if item.price >= body.min_price]
    if body.max_price is not None:
        results=[item for item in results if item.price <= body.max_price]
    return results