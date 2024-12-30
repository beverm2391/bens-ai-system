"""
Integration tests for ExaClient.
"""
import os
import pytest
from src.clients.exa_client import ExaClient, ExaError

pytestmark = pytest.mark.external

@pytest.fixture
def client():
    """Create ExaClient instance."""
    api_key = os.getenv("EXA_API_KEY")
    if not api_key:
        pytest.skip("EXA_API_KEY not set")
    return ExaClient(api_key)

@pytest.mark.asyncio
async def test_search_basic(client):
    """Test basic search functionality."""
    results = await client.search("test query", num_results=1)
    assert isinstance(results, list)
    assert len(results) == 1
    assert "text" in results[0]
    assert "highlights" in results[0]

@pytest.mark.asyncio
async def test_search_with_domains(client):
    """Test search with domain filtering."""
    results = await client.search(
        "AI news",
        num_results=2,
        include_domains=["techcrunch.com"]
    )
    assert all("techcrunch.com" in r.get("url", "") for r in results)

@pytest.mark.asyncio
async def test_search_error_handling(client):
    """Test error handling."""
    with pytest.raises(ExaError):
        await client.search("")  # Empty query should raise error

@pytest.mark.asyncio
async def test_usage_stats(client):
    """Test usage statistics tracking."""
    initial_count = client.usage_stats["searches"]
    await client.search("test query", num_results=1)
    assert client.usage_stats["searches"] == initial_count + 1 