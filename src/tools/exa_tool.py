"""
Tool for semantic web search using Exa API.
"""
import os
import time
import logging
from typing import Dict, Any, List, Optional
from src.clients.exa_client import ExaClient

logger = logging.getLogger(__name__)

async def semantic_search(
    query: str,
    num_results: int = 10,
    search_type: str = "neural",
    include_domains: Optional[str] = None,
    exclude_domains: Optional[str] = None
) -> Dict[str, Any]:
    """
    Perform semantic search using Exa API
    
    Args:
        query: Search query string
        num_results: Number of results to return
        search_type: Type of search ("neural" or "keyword")
        include_domains: Comma-separated list of domains to include
        exclude_domains: Comma-separated list of domains to exclude
    """
    start_time = time.time()
    client = ExaClient()
    
    try:
        # Convert domain strings to lists
        include_list = include_domains.split(",") if include_domains else None
        exclude_list = exclude_domains.split(",") if exclude_domains else None
        
        results = await client.search(
            query,
            num_results=num_results,
            search_type=search_type,
            include_domains=include_list,
            exclude_domains=exclude_list
        )
        
        # Track usage metrics
        usage = {
            "queries": 1,
            "query_length": len(query),
            "results_returned": len(results),
            "search_type": search_type,
            "latency_seconds": time.time() - start_time,
            # TODO: Implement token tracking
            # "query_tokens": count_tokens(query),
            # TODO: Track content length
            # "total_content_length": sum(len(r.get("text", "")) for r in results)
        }
        
        return {
            "status": "success",
            "results": results,
            "usage": usage
        }
        
    except Exception as e:
        logger.error(f"Exa search failed: {e}")
        return {
            "status": "error",
            "message": str(e),
            "results": [],
            "usage": {
                "queries": 1,
                "query_length": len(query),
                "results_returned": 0,
                "search_type": search_type,
                "latency_seconds": time.time() - start_time
            }
        } 