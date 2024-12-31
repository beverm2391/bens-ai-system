import os
import json
from typing import Dict, Any
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def search(query: str, num_results: int = 10, include_domains: str = "", exclude_domains: str = "") -> Dict[str, Any]:
    """
    Perform a web search using SERP API
    
    Args:
        query: Search query string
        num_results: Number of results to return (default: 10)
        include_domains: Comma-separated list of domains to include
        exclude_domains: Comma-separated list of domains to exclude
        
    Returns:
        Dict containing search results
    """
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        raise ValueError("SERP_API_KEY environment variable not set")
        
    params = {
        "q": query,
        "num": num_results,
        "api_key": api_key
    }
    
    if include_domains:
        params["include_domains"] = include_domains
    if exclude_domains:
        params["exclude_domains"] = exclude_domains
        
    response = requests.get("https://serpapi.com/search", params=params)
    response.raise_for_status()
    
    return response.json()

# Claude tool schema
SERP_SCHEMA = {
    "name": "web_search",
    "description": """
    Performs a web search using SERP API to find relevant web pages and information.
    This tool should be used when you need to search the internet for current information.
    The search can be filtered to specific domains if needed.
    Results include titles, snippets, and URLs of relevant web pages.
    Note that this makes a real API call and consumes credits, so use judiciously.
    """,
    "input_schema": {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The search query string"
            },
            "num_results": {
                "type": "integer",
                "description": "Number of results to return",
                "default": 10
            },
            "include_domains": {
                "type": "string",
                "description": "Optional comma-separated list of domains to include",
                "default": ""
            },
            "exclude_domains": {
                "type": "string", 
                "description": "Optional comma-separated list of domains to exclude",
                "default": ""
            }
        },
        "required": ["query"]
    }
} 