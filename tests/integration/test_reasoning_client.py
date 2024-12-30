"""
Integration tests for ReasoningClient.
"""
import os
import json
import pytest
from src.clients.reasoning_client import ReasoningClient

# Skip integration tests if no API key
requires_api_key = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY environment variable not set"
)

@pytest.fixture
def api_key():
    """Get API key from environment."""
    return os.getenv("OPENAI_API_KEY", "dummy_key")

def test_client_init(api_key):
    """Test client initialization."""
    client = ReasoningClient(api_key)
    assert not client.structured_output
    
    client = ReasoningClient(api_key, structured_output=True)
    assert client.structured_output

@requires_api_key
@pytest.mark.asyncio
async def test_basic_reasoning(api_key):
    """Test basic reasoning without special features."""
    client = ReasoningClient(api_key)
    
    chunks = []
    async for chunk in client.reason(
        "What is 2 + 2 and why?",
        temperature=0
    ):
        chunks.append(chunk)
    
    response = "".join(chunks).lower()
    assert "4" in response
    assert any(word in response for word in ["because", "since", "as"])

@requires_api_key
@pytest.mark.asyncio
async def test_step_reasoning(api_key):
    """Test reasoning with specific steps."""
    client = ReasoningClient(api_key)
    
    chunks = []
    async for chunk in client.reason(
        "Explain how to make a sandwich.",
        steps=3,
        temperature=0
    ):
        chunks.append(chunk)
    
    response = "".join(chunks).lower()
    # Should have exactly 3 steps
    assert response.count("step 1") == 1
    assert response.count("step 2") == 1
    assert response.count("step 3") == 1

@requires_api_key
@pytest.mark.asyncio
async def test_chain_of_thought(api_key):
    """Test chain-of-thought reasoning."""
    client = ReasoningClient(api_key)
    
    chunks = []
    async for chunk in client.reason(
        "Should I bring an umbrella today if there are dark clouds?",
        chain_of_thought=True,
        temperature=0
    ):
        chunks.append(chunk)
    
    response = "".join(chunks).lower()
    # Should show thought process
    assert any(word in response for word in ["consider", "think", "because"])

@requires_api_key
@pytest.mark.asyncio
async def test_structured_output(api_key):
    """Test structured JSON output."""
    client = ReasoningClient(api_key, structured_output=True)
    
    chunks = []
    async for chunk in client.reason(
        "What is 3 * 4 and why?",
        temperature=0
    ):
        chunks.append(chunk)
    
    response = "".join(chunks)
    # Should be valid JSON with steps and conclusion
    data = json.loads(response)
    assert "steps" in data
    assert isinstance(data["steps"], list)
    assert "conclusion" in data

@requires_api_key
@pytest.mark.asyncio
async def test_few_shot_examples(api_key):
    """Test reasoning with examples."""
    client = ReasoningClient(api_key)
    
    examples = [
        {
            "question": "What is 2 + 3?",
            "reasoning": "I add the numbers together.",
            "answer": "5"
        }
    ]
    
    chunks = []
    async for chunk in client.reason(
        "What is 3 + 4?",
        examples=examples,
        temperature=0
    ):
        chunks.append(chunk)
    
    response = "".join(chunks).lower()
    assert "7" in response
    # Should follow similar pattern to example
    assert "add" in response 