import React, { useState, useEffect } from 'react';
import ChatWindow from '../components/chat/ChatWindow';
import { API_BASE_URL } from '../contexts/BackendConfig';
import { useAuth } from '../contexts/AuthContext';
import { useWebSocket } from '../contexts/WebSocketContext';

interface Channel {
  id: string;
  name: string;
  description: string;
  created_by: string;
  members: string[];
}

const Chat: React.FC = () => {
  const [currentChannel, setCurrentChannel] = useState('general');
  const [showCreateChannel, setShowCreateChannel] = useState(false);
  const [newChannelName, setNewChannelName] = useState('');
  const [newChannelDescription, setNewChannelDescription] = useState('');
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { token, user } = useAuth();
  const { isConnected } = useWebSocket();

  const fetchChannels = async () => {
    if (!token) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/channels`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const channelList = await response.json();
        setChannels(channelList);
        
        // Ensure we're in a valid channel
        if (!channelList.find((c: Channel) => c.name === currentChannel)) {
          setCurrentChannel('general');
        }
      }
    } catch (error) {
      console.error('Error fetching channels:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchChannels();
    }
  }, [token]);

  const handleCreateChannel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !newChannelName.trim()) return;

    try {
      const response = await fetch(`${API_BASE_URL}/channels/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          name: newChannelName.toLowerCase().replace(/\s+/g, '-'),
          description: newChannelDescription
        })
      });

      if (response.ok) {
        const channel = await response.json();
        await fetchChannels();
        setCurrentChannel(channel.name);
        setShowCreateChannel(false);
        setNewChannelName('');
        setNewChannelDescription('');
      } else {
        console.error('Failed to create channel:', await response.text());
      }
    } catch (error) {
      console.error('Error creating channel:', error);
    }
  };

  const handleJoinChannel = async (channelName: string) => {
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/channels/${channelName}/join`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        await fetchChannels();
        setCurrentChannel(channelName);
      }
    } catch (error) {
      console.error('Error joining channel:', error);
    }
  };

  const handleLeaveChannel = async (channelName: string) => {
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/channels/${channelName}/leave`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        await fetchChannels();
        if (currentChannel === channelName) {
          setCurrentChannel('general');
        }
      }
    } catch (error) {
      console.error('Error leaving channel:', error);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold mb-4">Channels</h2>
          <button
            onClick={() => setShowCreateChannel(true)}
            className="w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
            disabled={!isConnected}
          >
            Create Channel
          </button>
        </div>

        {showCreateChannel && (
          <div className="p-4 border-b">
            <form onSubmit={handleCreateChannel}>
              <input
                type="text"
                value={newChannelName}
                onChange={(e) => setNewChannelName(e.target.value)}
                placeholder="Channel name"
                className="w-full p-2 mb-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <input
                type="text"
                value={newChannelDescription}
                onChange={(e) => setNewChannelDescription(e.target.value)}
                placeholder="Channel description"
                className="w-full p-2 mb-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <div className="flex space-x-2">
                <button
                  type="submit"
                  disabled={!isConnected || !newChannelName.trim()}
                  className="flex-1 py-1 bg-green-500 text-white rounded hover:bg-green-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
                >
                  Create
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateChannel(false)}
                  className="flex-1 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                >
                  Cancel
                </button>
              </div>
            </form>
          </div>
        )}

        <div className="p-2 space-y-1">
          {isLoading ? (
            <div className="text-center py-4 text-gray-500">Loading channels...</div>
          ) : channels.map((channel) => {
            const isCurrentChannel = currentChannel === channel.name;
            const isMember = channel.members.includes(user?.id || '');
            const isOwner = channel.created_by === user?.id;
            const isDefaultChannel = channel.name === 'general' || channel.name === 'random';

            return (
              <div
                key={channel.id}
                className={`rounded ${isCurrentChannel ? 'bg-blue-100' : 'hover:bg-gray-100'}`}
              >
                <div className="p-2 flex items-center justify-between">
                  <button
                    onClick={() => isMember ? setCurrentChannel(channel.name) : handleJoinChannel(channel.name)}
                    className="text-left flex-1"
                    disabled={!isConnected}
                  >
                    <div className="font-medium">#{channel.name}</div>
                    <div className="text-sm text-gray-500">{channel.description}</div>
                  </button>
                  {!isDefaultChannel && (
                    <div className="ml-2">
                      {!isMember && (
                        <button
                          onClick={() => handleJoinChannel(channel.name)}
                          disabled={!isConnected}
                          className="px-2 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
                        >
                          Join
                        </button>
                      )}
                      {isMember && !isOwner && (
                        <button
                          onClick={() => handleLeaveChannel(channel.name)}
                          disabled={!isConnected}
                          className="px-2 py-1 text-sm bg-red-500 text-white rounded hover:bg-red-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
                        >
                          Leave
                        </button>
                      )}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1">
        <div className="h-full">
          <ChatWindow channelId={currentChannel} />
        </div>
      </div>
    </div>
  );
};

export default Chat; 