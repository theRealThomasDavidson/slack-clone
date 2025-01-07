import redis
import json
import logging
from typing import Optional, Dict, Set
from fastapi import WebSocket
import asyncio
from ..core.config import settings

logger = logging.getLogger(__name__)

class RedisManager:
    _instance = None
    _initialized = False
    _background_tasks = []

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self._initialized = True
            # Redis for pub/sub and data storage
            self.redis = redis.Redis(
                host=settings.REDIS_HOST,
                port=settings.REDIS_PORT,
                db=0,
                decode_responses=True
            )
            self.pubsub = self.redis.pubsub()
            
            # Keep WebSocket connections local (only for this instance)
            self.local_connections: Dict[str, WebSocket] = {}
            self.server_id = settings.SERVER_ID  # Unique ID for this server instance

    async def initialize(self):
        """Initialize async components"""
        if not hasattr(self, '_subscriber_task'):
            self._subscriber_task = asyncio.create_task(self.start_subscriber())
            self._health_check_task = asyncio.create_task(self.health_check())
            self._background_tasks.extend([self._subscriber_task, self._health_check_task])

    async def cleanup(self):
        """Cleanup background tasks"""
        for task in self._background_tasks:
            if not task.done():
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        self._background_tasks.clear()

    async def connect(self, websocket: WebSocket, username: str):
        """Connect a new WebSocket client"""
        logger.info(f"New WebSocket connection from user: {username}")
        await websocket.accept()
        self.local_connections[username] = websocket
        
        # Store user's server instance ID in Redis
        self.redis.hset("user_servers", username, self.server_id)
        logger.debug(f"Stored server mapping for user {username}: {self.server_id}")
        
        # Ensure background tasks are running
        await self.initialize()

    async def disconnect(self, username: str):
        """Disconnect a WebSocket client"""
        logger.info(f"Disconnecting user: {username}")
        self.local_connections.pop(username, None)
        self.redis.hdel("user_servers", username)
        
        # Remove from all channel subscriptions
        for channel in self.redis.smembers(f"user:{username}:channels"):
            await self.unsubscribe_from_channel(username, channel)

    async def subscribe_to_channel(self, username: str, channel_id: str):
        """Subscribe a user to a channel"""
        logger.info(f"Subscribing user {username} to channel {channel_id}")
        # Store subscription in Redis
        self.redis.sadd(f"channel:{channel_id}:users", username)
        self.redis.sadd(f"user:{username}:channels", channel_id)
        
        # Subscribe to Redis channel
        self.pubsub.subscribe(f"channel:{channel_id}")
        logger.debug(f"Subscribed to Redis channel: channel:{channel_id}")

    async def unsubscribe_from_channel(self, username: str, channel_id: str):
        """Unsubscribe a user from a channel"""
        logger.info(f"Unsubscribing user {username} from channel {channel_id}")
        self.redis.srem(f"channel:{channel_id}:users", username)
        self.redis.srem(f"user:{username}:channels", channel_id)
        
        # If no more users in channel, unsubscribe from Redis channel
        if not self.redis.scard(f"channel:{channel_id}:users"):
            self.pubsub.unsubscribe(f"channel:{channel_id}")

    async def broadcast_to_channel(self, message: dict, channel_id: str):
        """Broadcast a message to all users in a channel"""
        logger.info(f"Broadcasting message to channel {channel_id}")
        try:
            # Store message in Redis for history
            self.redis.lpush(f"channel:{channel_id}:messages", json.dumps(message))
            self.redis.ltrim(f"channel:{channel_id}:messages", 0, 99)  # Keep last 100 messages
            
            # Publish to Redis channel
            self.redis.publish(f"channel:{channel_id}", json.dumps(message))
        except redis.RedisError as e:
            logger.error(f"Redis error in broadcast_to_channel: {e}")

    async def get_channel_messages(self, channel_id: str, limit: int = 50) -> list:
        """Get recent messages from a channel"""
        try:
            messages = self.redis.lrange(f"channel:{channel_id}:messages", 0, limit - 1)
            return [json.loads(msg) for msg in messages]
        except redis.RedisError as e:
            logger.error(f"Redis error in get_channel_messages: {e}")
            return []

    async def start_subscriber(self):
        """Listen for Redis messages and forward to WebSocket clients"""
        logger.info("Starting Redis subscriber")
        try:
            while True:
                message = await asyncio.to_thread(self.pubsub.get_message, timeout=1)
                if message and message['type'] == 'message':
                    try:
                        channel = message['channel']
                        data = json.loads(message['data'])
                        
                        # Get all users subscribed to this channel
                        users = self.redis.smembers(f"channel:{channel}:users")
                        
                        # Send to all local users
                        for username in users:
                            if username in self.local_connections:
                                try:
                                    await self.local_connections[username].send_json(data)
                                except Exception as e:
                                    logger.error(f"Error sending message to user {username}: {e}")
                                    await self.disconnect(username)
                    except Exception as e:
                        logger.error(f"Error processing Redis message: {e}")
                await asyncio.sleep(0.1)
        except Exception as e:
            logger.error(f"Error in subscriber loop: {e}")

    async def health_check(self):
        """Periodic health check"""
        while True:
            try:
                self.redis.setex(f"server_health:{self.server_id}", 30, "alive")
                await asyncio.sleep(10)
            except Exception as e:
                logger.error(f"Health check failed: {e}")
                await asyncio.sleep(5)  # Shorter retry interval on failure 