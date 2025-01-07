import React from 'react';
import MessageList from './MessageList';
import MessageInput from './MessageInput';

interface ChatWindowProps {
  channelId: string;
}

const ChatWindow: React.FC<ChatWindowProps> = ({ channelId }) => {
  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-hidden">
        <MessageList channelId={channelId} />
      </div>
      <MessageInput channelId={channelId} />
    </div>
  );
};

export default ChatWindow; 