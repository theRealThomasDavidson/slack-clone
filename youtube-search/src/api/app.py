"""
FastAPI application setup.
"""
import logging
import sys
from typing import Dict, Any, List
from fastapi import FastAPI, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from functools import lru_cache
import uvicorn

from ..core.interfaces import SearchRequest, SearchResponse, QuestionRequest, QuestionResponse
from ..search.engine import TranscriptSearch
from ..search.summarize import TranscriptSummarizer

# Configure logging with a cleaner format
logging.basicConfig(
    level=logging.INFO,  # Default to INFO level
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    stream=sys.stdout
)

# Get logger for this module
logger = logging.getLogger("api")

# Configure component loggers
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)  # Reduce noise from uvicorn access logs
logging.getLogger("uvicorn.error").setLevel(logging.ERROR)    # Only show actual errors
logging.getLogger("fastapi").setLevel(logging.INFO)           # Standard FastAPI logs

def format_headers(headers: Dict[str, Any]) -> str:
    """Format headers for pretty printing."""
    return "\n".join(f"    {k}: {v}" for k, v in headers.items())

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only log non-health-check requests at INFO level
        if request.url.path != "/":
            logger.info(f"Request: {request.method} {request.url.path}")
            # Log headers at DEBUG level
            logger.debug(f"Headers:\n{format_headers(dict(request.headers))}")
        
        try:
            response = await call_next(request)
            
            # Log responses for non-200 status codes
            if response.status_code != 200 and request.url.path != "/":
                logger.warning(
                    f"Response: {response.status_code} for {request.method} {request.url.path}"
                )
            return response
        except Exception as e:
            logger.error(
                f"Error processing {request.method} {request.url.path}: {str(e)}", 
                exc_info=True
            )
            raise

# Cache instances to avoid recreating for each request
@lru_cache()
def get_search_client():
    return TranscriptSearch()

@lru_cache()
def get_summarizer():
    return TranscriptSummarizer()

app = FastAPI(
    title="YouTube Transcript Search",
    description="Search through video transcripts semantically",
    version="1.0.0"
)

# Add logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def healthcheck():
    """
    Healthcheck endpoint to verify the API is running.
    """
    return JSONResponse({
        "status": "healthy",
        "service": "YouTube Transcript Search API",
        "version": "1.0.0"
    })

@app.post("/api/search")
async def search(request: SearchRequest, search_client: TranscriptSearch = Depends(get_search_client)) -> SearchResponse:
    """
    Search through video transcripts.
    """
    logger.info(f"Searching for: {request.query}")
    try:
        response = await search_client.search(request)
        logger.info(f"Found {len(response.results)} results for query: {request.query}")
        return response
    except Exception as e:
        logger.error(f"Search failed for query '{request.query}': {str(e)}", exc_info=True)
        raise

@app.get("/api/channels")
async def get_channels(search_client: TranscriptSearch = Depends(get_search_client)) -> List[str]:
    """
    Get list of available channels.
    """
    try:
        channels = await search_client.get_channels()
        logger.info(f"Retrieved {len(channels)} channels")
        return channels
    except Exception as e:
        logger.error("Failed to retrieve channels", exc_info=True)
        raise

@app.post("/api/ask")
async def ask_question(request: QuestionRequest, summarizer: TranscriptSummarizer = Depends(get_summarizer)) -> QuestionResponse:
    """
    Answer questions using the video transcripts.
    """
    logger.info(f"Processing question: {request.question}")
    try:
        response = await summarizer.answer_question(request.question, request.num_segments)
        logger.info("Successfully generated answer")
        return response
    except Exception as e:
        logger.error(f"Failed to answer question: {str(e)}", exc_info=True)
        raise 