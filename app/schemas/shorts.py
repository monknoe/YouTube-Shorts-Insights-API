from sqlmodel import SQLModel
from datetime import datetime
from typing import Optional

class TopKeyword(SQLModel):
    keyword: str
    count: int
    
class TopChannel(SQLModel):
    channel: str
    count: int

class ShortsTimeline(SQLModel):
    date: str
    count: int

class ChannelStats(SQLModel):
    channel: str
    shorts_count: int

class ShortsStats(SQLModel):
    keyword: str
    total_videos: int
    unique_channels: int
    latest_upload: Optional[datetime]
    
class ShortsRead(SQLModel):
    id: int
    video_id: str
    title: str
    channel: str
    published_at: datetime
    thumbnail: str
    keyword: str

    class Config:
        from_attributes = True