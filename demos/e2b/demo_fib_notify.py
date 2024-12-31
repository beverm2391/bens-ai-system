#!/usr/bin/env python3
"""
Demo script showing Claude using multiple tools: E2B, SERP search, and notifications.
"""
import os
import logging
from dotenv import load_dotenv
from anthropic import Anthropic

# Import tools and schemas
from src.tools.tool_executor import ToolExecutor
from src.tools.e2b_tool import run_code
from src.tools.serp_tool import search_web
from src.tools.notify import handle_notification
from src.tools.config import (
    E2B_SCHEMA,
    NOTIFICATION_SCHEMA,
    SEARCH_SCHEMA
)

# Maximum number of tool calls to prevent infinite loops
MAX_TOOL_CALLS = 10

# Configure logging based on DEBUG_LEVEL
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
    logging.getLogger("e2b").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def handle_tool_error(tool_name: str, error: Exception) -> None:
    """Handle tool errors by logging and notifying"""
    error_msg = f"Tool {tool_name} failed: {str(error)}"
    logger.error(error_msg)
    try:
        handle_notification(
            message=error_msg,
            title="Tool Error",
            style="alert"
        )
    except Exception as e:
        logger.error(f"Failed to send error notification: {e}")

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize tool executor and register tools
    print("\nInitializing tools...")
    executor = ToolExecutor()
    
    # Register all tools
    executor.register_tool(
        name="execute_code",
        description=E2B_SCHEMA["description"],
        input_schema=E2B_SCHEMA,
        handler=run_code
    )
    executor.register_tool(
        name="search_web",
        description=SEARCH_SCHEMA["description"],
        input_schema=SEARCH_SCHEMA,
        handler=search_web
    )
    executor.register_tool(
        name="send_notification",
        description=NOTIFICATION_SCHEMA["description"],
        input_schema=NOTIFICATION_SCHEMA,
        handler=handle_notification
    )
    
    # Initialize Claude client
    client = Anthropic()
    
    # Updated prompt to use web search
    prompt = """You have access to these tools:
    1. execute_code: Run Python code in a sandbox
    2. search_web: Search the web using SERP API
    3. send_notification: Send system notifications to the user
    
    Please:
    1. Search for "python fibonacci sequence visualization matplotlib" and find an interesting example
    2. Write and execute code to create a similar visualization for the first 10 Fibonacci numbers using matplotlib
       (do not use turtle graphics as there is no display available)
    3. Send notifications about your progress
    
    Use the appropriate tool for each task.
    
    Important: 
    - You have a maximum of 10 tool calls available. Use them wisely.
    - If a tool returns an error, the demo will stop.
    - Always include a clear message when using the notification tool.
    - When writing code, use matplotlib to create visualizations and save to file."""
    
    print("\nAsking Claude to search and create visualization...")
    print("-" * 50)
    
    # Get tool schemas from executor
    tools = executor.get_all_tool_schemas()
    
    # Let Claude choose which tool to use
    message = client.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        tools=tools
    )
    
    # Handle tool calls with maximum limit
    tool_calls = 0
    while message.stop_reason == "tool_use" and tool_calls < MAX_TOOL_CALLS:
        tool_calls += 1
        print(f"\nTool call {tool_calls}/{MAX_TOOL_CALLS}")
        
        tool_use = next(block for block in message.content if block.type == "tool_use")
        tool_name = tool_use.name
        tool_input = tool_use.input
        
        try:
            if tool_name == "execute_code":
                print("\nExecuting visualization code...")
                result = run_code(**tool_input)
                if result.get("stderr"):
                    print(f"Code error: {result['stderr']}")
                else:
                    print(f"Result: {result['stdout']}")
            elif tool_name == "search_web":
                print("\nSearching the web...")
                result = search_web(**tool_input)
                if result["status"] == "error":
                    raise Exception(result["message"])
                print(f"Found {len(result['results'])} results")
            elif tool_name == "send_notification":
                print("\nSending notification...")
                result = handle_notification(**tool_input)
                if result["status"] != "success":
                    raise Exception("Notification failed")
            
            # Send the result back to Claude
            message = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1024,
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
            handle_tool_error(tool_name, e)
            break
    
    if tool_calls >= MAX_TOOL_CALLS:
        print(f"\nReached maximum tool calls limit ({MAX_TOOL_CALLS})")
        try:
            handle_notification(
                message="Demo stopped: Reached maximum number of tool calls",
                style="alert"
            )
        except Exception as e:
            logger.error(f"Failed to send limit notification: {e}")
    
    print("\nDemo completed!")
    print("-" * 50)

if __name__ == "__main__":
    main() 