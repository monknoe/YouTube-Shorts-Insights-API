from fastapi import APIRouter, Query, Depends
from sqlmodel import Session

from app.services.youtube_service import search_shorts,save_shorts
from app.core.database import get_session
from app.core.security import get_current_user


router = APIRouter(prefix="/youtube", tags=["YouTube"])

@router.get("/search")
def search_youtube_shorts(keyword: str = Query(..., description="Search keyword")):
    return search_shorts(keyword)

@router.post("/sync/{keyword}")
def sync_shorts(
    keyword: str,
    session: Session = Depends(get_session),
    user = Depends(get_current_user)
):
    videos = search_shorts(keyword)
    saved = save_shorts(session, videos, keyword)
    return {"saved_count": len(saved), "keyword": keyword}