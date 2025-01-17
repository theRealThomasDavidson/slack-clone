"""
Process Breaking Bad scripts to extract dialogue for main characters.
"""
from langchain_community.document_loaders.pdf import PyPDFLoader
import os
from .episode_cast_lists import episode_casts, stage_direction

def get_script_path(filename):
    """Get the full path to a script file."""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'docs', 'Breaking_Bad_Scripts', filename)

def find_next_substring(string, substrings):
    """Generator that yields text before each found substring and the substring that caused the split.

    Args:
        string (str): The string to search in.
        substrings (list or set): The substrings to search for.

    Yields:
        tuple: (text_before, splitting_substring)
               - text_before: Text before the found substring
               - splitting_substring: The substring that was found, or None if at end
    """
    current_pos = 0
    
    while current_pos < len(string):
        min_index = float('inf')
        next_substring = None
        
        # Find the earliest occurring substring from current position
        for substring in substrings:
            index = string.find(substring, current_pos)
            if index != -1 and index < min_index:
                min_index = index
                next_substring = substring
        
        # If no more substrings found, yield remaining text and stop
        if next_substring is None:
            if current_pos < len(string):
                yield string[current_pos:].strip(), None
            break
            
        # Yield text before the substring if there is any
        if min_index > current_pos:
            yield string[current_pos:min_index].strip(), next_substring
            
        # Move position to after the found substring
        current_pos = min_index + len(next_substring)


def get_character_lines(content, episode_info):
    """Extract lines for main characters from the script content."""
    # Create mapping from character names to their character type
    main_characters = {}
    
    # Add Walt's names
    for name in episode_info['character_mappings'].get('walt', ['WALT', "UNDERWEAR MAN"]):
        main_characters[name] = 'walt'
        
    # Add Jesse's names
    for name in episode_info['character_mappings'].get('jesse', ['JESSE']):
        main_characters[name] = 'jesse'
        
    # Add Skyler's names
    for name in ['SKYLER', 'SKYLAR']:
        main_characters[name] = 'skylar'
        
    # Add Hank's names
    main_characters['HANK'] = 'hank'
        
    # Add Saul's names
    for name in ['SAUL', 'SAUL GOODMAN']:
        main_characters[name] = 'saul'

    dialogue = {char_type: [] for char_type in ['walt', 'jesse', 'skylar', 'hank', 'saul']}
    
    current_speaker = None
    
    # Common stage direction indicators
    stage_indicators = [
        'INT.', 'EXT.', 'ANGLE', 'CUT TO', 'FADE', 'CONTINUED', 'HOUSE', 'ROOM', 'DAY', 'NIGHT',
        'CONTINUOUS', 'ON', 'REVEAL', 'VIEW', 'CAMERA', 'CLOSE', 'WIDE', 'BACK TO', 'SCENE',
        'MORNING', 'AFTERNOON', 'EVENING', 'LATER', 'MEANWHILE'
    ]
    
    # Process script using our generator
    for text_before, splitting_substring in find_next_substring(content, episode_info['cast'] + stage_direction):
        text = text_before.strip()
        
        # Skip empty text
        if not text:
            if splitting_substring in main_characters:
                current_speaker = splitting_substring
            continue
            
        # Skip if text looks like stage direction
        if (text.isupper() or 
            any(indicator in text.upper() for indicator in stage_indicators) or
            text.startswith('(') or
            ' - ' in text or
            '--' in text):
            if splitting_substring in main_characters:
                current_speaker = splitting_substring
            continue
            
        # If we have valid dialogue text and a current speaker
        if current_speaker in main_characters:
            # Clean up the line
            line = text.strip()
            if line and not line.isupper():  # One final check that it's not a stage direction
                dialogue[main_characters[current_speaker]].append(line)
            
        # Update speaker if the splitter is a character name
        if splitting_substring in main_characters:
            current_speaker = splitting_substring
        elif splitting_substring in stage_direction:
            # Keep the same speaker if it's just a stage direction
            pass
        else:
            # Reset speaker for any other case
            current_speaker = None
            
    return dialogue

def process_script(filename, episode_info):
    """Process a single script file."""
    # Get absolute path to project root
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    script_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'Breaking_Bad_Scripts')
    file_path = os.path.join(script_dir, filename)
    
    if not os.path.exists(file_path):
        print(f"File not found: {filename}")
        return None
        
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    
    # Combine content from all pages after page 3
    content = "\n".join(page.page_content for page in pages[3:])
    print(f"\nProcessing {len(pages)} pages from {filename}")
    
    return get_character_lines(content, episode_info)

def main():
    """Process all scripts and extract dialogue for main characters."""
    total_lines = {char: 0 for char in ['walt', 'jesse', 'skylar', 'hank', 'saul']}
    
    for filename, info in episode_casts.items():
        print(f"\n{'='*80}")
        print(f"Processing {info['title']}...")
        print(f"{'='*80}")
        
        if not info.get('character_mappings'):
            print("No character mappings found, skipping...")
            continue
            
        dialogue = process_script(filename, info)
        if dialogue:
            # Print episode-specific counts
            print("\nDialogue counts for this episode:")
            print('-' * 40)
            for character, lines in dialogue.items():
                if lines:
                    total_lines[character] += len(lines)
                    print(f"{character.upper()}: {len(lines)} lines")
                    
            # Print sample lines for characters who spoke
            print("\nSample dialogue:")
            print('-' * 40)
            for character, lines in dialogue.items():
                if lines:
                    print(f"\n{character.upper()}:")
                    for i, line in enumerate(lines[:3], 1):
                        print(f"{i}. {line[:100]}..." if len(line) > 100 else f"{i}. {line}")
        else:
            print(f"No dialogue found in {filename}")
    
    # Print total counts across all episodes
    print("\n" + "="*80)
    print("TOTAL DIALOGUE COUNTS ACROSS ALL EPISODES:")
    print("="*80)
    for character, count in total_lines.items():
        print(f"{character.upper()}: {count} lines")

def get_jesse_lines():
    """Extract all of Jesse's lines with episode context for vectorization."""
    jesse_documents = []
    
    for filename, info in episode_casts.items():
        if not info.get('character_mappings'):
            continue
            
        dialogue = process_script(filename, info)
        if dialogue and dialogue['jesse']:
            for line in dialogue['jesse']:
                jesse_documents.append({
                    'text': line,
                    'metadata': {
                        'episode': info['title'],
                        'filename': filename,
                        'character': 'jesse',
                        'type': 'dialogue'
                    }
                })
    
    return jesse_documents

if __name__ == "__main__":
    main()
    print("\nExtracting Jesse's lines for vectorization...")
    jesse_lines = get_jesse_lines()
    print(f"Found {len(jesse_lines)} lines from Jesse")
    print("\nSample entries:")
    for doc in jesse_lines[:3]:
        print(f"\nEpisode: {doc['metadata']['episode']}")
        print(f"Line: {doc['text']}") 