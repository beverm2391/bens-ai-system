"""
Unit tests for ExaClient.
"""
import pytest
from unittest.mock import Mock, patch
from src.clients.exa_client import ExaClient, ExaError

@pytest.fixture
def mock_exa():
    """Mock Exa client."""
    with patch("src.clients.exa_client.Exa") as mock:
        yield mock

def test_init_no_key():
    """Test initialization without API key."""
    with patch.dict("os.environ", {}, clear=True):  # Clear env vars
        with pytest.raises(ValueError):
            ExaClient(api_key=None)

def test_init_with_key(mock_exa):
    """Test initialization with API key."""
    client = ExaClient("test_key")
    assert client.api_key == "test_key"
    mock_exa.assert_called_once_with("test_key")

@pytest.mark.asyncio
async def test_search_success(mock_exa):
    """Test successful search."""
    # Mock search results
    mock_response = Mock()
    mock_result = Mock()
    mock_result.title = "Test Title"
    mock_result.url = "http://test.com"
    mock_result.text = "test content"
    mock_result.highlights = ["test highlight"]
    mock_response.results = [mock_result]
    mock_exa.return_value.search_and_contents.return_value = mock_response
    
    client = ExaClient("test_key")
    results = await client.search("test query")
    
    assert len(results) == 1
    assert results[0]["title"] == "Test Title"
    assert results[0]["text"] == "test content"
    assert results[0]["highlights"] == ["test highlight"]
    mock_exa.return_value.search_and_contents.assert_called_once()

@pytest.mark.asyncio
async def test_search_error(mock_exa):
    """Test search error handling."""
    mock_exa.return_value.search_and_contents.side_effect = Exception("API error")
    
    client = ExaClient("test_key")
    with pytest.raises(ExaError):
        await client.search("test query")

def test_usage_stats(mock_exa):
    """Test usage statistics."""
    client = ExaClient("test_key")
    assert client.usage_stats["searches"] == 0 