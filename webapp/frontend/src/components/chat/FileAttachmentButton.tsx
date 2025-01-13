import React, { useRef, useState } from 'react';

interface FileAttachmentButtonProps {
  channelId: string;
  onFileSelect: (files: File[]) => void;
  onError: (error: string) => void;
}

const FileAttachmentButton: React.FC<FileAttachmentButtonProps> = ({
  channelId,
  onFileSelect,
  onError
}) => {
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [isHovered, setIsHovered] = useState(false);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(event.target.files || []);
    if (files.length === 0) return;

    // Check if any file exceeds size limit
    const oversizedFiles = files.filter(file => file.size > 10 * 1024 * 1024);
    if (oversizedFiles.length > 0) {
      onError(`Some files exceed the 10MB limit: ${oversizedFiles.map(f => f.name).join(', ')}`);
      return;
    }

    // Check total size of all files
    const totalSize = files.reduce((sum, file) => sum + file.size, 0);
    if (totalSize > 30 * 1024 * 1024) {
      onError('Total size of all files must be less than 30MB');
      return;
    }

    onFileSelect(files);
    
    // Clear the input so the same files can be selected again
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => fileInputRef.current?.click()}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className="p-2 text-gray-500 hover:text-blue-500 hover:bg-gray-100 rounded-lg transition-colors"
        title="Attach files"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M15.172 7l-6.586 6.586a2 2 0 102.828 2.828l6.414-6.586a4 4 0 00-5.656-5.656l-6.415 6.585a6 6 0 108.486 8.486L20.5 13"
          />
        </svg>
      </button>

      {isHovered && (
        <div className="absolute bottom-full left-0 mb-2 px-2 py-1 text-xs text-white bg-gray-800 rounded whitespace-nowrap">
          Attach files (max 10MB each, 30MB total)
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        onChange={handleFileChange}
        className="hidden"
        accept="*/*"
        multiple
      />
    </div>
  );
};

export default FileAttachmentButton; 