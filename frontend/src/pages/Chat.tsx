import React, { useState } from 'react';
import ChatWindow from '../components/chat/ChatWindow';
import ChannelList from '../components/chat/ChannelList';
import UserList from '../components/chat/UserList';
import { useAuth } from '../contexts/AuthContext';

interface Channel {
  id: string;
  name: string;
  description: string;
  created_by: string;
  members: string[];
  channel_type: "public" | "private";
  member_exceptions: { [key: string]: "allowed" | "banned" };
}

const Chat: React.FC = () => {
  const [currentChannelId, setCurrentChannelId] = useState<string>('');

  const handleChannelSelect = (channelId: string) => {
    setCurrentChannelId(channelId);
  };

  return (
    <div className="flex h-screen bg-gray-800">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 flex flex-col h-full">
        <div className="flex-1 overflow-y-auto">
          <ChannelList 
            onChannelSelect={handleChannelSelect}
            selectedChannelId={currentChannelId}
          />
        </div>
        <div className="border-t border-gray-700 h-48">
          <div className="h-full overflow-y-auto">
            <UserList />
          </div>
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col h-full">
        {currentChannelId ? (
          <ChatWindow channelId={currentChannelId} />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            Select a channel to start chatting
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat; 