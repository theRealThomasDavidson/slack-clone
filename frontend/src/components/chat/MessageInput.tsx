import React, { useState, KeyboardEvent } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { API_BASE_URL } from '../../contexts/BackendConfig';
import FileAttachmentButton from './FileAttachmentButton';

interface MessageInputProps {
  channelId?: string;
  parentId?: string;
  onMessageSent?: () => void;
  placeholder?: string;
}

interface FileUploadProgress {
  file: File;
  progress: number;
}

const MessageInput: React.FC<MessageInputProps> = ({ 
  channelId, 
  parentId,
  onMessageSent,
  placeholder = "Type a message..."
}) => {
  const [message, setMessage] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [selectedFiles, setSelectedFiles] = useState<File[]>([]);
  const [uploadProgress, setUploadProgress] = useState<FileUploadProgress[]>([]);
  const { token } = useAuth();

  const formatFileSize = (bytes: number): string => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const handleFileSelect = (files: File[]) => {
    setSelectedFiles(files);
    setError(null);
    setUploadProgress(files.map(file => ({ file, progress: 0 })));
  };

  const uploadFile = async (file: File): Promise<void> => {
    const formData = new FormData();
    formData.append('file', file);

    return new Promise((resolve, reject) => {
      const xhr = new XMLHttpRequest();

      xhr.upload.addEventListener('progress', (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100);
          setUploadProgress(prev => 
            prev.map(p => p.file === file ? { ...p, progress } : p)
          );
        }
      });

      xhr.onload = () => {
        if (xhr.status === 200) {
          resolve();
        } else {
          reject(new Error(`Upload failed: ${xhr.status} ${xhr.statusText}`));
        }
      };

      xhr.onerror = () => reject(new Error('Upload failed'));

      xhr.open('POST', `${API_BASE_URL}/files/upload`);
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
      xhr.send(formData);
    });
  };

  const handleSend = async () => {
    if ((message.trim() || selectedFiles.length > 0) && !isSending) {
      setIsSending(true);
      setError(null);
      try {
        // Create FormData and append message content and IDs
        const formData = new FormData();
        formData.append('content', message.trim());
        if (channelId) formData.append('channel_id', channelId);
        if (parentId) formData.append('parent_id', parentId);

        // If there are files, append the first one
        if (selectedFiles.length > 0) {
          formData.append('file', selectedFiles[0]);
        }

        // Send message with optional file
        const response = await fetch(`${API_BASE_URL}/messages/`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => null);
          throw new Error(
            errorData?.detail || `API error: ${response.status} ${response.statusText}`
          );
        }

        // Clear form after successful send
        setMessage('');
        setSelectedFiles([]);
        setUploadProgress([]);
        onMessageSent?.();
      } catch (error) {
        console.error('Error sending message:', error);
        setError(error instanceof Error ? error.message : 'Failed to send message');
      } finally {
        setIsSending(false);
      }
    }
  };

  const handleKeyPress = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="border-t border-gray-200 p-4">
      <div className="flex items-end space-x-2">
        <div className="flex items-center space-x-2">
          <FileAttachmentButton
            channelId={channelId || 'thread'}
            onFileSelect={handleFileSelect}
            onError={setError}
          />
          {selectedFiles.length > 0 && (
            <div className="flex flex-col space-y-1 text-sm text-gray-600">
              {selectedFiles.map((file, index) => {
                const progress = uploadProgress.find(p => p.file === file)?.progress || 0;
                return (
                  <div key={index} className="flex items-center space-x-2">
                    <span>
                      {file.name} ({formatFileSize(file.size)})
                      {progress > 0 && progress < 100 && ` - ${progress}%`}
                    </span>
                    <button
                      onClick={() => {
                        setSelectedFiles(prev => prev.filter(f => f !== file));
                        setUploadProgress(prev => prev.filter(p => p.file !== file));
                      }}
                      className="text-gray-500 hover:text-red-500"
                      title="Remove file"
                    >
                      ✕
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={placeholder}
          className="flex-1 resize-none rounded-lg border border-gray-300 p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
          rows={1}
          disabled={isSending}
        />
        <button
          onClick={handleSend}
          disabled={(!message.trim() && selectedFiles.length === 0) || isSending}
          className={`px-4 py-2 rounded-lg ${
            (message.trim() || selectedFiles.length > 0) && !isSending
              ? 'bg-blue-500 text-white hover:bg-blue-600'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
          }`}
        >
          {isSending ? 'Sending...' : 'Send'}
        </button>
      </div>
      {error && (
        <p className="text-red-500 text-sm mt-2">
          {error}
        </p>
      )}
    </div>
  );
};

export default MessageInput; 