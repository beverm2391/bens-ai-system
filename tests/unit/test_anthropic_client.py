"""
Unit tests for AnthropicClient
"""
import pytest
import asyncio
from datetime import datetime
from src.clients.anthropic_client import AnthropicClient, UsageStats

def test_usage_stats():
    """Test UsageStats tracking"""
    stats = UsageStats()
    stats.add_request(100, 50, 0.005)
    
    assert stats.prompt_tokens == 100
    assert stats.completion_tokens == 50
    assert stats.total_cost == 0.005
    assert stats.requests == 1
    assert isinstance(stats.last_request, datetime)

def test_client_init():
    """Test client initialization and validation"""
    # Should raise on empty API key
    with pytest.raises(ValueError):
        AnthropicClient("")
    
    # Should raise on invalid model
    with pytest.raises(ValueError):
        AnthropicClient("test_key", model="invalid_model")
    
    # Should initialize with defaults
    client = AnthropicClient("test_key")
    assert client.model == "claude-2.1"
    assert client.default_max_tokens == 1024
    assert isinstance(client.stats, UsageStats)

def test_stream_validation():
    """Test parameter validation for stream method"""
    client = AnthropicClient("test_key")
    
    # Empty prompt
    with pytest.raises(ValueError):
        asyncio.run(client.stream("").__anext__())
    
    # Invalid temperature
    with pytest.raises(ValueError):
        asyncio.run(client.stream("test", temperature=-1).__anext__())
    with pytest.raises(ValueError):
        asyncio.run(client.stream("test", temperature=3).__anext__())
    
    # Invalid top_p
    with pytest.raises(ValueError):
        asyncio.run(client.stream("test", top_p=-0.5).__anext__())
    with pytest.raises(ValueError):
        asyncio.run(client.stream("test", top_p=1.5).__anext__())

def test_cost_calculation():
    """Test token cost calculations"""
    client = AnthropicClient("test_key")
    cost = client._calculate_cost(1000, 1000)  # 1k tokens each
    
    # For claude-2.1: $0.008 per 1k prompt, $0.024 per 1k completion
    expected = 0.008 + 0.024
    assert cost == expected 