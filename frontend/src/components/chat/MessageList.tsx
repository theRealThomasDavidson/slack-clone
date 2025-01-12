import React, { useEffect, useRef, useState } from 'react';
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
}

const MessageList: React.FC<MessageListProps> = ({
  messages,
  channelId,
  onAddReaction,
  onRemoveReaction
}) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [selectedMessage, setSelectedMessage] = useState<MessageData | null>(null);

  useEffect(() => {
    console.log('All Messages:', JSON.stringify(messages, null, 2));
    console.log('Selected Message:', selectedMessage ? JSON.stringify(selectedMessage, null, 2) : 'None');
    console.log('Filtered Messages:', JSON.stringify(
      messages.filter(message => 
        !message.parent_id && 
        (!selectedMessage || message.id !== selectedMessage.id)
      ), 
      null, 
      2
    ));
  }, [messages, selectedMessage]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleReply = (messageId: string) => {
    const message = messages.find(m => m.id === messageId);
    if (message) {
      setSelectedMessage(message);
    }
  };

  return (
    <div className="flex h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages
          .filter(message => 
            !message.parent_id && // Not a reply
            (!selectedMessage || message.id !== selectedMessage.id) // Not the currently selected thread message
          )
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
        ))}
        <div ref={messagesEndRef} />
      </div>

      {selectedMessage && (
        <div className="w-96 border-l border-gray-200">
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