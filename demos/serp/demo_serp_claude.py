#!/usr/bin/env python3
"""
Demo script showing Claude using the SERP tool for web searches.
"""
import os
import asyncio
from dotenv import load_dotenv
from src.clients.anthropic_client import AnthropicClient
from src.tools.tool_executor import ToolExecutor
from src.tools.serp_tool import search, SERP_SCHEMA

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize the client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    # Initialize tool executor and register tools
    executor = ToolExecutor()
    executor.register_tool(
        name="web_search",
        description=SERP_SCHEMA["description"],
        input_schema=SERP_SCHEMA["input_schema"],
        handler=search
    )
    
    # Initialize Claude client
    client = AnthropicClient(api_key=api_key)
    
    # Example prompt that will use web search
    prompt = """You are a helpful AI assistant with access to web search capabilities.
    Please demonstrate your ability to search the web by:
    1. Searching for the latest AI developments
    2. Then searching specifically on tech news sites (like techcrunch.com, wired.com)
    3. Summarize the key findings from both searches
    
    Between each search, explain what you're doing and why."""
    
    # Get tool schemas and handlers from executor
    tools = executor.get_all_tool_schemas()
    tool_handlers = executor.get_tool_handlers()
    
    # Stream the response
    try:
        async for chunk in client.stream(
            prompt,
            tools=tools,
            tool_handlers=tool_handlers,
            temperature=0.7
        ):
            print(chunk, end="", flush=True)
    except Exception as e:
        print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 