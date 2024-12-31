"""
Demo of metrics tracking capabilities.
"""
import time
import json
from datetime import datetime, timedelta
from typing import Dict, Any

from src.tools.tool_executor import ToolExecutor
from src.observability.metrics import MetricsTracker

# Mock tool handlers
def search_web(query: str) -> Dict[str, Any]:
    """Mock web search tool"""
    time.sleep(0.5)  # Simulate latency
    return {
        "results": [f"Result for {query}"],
        "usage": {
            "queries": 1
        }
    }

def execute_code(code: str) -> Dict[str, Any]:
    """Mock code execution tool"""
    time.sleep(2.0)  # Simulate longer execution time
    return {
        "result": f"Executed: {code}",
        "usage": {
            "execution_seconds": 2.0
        }
    }

def send_notification(message: str) -> Dict[str, Any]:
    """Mock notification tool - no usage metrics needed"""
    time.sleep(0.1)  # Simulate latency
    return {
        "success": True
    }

def main():
    # Initialize tool executor with metrics tracking
    executor = ToolExecutor(metrics_dir="demo_metrics")
    
    # Register tools with schemas and limits
    executor.register_tool(
        "search_web",
        search_web,
        {
            "type": "object",
            "properties": {
                "query": {"type": "string"}
            },
            "required": ["query"]
        },
        max_invocations=5
    )
    
    executor.register_tool(
        "execute_code",
        execute_code,
        {
            "type": "object",
            "properties": {
                "code": {"type": "string"}
            },
            "required": ["code"]
        },
        max_invocations=3
    )
    
    executor.register_tool(
        "send_notification",
        send_notification,
        {
            "type": "object",
            "properties": {
                "message": {"type": "string"}
            },
            "required": ["message"]
        },
        max_invocations=10
    )
    
    print("Running tool invocations...")
    
    # Execute some tools with metadata
    result = executor.execute_tool(
        "search_web",
        {"query": "python fibonacci"},
        metadata={"purpose": "research"}
    )
    print("- Search web completed")
    print(f"  Usage: {result.get('usage', {})}")
    
    result = executor.execute_tool(
        "execute_code",
        {"code": "print('Hello World')"},
        metadata={"purpose": "testing"}
    )
    print("- Execute code completed")
    print(f"  Usage: {result.get('usage', {})}")
    
    result = executor.execute_tool(
        "send_notification",
        {"message": "Task completed"},
        metadata={"purpose": "status"}
    )
    print("- Send notification completed")
    
    # Try to exceed a tool's limit
    try:
        print("\nTesting execution limits...")
        for i in range(5):
            result = executor.execute_tool(
                "execute_code",
                {"code": f"print({i})"},
                metadata={"iteration": i}
            )
            print(f"- Execute code iteration {i} completed")
            print(f"  Usage: {result.get('usage', {})}")
    except RuntimeError as e:
        print(f"Expected error: {e}")
    
    # Get metrics for different time periods
    now = datetime.now()
    
    # Last hour
    hour_ago = (now - timedelta(hours=1)).isoformat()
    hour_metrics = executor.get_metrics(start_date=hour_ago)
    print("\nTool Metrics (Last Hour):")
    print(json.dumps(hour_metrics, indent=2))
    
    # Last 24 hours (default)
    day_metrics = executor.get_metrics()
    print("\nTool Metrics (Last 24 Hours):")
    print(json.dumps(day_metrics, indent=2))
    
    # Custom range (last 15 minutes)
    minutes_15_ago = (now - timedelta(minutes=15)).isoformat()
    recent_metrics = executor.get_metrics(start_date=minutes_15_ago)
    print("\nTool Metrics (Last 15 Minutes):")
    print(json.dumps(recent_metrics, indent=2))
    
    print("\nTracking LLM interactions...")
    
    # Track some LLM interactions
    metrics_tracker = MetricsTracker(metrics_dir="demo_metrics")
    
    # GPT-4 interaction
    start_time = time.time()
    time.sleep(0.5)  # Simulate LLM latency
    
    metrics_tracker.track_llm_interaction(
        model="gpt-4",
        start_time=start_time,
        prompt_tokens=1000,  # 1K tokens
        completion_tokens=500,  # 500 tokens
        user_prompt="Write a detailed Fibonacci implementation with tests",
        assistant_response="Here's a comprehensive Fibonacci implementation...",
        metadata={"purpose": "code generation"}
    )
    print("- GPT-4 interaction completed")
    
    # GPT-3.5-turbo interaction
    start_time = time.time()
    time.sleep(0.3)  # Simulate LLM latency
    
    metrics_tracker.track_llm_interaction(
        model="gpt-3.5-turbo",
        start_time=start_time,
        prompt_tokens=800,
        completion_tokens=400,
        user_prompt="Explain the Fibonacci sequence",
        assistant_response="The Fibonacci sequence is...",
        metadata={"purpose": "explanation"}
    )
    print("- GPT-3.5 interaction completed")
    
    # Get LLM metrics for last hour
    llm_metrics = metrics_tracker.get_llm_metrics(start_date=hour_ago)
    print("\nLLM Metrics (Last Hour):")
    print(json.dumps(llm_metrics, indent=2))

if __name__ == "__main__":
    main() 