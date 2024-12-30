"""
Exa API client for semantic web search.
"""
import os
from typing import Dict, List, Optional, Any
from exa_py import Exa
import logging

logger = logging.getLogger(__name__)

class ExaError(Exception):
    """Base exception for Exa client errors."""
    pass

class ExaClient:
    """Client for Exa API with usage tracking."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Exa client.
        
        Args:
            api_key: Exa API key (optional, will use EXA_API_KEY env var if not provided)
        """
        self.api_key = api_key
        if not self.api_key:
            self.api_key = os.getenv("EXA_API_KEY")
            if not self.api_key:
                raise ValueError("Exa API key is required")
            
        self.client = Exa(self.api_key)
        self._search_count = 0
        
    async def search(
        self,
        query: str,
        *,
        num_results: int = 10,
        use_autoprompt: bool = True,
        search_type: str = "neural",
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        start_published_date: Optional[str] = None,
        end_published_date: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search and return results.
        
        Args:
            query: Search query string
            num_results: Number of results to return
            use_autoprompt: Whether to use Exa's query enhancement
            search_type: Type of search ("neural" or "keyword")
            include_domains: List of domains to include
            exclude_domains: List of domains to exclude
            start_date: Start date for crawled content
            end_date: End date for crawled content
            start_published_date: Start date for published content
            end_published_date: End date for published content
            
        Returns:
            List of search results with metadata
        """
        try:
            if not query.strip():
                raise ExaError("Search query cannot be empty")
                
            self._search_count += 1
            logger.info(f"Performing Exa search ({self._search_count}): {query}")
            
            # Get search results with contents
            response = self.client.search_and_contents(
                query,
                num_results=num_results,
                use_autoprompt=use_autoprompt,
                type=search_type,
                include_domains=include_domains,
                exclude_domains=exclude_domains,
                start_crawl_date=start_date,
                end_crawl_date=end_date,
                start_published_date=start_published_date,
                end_published_date=end_published_date,
                text=True,
                highlights=True
            )
            
            # Process results
            results = []
            for result in response.results:
                results.append({
                    "title": result.title,
                    "url": result.url,
                    "text": result.text if hasattr(result, "text") else None,
                    "highlights": result.highlights if hasattr(result, "highlights") else [],
                    "published_date": getattr(result, "published_date", None),
                    "author": getattr(result, "author", None)
                })
            
            logger.debug(f"Got {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Exa search failed: {str(e)}")
            raise ExaError(f"Search failed: {str(e)}")
            
    @property
    def usage_stats(self) -> Dict[str, int]:
        """Get current usage statistics."""
        return {
            "searches": self._search_count
        } 