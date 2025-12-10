from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime

class Shorts(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    video_id: str = Field(index=True)
    title: str
    channel: str
    published_at: datetime
    thumbnail: str
    keyword: str  # 搜尋關鍵字（之後做趨勢分析會用到）
