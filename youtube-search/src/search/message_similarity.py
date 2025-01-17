"""
Message similarity search implementation.
"""
from typing import List, Optional
from langchain_pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings

from ..core.interfaces import (
    SearchResult,
    SearchFilters,
    SearchResponse,
    ErrorResponse
)
from ..core.config import (
    OPENAI_API_KEY,
    PINECONE_API_KEY,
    PINECONE_INDEX,
    PINECONE_NAMESPACE,
    validate_env
)

class MessageSimilaritySearch:
    """Search for similar messages using vector similarity."""
    
    def __init__(self):
        validate_env()
        self.embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        self.vector_store = Pinecone.from_existing_index(
            index_name=PINECONE_INDEX,
            embedding=self.embeddings
        )
    
    async def find_similar(self, sample_message: str, k: int = 20) -> SearchResponse:
        """
        Find messages similar to the sample message.
        
        Args:
            sample_message: Message to find similar messages to
            k: Number of results to return (default: 20)
            
        Returns:
            SearchResponse containing similar messages and metadata
        """
        try:
            # Perform vector search
            results = self.vector_store.similarity_search_with_score(
                query=sample_message,
                k=k
            )
            
            # Convert to SearchResult objects
            search_results: List[SearchResult] = []
            for doc, score in results:
                metadata = doc.metadata
                result = SearchResult(
                    url=metadata.get("url", ""),
                    text=doc.page_content,
                    score=float(score),
                    start_time=float(metadata.get("timestamp", 0)),
                    title=metadata.get("channel_id", "Unknown Channel"),
                    channel=metadata.get("username", "Unknown User"),
                    metadata=metadata
                )
                search_results.append(result)
            
            return SearchResponse(
                results=search_results,
                total=len(search_results),
                query=sample_message,
                filters_applied=SearchFilters()
            )
            
        except Exception as e:
            raise ValueError(f"Similar message search failed: {str(e)}") 