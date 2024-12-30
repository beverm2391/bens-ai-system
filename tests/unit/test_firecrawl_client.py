import pytest
from unittest.mock import AsyncMock, patch
from src.clients.firecrawl_client import FirecrawlClient

@pytest.fixture
def client():
    return FirecrawlClient(api_key="test_key")

@pytest.mark.asyncio
async def test_scrape_url(client):
    mock_response = {"markdown": "# Test Content"}
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        mock_post.return_value.__aenter__.return_value.raise_for_status = AsyncMock()
        
        result = await client.scrape_url("https://example.com")
        assert result == mock_response

@pytest.mark.asyncio
async def test_crawl_url(client):
    mock_response = {"id": "test_job_id"}
    
    with patch("aiohttp.ClientSession.post") as mock_post:
        mock_post.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        mock_post.return_value.__aenter__.return_value.raise_for_status = AsyncMock()
        
        job_id = await client.crawl_url("https://example.com")
        assert job_id == "test_job_id"

@pytest.mark.asyncio
async def test_get_crawl_status(client):
    mock_response = {"status": "completed"}
    
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.return_value.__aenter__.return_value.json = AsyncMock(
            return_value=mock_response
        )
        mock_get.return_value.__aenter__.return_value.raise_for_status = AsyncMock()
        
        result = await client.get_crawl_status("test_job_id")
        assert result == mock_response 