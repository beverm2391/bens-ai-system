"""
Tool for searching the web using SERP API
"""
import os
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
        Dict containing search results
    """
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
                
        return {
            "status": "success",
            "results": results
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"SERP API request failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "results": []
        } 