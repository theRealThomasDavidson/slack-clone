# Chat API Documentation

A real-time chat application API built with FastAPI, WebSockets, and PostgreSQL.

## Overview

This API provides endpoints for:
- User authentication and management
- Real-time chat functionality
- Channel management
- File uploads
- Message reactions
- WebSocket connections for real-time updates

## Project Structure

```
api/
├── api/
│   ├── core/          # Core functionality (config, database)
│   ├── models/        # Pydantic models and schemas
│   ├── routes/        # API endpoints
│   ├── services/      # Business logic
│   ├── repositories/  # Database operations
│   └── utils/         # Utility functions
├── alembic/           # Database migrations
├── tests/             # Test suite
└── main.py           # Application entry point
```

## Detailed Documentation

- [Routes Documentation](api/routes/README.md)
- [Models Documentation](api/models/README.md)
- [Services Documentation](api/services/README.md)

## Example API Usage

### Authentication Flow

1. Register a new user:
```bash
curl -X POST "http://localhost:8000/api/auth/register" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "johndoe",
       "email": "john@example.com",
       "password": "secretpass",
       "display_name": "John Doe"
     }'
```
Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

2. Login:
```bash
curl -X POST "http://localhost:8000/api/auth/login" \
     -H "Content-Type: application/json" \
     -d '{
       "username": "johndoe",
       "password": "secretpass"
     }'
```
Response:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Channel Operations

1. Create a channel:
```bash
curl -X POST "http://localhost:8000/api/channels" \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "general",
       "description": "General discussion"
     }'
```
Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "general",
  "description": "General discussion",
  "owner_id": "user_id",
  "created_at": "2025-01-09T12:00:00Z"
}
```

### Chat Operations

1. Send a message:
```bash
curl -X POST "http://localhost:8000/api/chat/messages" \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{
       "content": "Hello, world!",
       "channel_id": "123e4567-e89b-12d3-a456-426614174000"
     }'
```
Response:
```json
{
  "id": "789e4567-e89b-12d3-a456-426614174000",
  "content": "Hello, world!",
  "user_id": "user_id",
  "channel_id": "123e4567-e89b-12d3-a456-426614174000",
  "created_at": "2025-01-09T12:01:00Z"
}
```

### WebSocket Connection

Connect to WebSocket for real-time updates:
```javascript
const ws = new WebSocket('ws://localhost:8000/api/ws/johndoe?token={token}');

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  console.log('Received:', message);
};
```

Example message received:
```json
{
  "type": "message",
  "data": {
    "id": "789e4567-e89b-12d3-a456-426614174000",
    "content": "Hello, world!",
    "user": {
      "username": "johndoe",
      "display_name": "John Doe"
    },
    "channel_id": "123e4567-e89b-12d3-a456-426614174000",
    "created_at": "2025-01-09T12:01:00Z"
  }
}
```

### Channel Management

1. Ban a user from a channel:
```bash
curl -X POST "http://localhost:8000/api/channels/{channel_id}/ban-by-username/{username}" \
     -H "Authorization: Bearer {token}"
```
Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "general",
  "description": "General discussion",
  "owner_id": "user_id",
  "created_at": "2025-01-09T12:00:00Z",
  "member_exceptions": [
    {
      "user_id": "banned_user_id",
      "created_at": "2025-01-09T12:01:00Z"
    }
  ]
}
```

2. Get banned users list:
```bash
curl -X GET "http://localhost:8000/api/channels/{channel_id}/banned-users" \
     -H "Authorization: Bearer {token}"
```
Response:
```json
[
  {
    "id": "banned_user_id",
    "username": "banneduser",
    "display_name": "Banned User"
  }
]
```

3. Unban a user:
```bash
curl -X POST "http://localhost:8000/api/channels/{channel_id}/unban-by-username/{username}" \
     -H "Authorization: Bearer {token}"
```
Response:
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "name": "general",
  "description": "General discussion",
  "owner_id": "user_id",
  "created_at": "2025-01-09T12:00:00Z",
  "member_exceptions": []
}
```

## Environment Variables

Create a `.env` file with the following variables:
```env
DATABASE_URL=postgresql://postgres:postgres@db:5432/chat_db
SECRET_KEY=your_secret_key_here
APP_NAME=Chat API
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Running the Application

1. Start the services:
```bash
docker-compose up --build
```

2. Run database migrations:
```bash
docker-compose exec api alembic upgrade head
```

3. Access the API documentation:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Testing

Run the test suite:
```bash
docker-compose exec api pytest
``` 