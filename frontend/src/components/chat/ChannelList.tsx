import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';

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
  // Mock channels for development
  const [channels] = useState<Channel[]>([
    {
      id: 'general',
      name: 'General',
      description: 'General discussion channel',
      owner_id: 'system',
      members: ['system']
    },
    {
      id: 'random',
      name: 'Random',
      description: 'Random discussions',
      owner_id: 'system',
      members: ['system']
    }
  ]);

  const [showCreateChannel, setShowCreateChannel] = useState(false);
  const [newChannelName, setNewChannelName] = useState('');

  const handleCreateChannel = (e: React.FormEvent) => {
    e.preventDefault();
    // In a real app, this would make an API call
    console.log('Creating channel:', newChannelName);
    setShowCreateChannel(false);
    setNewChannelName('');
  };

  return (
    <div className="h-full flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h2 className="text-lg font-semibold text-white mb-4">Channels</h2>
        <button
          onClick={() => setShowCreateChannel(true)}
          className="w-full py-2 px-4 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
        >
          Create Channel
        </button>
      </div>

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