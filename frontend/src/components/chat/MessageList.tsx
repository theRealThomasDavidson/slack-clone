import React, { useEffect, useRef } from 'react';
import Message from './Message';

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
}

interface MessageListProps {
  messages: MessageData[];
  channelId: string;
  onAddReaction: (channelId: string, messageId: string, emoji: string) => void;
  onRemoveReaction: (channelId: string, messageId: string, emoji: string) => void;
}

const MessageList: React.FC<MessageListProps> = ({
  messages,
  channelId,
  onAddReaction,
  onRemoveReaction
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="flex-1 overflow-y-auto p-4 space-y-4">
      {messages.map((message) => (
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
          onAddReaction={onAddReaction}
          onRemoveReaction={onRemoveReaction}
        />
      ))}
      <div ref={messagesEndRef} />
    </div>
  );
};

export default MessageList; 