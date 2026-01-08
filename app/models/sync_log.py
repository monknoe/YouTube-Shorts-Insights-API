from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class SyncLog(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    keyword: str
    synced_at: datetime
