# Chat Application API Documentation

## Base URL
```
http://your-api-domain/api
```

## Authentication

### Register
```typescript
POST /auth/register
Body: {
  username: string;
  password: string;
}
Response: {
  id: string;
  username: string;
  is_active: boolean;
}
```

### Login
```typescript
POST /auth/token
Body: {
  username: string;
  password: string;
}
Response: {
  access_token: string;
  token_type: "bearer";
}
```

### Logout
```typescript
POST /auth/logout
Headers: {
  Authorization: "Bearer ${token}"
}
Response: {
  message: "Successfully logged out"
}
```

## Channels

### Create Channel
```typescript
POST /channels
Headers: {
  Authorization: "Bearer ${token}"
}
Body: {
  name: string;
  description: string;
  type: "public" | "private";
}
Response: {
  id: string;
  name: string;
  description: string;
  created_by: string;
  type: string;
  created_at: string;
}
```

### Get All Channels
```typescript
GET /channels
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Channel[]
```

### Get User's Channels
```typescript
GET /channels/me
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Channel[]
```

### Join Channel
```typescript
POST /channels/{channel_id}/join
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Channel
```

### Leave Channel
```typescript
POST /channels/{channel_id}/leave
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Channel
```

### Ban User by ID
```typescript
POST /channels/{channel_id}/ban/{user_id}
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Channel
Description: Ban a user from a channel by their user ID. Only channel owners can ban users.
Error responses:
  - 404: User or channel not found
  - 400: Cannot ban yourself or channel owner
  - 403: Not channel owner
```

### Unban User by ID
```typescript
POST /channels/{channel_id}/unban/{user_id}
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Channel
Description: Unban a user from a channel by their user ID. Only channel owners can unban users.
Error responses:
  - 404: User or channel not found
  - 403: Not channel owner
```

### Ban User by Username
```typescript
POST /channels/{channel_id}/ban-by-username/{username}
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Channel
Description: Ban a user from a channel by their username. Only channel owners can ban users. Banned users cannot join or view the channel.
Error responses:
  - 404: User or channel not found
  - 400: Cannot ban yourself or channel owner
  - 403: Not channel owner
```

### Unban User by Username
```typescript
POST /channels/{channel_id}/unban-by-username/{username}
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Channel
Description: Unban a user from a channel by their username. Only channel owners can unban users. Unbanned users can rejoin the channel.
Error responses:
  - 404: User or channel not found
  - 403: Not channel owner
```

### Get Banned Users
```typescript
GET /channels/{channel_id}/banned-users
Headers: {
  Authorization: "Bearer ${token}"
}
Response: {
  id: string;
  username: string;
}[]
Description: Get a list of all banned users in a channel. Only channel owners can view the banned users list.
Error responses:
  - 403: Not channel owner
  - 404: Channel not found
```

## Messages

### REST Endpoints

#### Get Channel Messages
```typescript
GET /messages/channel/{channel_id}
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Message[]
Description: Get all messages in a channel
```

#### Add Message (REST)
```typescript
POST /messages
Headers: {
  Authorization: "Bearer ${token}"
}
Body: {
  content: string;
  channel_id: string;
}
Response: Message
Description: Add a new message to a channel
```

#### Delete Message
```typescript
DELETE /messages/{message_id}
Headers: {
  Authorization: "Bearer ${token}"
}
Response: {
  message: "Message deleted successfully"
}
Description: Delete a message (only the message author can delete)
```

### WebSocket Integration

#### Connection
```typescript
// Connect to WebSocket with authentication
const connectWebSocket = (token: string, username: string) => {
  const ws = new WebSocket(`ws://your-api-domain/api/ws/${username}?token=${token}`);
  return ws;
};
```

#### Message Format
```typescript
// Message structure for sending via WebSocket
interface OutgoingMessage {
  content: string;
  channel_id: string;
}

// Message structure received (both REST and WebSocket)
interface Message {
  id: string;
  content: string;
  channel_id: string;
  username: string;
  user_id: string;
  created_at: string;
}
```

## Reactions

### Add Reaction
```typescript
POST /reactions
Headers: {
  Authorization: "Bearer ${token}"
}
Body: {
  message_id: string;
  emoji: string;  // Unicode emoji (e.g., "👍", "❤️", "😊")
}
Response: {
  id: string;
  message_id: string;
  user_id: string;
  emoji: string;
  created_at: string;
}
```

### Remove Reaction
```typescript
DELETE /reactions/{reaction_id}
Headers: {
  Authorization: "Bearer ${token}"
}
Response: {
  message: "Reaction removed successfully"
}
```

### Get Message Reactions
```typescript
GET /reactions/message/{message_id}
Headers: {
  Authorization: "Bearer ${token}"
}
Response: {
  id: string;
  message_id: string;
  user_id: string;
  emoji: string;
  created_at: string;
}[]
```

## Files

### Upload File
```typescript
POST /files/upload
Headers: {
  Authorization: "Bearer ${token}"
}
Body: FormData {
  file: File;
  channel_id: string;
}
Response: {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  channel_id: string;
  uploaded_by: string;
  created_at: string;
}
```

### Download File
```typescript
GET /files/{file_id}
Headers: {
  Authorization: "Bearer ${token}"
}
Response: File (binary)
```

### Get Channel Files
```typescript
GET /files/channel/{channel_id}
Headers: {
  Authorization: "Bearer ${token}"
}
Response: {
  id: string;
  filename: string;
  content_type: string;
  size: number;
  channel_id: string;
  uploaded_by: string;
  created_at: string;
}[]
```

### Delete File
```typescript
DELETE /files/{file_id}
Headers: {
  Authorization: "Bearer ${token}"
}
Response: {
  message: "File deleted successfully"
}
Description: Only the file uploader or channel owner can delete files
``` 