import pytest
import os
from src.clients.together_client import TogetherClient

@pytest.mark.asyncio
async def test_together_chat_completion():
    client = TogetherClient()
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2?"}
    ]
    response = await client.chat_completion(messages)
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Check usage stats
    stats = client.usage_stats
    assert stats["prompt_tokens"] > 0
    assert stats["completion_tokens"] > 0
    assert stats["total_cost"] > 0
    assert stats["requests"] == 1

@pytest.mark.asyncio
async def test_together_completion():
    client = TogetherClient()
    response = await client.completion(
        "What is 2+2?",
        temperature=0.7,
        max_tokens=50
    )
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Verify stats accumulation
    stats = client.usage_stats
    assert stats["requests"] == 1
    assert stats["last_request"] is not None

@pytest.mark.asyncio
async def test_together_streaming():
    client = TogetherClient()
    chunks = []
    stream = await client.completion(
        "Count from 1 to 5.",
        stream=True,
        temperature=0.5
    )
    async for chunk in stream:  # Stream is already an async generator
        chunks.append(chunk)
    assert len(chunks) > 0
    assert all(isinstance(chunk, str) for chunk in chunks)
    
    # Verify streaming affects stats
    stats = client.usage_stats
    assert stats["requests"] == 1
    assert stats["completion_tokens"] > 0

@pytest.mark.asyncio
async def test_parameter_validation():
    client = TogetherClient()
    
    # Test invalid temperature
    with pytest.raises(ValueError, match="Temperature must be between 0 and 2"):
        await client.completion("Test", temperature=3.0)
    
    # Test invalid top_p
    with pytest.raises(ValueError, match="top_p must be between 0 and 1"):
        await client.completion("Test", top_p=1.5)
    
    # Test empty messages
    with pytest.raises(ValueError, match="Messages cannot be empty"):
        await client.chat_completion([])

@pytest.mark.asyncio
async def test_model_selection():
    client = TogetherClient(model="Qwen/Qwen2.5-Coder-32B-Instruct")
    response = await client.completion("Write a hello world in Python")
    assert isinstance(response, str)
    assert len(response) > 0
    
    # Verify model in stats
    stats = client.usage_stats
    assert stats["model"] == "Qwen/Qwen2.5-Coder-32B-Instruct"

@pytest.mark.asyncio
async def test_get_models():
    client = TogetherClient()
    models = await client.get_available_models()
    assert isinstance(models, list)
    assert len(models) > 0 