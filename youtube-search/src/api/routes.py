"""
API routes for the YouTube transcript search service.
"""
from typing import List, Optional
import time
from fastapi import Depends, HTTPException
from functools import lru_cache

from .app import app
from ..core.interfaces import (
    SearchRequest,
    SearchResponse,
    QuestionRequest,
    QuestionResponse,
    SourceSegment
)
from ..search.engine import TranscriptSearch
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

# Cache results
@lru_cache(maxsize=1000)
def get_cached_results(query: str, filters_str: str) -> Optional[SearchResponse]:
    return None  # TODO: Implement caching

# Dependencies
def get_search_client():
    return TranscriptSearch()

def get_summarizer():
    return TranscriptSummarizer()

def check_rate_limit():
    if not rate_limiter.is_allowed():
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please try again in a minute."
        )

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
        # Check cache
        filters_str = str(request.filters.dict() if request.filters else {})
        cached = get_cached_results(query=request.query, filters_str=filters_str)
        if cached:
            return cached
        
        # Perform search
        response = await search_client.search(request)
        
        # Cache results
        get_cached_results.cache_info()(request.query, filters_str, response)
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

@app.get("/api/channels", response_model=List[str])
def get_channels(
    search_client: TranscriptSearch = Depends(get_search_client)
) -> List[str]:
    """
    Get list of available channels.
    """
    return search_client.get_channels()

@app.post("/api/ask", response_model=QuestionResponse)
async def answer_question(
    request: QuestionRequest,
    summarizer: TranscriptSummarizer = Depends(get_summarizer),
    _: None = Depends(check_rate_limit)
) -> QuestionResponse:
    """
    Answer a question using relevant transcript segments.
    Returns the answer along with source segments used.
    """
    try:
        return await summarizer.answer_question(
            question=request.question,
            num_segments=request.num_segments
        )
        
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
        # Use more segments for philosophical questions to get broader context
        return await summarizer.answer_question(
            question=request.question,
            num_segments=request.num_segments or 15  # Default to more segments
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 