import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import { useAuth } from './AuthContext';
import { WS_BASE_URL, API_BASE_URL } from './BackendConfig';

interface Message {
  id: string;
  content: string;
  channel_id: string;  // Only use channel_id format
  username: string;
  user_id: string;
  timestamp: string;
}

interface WebSocketContextType {
  sendMessage: (content: string, channelId: string) => void;
  messages: Record<string, Message[]>;
  isConnected: boolean;
}

const WebSocketContext = createContext<WebSocketContextType | null>(null);

export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  return context;
};

interface QueuedMessage {
  content: string;
  channel_id: string;
  username?: string;
  user_id?: string;
}

export const WebSocketProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, token, isAuthenticated } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [messages, setMessages] = useState<Record<string, Message[]>>({});
  const wsRef = useRef<WebSocket | null>(null);
  const messageQueue = useRef<QueuedMessage[]>([]);
  const isConnecting = useRef(false);
  const retryCount = useRef(0);
  const maxRetries = 3;
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();

  const fetchChannelMessages = async (channelName: string) => {
    if (!token) return;
    
    try {
      // Handle both regular channels and DM channels
      const endpoint = channelName.startsWith('dm-') 
        ? `${API_BASE_URL}/messages/dm/${channelName.slice(3)}` 
        : `${API_BASE_URL}/messages/channel/${channelName}`;

      const response = await fetch(endpoint, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (response.ok) {
        const channelMessages = await response.json();
        setMessages(prev => ({
          ...prev,
          [channelName]: channelMessages
        }));
      }
    } catch (error) {
      console.error('Error fetching channel messages:', error);
    }
  };

  const getReconnectDelay = () => {
    return Math.min(500 * Math.pow(2, retryCount.current), 2000);
  };

  const connectWebSocket = () => {
    if (!user || !token) {
      console.log('❌ No user or token available, skipping WebSocket connection', { user: !!user, token: !!token });
      return;
    }

    if (isConnecting.current) {
      console.log('⏳ Connection attempt already in progress, skipping');
      return;
    }

    if (retryCount.current >= maxRetries) {
      console.log(`🛑 Max retries (${maxRetries}) reached, stopping reconnection attempts`);
      return;
    }

    if (reconnectTimeoutRef.current) {
      console.log('🔄 Clearing existing reconnect timeout');
      clearTimeout(reconnectTimeoutRef.current);
    }

    if (wsRef.current) {
      console.log('🔄 Closing existing WebSocket connection');
      wsRef.current.close();
    }

    isConnecting.current = true;
    const wsUrl = `${WS_BASE_URL}/${user.username}?token=${token}`;
    console.log('🔄 Attempting WebSocket connection:', {
      url: wsUrl,
      username: user.username,
      attempt: retryCount.current + 1,
      maxRetries,
      hasToken: !!token,
      isAuthenticated,
      currentWsState: wsRef.current?.readyState
    });
    
    try {
      const ws = new WebSocket(wsUrl);

      // Log the initial connection state
      console.log('🔵 WebSocket initial state:', {
        readyState: ws.readyState,
        url: wsUrl,
        username: user.username
      });

      ws.onopen = () => {
        console.log('🟢 WebSocket connected successfully');
        setIsConnected(true);
        isConnecting.current = false;
        retryCount.current = 0;
        
        // Send any queued messages
        while (messageQueue.current.length > 0) {
          const message = messageQueue.current.shift();
          if (message) {
            console.log('📤 Sending queued message:', message);
            ws.send(JSON.stringify(message));
          }
        }
      };

      ws.onmessage = async (event) => {
        console.log('Raw WS data received:', event.data);
        try {
          const message: Message = JSON.parse(event.data);
          
          if (message.channel_id) {
            console.log('New message:', message.content);
            // Add the new message to the existing messages
            setMessages(prev => {
              const existingMessages = [...(prev[message.channel_id] || [])];
              
              // Only add if not already present
              if (!existingMessages.find(m => m.id === message.id)) {
                existingMessages.push(message);
                // Sort by timestamp, newest last
                existingMessages.sort((a, b) => 
                  new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
                );
              }
              
              return {
                ...prev,
                [message.channel_id]: existingMessages
              };
            });
          } else {
            console.error('❌ Received message without channel_id:', message);
          }
        } catch (error) {
          console.error('❌ Error parsing WebSocket message:', error);
          console.error('Raw message:', event.data);
        }
      };

      ws.onclose = (event) => {
        const closeInfo = {
          code: event.code,
          reason: event.reason,
          wasClean: event.wasClean,
          timestamp: new Date().toISOString(),
          retryCount: retryCount.current
        };
        console.log('🔴 WebSocket closed:', closeInfo);
        setIsConnected(false);
        isConnecting.current = false;
        
        if (!event.wasClean && 
            event.code !== 1000 && 
            event.code !== 1008 && 
            isAuthenticated && 
            retryCount.current < maxRetries) {
          retryCount.current += 1;
          const delay = getReconnectDelay();
          console.log(`⏳ Scheduling reconnection attempt ${retryCount.current}/${maxRetries} in ${delay}ms`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            if (isAuthenticated) {
              console.log('🔄 Attempting to reconnect...');
              connectWebSocket();
            } else {
              console.log('❌ No longer authenticated, skipping reconnection');
            }
          }, delay);
        } else {
          console.log('❌ Not reconnecting:', {
            reason: event.wasClean ? 'Clean closure' :
                   event.code === 1000 ? 'Normal closure' :
                   event.code === 1008 ? 'Auth failure' :
                   !isAuthenticated ? 'Not authenticated' :
                   retryCount.current >= maxRetries ? 'Max retries exceeded' :
                   'Unknown reason',
            code: event.code,
            wasClean: event.wasClean,
            isAuthenticated,
            retryCount: retryCount.current
          });
        }
      };

      ws.onerror = (error) => {
        console.error('🔴 WebSocket error:', {
          error,
          readyState: ws.readyState,
          url: wsUrl,
          isAuthenticated,
          username: user?.username
        });
        isConnecting.current = false;
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Error creating WebSocket:', error);
      isConnecting.current = false;
    }
  };

  useEffect(() => {
    let mounted = true;

    console.log('🔍 WebSocket connection effect triggered:', {
      mounted,
      isAuthenticated,
      isConnected,
      isConnecting: isConnecting.current,
      retryCount: retryCount.current
    });

    if (mounted && isAuthenticated && !isConnected && !isConnecting.current) {
      console.log('🚀 Initiating WebSocket connection');
      connectWebSocket();
    }

    return () => {
      mounted = false;
      if (wsRef.current) {
        console.log('🧹 Cleaning up WebSocket connection');
        wsRef.current.close(1000, 'Component unmounting');
      }
    };
  }, [isAuthenticated]);

  const sendMessage = (content: string, channelId: string) => {
    const message = {
      content,
      channel_id: channelId,
      username: user?.username,
      user_id: user?.id
    };
    
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(message));
    } else {
      messageQueue.current.push(message);
      if (!isConnected && !isConnecting.current) {
        connectWebSocket();
      }
    }
  };

  const value = {
    sendMessage,
    messages,
    isConnected,
  };

  return (
    <WebSocketContext.Provider value={value}>
      {children}
    </WebSocketContext.Provider>
  );
};

export default WebSocketContext; 