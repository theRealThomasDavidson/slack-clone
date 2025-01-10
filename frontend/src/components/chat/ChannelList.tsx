import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { API_BASE_URL } from '../../contexts/BackendConfig';

interface Channel {
  id: string;
  name: string;
  description: string;
  owner_id: string;
  members: string[];
}

interface ChannelListProps {
  onChannelSelect: (channelId: string) => void;
  selectedChannelId?: string;
}

const ChannelList: React.FC<ChannelListProps> = ({ onChannelSelect, selectedChannelId }) => {
  const { token } = useAuth();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [showCreateChannel, setShowCreateChannel] = useState(false);
  const [newChannelName, setNewChannelName] = useState('');
  const [error, setError] = useState<string | null>(null);

  // Fetch channels
  const fetchChannels = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/channels/`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch channels');
      }
      
      const data = await response.json();
      setChannels(data);
    } catch (err) {
      console.error('Error fetching channels:', err);
      setError(err instanceof Error ? err.message : 'Failed to load channels');
    }
  };

  // Fetch channels on mount and when token changes
  useEffect(() => {
    if (token) {
      fetchChannels();
    }
  }, [token]);

  const handleCreateChannel = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    console.log('Attempting to create channel:', newChannelName);
    console.log('Using token:', token);

    try {
      const response = await fetch(`${API_BASE_URL}/channels/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: newChannelName,
          description: `${newChannelName} channel`
        })
      });

      console.log('Response status:', response.status);
      const responseData = await response.json();
      console.log('Response data:', responseData);

      if (!response.ok) {
        throw new Error(responseData.detail || 'Failed to create channel');
      }

      // Refresh the channels list
      await fetchChannels();
      
      // Reset form
      setShowCreateChannel(false);
      setNewChannelName('');
    } catch (err) {
      console.error('Error creating channel:', err);
      setError(err instanceof Error ? err.message : 'Failed to create channel');
    }
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white mb-4">Channels</h2>
        <button
          onClick={() => {
            console.log('Create Channel button clicked');
            console.log('Current showCreateChannel:', showCreateChannel);
            setShowCreateChannel(true);
            console.log('New showCreateChannel value should be true');
          }}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Create Channel
        </button>
      </div>

      {error && (
        <div className="p-4 text-red-500 bg-red-100 border-b border-red-200">
          {error}
        </div>
      )}

      {showCreateChannel && (
        <div className="p-4 border-b border-gray-700">
          <form onSubmit={handleCreateChannel}>
            <input
              type="text"
              value={newChannelName}
              onChange={(e) => {
                console.log('Channel name changed:', e.target.value);
                setNewChannelName(e.target.value);
              }}
              placeholder="Channel name"
              className="w-full p-2 mb-2 bg-gray-700 text-white rounded"
            />
            <div className="flex space-x-2">
              <button
                type="submit"
                className="flex-1 py-1 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Create
              </button>
              <button
                type="button"
                onClick={() => setShowCreateChannel(false)}
                className="flex-1 py-1 bg-red-600 text-white rounded hover:bg-red-700"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        {channels.map((channel) => (
          <button
            key={channel.id}
            onClick={() => onChannelSelect(channel.id)}
            className={`w-full p-4 text-left hover:bg-gray-700 transition-colors ${
              selectedChannelId === channel.id ? 'bg-gray-700' : ''
            }`}
          >
            <div className="text-white font-medium">#{channel.name}</div>
            <div className="text-gray-400 text-sm">{channel.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
};

export default ChannelList; 