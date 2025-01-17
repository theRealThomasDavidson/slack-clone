import React, { useState, useRef, useEffect } from 'react';
import { API_BASE_URL } from '../../contexts/BackendConfig';
import { useAuth } from '../../contexts/AuthContext';

interface SearchResult {
  text: string;
  score: number;
  channel_id: string;
  username: string;
  timestamp: string;
  url: string;
}

interface MessageSearchProps {
  onClose?: () => void;
  className?: string;
  onSelectMessage?: (channelId: string, messageTimestamp: string) => void;
}

const MessageSearch: React.FC<MessageSearchProps> = ({ onClose, className = '', onSelectMessage }) => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const { token } = useAuth();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        if (!loading) {
          setError(null);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [loading]);

  const handleSearch = async () => {
    if (!query.trim()) return;
    
    setLoading(true);
    setError(null);
    setResults([]);

    try {
      const response = await fetch(`${API_BASE_URL}/api/similar-messages`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message: query,
          k: 10,
          min_score: 0.7
        }),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => null);
        throw new Error(errorData?.detail || 'Search failed');
      }

      const data = await response.json();
      setResults(data.results);
    } catch (error) {
      console.error('Search error:', error);
      setError('Failed to search messages. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResultClick = (result: SearchResult) => {
    if (onSelectMessage) {
      onSelectMessage(result.channel_id, result.timestamp);
      if (onClose) {
        onClose();
      }
    }
  };

  const showDropdown = loading || results.length > 0 || error !== null;

  return (
    <div className={`relative ${className}`}>
      <div className="flex items-center gap-4">
        <div className="flex-1">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
            placeholder="Search for similar messages..."
            className="w-full px-4 py-2 bg-gray-800 text-white rounded-lg border border-gray-700 focus:outline-none focus:border-blue-500"
          />
        </div>
        <button
          onClick={handleSearch}
          disabled={loading}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none disabled:opacity-50"
        >
          {loading ? 'Searching...' : 'Search'}
        </button>
        {onClose && (
          <button
            onClick={onClose}
            className="p-2 text-gray-400 hover:text-white focus:outline-none"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        )}
      </div>

      {/* Dropdown Results */}
      {showDropdown && (
        <div 
          ref={dropdownRef}
          className="absolute z-50 mt-2 w-full bg-gray-800 border border-gray-700 rounded-lg shadow-lg max-h-96 overflow-y-auto"
        >
          {loading && (
            <div className="p-6 text-center text-gray-400">
              <div className="inline-block animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500 mb-2"></div>
              <div>Searching for similar messages...</div>
            </div>
          )}

          {error && (
            <div className="p-4 text-center text-red-400">
              {error}
            </div>
          )}

          {!loading && !error && results.length === 0 && (
            <div className="p-4 text-center text-gray-400">
              No similar messages found
            </div>
          )}

          {!loading && !error && results.length > 0 && (
            <div className="py-2">
              {results.map((result, index) => (
                <div
                  key={index}
                  onClick={() => handleResultClick(result)}
                  className="px-4 py-3 hover:bg-gray-700 cursor-pointer border-b border-gray-700 last:border-b-0"
                >
                  <div className="flex justify-between items-start mb-1">
                    <span className="text-sm font-medium text-blue-400">{result.username}</span>
                    <span className="text-xs text-gray-500">{new Date(result.timestamp).toLocaleString()}</span>
                  </div>
                  <p className="text-white text-sm mb-2">{result.text}</p>
                  <div className="flex justify-between items-center">
                    <span className="text-xs text-gray-400">Score: {(result.score * 100).toFixed(1)}%</span>
                    <span className="text-sm text-blue-400">
                      View message →
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default MessageSearch; 