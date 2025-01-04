"""
Tool management system with decorator support.
"""
from typing import Dict, List, Callable, Any, Optional
from dataclasses import dataclass
import functools

@dataclass
class Tool:
    """A tool that can be used by the agent."""
    name: str
    func: Callable
    description: str

class Toolbox:
    """Manages a collection of tools that can be used by the agent."""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Toolbox, cls).__new__(cls)
            cls._instance.tools = {}
        return cls._instance
    
    def add_tool(self, tool: Tool):
        """Add a tool to the toolbox."""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)

def tool(name: Optional[str] = None, description: Optional[str] = None):
    """
    Decorator to register a function as a tool.
    
    Example:
        @tool(description="Add two numbers")
        def add(x, y):
            return x + y
    """
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        tool_description = description or func.__doc__ or f"Execute {tool_name}"
        
        Toolbox().add_tool(Tool(
            name=tool_name,
            func=func,
            description=tool_description
        ))
        
        return func
    
    # Handle case where decorator is used without parentheses
    if callable(name):
        func = name
        name = None
        return decorator(func)
    
    return decorator