#!/usr/bin/env python3
"""
Script for searching the web using SERP API.
"""
import os
import sys
import json
import argparse
import requests
from typing import Dict, Any, List

def search(
    query: str,
    num_results: int = 10,
    include_domains: str = "",
    exclude_domains: str = ""
) -> Dict[str, Any]:
    """
    Search the web using SERP API.
    
    Args:
        query: Search query
        num_results: Number of results to return
        include_domains: Comma-separated list of domains to include
        exclude_domains: Comma-separated list of domains to exclude
        
    Returns:
        Dict containing search results
    """
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        raise ValueError("SERP_API_KEY environment variable is required")
    
    params = {
        "q": query,
        "api_key": api_key,
        "num": num_results,
        "output": "json"
    }
    
    if include_domains:
        params["sites"] = include_domains
    if exclude_domains:
        params["exclude"] = exclude_domains
    
    response = requests.get(
        "https://serpapi.com/search",
        params=params
    )
    response.raise_for_status()
    
    data = response.json()
    
    # Extract and clean up results
    results = []
    if "organic_results" in data:
        for result in data["organic_results"][:num_results]:
            results.append({
                "title": result.get("title", ""),
                "url": result.get("link", ""),
                "snippet": result.get("snippet", ""),
                "date": result.get("date", "")
            })
    
    return {
        "query": query,
        "num_results": len(results),
        "results": results
    }

def main():
    """Run the search script."""
    parser = argparse.ArgumentParser(description="Search the web using SERP API")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-n", "--num-results", type=int, default=10, help="Number of results to return")
    parser.add_argument("-i", "--include-domains", help="Comma-separated list of domains to include")
    parser.add_argument("-e", "--exclude-domains", help="Comma-separated list of domains to exclude")
    args = parser.parse_args()
    
    try:
        results = search(
            query=args.query,
            num_results=args.num_results,
            include_domains=args.include_domains or "",
            exclude_domains=args.exclude_domains or ""
        )
        print(json.dumps(results, indent=2))
        return 0
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main()) 