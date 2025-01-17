import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
import MessageSearch from './MessageSearch';
import { useApi } from '../../contexts/ApiContext';
import { useAuth } from '../../contexts/AuthContext';
import { API_BASE_URL } from '../../contexts/BackendConfig';

interface FileInfo {
  id: string;
  filename: string;
  size: number;
  content_type: string;
}

interface MessageData {
  id: string;
  content: string;
  username: string;
  user_id: string;
  channel_id: string;
  created_at: string;
  emojis: { [key: string]: string[] };
  file: FileInfo | null;
  parent_id: string | null;
  replies_count: number;
}

interface ChatWindowProps {
  channelId: string;
  selectedMessageTimestamp?: string | null;
  onMessageScrolled?: () => void;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ 
  channelId, 
  selectedMessageTimestamp,
  onMessageScrolled 
}) => {
  const [messages, setMessages] = useState<MessageData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [channelName, setChannelName] = useState<string>('');
  const [showSearch, setShowSearch] = useState(false);
  const api = useApi();
  const { token } = useAuth();

  const fetchMessages = async () => {
    if (!token) return;
    
    try {
      let endpoint;
      const channelIdStr = String(channelId);
      if (channelIdStr.startsWith('dm-')) {
        const targetUserId = channelIdStr.replace('dm-', '');
        endpoint = `${API_BASE_URL}/messages/dm/${targetUserId}`;
      } else {
        endpoint = `${API_BASE_URL}/messages/channel/${channelId}`;
      }

      const response = await fetch(endpoint, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || 'Failed to fetch messages');
      }
      
      const data = await response.json();
      setMessages(data);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch messages');
    }
  };

  // Fetch channel name
  useEffect(() => {
    const fetchChannelName = async () => {
      if (!token || !channelId) return;

      try {
        const channelIdStr = String(channelId);
        if (channelIdStr.startsWith('dm-')) {
          const targetUserId = channelIdStr.replace('dm-', '');
          const response = await fetch(`${API_BASE_URL}/users/${targetUserId}`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          if (response.ok) {
            const user = await response.json();
            setChannelName(`@${user.username}`);
          }
        } else {
          const response = await fetch(`${API_BASE_URL}/channels/${channelId}`, {
            headers: {
              'Authorization': `Bearer ${token}`
            }
          });
          if (response.ok) {
            const channel = await response.json();
            setChannelName(`#${channel.name}`);
          }
        }
      } catch (err) {
        console.error('Failed to fetch channel/user name:', err);
      }
    };

    fetchChannelName();
  }, [channelId, token]);

  const handleAddReaction = async (channelId: string, messageId: string, emoji: string) => {
    try {
      await api.addReaction(channelId, messageId, emoji);
      await fetchMessages();
    } catch (err) {
      setError('Failed to add reaction');
    }
  };

  const handleRemoveReaction = async (channelId: string, messageId: string, emoji: string) => {
    try {
      await api.removeReaction(channelId, messageId, emoji);
      await fetchMessages();
    } catch (err) {
      setError('Failed to remove reaction');
    }
  };

  useEffect(() => {
    if (token) {
      fetchMessages();
      const interval = setInterval(fetchMessages, 1000);
      return () => clearInterval(interval);
    }
  }, [channelId, token]);

  // Effect to scroll to selected message
  useEffect(() => {
    if (selectedMessageTimestamp && messages.length > 0) {
      const messageElement = document.querySelector(`[data-timestamp="${selectedMessageTimestamp}"]`);
      if (messageElement) {
        messageElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        messageElement.classList.add('bg-blue-900', 'transition-colors', 'duration-1000');
        setTimeout(() => {
          messageElement.classList.remove('bg-blue-900');
          if (onMessageScrolled) {
            onMessageScrolled();
          }
        }, 2000);
      }
    }
  }, [selectedMessageTimestamp, messages, onMessageScrolled]);

  return (
    <div className="flex flex-col h-full bg-gray-800">
      {/* Channel header */}
      <div className="p-4 border-b border-gray-700 flex justify-between items-center">
        <h2 className="text-lg font-semibold text-white">{channelName || 'Loading...'}</h2>
        <button
          onClick={() => setShowSearch(!showSearch)}
          className="p-2 text-gray-400 hover:text-white focus:outline-none"
          title="Search similar messages"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </button>
      </div>

      {/* Search area */}
      {showSearch && (
        <MessageSearch 
          onClose={() => setShowSearch(false)} 
          className="p-4 bg-gray-900 border-b border-gray-700"
        />
      )}

      {/* Messages area */}
      <div className="flex-1 overflow-y-auto">
        {error ? (
          <div className="text-red-500 p-4">{error}</div>
        ) : (
          <MessageList 
            messages={messages} 
            channelId={channelId}
            onAddReaction={handleAddReaction}
            onRemoveReaction={handleRemoveReaction}
            selectedMessageTimestamp={selectedMessageTimestamp}
          />
        )}
      </div>

      {/* Message input */}
      <div className="border-t border-gray-700">
        <MessageInput 
          channelId={channelId} 
          onMessageSent={fetchMessages}
        />
      </div>
    </div>
  );
};

export default ChatWindow; 