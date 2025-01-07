from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class ChannelCreate(BaseModel):
    name: str
    description: Optional[str] = None

class Channel(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    created_by: str
    created_at: datetime
    members: List[str] = []