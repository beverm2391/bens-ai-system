#!/usr/bin/env python3
"""
Script for consulting O1 for reasoning and critical thinking tasks.
"""
import os
import sys
import asyncio
from src.clients.reasoning_client import ReasoningClient

async def consult_o1(prompt: str) -> None:
    """
    Consult O1 with a prompt and print the response.
    
    Args:
        prompt: The question/task to reason about
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY environment variable not set")
        sys.exit(1)
        
    # Initialize client with chain-of-thought enabled
    client = ReasoningClient(api_key)
    
    print("\nConsulting O1...\n")
    print("-" * 40)
    
    # Stream the response
    async for chunk in client.reason(
        prompt,
        chain_of_thought=True,
        temperature=0  # Deterministic for consistency
    ):
        print(chunk, end="", flush=True)
    
    print("\n" + "-" * 40)
    
    # Print usage for tracking
    stats = client.usage_stats
    print(f"\nTokens used: {stats['total_tokens']}")
    print(f"Cost: ${stats['total_cost']:.4f}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python o1_consult.py \"Your prompt here\"")
        sys.exit(1)
        
    prompt = sys.argv[1]
    asyncio.run(consult_o1(prompt))

if __name__ == "__main__":
    main() 