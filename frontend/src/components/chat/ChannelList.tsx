import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useApi } from '../../contexts/ApiContext';
import { API_BASE_URL } from '../../contexts/BackendConfig';

interface Channel {
  id: string;
  name: string;
  description: string;
  owner_id: string;
  members: string[];
  is_dm?: boolean;
}

interface ChannelListProps {
  onChannelSelect: (channelId: string) => void;
  selectedChannelId?: string;
  children?: React.ReactNode;
}

const ChannelList: React.FC<ChannelListProps> = ({ 
  onChannelSelect, 
  selectedChannelId,
  children 
}) => {
  const { token } = useAuth();
  const api = useApi();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [users, setUsers] = useState<any[]>([]);
  const [showCreateChannel, setShowCreateChannel] = useState(false);
  const [newChannelName, setNewChannelName] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [page, setPage] = useState(1);
  const loader = useRef(null);
  const [lastUserFetchError, setLastUserFetchError] = useState<number>(0);
  const RETRY_DELAY = 30000; // 30 seconds

  const fetchUsers = async () => {
    // If there was an error in the last 30 seconds, skip this fetch
    if (Date.now() - lastUserFetchError < RETRY_DELAY) {
      return;
    }

    try {
      const usersData = await api.getUsers();
      // Filter out system user and any users with invalid data
      const validUsers = usersData.filter(user => 
        user && 
        user.id && 
        user.username && 
        !user.email?.includes('@chat.local')
      );
      setUsers(validUsers);
      setLastUserFetchError(0); // Reset error state on success
    } catch (err) {
      setLastUserFetchError(Date.now()); // Record time of error
      // Keep existing users list
    }
  };

  // Fetch channels with pagination
  const fetchChannels = async (pageNum: number, append: boolean = false) => {
    if (!token || isLoading) return;
    
    setIsLoading(true);
    try {
      const response = await fetch(`${API_BASE_URL}/channels?page=${pageNum}&limit=20`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to fetch channels');
      }
      
      const channelsData = await response.json();

      // Only try to fetch users if we haven't had a recent error
      if (Date.now() - lastUserFetchError >= RETRY_DELAY) {
        await fetchUsers();
      }

      // Convert users to channel-like objects
      const userChannels = users.map(user => ({
        id: `dm-${user.id}`,
        name: user.username,
        description: `Direct message with ${user.username}`,
        owner_id: user.id,
        members: [user.id],
        is_dm: true
      }));

      // Combine regular channels with user DM channels
      const allChannels = [...channelsData, ...userChannels];
      
      setHasMore(channelsData.length === 20);
      setChannels(prev => append ? [...prev, ...allChannels] : allChannels);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load channels');
    } finally {
      setIsLoading(false);
    }
  };

  // Set up polling interval
  useEffect(() => {
    if (token) {
      // Initial fetch
      fetchChannels(1, false);

      // Set up polling every 10 seconds
      const interval = setInterval(() => {
        fetchChannels(1, false);
      }, 10000);

      // Cleanup interval on unmount
      return () => clearInterval(interval);
    }
  }, [token]);

  // Handle pagination
  useEffect(() => {
    if (token && page > 1) {
      fetchChannels(page, true);
    }
  }, [token, page]);

  // Intersection observer for infinite scroll
  const handleObserver = useCallback((entries: IntersectionObserverEntry[]) => {
    const target = entries[0];
    if (target.isIntersecting && hasMore && !isLoading) {
      setPage(prev => prev + 1);
    }
  }, [hasMore, isLoading]);

  useEffect(() => {
    const option = {
      root: null,
      rootMargin: "20px",
      threshold: 1.0
    };
    const observer = new IntersectionObserver(handleObserver, option);
    if (loader.current) observer.observe(loader.current);
    return () => observer.disconnect();
  }, [handleObserver]);

  const handleCreateChannel = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/channels`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          name: newChannelName,
          description: `${newChannelName} channel`,
          is_private: false
        })
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create channel');
      }

      // Refresh the channels list
      await fetchChannels(1, false);
      
      // Reset form
      setShowCreateChannel(false);
      setNewChannelName('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create channel');
    }
  };

  return (
    <div className="h-full flex flex-col bg-gray-800">
      <div className="sticky top-0 z-10 bg-gray-900 p-4">
        <button
          onClick={() => setShowCreateChannel(true)}
          className="w-full py-2 px-4 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
        >
          + Create Channel
        </button>
      </div>

      {error && (
        <div className="p-4 text-red-500 bg-red-100">
          {error}
        </div>
      )}

      {showCreateChannel && (
        <div className="p-4 border-b border-gray-700">
          <form onSubmit={handleCreateChannel}>
            <input
              type="text"
              value={newChannelName}
              onChange={(e) => setNewChannelName(e.target.value)}
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

      <div className="flex-1 overflow-y-auto scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
        <div className="space-y-1">
          {channels.map((channel) => (
            <button
              key={channel.id}
              onClick={() => onChannelSelect(channel.id)}
              className={`w-full p-4 text-left hover:bg-gray-700 transition-colors ${
                selectedChannelId === channel.id ? 'bg-gray-700' : ''
              }`}
            >
              <div className="text-white font-medium">
                {channel.is_dm ? (
                  <span className="flex items-center gap-2">
                    <span className="text-gray-400">👤</span>
                    {channel.name}
                  </span>
                ) : (
                  <span className="flex items-center gap-2">
                    <span className="text-gray-400">#</span>
                    {channel.name}
                  </span>
                )}
              </div>
              <div className="text-gray-400 text-sm">{channel.description}</div>
            </button>
          ))}
          {isLoading && (
            <div className="text-center p-4 text-gray-400">
              Loading more channels...
            </div>
          )}
          <div ref={loader} />
        </div>
      </div>
    </div>
  );
};

export default ChannelList; 