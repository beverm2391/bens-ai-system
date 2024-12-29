"""
Integration tests for OpenAIClient.
"""
import os
import pytest
import asyncio
from src.clients.openai_client import OpenAIClient, UsageStats

# Skip integration tests if no API key
requires_api_key = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY environment variable not set"
)

@pytest.fixture
def api_key():
    """Get API key from environment."""
    return os.getenv("OPENAI_API_KEY", "dummy_key")

def test_usage_stats():
    """Test UsageStats tracking."""
    stats = UsageStats()
    
    # Test initial state
    assert stats.prompt_tokens == 0
    assert stats.completion_tokens == 0
    assert stats.total_tokens == 0
    assert stats.total_cost == 0.0
    assert stats.requests == 0
    
    # Test adding requests
    stats.add_request(10, 20, 0.05)
    assert stats.prompt_tokens == 10
    assert stats.completion_tokens == 20
    assert stats.total_tokens == 30
    assert stats.total_cost == 0.05
    assert stats.requests == 1
    
    # Test dict access
    assert stats["prompt_tokens"] == 10
    assert stats["completion_tokens"] == 20
    assert stats["total_tokens"] == 30
    assert stats["total_cost"] == 0.05
    assert stats["requests"] == 1
    
    with pytest.raises(KeyError):
        _ = stats["invalid_key"]

def test_client_init(api_key):
    """Test client initialization."""
    client = OpenAIClient(api_key)
    assert client.model == "gpt-4"
    assert client.default_max_tokens == 1000
    
    client = OpenAIClient(
        api_key,
        model="gpt-3.5-turbo",
        default_max_tokens=500
    )
    assert client.model == "gpt-3.5-turbo"
    assert client.default_max_tokens == 500

def test_calculate_cost(api_key):
    """Test cost calculation."""
    client = OpenAIClient(
        api_key,
        cost_per_1k_prompt=0.01,
        cost_per_1k_completion=0.02
    )
    cost = client._calculate_cost(1000, 2000)
    assert cost == 0.05  # (1 * 0.01) + (2 * 0.02)

@requires_api_key
@pytest.mark.asyncio
async def test_stream_validation(api_key):
    """Test stream parameter validation."""
    client = OpenAIClient(api_key)
    
    with pytest.raises(ValueError):
        async for _ in client.stream(""):  # Empty prompt
            pass
            
    with pytest.raises(ValueError):
        async for _ in client.stream("test", temperature=-1):
            pass
            
    with pytest.raises(ValueError):
        async for _ in client.stream("test", temperature=3):
            pass
            
    with pytest.raises(ValueError):
        async for _ in client.stream("test", top_p=-0.5):
            pass
            
    with pytest.raises(ValueError):
        async for _ in client.stream("test", top_p=1.5):
            pass

@requires_api_key
@pytest.mark.asyncio
async def test_stream_basic(api_key):
    """Test basic streaming."""
    client = OpenAIClient(api_key)
    
    chunks = []
    async for chunk in client.stream(
        "Say 'hello' and nothing else",
        temperature=0,
        max_tokens=10
    ):
        chunks.append(chunk)
    
    response = "".join(chunks).strip().lower()
    assert "hello" in response
    
    # Check usage tracking
    stats = client.usage_stats
    assert stats["requests"] == 1
    assert stats["prompt_tokens"] > 0
    assert stats["completion_tokens"] > 0
    assert stats["total_cost"] > 0

@requires_api_key
@pytest.mark.asyncio
async def test_stream_system(api_key):
    """Test system prompt."""
    client = OpenAIClient(api_key)
    
    chunks = []
    async for chunk in client.stream(
        "What are you?",
        system="You are a helpful AI assistant. Keep responses under 50 words.",
        temperature=0
    ):
        chunks.append(chunk)
    
    response = "".join(chunks).lower()
    assert len(response.split()) < 50  # Check word limit
    assert any(word in response for word in ["ai", "assistant", "help"])  # Check role understanding

@requires_api_key
@pytest.mark.asyncio
async def test_stream_parameters(api_key):
    """Test streaming with various parameters."""
    client = OpenAIClient(api_key)
    
    chunks = []
    async for chunk in client.stream(
        "Write a creative story about a cat.",
        max_tokens=100,
        temperature=0.9,
        top_p=0.9,
        frequency_penalty=0.5,
        presence_penalty=0.5,
        stop=["The end"]
    ):
        chunks.append(chunk)
    
    response = "".join(chunks)
    assert len(response) > 0
    assert "cat" in response.lower() 