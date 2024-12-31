#!/usr/bin/env python3
"""
Demo script showing Claude using the E2B tool for code execution.
"""
import os
import asyncio
import logging
from dotenv import load_dotenv
from anthropic import Anthropic
from src.clients.anthropic_client import AnthropicClient
from src.tools.tool_executor import ToolExecutor
from src.tools.e2b_tool import run_code, E2B_SCHEMA
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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
        name="execute_code",
        description=E2B_SCHEMA["description"],
        input_schema=E2B_SCHEMA["input_schema"],
        handler=run_code
    )
    
    # Initialize clients
    anthropic = Anthropic()  # For direct calls
    stream_client = AnthropicClient(api_key=api_key)  # For streaming
    
    # Example prompt that will use code execution
    prompt = """You are a helpful AI assistant with access to code execution capabilities.
    Run this code and tell me the result: print(2 + 2)"""
    
    print("\nStarting Claude code execution demo...")
    print("-" * 50)
    
    # Get tool schemas from executor
    tools = executor.get_all_tool_schemas()
    
    # First message to get tool request (direct)
    message = anthropic.messages.create(
        model="claude-3-sonnet-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
        tools=tools
    )
    
    print("\nInitial Response:")
    print(f"Stop Reason: {message.stop_reason}")
    print(f"Content: {message.content}")
    
    # If tool was used, send result back
    if message.stop_reason == "tool_use":
        tool_use = next(block for block in message.content if block.type == "tool_use")
        tool_name = tool_use.name
        tool_input = tool_use.input
        
        print(f"\nTool Used: {tool_name}")
        print(f"Tool Input: {tool_input}")
        
        # Execute tool
        result = run_code(**tool_input)
        print(f"\nTool Result: {result}")
        
        # Stream final response back to user
        print("\nFinal Response (streamed):")
        
        # Build message content
        message_content = f"""I executed the code print(2 + 2) and got the following result:
        {str(result)}
        
        Please explain what happened in simple terms."""
        
        async for chunk in stream_client.stream(
            message_content,
            system="You are a helpful AI assistant. Explain the code execution result clearly.",
            tools=tools,
            tool_handlers=executor.get_tool_handlers(),
            temperature=0.7
        ):
            if isinstance(chunk, str):
                print(chunk, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(main()) 