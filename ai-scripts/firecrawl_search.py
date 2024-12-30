#!/usr/bin/env python3
"""
Script to search and crawl websites using Firecrawl.
"""
import asyncio
import argparse
import json
from src.clients.firecrawl_client import FirecrawlClient, FirecrawlError

async def main(url: str, crawl: bool = False):
    client = FirecrawlClient()
    
    try:
        if crawl:
            print(f"Starting crawl of {url}...")
            job_id = await client.crawl_url(url)
            print(f"Crawl job started: {job_id}")
            
            print("Waiting for crawl to complete...")
            result = await client.wait_for_crawl(job_id)
            print(json.dumps(result, indent=2))
        else:
            print(f"Scraping {url}...")
            result = await client.scrape_url(url)
            print(json.dumps(result, indent=2))
            
    except FirecrawlError as e:
        print(f"Error: {str(e)}")
        return 1
    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Search and crawl websites using Firecrawl")
    parser.add_argument("url", help="URL to scrape or crawl")
    parser.add_argument("--crawl", action="store_true", help="Crawl entire site instead of single page")
    args = parser.parse_args()
    
    exit_code = asyncio.run(main(args.url, args.crawl))
    exit(exit_code) 