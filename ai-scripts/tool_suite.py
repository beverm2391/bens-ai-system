#!/usr/bin/env python3
"""
AI script for using multiple tools with Claude.
"""
import os
import sys
import json
import asyncio
import subprocess
from typing import Dict, Any, Optional, List
from src.clients.anthropic_client import AnthropicClient
from src.clients.notification_client import NotificationClient
from tools.tool_executor import ToolExecutor

# Tool definitions
NOTIFICATION_SCHEMA = {
    "type": "object",
    "properties": {
        "message": {
            "type": "string",
            "description": "The notification message to display to the user"
        },
        "title": {
            "type": "string",
            "description": "The notification title",
            "default": "AI System"
        },
        "subtitle": {
            "type": "string",
            "description": "Optional subtitle text",
            "default": ""
        },
        "style": {
            "type": "string",
            "enum": ["alert", "banner"],
            "description": "Notification style - alert for modal dialog, banner for notification center",
            "default": "banner"
        }
    },
    "required": ["message"]
}

SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "The search query"
        },
        "num_results": {
            "type": "integer",
            "description": "Number of results to return",
            "default": 10
        },
        "include_domains": {
            "type": "string",
            "description": "Comma-separated list of domains to include",
            "default": ""
        },
        "exclude_domains": {
            "type": "string",
            "description": "Comma-separated list of domains to exclude",
            "default": ""
        }
    },
    "required": ["query"]
}

SCRAPE_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "description": "The URL to scrape"
        }
    },
    "required": ["url"]
}

def handle_notification(**kwargs) -> Dict[str, str]:
    """Handle notification tool calls"""
    NotificationClient.notify(**kwargs)
    return {"status": "success"}

def handle_search(**kwargs) -> Dict[str, Any]:
    """Handle web search tool calls"""
    cmd = ["python", "ai-scripts/serp_search.py"]
    if kwargs.get("num_results"):
        cmd.extend(["-n", str(kwargs["num_results"])])
    if kwargs.get("include_domains"):
        cmd.extend(["-i", kwargs["include_domains"]])
    if kwargs.get("exclude_domains"):
        cmd.extend(["-e", kwargs["exclude_domains"]])
    cmd.append(kwargs["query"])
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"status": "success", "results": json.loads(result.stdout)}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": str(e), "stderr": e.stderr}

def handle_scrape(**kwargs) -> Dict[str, Any]:
    """Handle web scraping tool calls"""
    cmd = ["python", "ai-scripts/firecrawl_search.py", "scrape", kwargs["url"]]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return {"status": "success", "content": result.stdout}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "error": str(e), "stderr": e.stderr}

async def main():
    """Run the tool suite."""
    if len(sys.argv) < 2:
        print("Usage: tool_suite.py <prompt>")
        return 1
        
    # Get prompt from command line
    prompt = sys.argv[1]
    
    # Initialize tool executor and register tools
    executor = ToolExecutor()
    
    # Register tools from simplest to most complex
    executor.register_tool(
        name="send_notification",
        description="Send a notification to the user. Use banner style for regular updates and alert style for important messages that require attention.",
        input_schema=NOTIFICATION_SCHEMA,
        handler=handle_notification
    )
    
    executor.register_tool(
        name="web_search",
        description="Search the web using SERP API. Returns structured results including titles, snippets, and URLs.",
        input_schema=SEARCH_SCHEMA,
        handler=handle_search
    )
    
    executor.register_tool(
        name="scrape_webpage",
        description="Scrape content from a webpage. Returns the text content of the page.",
        input_schema=SCRAPE_SCHEMA,
        handler=handle_scrape
    )
    
    # Initialize Claude client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY environment variable is required", file=sys.stderr)
        return 1
        
    client = AnthropicClient(api_key=api_key)
    
    # Get tool schemas and handlers from executor
    tools = executor.get_all_tool_schemas()
    tool_handlers = executor.get_tool_handlers()
    
    # Add context to the prompt
    full_prompt = f"""You are a helpful AI assistant with access to multiple tools:

1. send_notification: Send macOS notifications (use sparingly, only when explicitly asked)
2. web_search: Search the web for information
3. scrape_webpage: Get content from a specific webpage

You can use these tools in combination. For example:
1. Search for relevant pages
2. Scrape the most relevant page
3. Send a notification with your findings

You can also use the results from one tool as input to another.
Always explain what you're planning to do before using tools.

User request: {prompt}"""
    
    # Stream the response
    try:
        async for chunk in client.stream(
            full_prompt,
            tools=tools,
            tool_handlers=tool_handlers,
            temperature=0.7  # Higher temperature for more creative tool use
        ):
            print(chunk, end="", flush=True)
        return 0
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 