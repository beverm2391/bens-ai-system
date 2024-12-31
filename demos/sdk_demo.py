#!/usr/bin/env python3
"""
Demo script showing Claude using multiple tools to:
1. Search for an SDK
2. Scrape its documentation
3. Generate example code based on the docs
"""
import os
import logging
from dotenv import load_dotenv
from anthropic import Anthropic

# Import tools and schemas
from src.tools.tool_executor import ToolExecutor, ToolLimits
from src.tools.serp_tool import search_web
from src.tools.firecrawl_tool import crawl_page
from src.tools.config import (
    SEARCH_SCHEMA,
    FIRECRAWL_SCHEMA
)

# Configure logging
debug_level = int(os.getenv("DEBUG_LEVEL", "0"))
logging.basicConfig(
    level=logging.DEBUG if debug_level > 0 else logging.WARNING,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Suppress httpx logging unless in debug mode
if debug_level == 0:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("anthropic").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize tool executor and register tools
    print("\nInitializing tools...")
    executor = ToolExecutor()
    
    # Register search tool with limits
    executor.register_tool(
        name="search_web",
        description=SEARCH_SCHEMA["description"],
        input_schema=SEARCH_SCHEMA,
        handler=search_web,
        limits=ToolLimits(
            max_calls=10,
            calls_per_minute=2,
            cooldown_seconds=1,
            reset_interval="hourly"
        )
    )
    
    # Register firecrawl tool with limits
    executor.register_tool(
        name="crawl_docs",
        description=FIRECRAWL_SCHEMA["description"],
        input_schema=FIRECRAWL_SCHEMA,
        handler=crawl_page,
        limits=ToolLimits(
            max_calls=5,
            calls_per_minute=1,
            cooldown_seconds=2,
            reset_interval="hourly"
        )
    )
    
    # Initialize Claude client
    client = Anthropic()
    
    # Example prompt for SDK exploration
    prompt = """You are a helpful AI assistant with access to web search and documentation crawling capabilities.

Please help me explore and understand how to use the 'stripe' Python SDK by:

1. Searching for the official Stripe Python SDK documentation
2. Crawling the relevant documentation pages
3. Writing example Python code that demonstrates:
   - Installing the SDK
   - Basic setup and authentication
   - A simple payment integration

Important notes:
- Focus on the latest stable version
- Include proper error handling
- Follow Python best practices
- Add helpful comments
- DO NOT execute the code, just return it

Use the appropriate tool for each task and explain your process."""
    
    print("\nStarting SDK exploration...")
    print("-" * 50)
    
    # Get tool schemas from executor
    tools = executor.get_all_tool_schemas()
    
    # Let Claude choose which tool to use
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=4096,  # Increased for longer code generation
        messages=[{"role": "user", "content": prompt}],
        tools=tools
    )
    
    # Handle tool calls
    while message.stop_reason == "tool_use":
        tool_use = next(block for block in message.content if block.type == "tool_use")
        tool_name = tool_use.name
        tool_input = tool_use.input
        
        try:
            # Execute tool and get result
            result = executor.execute_tool(tool_name, **tool_input)
            
            # Print progress
            if tool_name == "search_web":
                print(f"\nFound {len(result['results'])} search results")
            elif tool_name == "crawl_docs":
                print(f"\nCrawled documentation from {result['url']}")
                if result.get("linked_pages"):
                    print(f"Found {len(result['linked_pages'])} related pages")
            
            # Send result back to Claude
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=4096,
                messages=[
                    {"role": "user", "content": prompt},
                    {"role": "assistant", "content": message.content},
                    {
                        "role": "user", 
                        "content": [{
                            "type": "tool_result",
                            "tool_use_id": tool_use.id,
                            "content": str(result)
                        }]
                    }
                ],
                tools=tools
            )
            
        except Exception as e:
            print(f"\nError: {str(e)}")
            break
    
    # Print final response with example code
    print("\nGenerated Code:")
    print("-" * 50)
    print(message.content[0].text)
    
    # Print tool usage statistics
    print("\nTool Usage Statistics:")
    print("-" * 50)
    for name, usage in executor.get_all_tool_usage().items():
        print(f"\n{name}:")
        print(f"  Total calls: {usage.total_calls}")
        print(f"  Successful: {usage.successful_calls}")
        print(f"  Failed: {usage.failed_calls}")
        print(f"  Total cost: ${usage.total_cost:.2f}")

if __name__ == "__main__":
    main() 