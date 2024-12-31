#!/usr/bin/env python3
"""
Demo script showing Claude 3.5 Sonnet tool use with notifications.
"""
import os
import asyncio
from src.clients.anthropic_client import AnthropicClient
from src.clients.notification_client import NotificationClient
from src.executor.tool_executor import ToolExecutor

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

async def main():
    # Initialize the client
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY environment variable is required")
    
    # Initialize tool executor and register tools
    executor = ToolExecutor()
    executor.register_tool(
        name="send_notification",
        description="Send a notification to the user. Use banner style for regular updates and alert style for important messages that require attention.",
        input_schema=NOTIFICATION_SCHEMA,
        handler=handle_notification
    )
    
    # Initialize Claude client
    client = AnthropicClient(api_key=api_key)
    
    # Example prompt that will use notifications
    prompt = """You are a helpful AI assistant with access to system notifications.
    Please demonstrate your ability to send notifications by:
    1. Sending a welcome banner notification
    2. Sending an important alert notification
    3. Sending a final banner notification
    
    Between each notification, explain what you're doing."""
    
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