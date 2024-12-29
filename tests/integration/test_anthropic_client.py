"""
Integration tests for AnthropicClient
"""
import pytest
import os
import asyncio
from src.clients.anthropic_client import AnthropicClient

@pytest.mark.skipif(not os.getenv("ANTHROPIC_API_KEY"), reason="No API key")
@pytest.mark.asyncio
async def test_stream_integration():
    """Test streaming completion with real API"""
    client = AnthropicClient(os.getenv("ANTHROPIC_API_KEY"))
    
    # Test basic streaming
    chunks = []
    async for chunk in client.stream("Say 'test' and nothing else"):
        chunks.append(chunk)
    
    # Verify we got some response
    assert len(chunks) > 0
    assert "test" in "".join(chunks).lower()
    
    # Verify stats were updated
    stats = client.usage_stats
    assert stats["requests"] == 1
    assert stats["prompt_tokens"] > 0
    assert stats["completion_tokens"] > 0
    assert stats["total_cost"] > 0 