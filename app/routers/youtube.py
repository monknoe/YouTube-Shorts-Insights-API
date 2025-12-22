from fastapi import APIRouter, Query, Depends
from sqlmodel import Session, select

from app.services.youtube_service import search_shorts,save_shorts
from app.core.database import get_session
from app.core.security import get_current_user
from app.schemas.shorts import ShortsRead, ShortsStats,ChannelStats,ShortsTimeline,TopChannel,TopKeyword
from app.services import youtube_service

router = APIRouter(prefix="/youtube", tags=["YouTube"])

@router.get("/shorts/search")
def search_youtube_shorts(keyword: str = Query(..., description="Search keyword")):
    return youtube_service.search_shorts(keyword)

@router.post("/sync/{keyword}")
def sync_shorts(
    keyword: str,
    session: Session = Depends(get_session),
    user = Depends(get_current_user)
):
    videos = youtube_service.search_shorts(keyword)
    saved = youtube_service.save_shorts(session, videos, keyword)
    return {"saved_count": len(saved), "keyword": keyword}


@router.get("/shorts", response_model=list[ShortsRead])
def list_shorts(
    keyword: str | None = None,
    channel: str | None = None,
    sort_by: str = "published_at",
    order: str = "desc",
    session: Session = Depends(get_session)
):
    return youtube_service.list_shorts_from_db(
        session=session,
        keyword=keyword,
        channel=channel,
        sort_by=sort_by,
        order=order,
    )

@router.get("/shorts/search/{keyword}")
def list_shorts(keyword: str, session: Session = Depends(get_session)):
    return youtube_service.get_shorts_by_keyword(session, keyword)

@router.get("/shorts/stats/channel", response_model=list[ChannelStats])
def channel_stats(
    session: Session = Depends(get_session)
):
    return youtube_service.get_channel_stats(session)

@router.get("/shorts/stats/{keyword}", response_model=ShortsStats)
def shorts_stats(
    keyword: str,
    session: Session = Depends(get_session),
):
    return youtube_service.get_shorts_stats(session, keyword)

@router.get("/timeline", response_model=list[ShortsTimeline])
def shorts_timeline(
    keyword: str | None = Query(None),
    interval: str = Query("day", regex="^(day|week)$"),
    session: Session = Depends(get_session),
):
    return youtube_service.get_shorts_timeline(
        session=session,
        keyword=keyword,
        interval=interval
    )

@router.get("/top-channels", response_model=list[TopChannel])
def top_channels(
    limit: int = Query(10, ge=1, le=100),
    days: int | None = Query(None, ge=1),
    session: Session = Depends(get_session),
):
    return youtube_service.get_top_channels(
        session=session,
        limit=limit,
        days=days,
    )

@router.get("/top-keywords", response_model=list[TopKeyword])
def top_keywords(
    limit: int = Query(10, ge=1, le=100),
    days: int | None = Query(None, ge=1),
    session: Session = Depends(get_session),
):
    return youtube_service.get_top_keywords(
        session=session,
        limit=limit,
        days=days,
    )