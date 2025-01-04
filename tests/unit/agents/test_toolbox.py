"""Tests for the toolbox and tool decorator."""
import pytest
from src.agents.toolbox import Toolbox, tool as tool_decorator, Tool

def test_manual_tool_creation():
    """Test creating and using a tool manually."""
    toolbox = Toolbox()
    
    def add(x, y):
        return x + y
        
    tool_instance = Tool(
        name="add",
        func=add,
        description="Add two numbers"
    )
    
    toolbox.add_tool(tool_instance)
    tool = toolbox.get_tool("add")
    assert tool.func(5, 3) == 8

def test_tool_decorator_basic():
    """Test basic tool decorator usage."""
    toolbox = Toolbox()
    
    @tool_decorator
    def subtract(x, y):
        """Subtract two numbers."""
        return x - y
    
    tool = toolbox.get_tool("subtract")
    assert tool.func(5, 3) == 2
    assert tool.description == "Subtract two numbers."

def test_tool_decorator_with_params():
    """Test tool decorator with explicit parameters."""
    toolbox = Toolbox()
    
    @tool_decorator(name="mult", description="Multiply two numbers")
    def multiply(x, y):
        return x * y
    
    tool = toolbox.get_tool("mult")
    assert tool.func(4, 3) == 12
    assert tool.name == "mult"
    assert tool.description == "Multiply two numbers"

def test_toolbox_singleton():
    """Test that all toolbox instances share the same tools."""
    @tool_decorator
    def add(x, y):
        """Add two numbers."""
        return x + y
    
    toolbox1 = Toolbox()
    toolbox2 = Toolbox()
    
    assert toolbox1.get_tool("add") is toolbox2.get_tool("add")
    assert toolbox1.get_tool("add").func(5, 3) == 8

def test_tool_not_found():
    """Test error handling for non-existent tools."""
    toolbox = Toolbox()
    assert toolbox.get_tool("nonexistent") is None