from fastapi import APIRouter, Depends
from sqlmodel import Session
from typing import List

from app.database import get_session
from app.schemas.item import ItemCreate, ItemRead, RequestBody
from app.models.item import Item
from app.crud.item import create_item, get_items, get_item_by_id, update_item_db, delete_item_db, search_items_db

router = APIRouter(prefix="/items", tags=["Items"])

@router.post("/", response_model=ItemRead)
def create_item_route(
    item: ItemCreate,
    session: Session = Depends(get_session)
):
    return create_item(session, item)

@router.get("/", response_model=List[ItemRead])
def list_items(
    session: Session = Depends(get_session)
):
    return get_items(session)

@router.get("/{item_id}")
def read_item(item_id: int, session: Session = Depends(get_session)):
    return get_item_by_id(session, item_id)

@router.put("/{item_id}")
def update_item(item_id: int, item_data: Item, session: Session = Depends(get_session)):
    return update_item_db(session, item_id, item_data.dict())

@router.delete("/{item_id}")
def delete_item(item_id: int, session: Session = Depends(get_session)):
    return delete_item_db(session, item_id)

@router.post("/search_body")
def search_items(body: RequestBody, session: Session = Depends(get_session)):
    return search_items_db(session, body) 