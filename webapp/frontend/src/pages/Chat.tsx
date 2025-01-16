import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import ChatWindow from '../components/chat/ChatWindow';
import ChannelList from '../components/chat/ChannelList';
import { useAuth } from '../contexts/AuthContext';

interface Channel {
  id: string;
  name: string;
  description: string;
  created_by: string;
  members: string[];
  channel_type: "public" | "private" | "dm";
  member_exceptions: { [key: string]: "allowed" | "banned" };
}

const Chat: React.FC = () => {
  const navigate = useNavigate();
  const [currentChannelId, setCurrentChannelId] = useState<string>('');
  const [activeDmUserId, setActiveDmUserId] = useState<string>('');
  const [navigating, setNavigating] = useState(false);

  const handleChannelSelect = (channelId: string) => {
    setCurrentChannelId(channelId);
    // If it's a DM channel, extract the user ID
    if (channelId.startsWith('dm-')) {
      setActiveDmUserId(channelId.replace('dm-', ''));
    } else {
      setActiveDmUserId('');
    }
  };

  const handleYouTubeSearchClick = () => {
    setNavigating(true);
    // Check if there's a recent search state (within last 30 minutes)
    const savedState = localStorage.getItem('youtube_search_state');
    if (savedState) {
      const state = JSON.parse(savedState);
      const lastVisited = new Date(state.lastVisited);
      const thirtyMinutesAgo = new Date(Date.now() - 30 * 60 * 1000);
      
      // If the state is older than 30 minutes, clear it
      if (lastVisited < thirtyMinutesAgo) {
        localStorage.removeItem('youtube_search_state');
      }
    }
    navigate('/youtube-search');
  };

  return (
    <div className="flex h-screen bg-gray-800">
      {/* Sidebar */}
      <div className="w-64 bg-gray-900 flex flex-col h-full">
        <div className="p-4 bg-gray-800 border-b border-gray-700">
          <button
            onClick={handleYouTubeSearchClick}
            disabled={navigating}
            className="w-full px-4 py-2 text-sm bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 transition-colors duration-200"
          >
            {navigating ? 'Loading Search...' : 'YouTube Transcript Search'}
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          <ChannelList 
            onChannelSelect={handleChannelSelect}
            selectedChannelId={currentChannelId}
            activeDmUserId={activeDmUserId}
          />
        </div>
      </div>

      {/* Main chat area */}
      <div className="flex-1 flex flex-col h-full">
        {currentChannelId ? (
          <ChatWindow channelId={currentChannelId} />
        ) : (
          <div className="flex items-center justify-center h-full text-gray-400">
            Select a channel or user to start chatting
          </div>
        )}
      </div>
    </div>
  );
};

export default Chat; 