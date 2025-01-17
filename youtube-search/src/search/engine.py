"""
Search implementation for YouTube transcripts and messages.
"""
from typing import List, Optional
import logging
from langchain_pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from ..core.interfaces import (
    SearchResult,
    SearchFilters,
    SearchResponse,
    ErrorResponse,
    SearchRequest,
    ChunkMetadata
)
from ..core.config import (
    OPENAI_API_KEY,
    PINECONE_API_KEY,
    PINECONE_INDEX,
    PINECONE_NAMESPACE,
    validate_env
)

class BaseSearch:
    """Base class for search functionality."""
    
    def __init__(self):
        """Initialize the search with Pinecone and OpenAI."""
        validate_env()
        
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Pinecone(
            index_name=PINECONE_INDEX,
            embedding=self.embeddings,
            namespace=PINECONE_NAMESPACE
        )

class TranscriptSearch(BaseSearch):
    """Search implementation for YouTube transcripts."""
    
    def __init__(self):
        """Initialize the search with Pinecone and OpenAI."""
        validate_env()
        
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Pinecone(
            index_name=PINECONE_INDEX,
            embedding=self.embeddings,
            namespace="youtube_transcripts"  # Specific namespace for YouTube transcripts
        )

    async def search(
        self,
        request: SearchRequest
    ) -> SearchResponse:
        """
        Search for relevant transcript chunks.
        
        Args:
            request: SearchRequest containing query and optional filters
        
        Returns:
            SearchResponse with results and metadata
        """
        try:
            filters = request.filters or SearchFilters()
            
            # Perform vector search
            results = self.vector_store.similarity_search_with_score(
                query=request.query,
                k=filters.max_results
            )
            
            # Convert to SearchResult objects
            search_results: List[SearchResult] = []
            for doc, score in results:
                if score >= filters.min_score:
                    # Extract metadata with defaults
                    metadata = doc.metadata
                    
                    # Create metadata object
                    chunk_metadata = ChunkMetadata(
                        video_id=metadata.get("video_id", "unknown"),
                        title=metadata.get("title", "Unknown Video"),
                        channel=metadata.get("channel", "Unknown Channel"),
                        start_time=float(metadata.get("start_time", 0)),
                        end_time=float(metadata.get("end_time", 0)),
                        url=metadata.get("url", "https://www.youtube.com/watch?v=unknown"),
                        segment_index=int(metadata.get("segment_index", 0)),
                        total_segments=int(metadata.get("total_segments", 1)),
                        chunk_size=len(doc.page_content)
                    )
                    
                    result = SearchResult(
                        url=chunk_metadata.url,
                        text=doc.page_content,
                        score=float(score),
                        start_time=chunk_metadata.start_time,
                        title=chunk_metadata.title,
                        channel=chunk_metadata.channel,
                        metadata=chunk_metadata
                    )
                    
                    # Apply channel filter if specified
                    if filters.channel and result.channel != filters.channel:
                        continue
                    
                    search_results.append(result)
            
            return SearchResponse(
                results=search_results,
                total=len(search_results),
                query=request.query,
                filters_applied=filters
            )
            
        except Exception as e:
            raise ValueError(f"Search failed: {str(e)}")

class MessageSearch(BaseSearch):
    """Search implementation for chat messages."""
    
    def __init__(self):
        """Initialize the search with Pinecone and OpenAI."""
        logger.info("Initializing MessageSearch")
        validate_env()
        
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Pinecone(
            index_name=PINECONE_INDEX,
            embedding=self.embeddings,
            namespace="chat-messages"  # Specific namespace for chat messages
        )
        logger.info(f"MessageSearch initialized with index {PINECONE_INDEX} and namespace chat-messages")

    async def search(
        self,
        request: SearchRequest
    ) -> SearchResponse:
        """
        Search for similar messages.
        
        Args:
            request: SearchRequest containing query and optional filters
        
        Returns:
            SearchResponse with results and metadata
        """
        try:
            logger.info(f"Searching for messages similar to: {request.query}")
            filters = request.filters or SearchFilters()
            
            # Perform vector search
            logger.info(f"Performing vector search with k={filters.max_results}")
            results = self.vector_store.similarity_search_with_score(
                query=request.query,
                k=filters.max_results
            )
            logger.info(f"Vector search returned {len(results)} results")
            
            # Convert to SearchResult objects
            search_results: List[SearchResult] = []
            for doc, score in results:
                if score >= filters.min_score:
                    metadata = doc.metadata
                    # Create a dummy metadata object that matches the expected structure
                    chunk_metadata = ChunkMetadata(
                        video_id=str(metadata.get("channel_id", "unknown")),
                        title=metadata.get("username", "Unknown User"),
                        channel=metadata.get("username", "Unknown User"),
                        start_time=0.0,  # Use 0.0 since we don't need this for messages
                        end_time=0.0,    # Use 0.0 since we don't need this for messages
                        url=f"/channels/{metadata.get('channel_id', 'unknown')}",
                        segment_index=0,  # Not relevant for messages
                        total_segments=1, # Not relevant for messages
                        chunk_size=len(doc.page_content)
                    )
                    
                    result = SearchResult(
                        url=f"/channels/{metadata.get('channel_id', 'unknown')}?t={metadata.get('timestamp', '')}",
                        text=doc.page_content,
                        score=float(score),
                        start_time=0.0,  # Use 0.0 since we don't need this for messages
                        title=metadata.get("username", "Unknown User"),
                        channel=metadata.get("username", "Unknown User"),
                        metadata=chunk_metadata
                    )
                    
                    # Apply channel filter if specified
                    if filters.channel and result.channel != filters.channel:
                        continue
                    
                    search_results.append(result)
            
            logger.info(f"Returning {len(search_results)} filtered results")
            return SearchResponse(
                results=search_results,
                total=len(search_results),
                query=request.query,
                filters_applied=filters
            )
            
        except Exception as e:
            logger.error(f"Message search failed: {str(e)}")
            raise ValueError(f"Message search failed: {str(e)}")

    def get_channels(self) -> List[str]:
        """Get list of available channels."""
        return ["Wisecrack"]  # Currently only using Wisecrack videos 