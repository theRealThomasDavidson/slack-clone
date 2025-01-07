from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, Set
import logging
import asyncio

logger = logging.getLogger(__name__)

class ConnectionManager:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            # Map username to their websocket connection
            self.active_connections: Dict[str, WebSocket] = {}
            # Map channel_id to set of subscribed usernames
            self.channel_subscriptions: Dict[str, Set[str]] = {}
            self._initialized = True

    async def connect(self, websocket: WebSocket, username: str):
        logger.debug(f"Accepting WebSocket connection for user {username}")
        await websocket.accept()
        self.active_connections[username] = websocket
        logger.debug(f"Connected users: {list(self.active_connections.keys())}")

    async def disconnect(self, websocket: WebSocket):
        logger.debug("Disconnecting WebSocket")
        # Find and remove the username associated with this websocket
        for username, ws in list(self.active_connections.items()):
            if ws == websocket:
                del self.active_connections[username]
                # Remove user from all channel subscriptions
                for subscribers in self.channel_subscriptions.values():
                    subscribers.discard(username)
                logger.debug(f"Disconnected user {username}")
                break

    async def subscribe_to_channel(self, username: str, channel_id: str):
        logger.debug(f"Subscribing user {username} to channel {channel_id}")
        if channel_id not in self.channel_subscriptions:
            self.channel_subscriptions[channel_id] = set()
        self.channel_subscriptions[channel_id].add(username)
        logger.debug(f"Channel {channel_id} subscribers: {self.channel_subscriptions[channel_id]}")

    async def unsubscribe_from_channel(self, username: str, channel_id: str):
        logger.debug(f"Unsubscribing user {username} from channel {channel_id}")
        if channel_id in self.channel_subscriptions:
            self.channel_subscriptions[channel_id].discard(username)

    async def broadcast_to_channel(self, message: dict, channel_id: str):
        logger.debug(f"Broadcasting message to channel {channel_id}")
        if channel_id not in self.channel_subscriptions:
            logger.debug(f"No subscribers for channel {channel_id}")
            return
            
        # Get all subscribers for this channel
        subscribers = self.channel_subscriptions[channel_id]
        
        # Send to all subscribed users
        for username in subscribers:
            if username in self.active_connections:
                try:
                    # Add 3-second timeout to send operation
                    await asyncio.wait_for(
                        self.active_connections[username].send_json(message),
                        timeout=3.0  # seconds
                    )
                    logger.debug(f"Message sent to user {username}")
                except asyncio.TimeoutError:
                    logger.error(f"Timeout sending message to {username}")
                except Exception as e:
                    logger.error(f"Error sending to {username}: {str(e)}")
            else:
                logger.debug(f"User {username} not connected")

    async def broadcast(self, message: dict):
        logger.debug("Broadcasting message globally")
        # For backwards compatibility or global messages
        for username, connection in self.active_connections.items():
            logger.debug(f"Sending message to user {username}")
            await connection.send_json(message)

    def is_connected(self, username: str) -> bool:
        return username in self.active_connections

    def get_connection(self, username: str) -> WebSocket:
        return self.active_connections.get(username) 