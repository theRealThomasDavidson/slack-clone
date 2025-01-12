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
}

const UserList: React.FC<UserListProps> = ({ onUserClick }) => {
  const { token, user: currentUser } = useAuth();
  const [users, setUsers] = React.useState<User[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);

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

  if (isLoading) {
    return (
      <div className="text-center p-4 text-gray-400">
        Loading users...
      </div>
    );
  }

  if (users.length === 0) {
    return (
      <div className="text-center p-4 text-gray-400">
        No other users found
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {users.map((user) => (
        <div
          key={user.id}
          onClick={() => onUserClick(user)}
          className="p-4 flex items-center space-x-3 hover:bg-gray-700 transition-colors cursor-pointer"
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
        </div>
      ))}
    </div>
  );
};

export default UserList; 