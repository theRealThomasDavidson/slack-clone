import React, { useState, useEffect } from 'react';
import { useWebSocket } from '../../contexts/WebSocketContext';

const NotificationBadge: React.FC = () => {
  const { socket } = useWebSocket();
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    fetchUnreadCount();

    if (socket) {
      socket.addEventListener('message', handleWebSocketMessage);
      return () => {
        socket.removeEventListener('message', handleWebSocketMessage);
      };
    }
  }, [socket]);

  const handleWebSocketMessage = (event: MessageEvent) => {
    const data = JSON.parse(event.data);
    if (data.type === 'notification') {
      setUnreadCount(prev => prev + 1);
    } else if (data.type === 'notification_read') {
      setUnreadCount(prev => Math.max(0, prev - 1));
    }
  };

  const fetchUnreadCount = async () => {
    try {
      const response = await fetch('/api/notifications/unread/count');
      if (!response.ok) throw new Error('Failed to fetch unread count');
      const data = await response.json();
      setUnreadCount(data.count);
    } catch (err) {
      console.error('Failed to load unread count:', err);
    }
  };

  if (unreadCount === 0) return null;

  return (
    <div className="inline-flex items-center justify-center w-5 h-5 text-xs font-bold text-white bg-red-500 rounded-full">
      {unreadCount > 99 ? '99+' : unreadCount}
    </div>
  );
};

export default NotificationBadge; 