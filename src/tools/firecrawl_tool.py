"""
Tools for web scraping and crawling using Firecrawl API.
"""
import os
import logging
import asyncio
from typing import Dict, Any, List, Optional
from src.clients.firecrawl_client import FirecrawlClient, FirecrawlError

logger = logging.getLogger(__name__)

async def _scrape_with_client(url: str) -> Dict[str, Any]:
    """Scrape a single URL using FirecrawlClient"""
    try:
        client = FirecrawlClient()
        result = await client.scrape_url(url)
        return {
            "url": url,
            "status": "success",
            "content": result
        }
    except FirecrawlError as e:
        logger.error(f"Firecrawl scrape failed for {url}: {e}")
        return {
            "url": url,
            "status": "error",
            "message": str(e)
        }

async def _crawl_with_client(url: str, timeout: int = 300) -> Dict[str, Any]:
    """Start a crawl job and wait for results"""
    try:
        client = FirecrawlClient()
        job_id = await client.crawl_url(url)
        result = await client.wait_for_crawl(job_id, timeout=timeout)
        return {
            "url": url,
            "status": "success",
            "content": result
        }
    except FirecrawlError as e:
        logger.error(f"Firecrawl crawl failed for {url}: {e}")
        return {
            "url": url,
            "status": "error",
            "message": str(e)
        }

def scrape_page(url: str) -> Dict[str, Any]:
    """
    Scrape content from a single webpage using Firecrawl.
    
    Args:
        url: URL to scrape
        
    Returns:
        Dict containing scraped content
    """
    return asyncio.run(_scrape_with_client(url))

def crawl_site(url: str, timeout: int = 300) -> Dict[str, Any]:
    """
    Crawl a website starting from the given URL.
    
    Args:
        url: Starting URL to crawl
        timeout: Maximum time to wait for crawl completion (default: 300s)
        
    Returns:
        Dict containing crawled content graph
    """
    return asyncio.run(_crawl_with_client(url, timeout)) 