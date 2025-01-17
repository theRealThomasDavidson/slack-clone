"""
Type definitions and interfaces for the YouTube search system.
"""
from typing import List, Dict, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field

# Raw Data Types
class TranscriptSegment(BaseModel):
    text: str = Field(..., description="Transcript text")
    start: float = Field(..., description="Start time in seconds")
    duration: float = Field(..., description="Duration in seconds")

    model_config = {"json_schema_extra": {"examples": [{"text": "Sample transcript text", "start": 0.0, "duration": 5.0}]}}

class VideoTranscript(BaseModel):
    url: str = Field(..., description="YouTube video URL")
    title: str = Field(..., description="Video title")
    channel: str = Field(..., description="Channel name")
    segments: List[TranscriptSegment] = Field(..., description="List of transcript segments")
    total_segments: int = Field(..., description="Total number of segments")
    duration: float = Field(..., description="Total video duration in seconds")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "url": "https://youtube.com/watch?v=example",
                "title": "Sample Video",
                "channel": "Sample Channel",
                "segments": [],
                "total_segments": 0,
                "duration": 0.0
            }]
        }
    }

# Processed Data Types
class ChunkMetadata(BaseModel):
    video_id: str = Field(..., description="YouTube video ID")
    title: str = Field(..., description="Video title")
    channel: str = Field(..., description="Channel name")
    start_time: float = Field(..., description="Start time in seconds")
    end_time: float = Field(..., description="End time in seconds")
    url: str = Field(..., description="YouTube video URL")
    segment_index: int = Field(..., description="Index of the segment")
    total_segments: int = Field(..., description="Total number of segments")
    chunk_size: int = Field(..., description="Size of the chunk in characters")

class ProcessedChunk(BaseModel):
    text: str = Field(..., description="Chunk text")
    metadata: ChunkMetadata = Field(..., description="Chunk metadata")

# Search Types
class SearchResult(BaseModel):
    """Single search result with metadata."""
    url: str = Field(..., description="YouTube video URL with timestamp")
    text: str = Field(..., description="Matching transcript segment")
    score: float = Field(..., ge=0, le=1, description="Similarity score")
    start_time: float = Field(..., ge=0, description="Start time in seconds")
    title: str = Field(..., description="Video title")
    channel: str = Field(..., description="Channel name")
    metadata: ChunkMetadata = Field(..., description="Additional metadata about the chunk")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "url": "https://youtube.com/watch?v=example&t=123",
                "text": "Sample matching text",
                "score": 0.95,
                "start_time": 123.0,
                "title": "Sample Video",
                "channel": "Sample Channel"
            }]
        }
    }

class SearchFilters(BaseModel):
    """Search filters and parameters."""
    min_score: float = Field(0.7, ge=0, le=1, description="Minimum similarity score threshold")
    channel: Optional[str] = Field(None, description="Filter by channel name")
    max_results: int = Field(10, gt=0, description="Maximum number of results to return")
    date_after: Optional[datetime] = Field(None, description="Filter for content after this date")
    date_before: Optional[datetime] = Field(None, description="Filter for content before this date")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "min_score": 0.8,
                "channel": "Wisecrack",
                "max_results": 5
            }]
        }
    }

class SearchResponse(BaseModel):
    """Search response containing results and metadata."""
    results: List[SearchResult] = Field(default_factory=list, description="List of search results")
    total: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original search query")
    filters_applied: SearchFilters = Field(..., description="Filters used in the search")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "results": [],
                "total": 0,
                "query": "sample query",
                "filters_applied": {"min_score": 0.8, "max_results": 5}
            }]
        }
    }

# API Types
class ErrorResponse(BaseModel):
    """API error response."""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    status_code: int = Field(..., description="HTTP status code")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "error": "Not found",
                "detail": "The requested resource was not found",
                "status_code": 404
            }]
        }
    }

class SearchRequest(BaseModel):
    """Search request parameters."""
    query: str = Field(..., description="Search query text")
    filters: Optional[SearchFilters] = Field(None, description="Optional search filters")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "query": "explain the ending of Breaking Bad",
                "filters": {
                    "min_score": 0.8,
                    "channel": "Wisecrack",
                    "max_results": 5
                }
            }
        }
    }

# Cache Types
class CacheKey(BaseModel):
    query: str = Field(..., description="Search query")
    filters: Dict[str, Union[str, int, float, None]] = Field(..., description="Applied filters")

class CacheEntry(BaseModel):
    results: List[SearchResult] = Field(..., description="Cached search results")
    timestamp: datetime = Field(..., description="Cache entry timestamp")
    ttl: int = Field(..., description="Time to live in seconds")

# Question Types
class QuestionRequest(BaseModel):
    """Question answering request."""
    question: str = Field(..., description="The question to answer")
    num_segments: int = Field(10, gt=0, description="Number of transcript segments to consider")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "question": "What does Walter White mean by 'I am the one who knocks'?",
                "num_segments": 15
            }
        }
    }

class SourceSegment(BaseModel):
    """Source segment metadata."""
    title: str = Field(..., description="Video title")
    url: str = Field(..., description="Video URL")
    timestamps: List[int] = Field(..., description="List of timestamps in seconds where content appears")
    text: str = Field(..., description="Combined segment text")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "title": "Sample Video",
                "url": "https://youtube.com/watch?v=example",
                "timestamps": [123, 456, 789],
                "text": "Combined segment text"
            }]
        }
    }

class QuestionResponse(BaseModel):
    """Question answering response."""
    answer: str = Field(..., description="Generated answer with citations")
    question: str = Field(..., description="Original question")
    source_segments: List[SourceSegment] = Field(..., description="Source segments used to generate the answer")

    model_config = {
        "json_schema_extra": {
            "examples": [{
                "answer": "Sample answer with citations",
                "question": "Sample question",
                "source_segments": []
            }]
        }
    }

# Message Types
class MessageSimilarityRequest(BaseModel):
    """Request for finding similar messages."""
    message: str = Field(..., description="The message to find similar messages for")
    max_results: int = Field(10, gt=0, description="Maximum number of results to return")
    min_score: float = Field(0.7, ge=0, le=1, description="Minimum similarity score threshold")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "I am the one who knocks",
                "max_results": 5,
                "min_score": 0.7
            }
        }
    }

class MessageSearchResult(BaseModel):
    """Single message search result with metadata."""
    text: str = Field(..., description="The message content")
    score: float = Field(..., ge=0, le=1, description="Similarity score")
    channel_id: str = Field(..., description="Channel ID")
    username: str = Field(..., description="Username who sent the message")
    timestamp: str = Field(..., description="Message timestamp")
    url: str = Field(..., description="URL to the message in the channel")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "text": "hey guys this weekend i am going to rev up my bacon and go for a stroll are yall in?",
                "score": 0.95,
                "channel_id": "1",
                "username": "alice",
                "timestamp": "2025-01-17T18:01:34.190312",
                "url": "/channels/1?t=2025-01-17T18:01:34.190312"
            }
        }
    }

class MessageSearchResponse(BaseModel):
    """Search response containing message results."""
    results: List[MessageSearchResult] = Field(default_factory=list, description="List of similar messages")
    total: int = Field(..., description="Total number of results")
    query: str = Field(..., description="Original message query")
    
    model_config = {
        "json_schema_extra": {
            "example": {
                "results": [],
                "total": 0,
                "query": "how do you stroll with bacon?"
            }
        }
    }
