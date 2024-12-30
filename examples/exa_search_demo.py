"""
Demo script for Exa search integration.
Shows basic search, domain filtering, and error handling.
"""
import asyncio
from src.clients.exa_client import ExaClient, ExaError

async def demo():
    print("=== Exa Search Demo ===\n")
    
    client = ExaClient()
    
    print("1. Basic search:")
    results = await client.search(
        "latest developments in AI safety",
        num_results=2
    )
    print(f"Found {len(results)} results")
    for r in results:
        print(f"\nTitle: {r.get('title')}")
        print(f"URL: {r.get('url')}")
        print(f"Highlights: {r.get('highlights')[:1]}")
    print("\nUsage stats:", client.usage_stats)
    
    print("\n2. Domain-filtered search:")
    results = await client.search(
        "AI news",
        num_results=2,
        include_domains=["techcrunch.com"]
    )
    print(f"Found {len(results)} TechCrunch results")
    for r in results:
        print(f"\nTitle: {r.get('title')}")
        print(f"URL: {r.get('url')}")
    
    print("\n3. Error handling:")
    try:
        await client.search("")  # Empty query
        print("Should have raised error!")
    except ExaError as e:
        print(f"Caught expected error: {e}")

if __name__ == "__main__":
    asyncio.run(demo()) 