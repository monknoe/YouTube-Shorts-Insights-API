from fastapi import APIRouter, Query, Depends
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_user
from app.schemas import shorts
from app.services import youtube_service
from app.services import sync_service

router = APIRouter(prefix="/youtube", tags=["YouTube"])

@router.post("/sync/{keyword}")
def sync_shorts(
    keyword: str,
    session: Session = Depends(get_session),
    user = Depends(get_current_user)
):
    videos = youtube_service.search_shorts(keyword)
    saved = sync_service.save_shorts(session, videos, keyword)
    return {"saved_count": len(saved), "keyword": keyword}


@router.get("/growth", response_model=shorts.ShortsGrowth)
def shorts_growth(
    days: int = Query(7, ge=1, le=90),
    keyword: str | None = Query(None),
    session: Session = Depends(get_session),
):
    return youtube_service.get_shorts_growth(
        session=session,
        days=days,
        keyword=keyword,
    )

@router.post("/auto/{keyword}")
def sync_shorts(
    keyword: str, 
    session: Session = Depends(get_session),
    user= Depends(get_current_user)
    ):
    if not sync_service.should_sync(session, keyword):
        return {
            "message": "Already synced in last 24 hours"
        }

    videos = youtube_service.search_shorts(keyword)
    saved = sync_service.save_shorts(session, videos, keyword)
    sync_service.record_sync(session, keyword)

    return {
        "message": "Sync completed",
        "saved_count": len(saved)
    }
