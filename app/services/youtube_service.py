from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from sqlmodel import Session, select, desc
from datetime import datetime, timedelta,timezone
from sqlalchemy import func


from app.models.shorts import Shorts
from app.schemas.shorts import ShortsStats
from app.core.database import get_session
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build("youtube", "v3", developerKey=API_KEY)

def search_shorts(keyword: str, max_results: int = 10):#just for search function not sync with db
    """
    以關鍵字搜尋 YouTube Shorts
    """
    request = youtube.search().list(
        q=keyword,
        part="snippet",
        type="video",
        videoDuration="any",   # short = < 60 seconds
        maxResults=max_results,
    )

    response = request.execute()

    videos = []
    for item in response.get("items", []):
        videos.append({
            "video_id": item["id"]["videoId"],
            "title": item["snippet"]["title"],
            "channel": item["snippet"]["channelTitle"],
            "published_at": datetime.fromisoformat(item["snippet"]["publishedAt"].replace("Z", "+00:00")),
            "thumbnail": item["snippet"]["thumbnails"]["high"]["url"]
        })

    return videos

def list_shorts_from_db(
    session: Session,
    keyword: str | None = None,
    channel: str | None = None,
    sort_by: str = "published_at",
    order: str = "desc",
):
    statement = select(Shorts)

    # keyword
    if keyword:
        statement = statement.where(Shorts.keyword == keyword)

    # channel
    if channel:
        statement = statement.where(Shorts.channel == channel)

    # sort
    order_by = desc(getattr(Shorts, sort_by)) if order == "desc" else getattr(Shorts, sort_by)
    statement = statement.order_by(order_by)

    results = session.exec(statement).all()
    return results

def get_shorts_by_keyword(session: Session, keyword: str):
    statement = (
        select(Shorts)
        .where(Shorts.keyword == keyword)
        .order_by(Shorts.published_at.desc())  # 最新的在最上面
    )

    return session.exec(statement).all()

def get_shorts_stats(session: Session, keyword: str) -> ShortsStats:
    statement = select(Shorts).where(Shorts.keyword == keyword)
    items = session.exec(statement).all()

    if not items:
        return ShortsStats(
            keyword=keyword,
            total_videos=0,
            unique_channels=0,
            latest_upload=None
        )

    total = len(items)
    channels = len({item.channel for item in items})
    latest = max(item.published_at for item in items)

    return ShortsStats(
        keyword=keyword,
        total_videos=total,
        unique_channels=channels,
        latest_upload=latest
    )

def get_channel_stats(session: Session):
    """
    每個頻道有幾支 Shorts
    """
    statement = (
        select(
            Shorts.channel,
            func.count(Shorts.id).label("shorts_count")
        )
        .group_by(Shorts.channel)
    )

    result = session.exec(statement).all()
    return result

def get_shorts_timeline(
    session: Session,
    keyword: str | None = None,
    interval: str = "day",
):
    if interval == "day":
        time_col = func.date(Shorts.published_at)
    elif interval == "week":
        time_col = func.strftime("%Y-%W", Shorts.published_at)
    else:
        raise ValueError("interval must be 'day' or 'week'")

    statement = (
        select(
            time_col.label("date"),
            func.count(Shorts.id).label("count")
        )
    )

    if keyword:
        statement = statement.where(Shorts.keyword == keyword)

    statement = (
        statement
        .group_by("date")
        .order_by("date")
    )

    rows = session.exec(statement).all()

    return [
        {
            "date": row[0],
            "count": row[1]
        }
        for row in rows
    ]

def get_top_channels(
    session: Session,
    limit: int = 10,
    days: int | None = None,
):
    statement = select(
        Shorts.channel,
        func.count(Shorts.id).label("count")
    )

    if days is not None:
        since = datetime.now(timezone.utc) - timedelta(days=days)
        statement = statement.where(Shorts.published_at >= since)

    statement = (
        statement
        .group_by(Shorts.channel)
        .order_by(func.count(Shorts.id).desc())
        .limit(limit)
    )

    rows = session.exec(statement).all()

    return [
        {"channel": channel, "count": count}
        for channel, count in rows
    ]

def get_top_keywords(
    session: Session,
    limit: int = 10,
    days: int | None = None,
):
    statement = select(
        Shorts.keyword,
        func.count(Shorts.id).label("count")
    )

    if days is not None:
        max_time = session.exec(
            select(func.max(Shorts.published_at))
        ).one()

        if max_time:
            since = max_time - timedelta(days=days)
            statement = statement.where(Shorts.published_at >= since)

    statement = (
        statement
        .group_by(Shorts.keyword)
        .order_by(func.count(Shorts.id).desc())
        .limit(limit)
    )

    rows = session.exec(statement).all()

    return [
        {"keyword": keyword, "count": count}
        for keyword, count in rows
    ]


def get_shorts_growth(
    session: Session,
    days: int = 7,
    keyword: str | None = None,
):
    # 1) 以 DB 最新時間為基準
    max_time = session.exec(
        select(func.max(Shorts.published_at))
    ).one()

    if not max_time:
        return {
            "current_count": 0,
            "previous_count": 0,
            "growth_rate": 0.0
        }

    current_start = max_time - timedelta(days=days)
    previous_start = max_time - timedelta(days=days * 2)

    # 2) 本期
    current_stmt = select(func.count(Shorts.id)).where(
        Shorts.published_at >= current_start
    )
    # 3) 前一期
    previous_stmt = select(func.count(Shorts.id)).where(
        Shorts.published_at >= previous_start,
        Shorts.published_at < current_start
    )

    if keyword:
        current_stmt = current_stmt.where(Shorts.keyword == keyword)
        previous_stmt = previous_stmt.where(Shorts.keyword == keyword)

    current_count = session.exec(current_stmt).one()
    previous_count = session.exec(previous_stmt).one()

    # 4) 成長率計算（防呆）
    if previous_count == 0:
        growth_rate = 100.0 if current_count > 0 else 0.0
    else:
        growth_rate = ((current_count - previous_count) / previous_count) * 100

    return {
        "current_count": current_count,
        "previous_count": previous_count,
        "growth_rate": round(growth_rate, 2),
    }