#!/usr/bin/env python3
"""
Script to perform Google searches using SERP API.
Integrates with Firecrawl for content extraction if needed.
"""

import asyncio
import argparse
import logging
from typing import Optional, List, Dict
import json
from src.clients.serp_client import SerpClient
from src.clients.firecrawl_client import FirecrawlClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def search_and_maybe_crawl(
    query: str,
    num_results: int = 5,
    crawl: bool = False,
    output_file: Optional[str] = None
) -> List[Dict]:
    """
    Search using SERP API and optionally crawl results.
    
    Args:
        query: Search query
        num_results: Number of results to return
        crawl: Whether to crawl the results with Firecrawl
        output_file: Optional file to save results to
        
    Returns:
        List of search results with optional content
    """
    serp_client = SerpClient()
    results = await serp_client.search(query, num_results=num_results)
    
    if crawl:
        firecrawl_client = FirecrawlClient()
        for result in results:
            try:
                content = await firecrawl_client.scrape_url(result['link'])
                result['content'] = content
            except Exception as e:
                logger.error(f"Failed to crawl {result['link']}: {str(e)}")
                result['content'] = None
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
            logger.info(f"Results saved to {output_file}")
    
    return results

def main():
    parser = argparse.ArgumentParser(description="Search using SERP API with optional crawling")
    parser.add_argument("query", help="Search query")
    parser.add_argument("-n", "--num-results", type=int, default=5,
                       help="Number of results to return (default: 5)")
    parser.add_argument("-c", "--crawl", action="store_true",
                       help="Crawl the search results with Firecrawl")
    parser.add_argument("-o", "--output", help="Save results to this file")
    parser.add_argument("-v", "--verbose", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    try:
        results = asyncio.run(search_and_maybe_crawl(
            args.query,
            num_results=args.num_results,
            crawl=args.crawl,
            output_file=args.output
        ))
        
        # Print results to console
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Title: {result['title']}")
            print(f"URL: {result['link']}")
            print(f"Snippet: {result['snippet']}")
            if args.crawl and result.get('content'):
                print("Content preview:")
                preview = result['content'][:200] + "..." if len(result['content']) > 200 else result['content']
                print(preview)
            print("-" * 80)
            
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main()) 