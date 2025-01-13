import React, { createContext, useContext } from 'react';
import { useAuth } from './AuthContext';
import { API_BASE_URL } from './BackendConfig';

interface ApiContextType {
  // Messages
  getChannelMessages: (channelId: string) => Promise<any[]>;
  sendMessage: (channelId: string, content: string) => Promise<any>;
  deleteMessage: (messageId: string) => Promise<void>;

  // Channels
  getChannels: () => Promise<any[]>;
  getMyChannels: () => Promise<any[]>;
  createChannel: (name: string, description: string) => Promise<any>;
  joinChannel: (channelId: string) => Promise<void>;
  leaveChannel: (channelId: string) => Promise<void>;

  // Users
  getUsers: () => Promise<any[]>;

  // Files
  uploadFile: (file: File, channelId: string) => Promise<any>;
  downloadFile: (fileId: string) => Promise<Blob>;
  deleteFile: (fileId: string) => Promise<void>;

  // Reactions
  addReaction: (channelId: string, messageId: string, emoji: string) => Promise<Response>;
  removeReaction: (channelId: string, messageId: string, emoji: string) => Promise<Response>;
  getMessageReactions: (channelId: string, messageId: string) => Promise<any[]>;
}

const ApiContext = createContext<ApiContextType | null>(null);

export const useApi = () => {
  const context = useContext(ApiContext);
  if (!context) {
    throw new Error('useApi must be used within an ApiProvider');
  }
  return context;
};

export const ApiProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { token } = useAuth();

  const fetchApi = async (endpoint: string, options: RequestInit = {}) => {
    if (!token) {
      throw new Error('No authentication token available');
    }

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers: {
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => null);
      throw new Error(errorData?.detail || `API error: ${response.status} ${response.statusText}`);
    }

    return response;
  };

  const api: ApiContextType = {
    // Messages
    getChannelMessages: async (channelId) => {
      const response = await fetchApi(`/messages/channel/${channelId}`);
      return response.json();
    },

    sendMessage: async (channelId, content) => {
      const response = await fetchApi('/messages', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ channel_id: channelId, content }),
      });
      return response.json();
    },

    deleteMessage: async (messageId) => {
      await fetchApi(`/messages/${messageId}`, {
        method: 'DELETE',
      });
    },

    // Channels
    getChannels: async () => {
      const response = await fetchApi('/channels');
      return response.json();
    },

    getMyChannels: async () => {
      const response = await fetchApi('/channels/me');
      return response.json();
    },

    createChannel: async (name, description) => {
      const response = await fetchApi('/channels', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, description }),
      });
      return response.json();
    },

    joinChannel: async (channelId) => {
      await fetchApi(`/channels/${channelId}/join`, {
        method: 'POST',
      });
    },

    leaveChannel: async (channelId) => {
      await fetchApi(`/channels/${channelId}/leave`, {
        method: 'POST',
      });
    },

    // Users
    getUsers: async () => {
      const response = await fetchApi('/users');
      return response.json();
    },

    // Files
    uploadFile: async (file, channelId) => {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('channel_id', channelId);

      const response = await fetchApi('/files/upload', {
        method: 'POST',
        body: formData,
      });
      return response.json();
    },

    downloadFile: async (fileId) => {
      const response = await fetchApi(`/files/${fileId}`);
      return response.blob();
    },

    deleteFile: async (fileId) => {
      await fetchApi(`/files/${fileId}`, {
        method: 'DELETE',
      });
    },

    // Reactions
    addReaction: async (channelId: string, messageId: string, emoji: string) => {
      try {
        console.log('Adding reaction:', { channelId, messageId, emoji });
        const response = await fetchApi(`/channels/${channelId}/messages/${messageId}/reactions?emoji=${encodeURIComponent(emoji)}`, {
          method: 'POST'
        });
        console.log('Add reaction response:', response);
        return response;
      } catch (error) {
        console.error('Failed to add reaction:', error);
        throw error;
      }
    },

    removeReaction: async (channelId: string, messageId: string, emoji: string) => {
      try {
        console.log('Removing reaction:', { channelId, messageId, emoji });
        const response = await fetchApi(`/channels/${channelId}/messages/${messageId}/reactions/${encodeURIComponent(emoji)}`, {
          method: 'DELETE'
        });
        console.log('Remove reaction response:', response);
        return response;
      } catch (error) {
        console.error('Failed to remove reaction:', error);
        throw error;
      }
    },

    getMessageReactions: async (channelId: string, messageId: string) => {
      try {
        const response = await fetchApi(`/channels/${channelId}/messages/${messageId}/reactions`);
        return response.json();
      } catch (error) {
        console.error('Failed to get reactions:', error);
        throw error;
      }
    },
  };

  return (
    <ApiContext.Provider value={api}>
      {children}
    </ApiContext.Provider>
  );
};

export default ApiContext; 