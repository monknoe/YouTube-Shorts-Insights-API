from googleapiclient.discovery import build
from dotenv import load_dotenv
import os
from sqlmodel import Session, select
from datetime import datetime

from app.models.shorts import Shorts
load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build("youtube", "v3", developerKey=API_KEY)

def search_shorts(keyword: str, max_results: int = 10):
    """
    以關鍵字搜尋 YouTube Shorts
    """
    request = youtube.search().list(
        q=keyword,
        part="snippet",
        type="video",
        videoDuration="short",   # short = < 60 seconds
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

def save_shorts(session: Session, videos: list, keyword: str):
    saved = []

    for v in videos:
        # 檢查是否已存在（避免重複）
        statement = select(Shorts).where(Shorts.video_id == v["video_id"])
        exists = session.exec(statement).first()

        if exists:
            continue
        
        item = Shorts(
            video_id=v["video_id"],
            title=v["title"],
            channel=v["channel"],
            published_at=v["published_at"],
            thumbnail=v["thumbnail"],
            keyword=keyword
        )

        session.add(item)
        saved.append(item)

    session.commit()
    return saved