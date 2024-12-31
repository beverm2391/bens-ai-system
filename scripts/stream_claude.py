#!/usr/bin/env python3
"""
Simple script to stream Claude's responses to the terminal.
"""
import os
import sys
import asyncio
import logging
from src.clients.anthropic_client import AnthropicClient

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    # Get API key from environment
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: Please set the ANTHROPIC_API_KEY environment variable")
        sys.exit(1)
    
    logger.debug(f"API key found (length: {len(api_key)})")
    
    # Initialize client
    try:
        client = AnthropicClient(api_key)
        logger.debug("Client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize client: {str(e)}")
        sys.exit(1)
    
    # Get prompt from command line args or use interactive mode
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        print("Enter your prompt (Ctrl+D to submit):")
        prompt = sys.stdin.read().strip()
        if not prompt:
            print("Error: Empty prompt")
            sys.exit(1)
    
    logger.debug(f"Prompt: {prompt}")
    
    try:
        # Stream response
        print("\nClaude:", end=" ", flush=True)
        async for chunk in client.stream(prompt):
            print(chunk, end="", flush=True)
        print("\n")
        
        # Show usage stats
        stats = client.usage_stats
        print(f"\nUsage Statistics:")
        print(f"Prompt tokens: {stats['prompt_tokens']}")
        print(f"Completion tokens: {stats['completion_tokens']}")
        print(f"Total cost: ${stats['total_cost']:.4f}")
        
    except Exception as e:
        logger.error(f"Error during streaming: {str(e)}")
        print(f"\nError: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 