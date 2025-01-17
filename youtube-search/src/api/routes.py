"""
API routes for the YouTube transcript search service.
"""
from typing import List, Optional
import time
import logging
from fastapi import Depends, HTTPException, Response
from functools import lru_cache

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from .app import app
from ..core.interfaces import (
    SearchRequest,
    SearchResponse,
    SearchFilters,
    QuestionRequest,
    QuestionResponse,
    SourceSegment,
    MessageSimilarityRequest,
    MessageSearchResponse,
    MessageSearchResult
)
from ..search.engine import TranscriptSearch, MessageSearch
from ..search.summarize import TranscriptSummarizer

# Rate limiting
class RateLimiter:
    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.requests = []
    
    def is_allowed(self) -> bool:
        now = time.time()
        minute_ago = now - 60
        
        # Remove requests older than 1 minute
        self.requests = [req for req in self.requests if req > minute_ago]
        
        if len(self.requests) >= self.requests_per_minute:
            return False
        
        self.requests.append(now)
        return True

rate_limiter = RateLimiter()

# Dependencies
def get_search_client():
    return TranscriptSearch()

def get_message_search():
    return MessageSearch()

def get_summarizer():
    return TranscriptSummarizer()

def check_rate_limit():
    if not rate_limiter.is_allowed():
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again in a minute."
        )

# Log available endpoints on startup
@app.on_event("startup")
async def startup_event():
    logger.info("=== YouTube Search API Starting ===")
    logger.info("Available endpoints:")
    logger.info("  POST /api/search - Search transcripts")
    logger.info("  POST /api/philosophy - Ask philosophical questions")
    logger.info("  POST /api/similar-messages - Find similar messages")
    logger.info("=====================================")

@app.post("/api/search", response_model=SearchResponse)
async def search_transcripts(
    request: SearchRequest,
    search_client: TranscriptSearch = Depends(get_search_client),
    _: None = Depends(check_rate_limit)
) -> SearchResponse:
    """
    Search through video transcripts.
    """
    try:
        return await search_client.search(request)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/api/philosophy", response_model=QuestionResponse)
async def answer_philosophical_question(
    request: QuestionRequest,
    summarizer: TranscriptSummarizer = Depends(get_summarizer),
    _: None = Depends(check_rate_limit)
) -> QuestionResponse:
    """
    Ask philosophical questions about various topics.
    Uses Wisecrack's video essays for philosophical analysis.
    
    Example questions:
    - What is the philosophy behind Fight Club?
    - How does Rick and Morty explore existentialism?
    - What are the philosophical themes in The Matrix?
    """
    try:
        return await summarizer.answer_question(
            question=request.question,
            num_segments=request.num_segments or 15  # Default to more segments
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.post("/api/similar-messages", response_model=MessageSearchResponse)
async def find_similar_messages(
    request: MessageSimilarityRequest,
    message_search: MessageSearch = Depends(get_message_search),
    _: None = Depends(check_rate_limit)
) -> MessageSearchResponse:
    """
    Find messages similar to a sample message.
    Returns ranked results with similarity scores and links to channel locations.
    """
    logger.info(f"Received similar messages request: {request.message}")
    try:
        # Convert MessageSimilarityRequest to SearchRequest
        search_request = SearchRequest(
            query=request.message,
            filters=SearchFilters(
                max_results=request.max_results,
                min_score=request.min_score
            )
        )
        logger.info(f"Searching with request: {search_request}")
        search_response = await message_search.search(search_request)
        logger.info(f"Found {len(search_response.results)} results")
        
        # Convert SearchResponse to MessageSearchResponse
        message_results = []
        for result in search_response.results:
            # Access metadata fields directly since it's a ChunkMetadata object
            message_results.append(MessageSearchResult(
                text=result.text,
                score=result.score,
                channel_id=result.metadata.video_id,  # We store channel_id in video_id field
                username=result.metadata.channel,     # We store username in channel field
                timestamp=result.url.split("?t=")[1] if "?t=" in result.url else "",
                url=result.url
            ))
        
        response = MessageSearchResponse(
            results=message_results,
            total=len(message_results),
            query=request.message
        )
        logger.info(f"Returning response with {len(message_results)} results")
        return response
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/health")
async def health_check():
    """
    Simple health check endpoint.
    """
    logger.info("Health check requested")
    return {"status": "ok"} 