"""
Search implementation for YouTube transcripts.
"""
from typing import List, Optional
from langchain_pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings

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

class TranscriptSearch:
    def __init__(self):
        """Initialize the search with Pinecone and OpenAI."""
        validate_env()
        
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Pinecone(
            index_name=PINECONE_INDEX,
            embedding=self.embeddings,
            namespace=PINECONE_NAMESPACE
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
    
    def get_channels(self) -> List[str]:
        """Get list of available channels."""
        return ["Wisecrack"]  # Currently only using Wisecrack videos 