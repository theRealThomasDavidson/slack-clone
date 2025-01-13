import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { API_BASE_URL } from '../../contexts/BackendConfig';

interface User {
  id: string;
  username: string;
  online_status: boolean;
}

interface UserListProps {
  onUserClick: (user: User) => void;
  activeDmUserId?: string;
}

const UserList: React.FC<UserListProps> = ({ onUserClick, activeDmUserId }) => {
  const { token, user: currentUser } = useAuth();
  const [users, setUsers] = React.useState<User[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);
  const [searchQuery, setSearchQuery] = React.useState('');

  const fetchUsers = async () => {
    if (!token) return;
    
    try {
      const response = await fetch(`${API_BASE_URL}/users`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (!response.ok) {
        throw new Error('Failed to fetch users');
      }
      
      const data = await response.json();
      // Filter out the current user
      const otherUsers = data.filter((user: User) => user.username !== currentUser?.username);
      setUsers(otherUsers);
    } catch (err) {
      console.error('Error fetching users:', err);
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    fetchUsers();
    // Poll for user presence every 5 seconds
    const interval = setInterval(fetchUsers, 5000);
    return () => clearInterval(interval);
  }, [token, currentUser?.username]);

  // Filter users based on search query
  const filteredUsers = React.useMemo(() => {
    if (!searchQuery) return users;
    const lowerQuery = searchQuery.toLowerCase();
    return users.filter(user => 
      user.username.toLowerCase().includes(lowerQuery)
    );
  }, [users, searchQuery]);

  // Sort users: active DM first, then online users, then offline users
  const sortedUsers = React.useMemo(() => {
    return [...filteredUsers].sort((a, b) => {
      // Active DM user comes first
      if (a.id === activeDmUserId) return -1;
      if (b.id === activeDmUserId) return 1;
      // Then sort by online status
      if (a.online_status && !b.online_status) return -1;
      if (!a.online_status && b.online_status) return 1;
      // Finally sort by username
      return a.username.localeCompare(b.username);
    });
  }, [filteredUsers, activeDmUserId]);

  if (isLoading) {
    return (
      <div className="text-center p-4 text-gray-400">
        Loading users...
      </div>
    );
  }

  return (
    <div className="flex flex-col h-full">
      {/* Search bar */}
      <div className="p-4 border-b border-gray-700">
        <input
          type="text"
          placeholder="Search users..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-3 py-2 bg-gray-700 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* User list */}
      <div className="flex-1 overflow-y-auto">
        {sortedUsers.length === 0 ? (
          <div className="text-center p-4 text-gray-400">
            {searchQuery ? 'No users found' : 'No other users'}
          </div>
        ) : (
          <div className="space-y-1">
            {sortedUsers.map((user) => (
              <div
                key={user.id}
                onClick={() => onUserClick(user)}
                className={`p-4 flex items-center space-x-3 hover:bg-gray-700 transition-colors cursor-pointer ${
                  user.id === activeDmUserId ? 'bg-gray-700' : ''
                }`}
              >
                <div className="relative">
                  <div 
                    className={`w-3 h-3 rounded-full ${
                      user.online_status 
                        ? 'bg-green-500 animate-pulse' 
                        : 'bg-red-500'
                    } transition-colors duration-300 shadow-lg`} 
                    title={user.online_status ? 'Online' : 'Offline'}
                  />
                  {user.online_status && (
                    <div 
                      className="absolute inset-0 w-3 h-3 rounded-full bg-green-500 animate-ping opacity-75"
                    />
                  )}
                </div>
                <span className={`${
                  user.online_status 
                    ? 'text-green-500' 
                    : 'text-red-500'
                } transition-colors duration-300`}>
                  @{user.username}
                </span>
                {user.id === activeDmUserId && (
                  <span className="ml-auto text-sm text-blue-400">Active Chat</span>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default UserList; 