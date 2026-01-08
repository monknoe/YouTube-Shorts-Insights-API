from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.models.sync_log import SyncLog
from app.models.shorts import Shorts

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

def should_sync(session: Session, keyword: str) -> bool:
    stmt = (
        select(SyncLog)
        .where(SyncLog.keyword == keyword)
        .order_by(SyncLog.synced_at.desc())
    )

    last = session.exec(stmt).first()

    if not last:
        return True

    return datetime.utcnow() - last.synced_at > timedelta(hours=24)


def record_sync(session: Session, keyword: str):
    log = SyncLog(
        keyword=keyword,
        synced_at=datetime.utcnow()
    )
    session.add(log)
    session.commit()
