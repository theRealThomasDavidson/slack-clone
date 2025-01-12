import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import EmojiPicker from './EmojiPicker';
import { API_BASE_URL } from '../../contexts/BackendConfig';

interface FileInfo {
  id: string;
  filename: string;
  size: number;
  content_type: string;
}

interface FileDisplayProps {
  file: FileInfo;
  onDownload: () => void;
  isOwnMessage: boolean;
}

const FileDisplay: React.FC<FileDisplayProps> = ({ file, onDownload, isOwnMessage }) => (
  <div className={`flex items-center gap-2 p-2 rounded-lg ${
    isOwnMessage ? 'bg-blue-600' : 'bg-gray-100'
  }`}>
    <svg 
      xmlns="http://www.w3.org/2000/svg" 
      className={`h-5 w-5 ${isOwnMessage ? 'text-white' : 'text-gray-600'}`} 
      fill="none" 
      viewBox="0 0 24 24" 
      stroke="currentColor"
    >
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13" />
    </svg>
    <button
      onClick={onDownload}
      className={`text-left hover:underline cursor-pointer ${
        isOwnMessage ? 'text-white' : 'text-gray-800'
      }`}
    >
      {file.filename} ({(file.size / 1024).toFixed(1)} KB)
    </button>
  </div>
);

interface MessageProps {
  id: string;
  content: string;
  username: string;
  userId: string;
  channelId: string;
  createdAt: string;
  emojis: { [key: string]: string[] };
  file?: FileInfo | null;
  repliesCount?: number;
  onAddReaction: (channelId: string, messageId: string, emoji: string) => void;
  onRemoveReaction: (channelId: string, messageId: string, emoji: string) => void;
  onReply: (messageId: string) => void;
}

const Message: React.FC<MessageProps> = ({
  id,
  content,
  username,
  userId,
  channelId,
  createdAt,
  emojis,
  file,
  repliesCount = 0,
  onAddReaction,
  onRemoveReaction,
  onReply
}) => {
  const { user, token } = useAuth();
  const [showEmojiPicker, setShowEmojiPicker] = useState(false);

  const handleEmojiSelect = (emoji: { native: string }) => {
    onAddReaction(channelId, id, emoji.native);
    setShowEmojiPicker(false);
  };

  const handleReactionClick = (emoji: string) => {
    const users = emojis[emoji] || [];
    if (users.includes(user?.username || '')) {
      onRemoveReaction(channelId, id, emoji);
    } else {
      onAddReaction(channelId, id, emoji);
    }
  };

  const handleFileDownload = async () => {
    if (!file) return;
    try {
      const response = await fetch(`${API_BASE_URL}/files/${file.id}`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (!response.ok) throw new Error('Download failed');
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = file.filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
    } catch (error) {
      alert('Failed to download file. Please try again.');
    }
  };

  const isOwnMessage = userId === user?.id;

  return (
    <div className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'} mb-2`}>
      <div className="relative group max-w-[80%]">
        <div
          className={`rounded-lg p-3 shadow-sm ${
            isOwnMessage
              ? 'bg-blue-500 text-white ml-auto rounded-br-none'
              : userId === '00000000-0000-0000-0000-000000000000'
              ? 'bg-gray-200 text-gray-700 rounded-bl-none'
              : 'bg-white border border-gray-200 text-gray-900 rounded-bl-none'
          }`}
        >
          <div className="flex items-center gap-2 mb-1">
            <span className="font-semibold text-sm">{username || 'System'}</span>
            <span className={`text-xs ${isOwnMessage ? 'text-blue-100' : 'text-gray-500'}`}>
              {new Date(createdAt).toLocaleString('en-US', {
                hour: 'numeric',
                minute: 'numeric',
                hour12: true
              })}
            </span>
          </div>
          <p className="mt-1 break-words">
            {content.split('Uploaded file:')[0]}
          </p>
          {file && (
            <FileDisplay 
              file={file}
              onDownload={handleFileDownload}
              isOwnMessage={isOwnMessage}
            />
          )}
        </div>

        <div className="mt-1 flex flex-col items-start gap-1">
          <div className="flex items-center gap-2">
            {/* Existing reactions */}
            {Object.keys(emojis).length > 0 && (
              <div className="flex flex-wrap gap-1 ml-2">
                {Object.entries(emojis).map(([emoji, users]) => (
                  <button
                    key={emoji}
                    onClick={() => handleReactionClick(emoji)}
                    title={users.join(', ')}
                    className={`
                      px-1.5 py-0.5 rounded-md text-sm flex items-center gap-1
                      ${users.includes(user?.username || '')
                        ? 'bg-blue-100 text-blue-800 border border-blue-200'
                        : 'bg-gray-100 text-gray-800 border border-gray-200'
                      }
                      hover:scale-105 transform transition-all duration-150
                      hover:shadow-sm
                      active:scale-95
                    `}
                  >
                    <span className="select-none">{emoji}</span>
                    {users.length > 1 && (
                      <span className="text-xs font-medium">{users.length}</span>
                    )}
                  </button>
                ))}
              </div>
            )}

            <div className="flex items-center gap-2 ml-2">
              {/* Add reaction button */}
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setShowEmojiPicker(!showEmojiPicker);
                }}
                className={`
                  px-2 py-0.5 rounded-md text-sm
                  ${showEmojiPicker ? 'bg-gray-200' : 'bg-transparent'}
                  hover:bg-gray-100 transition-colors
                  opacity-0 group-hover:opacity-100
                `}
              >
                <span className="text-gray-500">+ Add reaction</span>
              </button>

              {/* Reply button */}
              <button
                onClick={() => onReply(id)}
                className={`
                  px-2 py-0.5 rounded-md text-sm
                  bg-transparent hover:bg-gray-100
                  transition-all duration-200
                  opacity-0 group-hover:opacity-100
                  flex items-center gap-1
                  hover:text-blue-600
                `}
              >
                <svg 
                  xmlns="http://www.w3.org/2000/svg" 
                  className="h-4 w-4 text-gray-500 group-hover:text-blue-500" 
                  fill="none" 
                  viewBox="0 0 24 24" 
                  stroke="currentColor"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth={2} 
                    d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" 
                  />
                </svg>
                <span className="text-gray-500 group-hover:text-blue-500">
                  {repliesCount > 0 ? `${repliesCount} ${repliesCount === 1 ? 'reply' : 'replies'}` : 'Reply'}
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* Emoji picker */}
        {showEmojiPicker && (
          <div className="absolute bottom-full mb-2 right-0">
            <EmojiPicker
              onEmojiSelect={handleEmojiSelect}
              onClickOutside={() => setShowEmojiPicker(false)}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default Message; 