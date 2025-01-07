from pydantic import BaseModel, Field, ConfigDict, field_validator
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

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda dt: dt.isoformat()}
    )

    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_timestamp(cls, value):
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                try:
                    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        return value

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        data = super().model_dump(**kwargs)
        if isinstance(self.timestamp, datetime):
            data['timestamp'] = self.timestamp.isoformat()
        return data