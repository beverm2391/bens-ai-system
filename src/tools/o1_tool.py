"""
Tool for structured reasoning using O1 (OpenAI-based reasoning).
"""
import os
import logging
import json
import asyncio
from typing import Dict, Any
from src.clients.reasoning_client import ReasoningClient

logger = logging.getLogger(__name__)

async def _reason_with_client(prompt: str, steps: int) -> Dict[str, Any]:
    """Use O1 client for reasoning"""
    # Initialize client with structured output
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set")
        
    client = ReasoningClient(
        api_key=api_key,
        structured_output=True
    )
    
    # Add implementation-focused wrapper to prompt
    full_prompt = f"""
    Analyze this problem and plan a Python implementation:
    {prompt}
    
    Consider:
    - Core algorithms and data structures
    - API design and interfaces
    - Error handling and edge cases
    - Performance implications
    - Testing strategy
    
    Provide concrete implementation details.
    """
    
    # Get structured reasoning
    response = []
    async for chunk in client.reason(
        full_prompt,
        steps=steps,
        chain_of_thought=True
    ):
        response.append(chunk)
        
    # Parse JSON response
    return json.loads("".join(response))

def reason_about(prompt: str, steps: int = 5) -> Dict[str, Any]:
    """
    Use O1 reasoning to analyze and plan implementation.
    
    Args:
        prompt: What to reason about
        steps: Number of reasoning steps (default: 5)
        
    Returns:
        Dict containing structured reasoning steps and conclusion
    """
    try:
        result = asyncio.run(_reason_with_client(prompt, steps))
        return {
            "status": "success",
            "reasoning": result
        }
    except Exception as e:
        logger.error(f"O1 reasoning failed: {e}")
        return {
            "status": "error",
            "message": str(e)
        } 