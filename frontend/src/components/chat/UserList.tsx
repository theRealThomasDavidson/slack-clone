import React from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { API_BASE_URL } from '../../contexts/BackendConfig';

interface User {
  id: string;
  username: string;
  is_online?: boolean;
}

const UserList: React.FC = () => {
  const { token } = useAuth();
  const [users, setUsers] = React.useState<User[]>([]);
  const [isLoading, setIsLoading] = React.useState(true);

  React.useEffect(() => {
    const fetchUsers = async () => {
      if (!token) return;
      
      setIsLoading(true);
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
        console.log('Fetched users:', data);
        setUsers(data);
      } catch (err) {
        console.error('Error fetching users:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUsers();
  }, [token]);

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
        No users found
      </div>
    );
  }

  return (
    <div className="space-y-1">
      {users.map((user) => (
        <div
          key={user.id}
          className="p-4 flex items-center space-x-2 hover:bg-gray-700 transition-colors cursor-pointer"
        >
          <div className={`w-2 h-2 rounded-full ${user.is_online ? 'bg-green-500' : 'bg-gray-500'}`} />
          <span className="text-white">{user.username}</span>
        </div>
      ))}
    </div>
  );
};

export default UserList; 