import pytest
from unittest.mock import patch, MagicMock
from src.clients.serp_client import SerpClient, SerpError
from src.config.serp_config import SERP_CONFIG

@pytest.fixture
def mock_search_response():
    return {
        "organic_results": [
            {
                "title": "Test Result 1",
                "link": "https://example.com/1",
                "snippet": "This is test result 1"
            },
            {
                "title": "Test Result 2",
                "link": "https://example.com/2",
                "snippet": "This is test result 2"
            }
        ]
    }

@pytest.fixture
def mock_error_response():
    return {"error": "API Error"}

class TestSerpClient:
    
    @pytest.fixture
    def client(self):
        with patch.dict('os.environ', {'SERP_API_KEY': 'test_key'}):
            return SerpClient()

    @pytest.mark.asyncio
    async def test_search_success(self, client, mock_search_response):
        """Test successful search with mocked response."""
        with patch('src.clients.serp_client.GoogleSearch') as mock:
            mock.return_value.get_dict.return_value = mock_search_response
            results = await client.search("test query", num_results=2)
            
            assert len(results) == 2
            assert results[0]["title"] == "Test Result 1"
            assert results[0]["link"] == "https://example.com/1"
            assert results[0]["snippet"] == "This is test result 1"

    @pytest.mark.asyncio
    async def test_search_api_error(self, client, mock_error_response):
        """Test handling of API errors."""
        with patch('src.clients.serp_client.GoogleSearch') as mock:
            mock.return_value.get_dict.return_value = mock_error_response
            with pytest.raises(SerpError, match="SERP API error: API Error"):
                await client.search("test query")

    @pytest.mark.asyncio
    async def test_search_params(self, client, mock_search_response):
        """Test that search parameters are correctly constructed."""
        with patch('src.clients.serp_client.GoogleSearch') as mock_google_search:
            # Configure the mock
            mock_google_search.return_value.get_dict.return_value = mock_search_response
            
            await client.search("test query", num_results=5)
            
            # Verify correct parameters were passed
            call_args = mock_google_search.call_args[0][0]
            assert call_args["q"] == "test query"
            assert call_args["num"] == 5
            assert call_args["api_key"] == "test_key"
            assert call_args["hl"] == SERP_CONFIG["hl"]
            assert call_args["gl"] == SERP_CONFIG["gl"]

    @pytest.mark.asyncio
    async def test_rate_limit_tracking(self, client, mock_search_response):
        """Test rate limit tracking with mocked responses."""
        with patch('src.clients.serp_client.GoogleSearch') as mock:
            mock.return_value.get_dict.return_value = mock_search_response
            # Set low limit for testing
            client._monthly_limit = 3
            client._monthly_searches = 0  # Reset counter
            
            # First two searches should work
            await client.search("test 1")
            await client.search("test 2")
            
            # Third search should hit rate limit
            with pytest.raises(SerpError, match="Monthly search limit reached"):
                await client.search("test 3")
                await client.search("test 4")  # This should trigger the limit 