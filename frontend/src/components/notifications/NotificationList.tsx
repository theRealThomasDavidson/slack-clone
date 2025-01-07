import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useWebSocket } from '../../contexts/WebSocketContext';

interface Notification {
  id: string;
  type: 'mention' | 'channel_invite';
  content: string;
  channel_id: string;
  message_id?: string;
  created_at: string;
  read: boolean;
}

interface NotificationPreferences {
  mentions: boolean;
  channel_invites: boolean;
  direct_messages: boolean;
}

const NotificationList: React.FC = () => {
  const { user } = useAuth();
  const { socket } = useWebSocket();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [preferences, setPreferences] = useState<NotificationPreferences>({
    mentions: true,
    channel_invites: true,
    direct_messages: false
  });
  const [showPreferences, setShowPreferences] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    fetchNotifications();
    fetchPreferences();

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
      setNotifications(prev => [data.data, ...prev]);
    }
  };

  const fetchNotifications = async () => {
    try {
      const response = await fetch('/api/notifications');
      if (!response.ok) throw new Error('Failed to fetch notifications');
      const data = await response.json();
      setNotifications(data);
    } catch (err) {
      setError('Failed to load notifications');
    }
  };

  const fetchPreferences = async () => {
    try {
      const response = await fetch('/api/notifications/preferences');
      if (!response.ok) throw new Error('Failed to fetch preferences');
      const data = await response.json();
      setPreferences(data);
    } catch (err) {
      setError('Failed to load preferences');
    }
  };

  const markAsRead = async (notificationId: string) => {
    try {
      const response = await fetch(`/api/notifications/${notificationId}/read`, {
        method: 'POST'
      });
      if (!response.ok) throw new Error('Failed to mark notification as read');
      
      setNotifications(prev =>
        prev.map(n =>
          n.id === notificationId ? { ...n, read: true } : n
        )
      );
    } catch (err) {
      setError('Failed to mark notification as read');
    }
  };

  const clearAll = async () => {
    try {
      const response = await fetch('/api/notifications/clear', {
        method: 'POST'
      });
      if (!response.ok) throw new Error('Failed to clear notifications');
      setNotifications([]);
    } catch (err) {
      setError('Failed to clear notifications');
    }
  };

  const updatePreferences = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/notifications/preferences', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(preferences)
      });

      if (!response.ok) throw new Error('Failed to update preferences');
      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      setError('Failed to update preferences');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-lg font-semibold">Notifications</h2>
        <div className="space-x-2">
          <button
            onClick={() => setShowPreferences(!showPreferences)}
            className="px-3 py-1 text-sm rounded-md bg-gray-100 hover:bg-gray-200"
          >
            Preferences
          </button>
          {notifications.length > 0 && (
            <button
              onClick={clearAll}
              className="px-3 py-1 text-sm rounded-md bg-red-100 hover:bg-red-200 text-red-700"
            >
              Clear All
            </button>
          )}
        </div>
      </div>

      {showPreferences && (
        <div className="bg-white p-4 rounded-md shadow space-y-4">
          <h3 className="font-medium">Notification Settings</h3>
          <div className="space-y-2">
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={preferences.mentions}
                onChange={e => setPreferences(prev => ({ ...prev, mentions: e.target.checked }))}
                className="rounded"
              />
              <span>Mentions</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={preferences.channel_invites}
                onChange={e => setPreferences(prev => ({ ...prev, channel_invites: e.target.checked }))}
                className="rounded"
              />
              <span>Channel Invites</span>
            </label>
            <label className="flex items-center space-x-2">
              <input
                type="checkbox"
                checked={preferences.direct_messages}
                onChange={e => setPreferences(prev => ({ ...prev, direct_messages: e.target.checked }))}
                className="rounded"
              />
              <span>Direct Messages</span>
            </label>
          </div>
          <button
            onClick={updatePreferences}
            disabled={isLoading}
            className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
          >
            {isLoading ? 'Saving...' : 'Save Preferences'}
          </button>
          {success && <div className="text-green-600 text-sm">Preferences updated</div>}
        </div>
      )}

      {error && (
        <div className="text-red-600 text-sm">{error}</div>
      )}

      <div className="space-y-2">
        {notifications.map(notification => (
          <div
            key={notification.id}
            onClick={() => markAsRead(notification.id)}
            className={`p-3 rounded-md cursor-pointer ${
              notification.read ? 'bg-gray-50' : 'bg-blue-50'
            }`}
          >
            <div className="text-sm">{notification.content}</div>
            <div className="text-xs text-gray-500 mt-1">
              {new Date(notification.created_at).toLocaleString()}
            </div>
          </div>
        ))}
        {notifications.length === 0 && (
          <div className="text-gray-500 text-center py-4">
            No notifications
          </div>
        )}
      </div>
    </div>
  );
};

export default NotificationList; 