import React, { useEffect, useRef, useState, useCallback } from 'react';
import Message from './Message';
import ThreadView from './ThreadView';

interface FileInfo {
  id: string;
  filename: string;
  size: number;
  content_type: string;
}

interface MessageData {
  id: string;
  content: string;
  username: string;
  user_id: string;
  channel_id: string;
  created_at: string;
  emojis: { [key: string]: string[] };
  file: FileInfo | null;
  parent_id: string | null;
  replies_count: number;
}

interface MessageListProps {
  messages: MessageData[];
  channelId: string;
  onAddReaction: (channelId: string, messageId: string, emoji: string) => void;
  onRemoveReaction: (channelId: string, messageId: string, emoji: string) => void;
  onLoadMore?: () => Promise<void>;
  hasMore?: boolean;
}

const MessageList: React.FC<MessageListProps> = ({
  messages,
  channelId,
  onAddReaction,
  onRemoveReaction,
  onLoadMore,
  hasMore = false
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const observerRef = useRef<IntersectionObserver | null>(null);
  const loadingRef = useRef<HTMLDivElement>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [shouldScrollToBottom, setShouldScrollToBottom] = useState(true);
  const [selectedMessage, setSelectedMessage] = useState<MessageData | null>(null);

  const scrollToBottom = () => {
    if (shouldScrollToBottom) {
      messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    }
  };

  // Handle scroll events to determine if we should auto-scroll
  const handleScroll = useCallback((e: Event) => {
    const target = e.target as HTMLDivElement;
    const isNearBottom = target.scrollHeight - target.scrollTop - target.clientHeight < 100;
    setShouldScrollToBottom(isNearBottom);
  }, []);

  // Set up scroll event listener
  useEffect(() => {
    const container = messagesEndRef.current?.parentElement;
    if (container) {
      container.addEventListener('scroll', handleScroll);
      return () => container.removeEventListener('scroll', handleScroll);
    }
  }, [handleScroll]);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Set up intersection observer for infinite scroll
  useEffect(() => {
    if (!onLoadMore || !hasMore) return;

    const handleObserver = async (entries: IntersectionObserverEntry[]) => {
      const [target] = entries;
      if (target.isIntersecting && !isLoading && hasMore) {
        setIsLoading(true);
        await onLoadMore();
        setIsLoading(false);
      }
    };

    const options = {
      root: null,
      rootMargin: '20px',
      threshold: 0.1
    };

    observerRef.current = new IntersectionObserver(handleObserver, options);
    if (loadingRef.current) {
      observerRef.current.observe(loadingRef.current);
    }

    return () => {
      if (observerRef.current) {
        observerRef.current.disconnect();
      }
    };
  }, [onLoadMore, hasMore, isLoading]);

  const handleReply = (messageId: string) => {
    const message = messages.find(m => m.id === messageId);
    if (message) {
      setSelectedMessage(message);
    }
  };

  return (
    <div className="flex h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4 scrollbar-thin scrollbar-thumb-gray-600 scrollbar-track-gray-800">
        {/* Loading indicator at the top */}
        <div ref={loadingRef} className="h-4">
          {isLoading && (
            <div className="text-center text-gray-400 text-sm">
              Loading more messages...
            </div>
          )}
        </div>

        {messages.length === 0 ? (
          <div className="text-center text-gray-400 py-8">
            No messages yet. Start the conversation!
          </div>
        ) : (
          messages
            .filter(message => 
              !message.parent_id && // Not a reply
              (!selectedMessage || message.id !== selectedMessage.id) // Not the currently selected thread message
            )
            .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()) // Sort by timestamp, newest first
            .map((message) => (
              <Message
                key={message.id}
                id={message.id}
                content={message.content}
                username={message.username}
                userId={message.user_id}
                channelId={channelId}
                createdAt={message.created_at}
                emojis={message.emojis}
                file={message.file}
                repliesCount={message.replies_count}
                onAddReaction={onAddReaction}
                onRemoveReaction={onRemoveReaction}
                onReply={handleReply}
              />
            ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {selectedMessage && (
        <div className="w-96 border-l border-gray-700 bg-gray-800">
          <ThreadView
            parentMessage={selectedMessage}
            onClose={() => setSelectedMessage(null)}
          />
        </div>
      )}
    </div>
  );
};

export default MessageList; 