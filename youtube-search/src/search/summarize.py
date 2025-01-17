"""
Summarize search results to answer questions about philosophical discussions.
"""
from typing import List, Dict
from collections import defaultdict
import re
from urllib.parse import urlparse, parse_qs
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate

from ..core.interfaces import (
    SearchRequest,
    SearchFilters,
    QuestionResponse,
    SourceSegment
)
from ..core.config import OPENAI_API_KEY, validate_env
from .engine import TranscriptSearch

def extract_video_id(url: str) -> str:
    """Extract video ID from YouTube URL."""
    # Handle both full URLs and video IDs
    if len(url) == 11:
        return url
        
    parsed = urlparse(url)
    if parsed.hostname == 'youtu.be':
        return parsed.path[1:]
    if parsed.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed.path == '/watch':
            return parse_qs(parsed.query)['v'][0]
    return url

SUMMARY_PROMPT = """You are analyzing philosophical discussions and explanations from video transcripts.
Given the following question and relevant transcript segments, provide a clear and thoughtful answer.

Question: {question}

Relevant segments:
{segments}

Please provide:
1. A comprehensive answer to the question based on the philosophical discussions in the segments
2. Key philosophical points and arguments from the segments
3. When referencing ideas from the videos, include the full video title and URL instead of just segment numbers
   For example, instead of "As mentioned in [1]", say "As discussed in 'The Philosophy of Fight Club' (URL)"

Answer:"""

class TranscriptSummarizer:
    def __init__(self):
        """Initialize the summarizer with search and LLM."""
        validate_env()
        
        self.search_client = TranscriptSearch()
        self.llm = ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0
        )
        self.prompt = ChatPromptTemplate.from_template(SUMMARY_PROMPT)
    
    async def answer_question(self, question: str, num_segments: int = 10) -> QuestionResponse:
        """
        Search for relevant segments and summarize them to answer the question.
        
        Args:
            question: The question to answer
            num_segments: Number of relevant segments to consider
            
        Returns:
            QuestionResponse containing the answer and source segments
        """
        # Search for relevant segments
        request = SearchRequest(
            query=question,
            filters=SearchFilters(
                min_score=0.7,
                max_results=num_segments
            )
        )
        
        response = await self.search_client.search(request)
        
        # Group segments by video_id
        video_segments: Dict[str, List[dict]] = defaultdict(list)
        for result in response.results:
            # Extract video ID from URL
            video_id = extract_video_id(result.url)
            timestamp = int(result.start_time)
            video_segments[video_id].append({
                "title": result.title,
                "url": result.url,
                "timestamp": timestamp,
                "text": result.text
            })
        
        # Format segments for the prompt
        segments = []
        source_segments = []
        
        # Process each video's segments
        for video_id, results in video_segments.items():
            # Sort segments by timestamp
            results.sort(key=lambda x: x["timestamp"])
            
            # Collect all text and timestamps
            texts = []
            timestamps = []
            
            for result in results:
                texts.append(result["text"])
                timestamps.append(result["timestamp"])
            
            # Create combined segment for prompt
            title = results[0]["title"]
            base_url = f"https://youtube.com/watch?v={video_id}"
            timestamps_str = ", ".join(f"{t}s" for t in timestamps)
            
            segments.append(
                f"From '{title}' at timestamps [{timestamps_str}]:\n"
                f"{' '.join(texts)}\n"
                f"URL: {base_url}\n"
            )
            
            # Create source segment with combined info
            source_segments.append(
                SourceSegment(
                    title=title,
                    url=base_url,
                    timestamps=timestamps,  # Include all timestamps
                    text=" ".join(texts)  # Combine all text
                )
            )
        
        # Generate summary
        messages = self.prompt.format_messages(
            question=question,
            segments="\n".join(segments)
        )
        
        # Get response
        response = self.llm.invoke(messages)
        
        # Return structured response
        return QuestionResponse(
            answer=response.content,
            question=question,
            source_segments=source_segments
        ) 