import React, { useState, useEffect } from 'react';
import ChatWindow from '../components/chat/ChatWindow';
import { API_BASE_URL } from '../contexts/BackendConfig';
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
  const [currentChannel, setCurrentChannel] = useState('general');
  const [currentChannelId, setCurrentChannelId] = useState<string>('');
  const [showCreateChannel, setShowCreateChannel] = useState(false);
  const [newChannelName, setNewChannelName] = useState('');
  const [newChannelDescription, setNewChannelDescription] = useState('');
  const [channels, setChannels] = useState<Channel[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const { token, user } = useAuth();
  const [error, setError] = useState<string | null>(null);
  const [showModeration, setShowModeration] = useState(false);
  const [selectedChannel, setSelectedChannel] = useState<Channel | null>(null);
  const [bannedUsers, setBannedUsers] = useState<any[]>([]);

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

  // Update currentChannelId when channels or currentChannel changes
  useEffect(() => {
    const channel = channels.find(c => c.name === currentChannel);
    if (channel) {
      setCurrentChannelId(channel.id);
    } else if (channels.length > 0) {
      // If current channel not found but channels exist, set to first channel
      const defaultChannel = channels.find(c => c.name === 'general') || channels[0];
      setCurrentChannel(defaultChannel.name);
      setCurrentChannelId(defaultChannel.id);
    }
  }, [channels, currentChannel]);

  const handleCreateChannel = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !newChannelName.trim()) return;

    setError(null); // Clear any previous errors
    try {
      const response = await fetch(`${API_BASE_URL}/channels`, {
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

      const data = await response.json();
      if (response.ok) {
        await fetchChannels();
        setCurrentChannel(data.name);
        setShowCreateChannel(false);
        setNewChannelName('');
        setNewChannelDescription('');
      } else {
        setError(data.detail || 'Failed to create channel');
      }
    } catch (error) {
      console.error('Error creating channel:', error);
      setError('Failed to create channel. Please try again.');
    }
  };

  const handleJoinChannel = async (channelId: string) => {
    // Simply switch to the channel
    const targetChannel = channels.find((c: Channel) => c.id === channelId);
    if (targetChannel) {
      setCurrentChannel(targetChannel.name);
      setCurrentChannelId(targetChannel.id);
    }
  };

  const handleLeaveChannel = async (channelId: string) => {
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/channels/${channelId}/leave`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        await fetchChannels();
        const channel = channels.find(c => c.id === channelId);
        if (currentChannel === channel?.name) {
          setCurrentChannel('general');
        }
      }
    } catch (error) {
      console.error('Error leaving channel:', error);
    }
  };

  const handleBanUser = async (channelName: string, userId: string) => {
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/channels/${channelName}/ban/${userId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        await fetchChannels();
      }
    } catch (error) {
      console.error('Error banning user:', error);
    }
  };

  const handleUnbanUser = async (channelName: string, userId: string) => {
    if (!token) return;

    try {
      const response = await fetch(`${API_BASE_URL}/channels/${channelName}/unban/${userId}`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        await fetchChannels();
      }
    } catch (error) {
      console.error('Error unbanning user:', error);
    }
  };

  return (
    <div className="flex h-screen bg-gray-100">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r flex flex-col h-full">
        <div className="p-4 border-b flex-shrink-0">
          <h2 className="text-lg font-semibold mb-4">Channels</h2>
          <button
            onClick={() => {
              console.log('Create Channel button clicked');
              setShowCreateChannel(true);
            }}
            className="w-full py-2 px-4 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
          >
            Create Channel
          </button>
        </div>

        {error && (
          <div className="p-4 text-red-500 bg-red-100 border-b border-red-200 flex-shrink-0">
            {error}
          </div>
        )}

        {showCreateChannel && (
          <div className="p-4 border-b flex-shrink-0">
            <form onSubmit={handleCreateChannel}>
              <input
                type="text"
                value={newChannelName}
                onChange={(e) => {
                  console.log('Channel name changed:', e.target.value);
                  setNewChannelName(e.target.value);
                }}
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
                  disabled={!newChannelName.trim()}
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

        <div className="flex-1 overflow-y-auto">
          <div className="p-2 space-y-1">
            {isLoading ? (
              <div className="text-center py-4 text-gray-500">Loading channels...</div>
            ) : channels.map((channel) => {
              const isCurrentChannel = currentChannel === channel.name;
              const isDefaultChannel = channel.name === 'general' || channel.name === 'random';

              return (
                <div
                  key={channel.id}
                  className={`rounded ${isCurrentChannel ? 'bg-blue-100' : 'hover:bg-gray-100'}`}
                >
                  <div className="p-2 flex items-center justify-between">
                    <button
                      onClick={() => handleJoinChannel(channel.id)}
                      className="text-left flex-1"
                    >
                      <div className="font-medium">#{channel.name}</div>
                      <div className="text-sm text-gray-500">{channel.description}</div>
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1">
        <div className="h-full">
          <ChatWindow channelId={currentChannelId} />
        </div>
      </div>
    </div>
  );
};

export default Chat; 