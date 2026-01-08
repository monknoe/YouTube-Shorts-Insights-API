from sqlmodel import Session, select
from datetime import datetime, timedelta
from app.models.analysis_cache import AnalysisCache
import json

CACHE_TTL = timedelta(minutes=30)

def get_cache(session: Session, key: str):
    stmt = select(AnalysisCache).where(AnalysisCache.cache_key == key)
    cache = session.exec(stmt).first()

    if not cache:
        return None

    if datetime.utcnow() - cache.updated_at > CACHE_TTL:
        return None

    return json.loads(cache.data)


def set_cache(session: Session, key: str, data):
    stmt = select(AnalysisCache).where(AnalysisCache.cache_key == key)
    cache = session.exec(stmt).first()

    if cache:
        cache.data = json.dumps(data)
        cache.updated_at = datetime.utcnow()
    else:
        cache = AnalysisCache(
            cache_key=key,
            data=json.dumps(data),
            updated_at=datetime.utcnow()
        )
        session.add(cache)

    session.commit()
