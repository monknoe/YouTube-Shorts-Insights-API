from sqlmodel import SQLModel, Field
from datetime import datetime
from typing import Optional

class AnalysisCache(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    cache_key: str
    data: str   # JSON string
    updated_at: datetime
