#!/usr/bin/env python3
"""
Basic demo of Claude using E2B tool without streaming.
This is a simplified version to verify tool use flow.
"""
import os
import logging
from dotenv import load_dotenv
from anthropic import Anthropic
from src.tools.tool_executor import ToolExecutor
from src.tools.e2b_tool import run_code, E2B_SCHEMA

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
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
    
    # Initialize Claude client
    client = Anthropic()
    
    # Example prompt that will use code execution
    prompt = """You are a helpful AI assistant with access to code execution capabilities.
    Run this code and tell me the result: print(2 + 2)"""
    
    print("\nStarting Claude code execution demo (basic version)...")
    print("-" * 50)
    
    # Get tool schemas from executor
    tools = executor.get_all_tool_schemas()
    
    # First message to get tool request
    message = client.messages.create(
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
        
        # Send result back to Claude
        final_response = client.messages.create(
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
        
        print("\nFinal Response:")
        print(final_response.content)

if __name__ == "__main__":
    main() 