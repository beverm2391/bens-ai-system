"""
Tool management system with decorator support.
Allows tools to be defined using @tool decorator or added manually.
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
    """
    Manages a collection of tools that can be used by the agent.
    Tools can be added via decorator or manually.
    """
    _instance = None
    
    def __new__(cls):
        """Singleton pattern to ensure all decorators use the same toolbox."""
        if cls._instance is None:
            cls._instance = super(Toolbox, cls).__new__(cls)
            cls._instance.tools = {}
        return cls._instance
    
    def __init__(self):
        """Initialize toolbox if not already initialized."""
        if not hasattr(self, 'tools'):
            self.tools: Dict[str, Tool] = {}
    
    def add_tool(self, tool: Tool):
        """Add a tool to the toolbox."""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """Get a tool by name."""
        return self.tools.get(name)
    
    def execute_tool(self, name: str, *args, **kwargs) -> Any:
        """Execute a tool by name with given arguments."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool {name} not found")
        return tool.func(*args, **kwargs)

def tool(name: Optional[str] = None, description: Optional[str] = None):
    """
    Decorator to register a function as a tool.
    
    Args:
        name: Optional name for the tool. If not provided, uses function name
        description: Optional description. If not provided, uses docstring
        
    Example:
        @tool(description="Add two numbers")
        def add(x, y):
            return x + y
            
        @tool("multiply", "Multiply two numbers")
        def mult(x, y):
            return x * y
    """
    def decorator(func: Callable) -> Callable:
        # Get tool name
        tool_name = name or func.__name__
        
        # Get description from argument or docstring
        tool_description = description or func.__doc__ or f"Execute {tool_name}"
        
        # Create and register tool
        tool_instance = Tool(
            name=tool_name,
            func=func,
            description=tool_description
        )
        Toolbox().add_tool(tool_instance)
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        return wrapper
    
    # Handle case where decorator is used without parentheses
    if callable(name):
        func = name
        name = None
        return decorator(func)
    
    return decorator