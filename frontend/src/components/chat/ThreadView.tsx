import React, { useState, useEffect } from 'react';
import { useApi } from '../../contexts/ApiContext';
import { useAuth } from '../../contexts/AuthContext';
import MessageInput from './MessageInput';
import { API_BASE_URL } from '../../contexts/BackendConfig';

interface ThreadViewProps {
  parentMessage: MessageData;
  onClose: () => void;
}

interface MessageData {
  id: string;
  content: string;
  username: string;
  user_id: string;
  channel_id: string | null;
  created_at: string;
  emojis: { [key: string]: string[] };
  file: FileInfo | null;
  parent_id: string | null;
  replies_count: number;
  parent_message?: MessageData;
}

interface FileInfo {
  id: string;
  filename: string;
  size: number;
  content_type: string;
}

const ThreadView: React.FC<ThreadViewProps> = ({ parentMessage, onClose }) => {
  const [replies, setReplies] = useState<MessageData[]>([]);
  const [error, setError] = useState<string | null>(null);
  const api = useApi();
  const { token } = useAuth();

  const fetchReplies = async () => {
    if (!token) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/messages/thread/${parentMessage.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json'
        }
      });
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || 'Failed to fetch replies');
      }
      
      const data = await response.json();
      setReplies(data);
      setError(null);
    } catch (err) {
      console.error('Error fetching replies:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch replies');
    }
  };

  useEffect(() => {
    fetchReplies();
    const interval = setInterval(fetchReplies, 1000);
    return () => clearInterval(interval);
  }, [parentMessage.id, token]);

  const renderMessage = (message: MessageData, isParent: boolean = false) => (
    <div className={`p-4 ${isParent ? 'bg-gray-50' : 'bg-white'} rounded-lg ${!isParent && 'shadow-sm'}`}>
      <div className="flex items-center gap-2">
        <div className="font-medium text-gray-900">{message.username}</div>
        <div className="text-xs text-gray-500">
          {new Date(message.created_at).toLocaleString()}
        </div>
      </div>
      <div className="mt-1 text-gray-700">{message.content}</div>
      {message.file && (
        <div className="mt-2 text-sm text-blue-600 hover:underline">
          📎 {message.file.filename}
        </div>
      )}
    </div>
  );

  return (
    <div className="flex flex-col h-full border-l border-gray-200">
      <div className="p-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h2 className="text-lg font-semibold">Thread</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <span className="sr-only">Close thread</span>
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4">
        {/* Parent Message */}
        <div className="mb-6">
          {renderMessage(parentMessage, true)}
        </div>

        {/* Replies */}
        <div className="space-y-6">
          {error ? (
            <div className="text-red-500 p-4">{error}</div>
          ) : (
            replies.map((reply) => (
              <div key={reply.id} className="space-y-2">
                {reply.parent_message && reply.parent_message.id !== parentMessage.id && (
                  <div className="ml-4 pl-4 border-l-2 border-gray-200">
                    {renderMessage(reply.parent_message)}
                  </div>
                )}
                <div className={reply.parent_message && reply.parent_message.id !== parentMessage.id ? 'ml-8' : ''}>
                  {renderMessage(reply)}
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      <div className="p-4 border-t border-gray-200">
        <MessageInput 
          parentId={parentMessage.id}
          onMessageSent={fetchReplies}
          placeholder="Reply in thread..."
        />
      </div>
    </div>
  );
};

export default ThreadView; 