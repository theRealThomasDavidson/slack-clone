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

interface User {
  id: string;
  username: string;
  email: string;
}

interface ChannelListProps {
  onChannelSelect: (channelId: string) => void;
  selectedChannelId?: string;
  children?: React.ReactNode;
}

export const ChannelList: React.FC<ChannelListProps> = ({ 
  onChannelSelect, 
  selectedChannelId,
  children 
}) => {
  const api = useApi();
  const { user: currentUser } = useAuth();
  const { token } = useAuth();
  const [channels, setChannels] = useState<Channel[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [activeDMs, setActiveDMs] = useState<Set<string>>(new Set());
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
    try {
      const users = await api.getUsers();
      const validUsers = users.filter(user => 
        user && 
        user.username && 
        user.username !== currentUser?.username
      );
      setUsers(validUsers);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch users:', err);
      setError('Failed to fetch users');
    }
  };

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
      
      // Filter out DM channels from regular channels
      const regularChannels = channelsData.filter((channel: Channel) => !channel.name.startsWith('DM_'));

      if (Date.now() - lastUserFetchError >= RETRY_DELAY) {
        await fetchUsers();
      }

      // Convert users to channel-like objects for active DMs
      const userChannels = users
        .filter(user => activeDMs.has(user.username))
        .map(user => ({
          id: `dm-${user.id}`,
          name: user.username,
          description: `Direct message with ${user.username}`,
          owner_id: user.id,
          members: [user.id],
          is_dm: true
        }));

      const allChannels = [...regularChannels, ...userChannels];
      
      setHasMore(channelsData.length === 20);
      setChannels(prev => append ? [...prev, ...allChannels] : allChannels);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load channels');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchChannels(1, false);
      const interval = setInterval(() => {
        fetchChannels(1, false);
      }, 10000);
      return () => clearInterval(interval);
    }
  }, [token]);

  useEffect(() => {
    if (token && page > 1) {
      fetchChannels(page, true);
    }
  }, [token, page]);

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

      await fetchChannels(1, false);
      setShowCreateChannel(false);
      setNewChannelName('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create channel');
    }
  };

  const handleUserClick = async (user: User) => {
    try {
      // Create or get DM channel using GET endpoint
      const response = await fetch(`${API_BASE_URL}/channels/dm/${user.username}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to create/get DM channel');
      }

      const channel = await response.json();
      
      // Add user to active DMs and select the channel using username
      setActiveDMs(prev => new Set([...prev, user.username]));
      onChannelSelect(`dm-${user.username}`); // Use username instead of ID
    } catch (error) {
      console.error('Error creating DM channel:', error);
      setError('Failed to start DM conversation');
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
                className="flex-1 py-2 px-4 bg-green-600 text-white rounded hover:bg-green-700"
              >
                Create
              </button>
              <button
                type="button"
                onClick={() => setShowCreateChannel(false)}
                className="py-2 px-4 bg-gray-600 text-white rounded hover:bg-gray-700"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      <div className="flex-1 overflow-y-auto">
        {/* Channels Section */}
        <div className="p-4">
          <h2 className="text-gray-400 text-sm font-semibold mb-2">Channels</h2>
          {channels
            .filter(channel => !channel.is_dm)
            .map(channel => (
              <button
                key={channel.id}
                onClick={() => onChannelSelect(channel.id)}
                className={`w-full text-left p-2 rounded mb-1 ${
                  selectedChannelId === channel.id
                    ? 'bg-gray-700 text-white'
                    : 'text-gray-400 hover:bg-gray-700 hover:text-white'
                }`}
              >
                # {channel.name}
              </button>
            ))}
        </div>

        {/* Direct Messages Section */}
        <div className="p-4 border-t border-gray-700">
          <h2 className="text-gray-400 text-sm font-semibold mb-2">Direct Messages</h2>
          {users.map(user => (
            <button
              key={user.id}
              onClick={() => handleUserClick(user)}
              className={`w-full text-left p-2 rounded mb-1 ${
                selectedChannelId === `dm-${user.username}` // Use username instead of ID
                  ? 'bg-gray-700 text-white'
                  : 'text-gray-400 hover:bg-gray-700 hover:text-white'
              }`}
            >
              @ {user.username}
            </button>
          ))}
        </div>
      </div>

      <div ref={loader} className="h-4" />
    </div>
  );
};

export default ChannelList; 