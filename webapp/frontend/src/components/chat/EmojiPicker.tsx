import React, { useEffect, useRef } from 'react';
import data from '@emoji-mart/data';
import Picker from '@emoji-mart/react';

interface EmojiData {
  native: string;
  [key: string]: any;
}

interface EmojiPickerProps {
  onEmojiSelect: (emoji: EmojiData) => void;
  onClickOutside?: () => void;
}

const EmojiPicker: React.FC<EmojiPickerProps> = ({ onEmojiSelect, onClickOutside }) => {
  const pickerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    console.log('EmojiPicker mounted');
    console.log('Emoji data loaded:', !!data);
    
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (pickerRef.current && !pickerRef.current.contains(target)) {
        console.log('Click detected outside emoji picker');
        onClickOutside?.();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [onClickOutside]);

  return (
    <div 
      ref={pickerRef}
      className="fixed inset-0 flex items-center justify-center bg-black/50 z-[1000]" 
      onClick={(e) => e.stopPropagation()}
    >
      <div className="bg-white rounded-lg shadow-lg">
        <Picker
          data={data}
          onEmojiSelect={(emoji: EmojiData) => {
            console.log('Emoji selected from picker:', emoji);
            onEmojiSelect(emoji);
          }}
          theme="light"
          previewPosition="none"
          skinTonePosition="none"
          searchPosition="top"
          navPosition="bottom"
          perLine={8}
          maxFrequentRows={1}
          autoFocus={true}
          onClickOutside={() => {
            console.log('Picker internal click outside');
          }}
        />
      </div>
    </div>
  );
};

export default EmojiPicker; 