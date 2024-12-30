import os
from typing import Dict, List, Optional
from serpapi import GoogleSearch
import logging
from src.config.serp_config import SERP_CONFIG

logger = logging.getLogger(__name__)

class SerpError(Exception):
    """Base exception for SERP client errors."""
    pass

class SerpClient:
    """Client for SERP API with usage tracking and rate limit handling."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SERP_API_KEY")
        if not self.api_key:
            raise ValueError("SERP API key is required")
        
        # Track monthly usage
        self._monthly_searches = 0
        self._monthly_limit = SERP_CONFIG["monthly_limit"]
        
    def _track_search(self) -> None:
        """Track search usage and check limits."""
        self._monthly_searches += 1
        if self._monthly_searches >= self._monthly_limit:
            raise SerpError(f"Monthly search limit reached ({self._monthly_searches}/{self._monthly_limit})")
        logger.info(f"SERP API usage: {self._monthly_searches}/{self._monthly_limit} searches this month")

    async def search(self, query: str, num_results: int = 10) -> List[Dict]:
        """
        Search Google and return structured results.
        
        Args:
            query: Search query string
            num_results: Number of results to return (default 10)
            
        Returns:
            List of dicts containing:
                - title: Result title
                - link: URL
                - snippet: Description snippet
        """
        try:
            self._track_search()
            
            search_params = {
                "q": query,
                "num": num_results,
                "api_key": self.api_key,
                **SERP_CONFIG
            }
            
            search = GoogleSearch(search_params)
            results = search.get_dict()
            
            if "error" in results:
                raise SerpError(f"SERP API error: {results['error']}")
                
            if "organic_results" not in results:
                return []
                
            structured_results = []
            for result in results["organic_results"]:
                structured_results.append({
                    "title": result.get("title"),
                    "link": result.get("link"),
                    "snippet": result.get("snippet")
                })
                
            return structured_results
            
        except Exception as e:
            logger.error(f"SERP search failed: {str(e)}")
            raise SerpError(f"Search failed: {str(e)}") 