"""
Demo script for ReasoningClient showing various reasoning patterns.
"""
import os
import json
import asyncio
from src.clients.reasoning_client import ReasoningClient

# Set debug level to see detailed output
os.environ["DEBUG_LEVEL"] = "1"

async def main():
    # Initialize client
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Please set OPENAI_API_KEY environment variable")
        return
    
    client = ReasoningClient(api_key)
    
    print("\n=== Basic Reasoning ===")
    chunks = []
    async for chunk in client.reason(
        "What is the sum of 15 and 27, and explain your reasoning?"
    ):
        chunks.append(chunk)
        print(chunk, end="", flush=True)
    print("\nFinal response:", "".join(chunks))
    
    print("\n=== Step-by-Step (3 steps) ===")
    chunks = []
    async for chunk in client.reason(
        "How do you make a peanut butter and jelly sandwich?",
        steps=3
    ):
        chunks.append(chunk)
        print(chunk, end="", flush=True)
    print("\nFinal response:", "".join(chunks))
    
    print("\n=== Chain of Thought ===")
    chunks = []
    async for chunk in client.reason(
        "If it takes 10 minutes to boil an egg, how long will it take to boil 4 eggs?",
        chain_of_thought=True
    ):
        chunks.append(chunk)
        print(chunk, end="", flush=True)
    print("\nFinal response:", "".join(chunks))
    
    print("\n=== Structured Output ===")
    client = ReasoningClient(api_key, structured_output=True)
    chunks = []
    async for chunk in client.reason(
        "What is 7 * 8 and explain your reasoning?"
    ):
        chunks.append(chunk)
        print(chunk, end="", flush=True)
    print("\nFinal response (parsed):")
    print(json.dumps(json.loads("".join(chunks)), indent=2))
    
    print("\n=== Few-Shot Learning ===")
    examples = [
        {
            "question": "What is 2 + 3?",
            "reasoning": "To add 2 and 3, I combine the quantities: 2 units plus 3 units equals 5 units.",
            "answer": "The answer is 5."
        }
    ]
    client = ReasoningClient(api_key)
    chunks = []
    async for chunk in client.reason(
        "What is 7 + 9?",
        examples=examples
    ):
        chunks.append(chunk)
        print(chunk, end="", flush=True)
    print("\nFinal response:", "".join(chunks))
    
    print("\n=== Usage Statistics ===")
    stats = client.usage_stats
    print(f"Total tokens: {stats['total_tokens']}")
    print(f"Total cost: ${stats['total_cost']:.4f}")
    print(f"Total requests: {stats['requests']}")

if __name__ == "__main__":
    asyncio.run(main()) 