from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, Dict, Any

class MessageCreate(BaseModel):
    content: str = Field(..., max_length=1000)
    channel_id: str
    username: Optional[str] = None
    user_id: Optional[str] = None

class Message(MessageCreate):
    id: str
    username: str  # Override optional
    user_id: str   # Override optional
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    model_config = ConfigDict(from_attributes=True)

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        data = super().model_dump(**kwargs)
        data['timestamp'] = self.timestamp.isoformat()
        return data