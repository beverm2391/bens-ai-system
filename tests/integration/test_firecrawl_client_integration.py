import pytest
from src.clients.firecrawl_client import FirecrawlClient

@pytest.mark.integration
@pytest.mark.asyncio
async def test_firecrawl_scrape_integration():
    client = FirecrawlClient()
    result = await client.scrape_url("https://example.com")
    assert "data" in result
    assert "markdown" in result["data"]

@pytest.mark.integration
@pytest.mark.asyncio
async def test_firecrawl_crawl_workflow():
    client = FirecrawlClient()
    
    # Start crawl
    job_id = await client.crawl_url("https://example.com")
    assert job_id
    
    # Check status
    status = await client.get_crawl_status(job_id)
    assert "success" in status 