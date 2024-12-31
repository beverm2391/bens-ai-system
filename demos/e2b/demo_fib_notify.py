#!/usr/bin/env python3
"""
Demo script showing Claude using both E2B and notification tools.
"""
import os
import logging
from dotenv import load_dotenv
from anthropic import Anthropic
from src.tools.tool_executor import ToolExecutor
from src.tools.e2b_tool import run_code, E2B_SCHEMA
from src.clients.notification_client import NotificationClient

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

# Tool definition for notifications
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

def handle_notification(**kwargs):
    """Handle notification tool calls from Claude"""
    NotificationClient.notify(**kwargs)
    return {"status": "success"}

def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize tool executor and register tools
    print("\nInitializing tools...")
    executor = ToolExecutor()
    executor.register_tool(
        name="execute_code",
        description=E2B_SCHEMA["description"],
        input_schema=E2B_SCHEMA["input_schema"],
        handler=run_code
    )
    executor.register_tool(
        name="send_notification",
        description="Send a notification to the user. Use banner style for regular updates.",
        input_schema=NOTIFICATION_SCHEMA,
        handler=handle_notification
    )
    
    # Initialize Claude client
    client = Anthropic()
    
    # Prompt for Claude to write and execute Fibonacci, then notify
    prompt = """You have access to two tools:
    1. execute_code: Run Python code in a sandbox
    2. send_notification: Send system notifications to the user
    
    Please:
    1. Write and execute a simple iterative Fibonacci function that calculates the nth number
    2. Calculate the 10th Fibonacci number
    3. Send a banner notification with the result
    
    Use the appropriate tool for each task."""
    
    print("\nAsking Claude to write and execute Fibonacci function...")
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
    
    # Handle tool calls
    while message.stop_reason == "tool_use":
        tool_use = next(block for block in message.content if block.type == "tool_use")
        tool_name = tool_use.name
        tool_input = tool_use.input
        
        if tool_name == "execute_code":
            print("\nExecuting Fibonacci code...")
            result = run_code(**tool_input)
            print(f"Result: {result['stdout']}")
        elif tool_name == "send_notification":
            print("\nSending notification...")
            result = handle_notification(**tool_input)
        
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
    
    print("\nDemo completed!")
    print("-" * 50)

if __name__ == "__main__":
    main() 