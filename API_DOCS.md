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
  email: string;
  password: string;
  display_name: string;
}
Response: {
  id: string;
  username: string;
  email: string;
  display_name: string;
  is_online: boolean;
  created_at: string;
}
```

### Login
```typescript
POST /auth/login
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
POST /channels/
Headers: {
  Authorization: "Bearer ${token}"
}
Body: {
  name: string;
  description: string;
}
Response: {
  id: string;
  name: string;
  description: string;
  owner_id: string;
  members: string[];
  created_at: string;
}
```

### Get All Channels
```typescript
GET /channels/
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
POST /channels/{channel_name}/join
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Channel
```

### Leave Channel
```typescript
POST /channels/{channel_name}/leave
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Channel
```

## Messages

### Get Recent Messages
```typescript
GET /messages
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Message[]
```

### Get Channel Messages
```typescript
GET /messages/{channel_id}
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Message[]
```

### Get User Messages
```typescript
GET /messages/me
Headers: {
  Authorization: "Bearer ${token}"
}
Response: Message[]
```

## WebSocket Integration

### Connection
```typescript
// Connect to WebSocket with authentication
const connectWebSocket = (token: string, username: string) => {
  const ws = new WebSocket(`ws://your-api-domain/api/ws/${username}?token=${token}`);
  return ws;
};
```

### Message Format
```typescript
// Message structure for sending
interface OutgoingMessage {
  content: string;
  channel_id: string;
}

// Message structure received
interface IncomingMessage {
  id: string;
  content: string;
  channel_id: string;
  username: string;
  user_id: string;
  timestamp: string;
}
```

### Example React Integration
```typescript
import { useEffect, useRef } from 'react';

const ChatComponent = () => {
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    // Connect to WebSocket
    const token = "your-auth-token";
    const username = "current-username";
    wsRef.current = new WebSocket(`ws://your-api-domain/api/ws/${username}?token=${token}`);

    // Handle incoming messages
    wsRef.current.onmessage = (event) => {
      const message: IncomingMessage = JSON.parse(event.data);
      // Handle the message (e.g., update state, display in UI)
      console.log('Received message:', message);
    };

    // Handle connection open
    wsRef.current.onopen = () => {
      console.log('WebSocket connected');
    };

    // Handle errors
    wsRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Handle connection close
    wsRef.current.onclose = () => {
      console.log('WebSocket disconnected');
      // Implement reconnection logic if needed
    };

    // Cleanup on unmount
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  // Function to send a message
  const sendMessage = (content: string, channelId: string) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      const message: OutgoingMessage = {
        content,
        channel_id: channelId
      };
      wsRef.current.send(JSON.stringify(message));
    }
  };

  return (
    // Your chat UI components
  );
};

export default ChatComponent;
```

### WebSocket Events

1. **Connection**
   - WebSocket connects automatically when you provide the token
   - Receives message history for user's channels
   - Auto-subscribes to user's channels

2. **Sending Messages**
   - Send JSON message with content and channel_id
   - Receive immediate feedback through WebSocket
   - All channel members receive the message in real-time

3. **Receiving Messages**
   - Messages include full details (id, content, user, timestamp)
   - Messages are ordered by timestamp
   - Messages include channel context

4. **Error Handling**
   - Connection errors (4001: Invalid token)
   - Username mismatch (4003: Username doesn't match token)
   - Regular WebSocket errors (connection lost, etc.)

### Best Practices

1. **Connection Management**
   ```typescript
   // Implement reconnection with exponential backoff
   const connectWithRetry = (token: string, username: string, retries = 0) => {
     const ws = new WebSocket(`ws://your-api-domain/api/ws/${username}?token=${token}`);
     
     ws.onclose = () => {
       const timeout = Math.min(1000 * Math.pow(2, retries), 10000);
       setTimeout(() => connectWithRetry(token, username, retries + 1), timeout);
     };
     
     return ws;
   };
   ```

2. **Message Queue**
   ```typescript
   // Queue messages when connection is lost
   const messageQueue: OutgoingMessage[] = [];
   
   ws.onopen = () => {
     while (messageQueue.length > 0) {
       const message = messageQueue.shift();
       if (message) {
         ws.send(JSON.stringify(message));
       }
     }
   };
   
   const sendMessage = (content: string, channelId: string) => {
     const message: OutgoingMessage = { content, channel_id: channelId };
     if (ws.readyState === WebSocket.OPEN) {
       ws.send(JSON.stringify(message));
     } else {
       messageQueue.push(message);
     }
   };
   ```

3. **State Management**
   ```typescript
   // Example using React context for chat state
   interface ChatState {
     messages: Record<string, IncomingMessage[]>; // Keyed by channel_id
     channels: Channel[];
     connected: boolean;
   }
   
   const ChatContext = createContext<ChatState>({
     messages: {},
     channels: [],
     connected: false
   });
   ```

This API is fully compatible with React and follows standard WebSocket protocols. The WebSocket connection provides real-time updates, and the REST endpoints allow for data fetching and state management. The authentication flow uses JWT tokens which can be easily stored in localStorage or a secure cookie. 