"""Tests for the CodeAgent class."""
import pytest
import asyncio
from src.agents.code_agent import CodeAgent

@pytest.mark.asyncio
async def test_validate_code_with_allowed_imports():
    """Test code validation with allowed imports."""
    agent = CodeAgent()
    code = """
import json
import os
result = json.dumps(os.getcwd())
"""
    is_valid, message = agent.validate_code(code)
    assert is_valid
    assert message == ""

@pytest.mark.asyncio
async def test_validate_code_with_disallowed_imports():
    """Test code validation with disallowed imports."""
    agent = CodeAgent()
    code = """
import requests  # Not in base_imports
response = requests.get('https://example.com')
"""
    is_valid, message = agent.validate_code(code)
    assert not is_valid
    assert "requests" in message
    assert "is not allowed" in message

@pytest.mark.asyncio
async def test_execute_maintains_state():
    """Test that state persists between executions."""
    agent = CodeAgent()
    
    # First execution - print assignments for state tracking
    code1 = """x = 42
print(f"x = {x}")
y = x * 2
print(f"y = {y}")"""
    output1 = await agent.execute(code1)
    assert "42" in output1
    assert "84" in output1
    
    # Second execution should have access to previous state
    code2 = """z = x + y
print(f"z = {z}")"""
    output2 = await agent.execute(code2)
    assert "126" in output2

@pytest.mark.asyncio
async def test_execute_with_invalid_code():
    """Test execution with invalid Python code."""
    agent = CodeAgent()
    code = "this is not valid python"
    with pytest.raises(ValueError) as exc:
        await agent.execute(code)
    assert "SyntaxError" in str(exc.value)

@pytest.mark.asyncio
async def test_generate_code():
    """Test code generation from prompt."""
    agent = CodeAgent()
    code = await agent.generate("Write code to add 2 and 2")
    assert isinstance(code, str)
    is_valid, _ = agent.validate_code(code)
    assert is_valid

@pytest.mark.asyncio
async def test_run_workflow():
    """Test the full run workflow."""
    agent = CodeAgent()
    response = await agent.run("Calculate 6 times 7")
    assert "42" in response.lower()  # Response should mention the result 