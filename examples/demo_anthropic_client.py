"""
Demo script for AnthropicClient showing streaming, system prompts, and parameter control.
"""
import os
import asyncio
from src.clients.anthropic_client import AnthropicClient

# Set debug level to see detailed output
os.environ["DEBUG_LEVEL"] = "1"

async def main():
    # Initialize client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Please set ANTHROPIC_API_KEY environment variable")
        return
    
    client = AnthropicClient(api_key)
    
    print("\n=== Basic Streaming ===")
    chunks = []
    async for chunk in client.stream("Say 'hello' and nothing else"):
        chunks.append(chunk)
        print(chunk, end="", flush=True)
    print("\nFinal response:", "".join(chunks))
    
    print("\n=== System Prompt ===")
    chunks = []
    async for chunk in client.stream(
        "What are you?",
        system="You are a friendly robot. Keep responses under 50 words."
    ):
        chunks.append(chunk)
        print(chunk, end="", flush=True)
    print("\nFinal response:", "".join(chunks))
    
    print("\n=== Parameter Control ===")
    chunks = []
    async for chunk in client.stream(
        "Write a creative story about a cat.",
        max_tokens=100,
        temperature=0.9,
        top_p=0.9
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