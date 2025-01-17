# Data Models Documentation

## Authentication Models

### Token
```python
class Token(BaseModel):
    access_token: str
    token_type: str
```

### TokenData
```python
class TokenData(BaseModel):
    username: str | None = None
```

### LoginRequest
```python
class LoginRequest(BaseModel):
    username: str
    password: str
```

### RegisterRequest
```python
class RegisterRequest(BaseModel):
    username: str
    email: str
    password: str
    display_name: str | None = None
```

## User Models

### User
```python
class User(BaseModel):
    id: str
    username: str
    email: str
    display_name: str | None
    is_online: bool
    created_at: datetime
```

### UserCreate
```python
class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    display_name: str | None = None
```

## Channel Models

### Channel
```python
class Channel(BaseModel):
    id: str
    name: str
    description: str | None
    owner_id: str
    created_at: datetime
```

### ChannelCreate
```python
class ChannelCreate(BaseModel):
    name: str
    description: str | None = None
```

## Message Models

### Message
```python
class Message(BaseModel):
    id: str
    content: str
    user_id: str
    channel_id: str
    created_at: datetime
```

### MessageCreate
```python
class MessageCreate(BaseModel):
    content: str
    channel_id: str
```

## Reaction Models

### Reaction
```python
class Reaction(BaseModel):
    id: str
    emoji: str
    user_id: str
    message_id: str
    created_at: datetime
```

### ReactionCreate
```python
class ReactionCreate(BaseModel):
    emoji: str
    message_id: str
``` 