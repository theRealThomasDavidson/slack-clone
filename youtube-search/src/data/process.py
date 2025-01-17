"""
Process raw YouTube transcripts into chunks and save them to files.
"""
from typing import List, Dict
import json
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the project root directory (youtube-search)
PROJECT_ROOT = Path(__file__).parent.parent

def get_chunk_text(segments: List[Dict], title: str) -> str:
    """Combine segments into a single text with title."""
    text = f"Title: {title}\n\nTranscript segment: "
    text += " ".join(seg["text"] for seg in segments)
    return text

def split_segments(segments: List[Dict], title: str, max_chars: int = 1000, overlap_segments: int = 2) -> List[List[Dict]]:
    """Split segments into chunks maximizing size while staying under max_chars with overlap between chunks."""
    chunks = []
    current_segments = []
    
    for i in range(len(segments)):
        current_segments.append(segments[i])
        current_text = get_chunk_text(current_segments, title)
        
        # Keep adding segments until we hit max size or run out
        while i + 1 < len(segments):
            next_text = get_chunk_text(current_segments + [segments[i + 1]], title)
            if len(next_text) > max_chars:
                break
            current_segments.append(segments[i + 1])
            i += 1
            current_text = next_text
        
        # If we have enough segments, store the chunk and keep overlap for next one
        if len(current_text) > max_chars * 0.7 or i == len(segments) - 1:
            chunks.append(current_segments)
            
            if i < len(segments) - 1:
                # Keep overlap for next chunk
                current_segments = current_segments[-overlap_segments:]
            else:
                # Clear segments if we're at the end
                current_segments = []
    
    # Handle any remaining segments
    if current_segments:
        # Try to combine with previous chunk if too small
        if chunks and len(get_chunk_text(current_segments, title)) < max_chars * 0.5:
            chunks[-1].extend(current_segments[overlap_segments:])
        else:
            chunks.append(current_segments)
    
    return chunks

def process_transcript_file(file_path: Path) -> List[Dict]:
    """Process a single transcript file into chunks with metadata."""
    with open(file_path, 'r', encoding='utf-8') as f:
        transcript_data = json.load(f)
    
    processed_chunks = []
    total_chars = 0
    min_chunk_size = float('inf')
    max_chunk_size = 0
    chunk_sizes = []
    segments_per_chunk = []  # Track number of segments in each chunk
    overlap_sizes = []       # Track overlap sizes between chunks
    
    video_count = len(transcript_data)
    for idx, (video_id, video_data) in enumerate(transcript_data.items(), 1):
        progress = (idx / video_count) * 100
        print(f"\rProcessing videos: {progress:.1f}%", end="", flush=True)
        title = video_data["title"]
        segments = video_data["segments"]
        chunks = split_segments(segments, title)
        
        # Calculate overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            current_text = get_chunk_text(chunks[i][-2:], title)  # Last 2 segments of current chunk
            next_text = get_chunk_text(chunks[i+1][:2], title)    # First 2 segments of next chunk
            overlap_size = len(current_text)
            overlap_sizes.append(overlap_size)
        
        for i, chunk_segments in enumerate(chunks):
            # Get text for the chunk
            chunk_text = get_chunk_text(chunk_segments, title)
            chunk_size = len(chunk_text)
            total_chars += chunk_size
            min_chunk_size = min(min_chunk_size, chunk_size)
            max_chunk_size = max(max_chunk_size, chunk_size)
            chunk_sizes.append(chunk_size)
            segments_per_chunk.append(len(chunk_segments))
            
            # Create chunk with metadata
            chunk = {
                "text": chunk_text,
                "metadata": {
                    "video_id": video_id,
                    "title": title,
                    "channel": video_data["channel"],
                    "start_time": chunk_segments[0]["start"],
                    "end_time": chunk_segments[-1]["start"] + chunk_segments[-1]["duration"],
                    "url": f"{video_data['url']}&t={int(chunk_segments[0]['start'])}",
                    "segment_index": i + 1,
                    "total_segments": len(chunks),
                    "chunk_size": chunk_size,
                    "segments_count": len(chunk_segments)
                }
            }
            processed_chunks.append(chunk)
    
    # Print newline after processing all videos
    print()
    
    # Calculate statistics
    chunk_sizes.sort()
    segments_per_chunk.sort()
    overlap_sizes.sort()
    
    median_size = chunk_sizes[len(chunk_sizes) // 2]
    p25_size = chunk_sizes[len(chunk_sizes) // 4]
    p75_size = chunk_sizes[3 * len(chunk_sizes) // 4]
    
    median_segments = segments_per_chunk[len(segments_per_chunk) // 2]
    avg_segments = sum(segments_per_chunk) / len(segments_per_chunk)
    
    median_overlap = overlap_sizes[len(overlap_sizes) // 2] if overlap_sizes else 0
    avg_overlap = sum(overlap_sizes) / len(overlap_sizes) if overlap_sizes else 0
    
    # Print chunk statistics
    print(f"\nChunk Statistics:")
    print(f"Total chunks: {len(processed_chunks)}")
    print(f"Average chunk size: {total_chars / len(processed_chunks):.1f} chars")
    print(f"Median chunk size: {median_size} chars")
    print(f"25th percentile: {p25_size} chars")
    print(f"75th percentile: {p75_size} chars")
    print(f"Minimum chunk size: {min_chunk_size} chars")
    print(f"Maximum chunk size: {max_chunk_size} chars")
    print(f"\nSegment Statistics:")
    print(f"Average segments per chunk: {avg_segments:.1f}")
    print(f"Median segments per chunk: {median_segments}")
    print(f"\nOverlap Statistics:")
    print(f"Average overlap size: {avg_overlap:.1f} chars")
    print(f"Median overlap size: {median_overlap} chars")
    
    return processed_chunks

def main():
    """Process all transcript files in data directory."""
    data_dir = PROJECT_ROOT / "data" / "transcripts"
    processed_dir = PROJECT_ROOT / "data" / "processed"
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each transcript file
    for file_path in data_dir.glob("*.json"):
        print(f"Processing transcript file: {file_path.name}")
        chunks = process_transcript_file(file_path)
        
        # Save chunks to processed directory
        output_path = processed_dir / f"processed_{file_path.name}"
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(chunks, f, indent=2, ensure_ascii=False)
        
        # Print final statistics
        print(f"\nGenerated {len(chunks)} chunks")
        print(f"Saved to {output_path.name}")

if __name__ == "__main__":
    main() 