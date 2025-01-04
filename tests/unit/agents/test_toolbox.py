"""Tests for the toolbox and tool decorator."""
import pytest
from src.agents.toolbox import Toolbox, tool, Tool

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
    result = toolbox.execute_tool("add", 5, 3)
    assert result == 8

def test_tool_decorator_basic():
    """Test basic tool decorator usage."""
    toolbox = Toolbox()
    
    @tool
    def subtract(x, y):
        """Subtract two numbers."""
        return x - y
    
    result = toolbox.execute_tool("subtract", 5, 3)
    assert result == 2
    
    tool_info = toolbox.get_tool("subtract")
    assert tool_info.description == "Subtract two numbers."

def test_tool_decorator_with_params():
    """Test tool decorator with explicit parameters."""
    toolbox = Toolbox()
    
    @tool(name="mult", description="Multiply two numbers")
    def multiply(x, y):
        return x * y
    
    result = toolbox.execute_tool("mult", 4, 3)
    assert result == 12
    
    tool_info = toolbox.get_tool("mult")
    assert tool_info.name == "mult"
    assert tool_info.description == "Multiply two numbers"

def test_toolbox_singleton():
    """Test that all toolbox instances share the same tools."""
    @tool
    def add(x, y):
        """Add two numbers."""
        return x + y
    
    toolbox1 = Toolbox()
    toolbox2 = Toolbox()
    
    assert toolbox1.get_tool("add") is toolbox2.get_tool("add")
    assert toolbox1.execute_tool("add", 5, 3) == 8

def test_tool_not_found():
    """Test error handling for non-existent tools."""
    toolbox = Toolbox()
    
    with pytest.raises(ValueError, match="Tool nonexistent not found"):
        toolbox.execute_tool("nonexistent", 1, 2)