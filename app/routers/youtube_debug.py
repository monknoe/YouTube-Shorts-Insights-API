from fastapi import APIRouter, Query, Depends
from sqlmodel import Session, select

from app.core.database import get_session
from app.core.security import get_current_user
from app.schemas import shorts
from app.services import youtube_service
from app.services import sync_service
from app.services import cache_service

router = APIRouter(prefix="/_debug/youtube", tags=["YouTube_debug"])

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
    saved = sync_service.save_shorts(session, videos, keyword)
    return {"saved_count": len(saved), "keyword": keyword}


@router.get("/shorts", response_model=list[shorts.ShortsRead])
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

@router.get("/shorts/stats/channel", response_model=list[shorts.ChannelStats])
def channel_stats(
    session: Session = Depends(get_session)
):
    return youtube_service.get_channel_stats(session)

@router.get("/shorts/stats/{keyword}", response_model=shorts.ShortsStats)
def shorts_stats(
    keyword: str,
    session: Session = Depends(get_session),
):
    return youtube_service.get_shorts_stats(session, keyword)

@router.get("/timeline", response_model=list[shorts.ShortsTimeline])
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

@router.get("/top-channels", response_model=list[shorts.TopChannel])
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

@router.get("/top-keywords", response_model=list[shorts.TopKeyword])
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

@router.get("/growth", response_model=shorts.ShortsGrowth)
def shorts_growth(
    days: int = Query(7, ge=1, le=90),
    keyword: str | None = Query(None),
    session: Session = Depends(get_session),
):
    cache_key = f"growth:{keyword}:{days}"

    cached = cache_service.get_cache(session, cache_key)
    if cached:
        return cached

    result = youtube_service.get_shorts_growth(session, days, keyword)

    cache_service.set_cache(session, cache_key, result)
    return result

    # return youtube_service.get_shorts_growth(
    #     session=session,
    #     days=days,
    #     keyword=keyword,
    # )

@router.post("/auto/{keyword}")
def sync_shorts(keyword: str, session: Session = Depends(get_session)):
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
