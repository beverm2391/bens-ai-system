#!/usr/bin/env python3
"""
AI script for sending notifications using Claude.
"""
import os
import sys
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
    """Run the notification script."""
    if len(sys.argv) < 2:
        print("Usage: notify.py <prompt>")
        return 1
        
    # Get prompt from command line
    prompt = sys.argv[1]
    
    # Initialize tool executor and register tools
    executor = ToolExecutor()
    executor.register_tool(
        name="send_notification",
        description="Send a notification to the user. Use banner style for regular updates and alert style for important messages that require attention.",
        input_schema=NOTIFICATION_SCHEMA,
        handler=handle_notification
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
    full_prompt = f"""You are a helpful AI assistant with access to system notifications.
    Your task is to send appropriate notifications based on the user's request.
    Use banner style for regular updates and alert style for important messages.
    
    User request: {prompt}"""
    
    # Stream the response
    try:
        async for chunk in client.stream(
            full_prompt,
            tools=tools,
            tool_handlers=tool_handlers,
            temperature=0.7
        ):
            print(chunk, end="", flush=True)
        return 0
    except Exception as e:
        print(f"\nError: {str(e)}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(asyncio.run(main())) 