"""
Tool for searching the web using SERP API
"""
import os
import time
import logging
from typing import Dict, Any
import requests

logger = logging.getLogger(__name__)

def search_web(query: str, num_results: int = 5) -> Dict[str, Any]:
    """
    Search the web using SERP API
    
    Args:
        query: Search query string
        num_results: Number of results to return (default 5)
        
    Returns:
        Dict containing search results and usage metrics
    """
    start_time = time.time()
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        raise ValueError("SERP_API_KEY environment variable not set")
        
    url = "https://serpapi.com/search"
    params = {
        "api_key": api_key,
        "q": query,
        "num": num_results,
        "engine": "google"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        
        # Extract organic results
        results = []
        if "organic_results" in data:
            for result in data["organic_results"][:num_results]:
                results.append({
                    "title": result.get("title", ""),
                    "link": result.get("link", ""),
                    "snippet": result.get("snippet", "")
                })
        
        # Track usage metrics
        usage = {
            "queries": 1,
            "query_length": len(query),
            "results_returned": len(results),
            "latency_seconds": time.time() - start_time,
            # TODO: Implement result content tracking
            # "total_snippet_length": sum(len(r.get("snippet", "")) for r in results),
            # TODO: Implement token tracking
            # "query_tokens": count_tokens(query)
        }
                
        return {
            "status": "success",
            "results": results,
            "usage": usage
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"SERP API request failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "results": [],
            "usage": {
                "queries": 1,
                "query_length": len(query),
                "results_returned": 0,
                "latency_seconds": time.time() - start_time
            }
        } 