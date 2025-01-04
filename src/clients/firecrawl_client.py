import os
import aiohttp
import asyncio
import logging
from typing import Dict, Optional, List
from aiohttp import ClientError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logger = logging.getLogger(__name__)

class FirecrawlError(Exception):
    """Base exception for Firecrawl client errors."""
    pass

class FirecrawlClient:
    """Client for interacting with Firecrawl API."""
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        """Initialize client with API key from parameter or environment."""
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("Firecrawl API key is required - set FIRECRAWL_API_KEY environment variable")
        if not isinstance(self.api_key, str) or not self.api_key.strip():
            raise ValueError("Invalid Firecrawl API key")
            
        logger.info("Initialized FirecrawlClient with API key")
        self.base_url = "https://api.firecrawl.dev/v1"
        self.max_retries = max_retries
        self._session = None
        
    async def __aenter__(self):
        """Async context manager entry."""
        logger.debug("Initializing client session")
        self._session = aiohttp.ClientSession()
        logger.debug("Client session initialized")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        logger.debug("Closing client session")
        if self._session:
            await self._session.close()
            self._session = None
        logger.debug("Client session closed")
        
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request with retries."""
        if not self._session:
            raise FirecrawlError("Client session not initialized - use async context manager")
            
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        if "headers" in kwargs:
            kwargs["headers"].update(headers)
        else:
            kwargs["headers"] = headers

        logger.debug(f"Making {method} request to {endpoint} with session {id(self._session)}")
        
        for attempt in range(self.max_retries):
            try:
                request = getattr(self._session, method)
                async with request(
                    f"{self.base_url}/{endpoint}",
                    **kwargs
                ) as response:
                    await response.raise_for_status()
                    data = await response.json()
                    logger.debug(f"Got response: {data}")
                    if not data.get("success"):
                        raise FirecrawlError(f"API error: {data.get('error', 'Unknown error')}")
                    return data.get("data", {})
            except ClientError as e:
                logger.error(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {str(e)}")
                if attempt == self.max_retries - 1:
                    raise FirecrawlError(f"Request failed after {self.max_retries} attempts: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
    async def scrape_url(self, url: str) -> Dict:
        """Scrape a single URL and get markdown content."""
        try:
            logger.info(f"Scraping URL: {url}")
            response = await self._make_request("post", "scrape", json={"url": url})
            if not response:
                raise FirecrawlError("No response from scraper")
            return response
        except Exception as e:
            raise FirecrawlError(f"Failed to scrape {url}: {str(e)}")

    async def crawl_url(self, url: str) -> str:
        """Start a crawl job and return the job ID."""
        response = await self._make_request("post", "crawl", json={"url": url})
        return response["id"]

    async def get_crawl_status(self, job_id: str) -> Dict:
        """Check status of a crawl job."""
        return await self._make_request("get", f"crawl/{job_id}")

    async def wait_for_crawl(self, job_id: str, timeout: int = 300, poll_interval: int = 5) -> Dict:
        """Wait for crawl job to complete with timeout."""
        start_time = asyncio.get_event_loop().time()
        while True:
            status = await self.get_crawl_status(job_id)
            if status.get("success"):
                return status
            
            if asyncio.get_event_loop().time() - start_time > timeout:
                raise FirecrawlError(f"Crawl job {job_id} timed out after {timeout} seconds")
            
            await asyncio.sleep(poll_interval) 