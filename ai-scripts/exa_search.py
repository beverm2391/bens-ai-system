"""
Script for performing semantic web searches using Exa API.
"""
import os
import sys
import json
import asyncio
from typing import Optional, List
from src.clients.exa_client import ExaClient

async def search(
    query: str,
    num_results: int = 10,
    use_autoprompt: bool = True,
    include_domains: Optional[List[str]] = None,
    exclude_domains: Optional[List[str]] = None
) -> str:
    """
    Perform semantic web search using Exa.
    
    Args:
        query: Search query
        num_results: Number of results to return
        use_autoprompt: Whether to use Exa's query enhancement
        include_domains: List of domains to include
        exclude_domains: List of domains to exclude
        
    Returns:
        JSON string with search results
    """
    try:
        client = ExaClient()
        results = await client.search(
            query,
            num_results=num_results,
            use_autoprompt=use_autoprompt,
            include_domains=include_domains,
            exclude_domains=exclude_domains
        )
        return json.dumps({"results": results}, indent=2)
        
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python exa_search.py <query> [num_results] [include_domains] [exclude_domains]")
        sys.exit(1)
        
    query = sys.argv[1]
    num_results = int(sys.argv[2]) if len(sys.argv) > 2 else 10
    include_domains = sys.argv[3].split(",") if len(sys.argv) > 3 else None
    exclude_domains = sys.argv[4].split(",") if len(sys.argv) > 4 else None
    
    print(asyncio.run(search(
        query,
        num_results=num_results,
        include_domains=include_domains,
        exclude_domains=exclude_domains
    ))) 