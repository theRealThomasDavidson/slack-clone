"""
Fetch video transcripts from YouTube channels and store them in a structured format.
"""
from youtube_transcript_api import YouTubeTranscriptApi
import os
from typing import List, Dict, Tuple
import json
from googleapiclient.discovery import build
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Required environment variables
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
if not YOUTUBE_API_KEY:
    raise ValueError("YOUTUBE_API_KEY environment variable is required")

# Get the project root directory (youtube-search)
PROJECT_ROOT = Path(__file__).parent.parent

class TranscriptFetcher:
    def __init__(self):
        self.youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        self.transcripts_data = {}  # Store all video data
        
        # Ensure data directory exists inside youtube-search
        self.data_dir = PROJECT_ROOT / "data" / "transcripts"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
    def get_channel_id(self, channel_url: str) -> str:
        """Extract channel ID from custom URL."""
        try:
            if '@' in channel_url:
                username = channel_url.split('@')[1].split('/')[0]
                print(f"Looking up channel ID for username: {username}")
                
                request = self.youtube.channels().list(
                    part="id,snippet",
                    forUsername=username
                )
                response = request.execute()
                
                if 'items' in response and response['items']:
                    channel_id = response['items'][0]['id']
                    print(f"Found channel ID: {channel_id}")
                    return channel_id, response['items'][0]['snippet']['title']
                else:
                    print("No channel found with that username")
                    print("Trying to search for the channel...")
                    search_request = self.youtube.search().list(
                        part="id,snippet",
                        q=username,
                        type="channel",
                        maxResults=1
                    )
                    search_response = search_request.execute()
                    
                    if 'items' in search_response and search_response['items']:
                        channel_id = search_response['items'][0]['id']['channelId']
                        channel_title = search_response['items'][0]['snippet']['title']
                        print(f"Found channel ID through search: {channel_id}")
                        return channel_id, channel_title
                        
            print("Could not find channel ID through any method")
            return None, None
        except Exception as e:
            print(f"Error in get_channel_id: {str(e)}")
            return None, None
            
    def save_transcripts_to_file(self, channel_name: str):
        """Save all processed transcripts to a JSON file."""
        filename = self.data_dir / f"transcripts_{channel_name}_{len(self.transcripts_data)}_videos.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.transcripts_data, f, indent=2, ensure_ascii=False)
        print(f"\nSaved transcript data to {filename}")
        
    def process_channel(self, channel_url: str):
        """Process all videos from a channel."""
        # Get channel info
        channel_id, channel_name = self.get_channel_id(channel_url)
        if not channel_id:
            print("No channel found to process")
            return
            
        # Get all video URLs
        video_urls = self.get_channel_videos(channel_id)
        
        if not video_urls:
            print("No videos found to process")
            return
            
        for i, (video_id, video_title) in enumerate(video_urls):
            if not i%10:
                print(f"Processing videos {100 * i / len(video_urls):.1f}% ({i+1} videos processed) complete", end="\r", flush=True)
            
            video_url = f"https://www.youtube.com/watch?v={video_id}"
            
            # Get transcript
            transcript = self.get_video_transcript(video_url)
            if not transcript:
                continue
                
            # Store the raw transcript segments using video_id as key
            self.transcripts_data[video_id] = {
                "url": video_url,
                "title": video_title,
                "channel": channel_name,
                "segments": transcript,
                "total_segments": len(transcript),
                "duration": transcript[-1]["start"] + transcript[-1]["duration"] if transcript else 0
            }
            print(f"\nVideo {video_id}: {len(transcript)} segments, duration: {self.transcripts_data[video_id]['duration']:.1f}s")
        
        # Save all transcripts to file
        self.save_transcripts_to_file(channel_name)
        print(f"\nProcessing complete - {len(video_urls)} videos processed")
        
    def get_channel_videos(self, channel_id: str) -> List[tuple]:
        """Get all video URLs and titles from a channel using YouTube Data API."""
        print(f"Fetching videos from channel ID: {channel_id}")
        
        video_data = []
        next_page_token = None
        
        while True:
            # Get channel's videos
            request = self.youtube.search().list(
                part="id,snippet",
                channelId=channel_id,
                maxResults=50,  # This is max per page allowed by API
                pageToken=next_page_token,
                type="video",
                order="date"  # Get newest videos first
            )
            
            try:
                response = request.execute()
                
                # Process videos
                for item in response['items']:
                    video_id = item['id']['videoId']
                    video_title = item['snippet']['title']
                    video_data.append((video_id, video_title))
                print(f"Found {len(video_data)} videos", end="\r")
                
                # Check if there are more pages
                next_page_token = response.get('nextPageToken')
                if not next_page_token:  # Only stop if no more pages
                    break
                    
            except Exception as e:
                print(f"Error fetching videos: {str(e)}")
                break
                
        print(f"Found {len(video_data)} videos")
        return video_data
        
    def get_video_transcript(self, video_url: str) -> List[Dict]:
        """Get transcript for a video."""
        try:
            video_id = video_url.split("v=")[1]
            if "&" in video_id:  # Handle additional URL parameters
                video_id = video_id.split("&")[0]
            transcript = YouTubeTranscriptApi.get_transcript(video_id)
            return transcript
        except Exception as e:
            print(f"Error getting transcript for {video_url}: {str(e)}")
            return []

def main():
    """Run the transcript fetcher."""
    fetcher = TranscriptFetcher()
    
    # Example channel URL - replace with your target channel
    channel_url = "https://www.youtube.com/@WisecrackEDU"
    fetcher.process_channel(channel_url)
    
if __name__ == "__main__":
    main() 