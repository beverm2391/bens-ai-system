"""Tests for the CodeAgent class."""
import pytest
import asyncio
from src.agents.code_agent import CodeAgent
from src.agents.toolbox import Tool

@pytest.fixture
def mock_sync_tool():
    """Fixture providing a simple synchronous addition tool."""
    return Tool(
        name="add_numbers",
        func=lambda x, y: x + y,
        description="Add two numbers together"
    )

@pytest.fixture
async def mock_async_tool():
    """Fixture providing a simple asynchronous multiplication tool."""
    async def async_multiply(x, y):
        await asyncio.sleep(0.1)  # Simulate async work
        return x * y
    
    return Tool(
        name="multiply_numbers",
        func=async_multiply,
        description="Multiply two numbers together"
    )

@pytest.fixture
def agent(mock_sync_tool):
    """Fixture providing a CodeAgent instance with a sync tool."""
    return CodeAgent(tools=[mock_sync_tool])

@pytest.mark.asyncio
async def test_sync_tool_execution():
    """Test execution of synchronous tools."""
    agent = CodeAgent(tools=[
        Tool(
            name="add_numbers",
            func=lambda x, y: x + y,
            description="Add two numbers together"
        )
    ])
    
    code = """
result = add_numbers(5, 3)
print(f"result = {result}")
"""
    output = await agent.execute(code)
    assert "result = 8" in output

@pytest.mark.asyncio
async def test_state_persistence():
    """Test that state persists between executions."""
    agent = CodeAgent()
    
    # First execution
    code1 = """
x = 42
result = x * 2
print(f"x = {x}")
print(f"result = {result}")
"""
    output1 = await agent.execute(code1)
    assert "x = 42" in output1
    assert "result = 84" in output1
    
    # Second execution should have access to previous state
    code2 = """
result = x + 8
print(f"result = {result}")
"""
    output2 = await agent.execute(code2)
    assert "result = 50" in output2

@pytest.mark.asyncio
async def test_error_handling():
    """Test that execution errors are properly handled."""
    agent = CodeAgent(tools=[
        Tool(
            name="divide",
            func=lambda x, y: x / y,
            description="Divide two numbers"
        )
    ])
    
    code = """
result = divide(10, 0)
"""
    with pytest.raises(ValueError, match=".*division by zero.*"):
        await agent.execute(code) 