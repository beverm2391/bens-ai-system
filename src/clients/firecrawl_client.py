import os
import aiohttp
import asyncio
from typing import Dict, Optional, List
from aiohttp import ClientError

class FirecrawlError(Exception):
    """Base exception for Firecrawl client errors."""
    pass

class FirecrawlClient:
    """Client for interacting with Firecrawl API."""
    
    def __init__(self, api_key: Optional[str] = None, max_retries: int = 3):
        self.api_key = api_key or os.getenv("FIRECRAWL_API_KEY")
        if not self.api_key:
            raise ValueError("Firecrawl API key is required")
        self.base_url = "https://api.firecrawl.dev/v1"
        self.max_retries = max_retries
        
    async def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request with retries."""
        headers = {"Authorization": f"Bearer {self.api_key}"}
        if "headers" in kwargs:
            kwargs["headers"].update(headers)
        else:
            kwargs["headers"] = headers

        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with getattr(session, method)(
                        f"{self.base_url}/{endpoint}",
                        **kwargs
                    ) as response:
                        await response.raise_for_status()
                        return await response.json()
            except ClientError as e:
                if attempt == self.max_retries - 1:
                    raise FirecrawlError(f"Request failed after {self.max_retries} attempts: {str(e)}")
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
        
    async def scrape_url(self, url: str) -> Dict:
        """Scrape a single URL and get markdown content."""
        return await self._make_request("post", "scrape", json={"url": url})

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