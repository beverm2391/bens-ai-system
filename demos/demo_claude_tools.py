#!/usr/bin/env python3
"""
Demo script showing Claude using multiple tools with usage tracking.
"""
import os
import json
import asyncio
import logging
from src.clients.anthropic_client import AnthropicClient
from src.tools.tool_executor import ToolExecutor
from src.tools.notify import send_notification
from src.tools.serp_tool import search_web
from src.tools.exa_tool import semantic_search
from src.tools.e2b_tool import run_code
from src.tools.config import (
    NOTIFICATION_SCHEMA,
    SEARCH_SCHEMA,
    E2B_SCHEMA
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def print_usage_metrics(tool_name: str, result: dict):
    """Print usage metrics for a tool execution"""
    if "usage" in result:
        print(f"\n{tool_name} Usage Metrics:")
        print(json.dumps(result["usage"], indent=2))

async def main():
    # Initialize the client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    # Initialize tool executor and register tools
    executor = ToolExecutor()
    
    # Register notification tool
    executor.register_tool(
        name="send_notification",
        description=NOTIFICATION_SCHEMA["description"],
        input_schema=NOTIFICATION_SCHEMA,
        handler=send_notification
    )
    
    # Register search tools
    executor.register_tool(
        name="search_web",
        description=SEARCH_SCHEMA["description"],
        input_schema=SEARCH_SCHEMA,
        handler=search_web
    )
    
    executor.register_tool(
        name="semantic_search",
        description="Perform semantic search using Exa API",
        input_schema={
            "type": "object",
            "properties": {
                "query": {"type": "string"},
                "num_results": {"type": "integer", "default": 10},
                "search_type": {"type": "string", "enum": ["neural", "keyword"], "default": "neural"},
                "include_domains": {"type": "string"},
                "exclude_domains": {"type": "string"}
            },
            "required": ["query"]
        },
        handler=semantic_search
    )
    
    # Register code execution tool
    executor.register_tool(
        name="execute_code",
        description=E2B_SCHEMA["description"],
        input_schema=E2B_SCHEMA,
        handler=run_code
    )
    
    # Initialize Claude client
    client = AnthropicClient(api_key=api_key)
    
    # Example prompt that will use multiple tools
    prompt = """You are a helpful AI assistant with access to multiple tools:
    - System notifications
    - Web search (both keyword and semantic)
    - Code execution
    
    Please demonstrate your capabilities by:
    1. Searching for information about the Fibonacci sequence
    2. Writing and executing code to calculate the 10th Fibonacci number
    3. Sending a notification with the result
    
    Between each step, explain what you're doing and show the usage metrics."""
    
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
            
            # If chunk contains tool result, print usage metrics
            if isinstance(chunk, dict) and "tool_calls" in chunk:
                for call in chunk["tool_calls"]:
                    if "result" in call:
                        print_usage_metrics(call["name"], call["result"])
                    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        # Send error notification
        try:
            result = send_notification(
                message=f"Demo failed: {str(e)}",
                title="Demo Error",
                style="alert"
            )
            print_usage_metrics("error_notification", result)
        except Exception as notify_error:
            logger.error(f"Failed to send error notification: {notify_error}")

if __name__ == "__main__":
    asyncio.run(main()) 