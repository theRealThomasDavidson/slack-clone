"""
FastAPI service for YouTube transcript search.
"""
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import time
from functools import lru_cache
from pydantic import BaseModel

from .interfaces import (
    SearchRequest,
    SearchResponse,
    SearchFilters,
    ErrorResponse
)
from .search import TranscriptSearch
from .summarize import TranscriptSummarizer

# Add new request/response models
class QuestionRequest(BaseModel):
    question: str
    num_segments: Optional[int] = 10
    
    class Config:
        schema_extra = {
            "example": {
                "question": "What are the main themes in Breaking Bad?",
                "num_segments": 10
            }
        }

class QuestionResponse(BaseModel):
    answer: str
    question: str

app = FastAPI(
    title="YouTube Transcript Search",
    description="Search through video transcripts semantically",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
        cached = get_cached_results(request.query, filters_str)
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
    """
    try:
        answer = await summarizer.answer_question(
            question=request.question,
            num_segments=request.num_segments
        )
        
        return QuestionResponse(
            answer=answer,
            question=request.question
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        ) 