import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

interface YouTubeSearchResponse {
  answer: string;
  question: string;
  source_segments: Array<{
    title: string;
    url: string;
    timestamps: number[];
    text: string;
  }>;
}

interface QuestionRequest {
  question: string;
  num_segments?: number;
}

// Helper function to extract video ID and timestamp from YouTube URL
const getYouTubeInfo = (url: string, timestamp: number = 0) => {
  const videoIdMatch = url.match(/(?:youtu\.be\/|youtube\.com\/(?:embed\/|v\/|watch\?v=|watch\?.+&v=))([^"&?\/\s]{11})/);
  const videoId = videoIdMatch ? videoIdMatch[1] : null;
  return {
    videoId,
    embedUrl: videoId ? `https://www.youtube.com/embed/${videoId}?start=${Math.floor(timestamp)}` : null
  };
};

const API_URL = 'http://ec2-18-119-162-96.us-east-2.compute.amazonaws.com:8001/api';

const YouTubeSearch: React.FC = () => {
  const navigate = useNavigate();

  // Initialize state from localStorage
  const [question, setQuestion] = useState(() => {
    const savedState = localStorage.getItem('youtube_search_state');
    if (savedState) {
      const state = JSON.parse(savedState);
      return state.question || '';
    }
    return '';
  });

  const [response, setResponse] = useState<YouTubeSearchResponse | null>(() => {
    const savedState = localStorage.getItem('youtube_search_state');
    if (savedState) {
      const state = JSON.parse(savedState);
      return state.response || null;
    }
    return null;
  });

  // Clear youtube_search_state after loading
  useEffect(() => {
    localStorage.removeItem('youtube_search_state');
  }, []);

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  // Save state to localStorage when it changes
  useEffect(() => {
    localStorage.setItem('youtube_search_question', question);
  }, [question]);

  useEffect(() => {
    if (response) {
      localStorage.setItem('youtube_search_response', JSON.stringify(response));
    }
  }, [response]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    const request: QuestionRequest = {
      question,
      num_segments: 15
    };

    try {
      console.log('Starting request...');
      const startTime = Date.now();
      
      const res = await fetch(`${API_URL}/ask`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Connection': 'keep-alive',
        },
        body: JSON.stringify(request),
        mode: 'cors',
        credentials: 'omit',
        keepalive: true,
      });

      const endTime = Date.now();
      console.log(`Request completed in ${(endTime - startTime) / 1000} seconds`);

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      setResponse(data);
    } catch (err: any) {
      console.error('Error details:', err);
      setError('Failed to get answer. Please try again. Error: ' + err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-800 text-gray-100">
      <div className="max-w-4xl mx-auto p-6">
        <div className="flex items-center gap-4 mb-6">
          <h1 className="text-2xl font-bold text-gray-100">YouTube Transcript Search</h1>
          <button
            onClick={() => {
              localStorage.setItem('youtube_search_state', JSON.stringify({
                question,
                response,
                lastVisited: new Date().toISOString()
              }));
              navigate('/chat');
            }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 16.707a1 1 0 01-1.414 0l-6-6a1 1 0 010-1.414l6-6a1 1 0 011.414 1.414L5.414 9H17a1 1 0 110 2H5.414l4.293 4.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            Back to Chat
          </button>
        </div>

        <form onSubmit={handleSubmit} className="mb-8">
          <div className="flex flex-col gap-4">
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Ask a question about any topic..."
              className="w-full p-3 bg-gray-700 text-gray-100 border border-gray-600 rounded resize-y min-h-[100px] placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
              required
            />
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 self-end transition-colors duration-200"
            >
              {loading ? 'Analyzing transcripts...' : 'Ask'}
            </button>
          </div>
        </form>

        {loading && (
          <div className="text-center py-8">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto mb-4"></div>
            <p className="text-gray-300">Analyzing video transcripts and formulating an answer...</p>
            <p className="text-sm text-gray-400 mt-2">This may take a minute</p>
          </div>
        )}

        {error && (
          <div className="text-red-400 mb-4 bg-red-900/50 p-3 rounded">{error}</div>
        )}

        {response && (
          <div className="space-y-6">
            <div>
              <h2 className="font-semibold mb-2 text-gray-100">Q: {response.question}</h2>
              <div className="whitespace-pre-wrap text-gray-300">{response.answer}</div>
            </div>

            <div>
              <h3 className="font-semibold mb-4 text-gray-100">Sources:</h3>
              <div className="space-y-6">
                {response.source_segments.map((segment, index) => {
                  const { embedUrl } = getYouTubeInfo(segment.url, segment.timestamps[0]);
                  return (
                    <div key={index} className="border border-gray-600 rounded-lg overflow-hidden bg-gray-700 shadow-lg">
                      {embedUrl && (
                        <div className="relative pb-[56.25%] h-0">
                          <iframe
                            src={embedUrl}
                            className="absolute top-0 left-0 w-full h-full"
                            title={segment.title}
                            frameBorder="0"
                            allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                            allowFullScreen
                          />
                        </div>
                      )}
                      <div className="p-4">
                        <h4 className="font-semibold text-lg mb-2 text-gray-100">{segment.title}</h4>
                        <div className="text-sm text-gray-400">
                          Jump to: {segment.timestamps.map(t => {
                            const minutes = Math.floor(t / 60);
                            const seconds = Math.floor(t % 60);
                            return `${minutes}:${seconds.toString().padStart(2, '0')}`;
                          }).join(', ')}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default YouTubeSearch;
