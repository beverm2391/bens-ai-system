import pytest
import pytest_asyncio
import logging
from src.clients.serp_client import SerpClient, SerpError

logging.basicConfig(level=logging.INFO)

@pytest.mark.integration
class TestSerpClientIntegration:
    
    @pytest_asyncio.fixture
    async def client(self):
        """Create a SERP client for testing."""
        client = SerpClient()
        yield client
    
    @pytest.mark.asyncio
    async def test_real_search_demo(self, client):
        """Real integration test demonstrating SERP client functionality."""
        try:
            # Search for something specific that should have stable results
            results = await client.search("OpenAI GPT-4 technical documentation", num_results=3)
            
            # Verify we got results
            assert len(results) > 0, "Should get at least one result"
            
            # Print results for manual verification
            print("\n=== Search Results ===")
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"Title: {result['title']}")
                print(f"URL: {result['link']}")
                print(f"Snippet: {result['snippet']}")
                
                # Basic validation
                assert result["title"], "Result should have a title"
                assert result["link"].startswith("http"), "Result should have a valid URL"
                assert result["snippet"], "Result should have a snippet"
            
            # Test rate limit tracking
            current_usage = client._monthly_searches
            print(f"\nMonthly API usage: {current_usage}/{client._monthly_limit}")
            
        except SerpError as e:
            pytest.fail(f"SERP API error: {str(e)}")
        except Exception as e:
            pytest.fail(f"Unexpected error: {str(e)}")
            
    @pytest.mark.asyncio
    async def test_rate_limit_demo(self, client):
        """Demonstrate rate limit handling with a small limit."""
        # Set a very low limit for demonstration
        client._monthly_limit = 2
        client._monthly_searches = 0
        
        try:
            # First search should work
            results1 = await client.search("test query 1", num_results=1)
            print("\n=== Rate Limit Test ===")
            print("First search successful")
            
            # Second search should work
            results2 = await client.search("test query 2", num_results=1)
            print("Second search successful")
            
            # Third search should hit rate limit
            print("Attempting third search (should fail)...")
            with pytest.raises(SerpError, match="Monthly search limit reached"):
                await client.search("test query 3", num_results=1)
            print("Rate limit caught successfully")
            
        except SerpError as e:
            if "Monthly search limit reached" not in str(e):
                pytest.fail(f"Unexpected SERP error: {str(e)}")
        except Exception as e:
            pytest.fail(f"Unexpected error: {str(e)}") 