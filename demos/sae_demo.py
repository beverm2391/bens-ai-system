#!/usr/bin/env python3
"""
Demo script showing Claude using multiple tools to:
1. Find and read the Anthropic SAE paper
2. Use O1 to plan an implementation
3. Generate Python code
"""
import os
import logging
from dotenv import load_dotenv
from anthropic import Anthropic

# Import tools and schemas
from src.tools.tool_executor import ToolExecutor, ToolLimits
from src.tools.serp_tool import search_web
from src.tools.firecrawl_tool import scrape_page, crawl_site
from src.tools.o1_tool import reason_about
from src.tools.config import (
    SEARCH_SCHEMA,
    SCRAPE_SCHEMA,
    CRAWL_SCHEMA,
    O1_SCHEMA
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
            max_calls=5,
            calls_per_minute=2,
            cooldown_seconds=1,
            reset_interval="hourly"
        )
    )
    
    # Register scraping tool with limits
    executor.register_tool(
        name="scrape_page",
        description=SCRAPE_SCHEMA["description"],
        input_schema=SCRAPE_SCHEMA,
        handler=scrape_page,
        limits=ToolLimits(
            max_calls=3,
            calls_per_minute=1,
            cooldown_seconds=2,
            reset_interval="hourly"
        )
    )
    
    # Register crawling tool with limits
    executor.register_tool(
        name="crawl_site",
        description=CRAWL_SCHEMA["description"],
        input_schema=CRAWL_SCHEMA,
        handler=crawl_site,
        limits=ToolLimits(
            max_calls=1,  # Crawling is expensive
            calls_per_minute=1,
            cooldown_seconds=5,
            reset_interval="hourly"
        )
    )
    
    # Register O1 reasoning tool with limits
    executor.register_tool(
        name="reason_about",
        description=O1_SCHEMA["description"],
        input_schema=O1_SCHEMA,
        handler=reason_about,
        limits=ToolLimits(
            max_calls=2,  # Planning is expensive
            calls_per_minute=1,
            cooldown_seconds=5,
            reset_interval="hourly"
        )
    )
    
    # Initialize Claude client
    client = Anthropic()
    
    # Prompt for SAE implementation
    prompt = """You have access to these tools:
    1. search_web: Search for web content
    2. scrape_page: Extract content from a specific page
    3. crawl_site: Crawl an entire site for content
    4. reason_about: Use O1 for implementation planning
    
    Please help me understand and implement the Anthropic SAE (Scalable Alignment by Example) approach:
    
    1. Search for and locate the Anthropic SAE paper
    2. Extract the key technical details using scraping/crawling
    3. Use O1 to analyze and plan a Python implementation
    4. Write example Python code that demonstrates the core concepts
    
    Focus on:
    - The core SAE training approach
    - Key algorithms and techniques
    - Data structures and interfaces
    - Error handling and edge cases
    
    Important notes:
    - Explain your process at each step
    - Include clear code comments
    - Focus on clean, maintainable code
    - DO NOT execute the code, just return it
    """
    
    print("\nStarting SAE exploration...")
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
            elif tool_name == "scrape_page":
                print(f"\nScraped content from {result['url']}")
            elif tool_name == "crawl_site":
                print(f"\nCrawled site starting at {result['url']}")
                if result.get("content", {}).get("linked_pages"):
                    print(f"Found {len(result['content']['linked_pages'])} related pages")
            elif tool_name == "reason_about":
                print("\nO1 analysis complete")
                if result.get("reasoning", {}).get("steps"):
                    print(f"Generated {len(result['reasoning']['steps'])} reasoning steps")
            
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