# Chat Application Backend Specification

## Technology Stack
- FastAPI for API development
- WebSocket for real-time communication
- Pydantic for data validation
- JWT for authentication

## Real-Time Communication Implementation

### WebSocket Architecture
- Endpoint: `/api/ws/{username}`
- Authentication via JWT token in query parameter
- Persistent bi-directional connection
- Channel subscription management
- Message routing by channel
- Automatic reconnection handling
- Connection state management

### Message Flow
1. Client establishes WebSocket connection with JWT token
2. Server validates token and username
3. Server sends message history to new connection
4. Server subscribes user to their channels
5. Client sends message to specific channel
6. Server validates message and channel membership
7. Server broadcasts message only to channel subscribers
8. Server handles disconnections and cleanup

### Channel Subscription System
- Users automatically subscribe to channels they join
- Messages are only broadcast to channel subscribers
- Real-time subscription updates on channel join/leave
- Efficient message routing to relevant users only
- Support for multiple channel subscriptions per user

### WebSocket Features
- Real-time message delivery
- Channel-specific message routing
- Message history on connection
- User presence tracking
- Connection state management
- Error handling and recovery
- Subscription management

### Client Implementation (React)
```javascript
// Connection setup
const wsConnect = (token, username) => {
  const ws = new WebSocket(`ws://api-url/api/ws/${username}?token=${token}`);
  return ws;
};

// Message handling
ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  // Update UI with new message
};

// Send messages
const sendMessage = (content) => {
  if (ws.readyState === WebSocket.OPEN) {
    ws.send(content);
  }
};
```

### Performance Benefits
- Reduced server load compared to HTTP polling
- Lower latency for message delivery
- Efficient bandwidth usage
- Real-time user presence updates
- Automatic message ordering

### Error Handling
- Connection loss detection
- Automatic reconnection attempts
- Message queue during disconnection
- Error state recovery
- Rate limiting protection

## Core Components

### Authentication System
- JWT-based authentication
- Token expiration and refresh mechanism
- Session tracking for WebSocket connections

### Repository Layer
- In-memory storage (V0/V1)
- Generic base repository pattern
- Separate repositories for:
  - Users
  - Messages
  - Channels

### Service Layer
- AuthService: Handles authentication and session management
- MessageService: Manages message creation and retrieval
- UserService: Handles user operations
- ChannelService: Manages channel operations

### WebSocket Management
- ConnectionManager for handling WebSocket connections
- Real-time message broadcasting
- User presence tracking

## Data Models

### User
- UUID-based identification
- Username (unique)
- Email (unique)
- Hashed password
- Online status tracking
- Last seen timestamp

### Message
- UUID-based identification
- Content (max 1000 chars)
- User reference
- Channel reference (optional)
- Timestamp

### Channel
- UUID-based identification
- Name (unique)
- Description
- Owner reference
- Member list
- Creation timestamp

## API Routes

### Authentication Routes
- POST `/api/auth/register`: Create new user account
- POST `/api/auth/login`: Authenticate and receive JWT token
- POST `/api/auth/logout`: End current session

### User Routes
- GET `/api/users/me`: Get current user profile
- GET `/api/users/{username}`: Get specific user profile
- GET `/api/users/`: List all users
- GET `/api/users/online`: List online users
- PATCH `/api/users/me`: Update current user profile
- POST `/api/users/me/status`: Update online status

### Channel Routes
- POST `/api/channels/`: Create new channel
- GET `/api/channels/`: List all channels
- GET `/api/channels/me`: List user's channels
- GET `/api/channels/{channel_name}`: Get specific channel
- POST `/api/channels/{channel_name}/join`: Join a channel
- POST `/api/channels/{channel_name}/leave`: Leave a channel
- DELETE `/api/channels/{channel_name}`: Delete a channel (owner only)

### Message Routes
- GET `/api/messages`: Get recent messages
- GET `/api/messages/me`: Get user's messages

### WebSocket Endpoints
- WS `/api/ws/{username}`: Real-time chat connection

## Request/Response Patterns

### Authentication Flow
1. Client registers user (POST `/api/auth/register`)
2. Client logs in (POST `/api/auth/login`)
3. Client receives JWT token
4. Client includes token in subsequent requests
5. Client connects to WebSocket with token

### Channel Flow
1. User creates or joins channel
2. User sends messages to channel
3. Messages are broadcast to all channel members
4. User can leave channel
5. Owner can delete channel

### Message Flow
1. Client establishes WebSocket connection
2. Client sends message through WebSocket
3. Server validates message and user
4. Server broadcasts message to relevant users
5. Clients receive real-time updates

## Security Requirements
- Password hashing using bcrypt
- JWT token validation
- WebSocket connection authentication
- Rate limiting
- CORS configuration 