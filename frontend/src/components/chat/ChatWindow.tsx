import React, { useState, useEffect } from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';
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
}

interface ChatWindowProps {
  channelId: string;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ channelId }) => {
  const [messages, setMessages] = useState<MessageData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const api = useApi();
  const { token } = useAuth();

  const fetchMessages = async () => {
    if (!token) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/messages/channel/${channelId}`, {
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
      console.error('Error fetching messages:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch messages');
    }
  };

  const handleAddReaction = async (channelId: string, messageId: string, emoji: string) => {
    try {
      await api.addReaction(channelId, messageId, emoji);
      await fetchMessages();
    } catch (err) {
      console.error('Error adding reaction:', err);
      setError('Failed to add reaction');
    }
  };

  const handleRemoveReaction = async (channelId: string, messageId: string, emoji: string) => {
    try {
      await api.removeReaction(channelId, messageId, emoji);
      await fetchMessages();
    } catch (err) {
      console.error('Error removing reaction:', err);
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

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-hidden">
        {error ? (
          <div className="text-red-500 p-4">{error}</div>
        ) : (
          <MessageList 
            messages={messages} 
            channelId={channelId}
            onAddReaction={handleAddReaction}
            onRemoveReaction={handleRemoveReaction}
          />
        )}
      </div>
      <MessageInput 
        channelId={channelId} 
        onMessageSent={fetchMessages}
      />
    </div>
  );
};

export default ChatWindow; 