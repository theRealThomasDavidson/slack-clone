# API Routes Documentation

## Authentication Routes (`/api/auth`)

### Register User
- **Endpoint**: `POST /api/auth/register`
- **Description**: Register a new user
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**: User object
  ```json
  {
    "id": "string",
    "username": "string",
    "is_active": true
  }
  ```

### Login
- **Endpoint**: `POST /api/auth/token`
- **Description**: Login a user
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Response**: JWT Token
  ```json
  {
    "access_token": "string",
    "token_type": "bearer"
  }
  ```

### Logout
- **Endpoint**: `POST /api/auth/logout`
- **Description**: Logout a user
- **Authentication**: Required (Bearer Token)
- **Response**:
  ```json
  {
    "message": "Successfully logged out"
  }
  ```

### Get Current User
- **Endpoint**: `GET /api/auth/me`
- **Description**: Get current user's profile
- **Authentication**: Required (Bearer Token)
- **Response**: User object
  ```json
  {
    "id": "string",
    "username": "string",
    "is_active": true
  }
  ```

## Channel Routes (`/api/channels`)

### Create Channel
- **Endpoint**: `POST /api/channels`
- **Description**: Create a new channel
- **Authentication**: Required (Bearer Token)
- **Request Body**:
  ```json
  {
    "name": "string (1-50 chars)",
    "description": "string",
    "type": "public" | "private"
  }
  ```
- **Response**: Channel object
  ```json
  {
    "id": "string",
    "name": "string",
    "description": "string",
    "created_by": "string",
    "type": "string",
    "created_at": "string"
  }
  ```

### List Channels
- **Endpoint**: `GET /api/channels`
- **Description**: List all public channels
- **Authentication**: Required (Bearer Token)
- **Response**: Array of Channel objects

### Get My Channels
- **Endpoint**: `GET /api/channels/me`
- **Description**: Get channels where the current user is a member
- **Authentication**: Required (Bearer Token)
- **Response**: Array of Channel objects

### Get Channel
- **Endpoint**: `GET /api/channels/{channel_id}`
- **Description**: Get channel details by ID
- **Authentication**: Required (Bearer Token)
- **Response**: Channel object

### Join Channel
- **Endpoint**: `POST /api/channels/{channel_id}/join`
- **Description**: Join a specific channel
- **Authentication**: Required (Bearer Token)
- **Response**: Updated Channel object

### Leave Channel
- **Endpoint**: `POST /api/channels/{channel_id}/leave`
- **Description**: Leave a specific channel
- **Authentication**: Required (Bearer Token)
- **Response**: Updated Channel object

### Ban User by ID
- **Endpoint**: `POST /api/channels/{channel_id}/ban/{user_id}`
- **Description**: Ban a user from a channel by their user ID
- **Authentication**: Required (Bearer Token)
- **Response**: Updated Channel object

### Unban User by ID
- **Endpoint**: `POST /api/channels/{channel_id}/unban/{user_id}`
- **Description**: Unban a user from a channel by their user ID
- **Authentication**: Required (Bearer Token)
- **Response**: Updated Channel object

### Ban User by Username
- **Endpoint**: `POST /api/channels/{channel_id}/ban-by-username/{username}`
- **Description**: Ban a user from a channel by their username
- **Authentication**: Required (Bearer Token)
- **Response**: Updated Channel object

### Unban User by Username
- **Endpoint**: `POST /api/channels/{channel_id}/unban-by-username/{username}`
- **Description**: Unban a user from a channel by their username
- **Authentication**: Required (Bearer Token)
- **Response**: Updated Channel object

### Get Banned Users
- **Endpoint**: `GET /api/channels/{channel_id}/banned-users`
- **Description**: Get list of banned users in a channel
- **Authentication**: Required (Bearer Token)
- **Response**: Array of User objects

## Messages

### Get Channel Messages
- **Endpoint**: `GET /api/messages/channel/{channel_id}`
- **Description**: Get all messages in a channel
- **Authentication**: Required (Bearer Token)
- **Response**: Array of Message objects

### Add Message
- **Endpoint**: `POST /api/messages`
- **Description**: Add a new message to a channel
- **Authentication**: Required (Bearer Token)
- **Request Body**:
  ```json
  {
    "content": "string",
    "channel_id": "string"
  }
  ```
- **Response**: Message object

### Delete Message
- **Endpoint**: `DELETE /api/messages/{message_id}`
- **Description**: Delete a message
- **Authentication**: Required (Bearer Token)
- **Response**:
  ```json
  {
    "message": "Message deleted successfully"
  }
  ```

## WebSocket Integration

### Connection
- **Endpoint**: `WS /api/ws/{username}?token={token}`
- **Description**: WebSocket connection for real-time chat
- **Authentication**: Required (Token in query parameter)

### Message Format
```typescript
// Outgoing message
{
  "content": "string",
  "channel_id": "string"
}

// Incoming message
{
  "id": "string",
  "content": "string",
  "channel_id": "string",
  "username": "string",
  "user_id": "string",
  "created_at": "string"
}
``` 