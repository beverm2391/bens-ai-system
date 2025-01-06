"""
Tool management system with decorator support.

This module provides a way to register and manage tools that can be used by the agent.
Tools are functions that can be registered either manually or using the @register_tool decorator.
The system uses a singleton pattern to ensure all tools are registered in the same toolbox.

Example:
    # Using the decorator
    @register_tool(description="Add two numbers")
    def add(x, y):
        return x + y

    # Manual registration
    def web_scrape(url):
        from bs4 import BeautifulSoup
        import requests
        response = requests.get(url)
        return BeautifulSoup(response.text, 'html.parser')
    
    toolbox = Toolbox()
    toolbox.add_tool(Tool(name="scrape", func=web_scrape, description="Scrape a webpage"))
"""
from typing import Dict, List, Callable, Any, Optional, TypeVar, ParamSpec, overload, Union, Set
from dataclasses import dataclass
import inspect
import ast

# Generic type variables for preserving function signatures
P = ParamSpec('P')  # Captures all parameter types of the decorated function
R = TypeVar('R')    # Captures the return type of the decorated function

@dataclass
class Tool:
    """
    Represents a tool that can be used by the agent.
    
    Attributes:
        name: The name used to invoke the tool
        func: The actual function that implements the tool
        description: Human-readable description of what the tool does
        
    The generic types P and R ensure that the original function's
    signature is preserved in type checking.
    """
    name: str
    func: Callable[P, R]
    description: str

    def validate_code(self) -> tuple[bool, str]:
        """
        Validate the tool's code using AST parsing.
        
        Returns:
            A tuple of (is_valid, error_message).
            If is_valid is False, error_message contains the reason.
        """
        try:
            source = inspect.getsource(self.func)
            # Remove indentation and decorator
            lines = source.split("\n")
            # Skip decorator if present
            while lines and (lines[0].strip().startswith("@") or not lines[0].strip()):
                lines = lines[1:]
            if not lines:
                return False, "Empty function body"
            
            # Get base indentation from first line
            base_indent = len(lines[0]) - len(lines[0].lstrip())
            # Remove base indentation from all lines
            source = "\n".join(line[base_indent:] if len(line) > base_indent else line 
                             for line in lines)
            
            tree = ast.parse(source)
            
            # Check for potentially dangerous operations
            for node in ast.walk(tree):
                # Check for exec/eval calls
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['exec', 'eval']:
                            return False, f"Use of {node.func.id} is not allowed"
                
                # Check for system/subprocess calls
                if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    for name in node.names:
                        if name.name in ['subprocess', 'os.system', 'os.popen']:
                            return False, f"Import of {name.name} is not allowed"
                
                # Check for file operations
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id == 'open':
                            return False, "Direct file operations are not allowed"
            
            return True, ""
            
        except (IOError, TypeError, SyntaxError) as e:
            return False, f"Code validation error: {str(e)}"

    @property
    def required_imports(self) -> Set[str]:
        """
        Automatically detect imports required by this tool by parsing its source code.
        
        Returns:
            A set of base module names that need to be imported for this tool.
            For example, 'from bs4 import BeautifulSoup' returns {'bs4'}.
        """
        try:
            source = inspect.getsource(self.func)
            # Remove indentation and decorator
            lines = source.split("\n")
            # Skip decorator if present
            while lines and (lines[0].strip().startswith("@") or not lines[0].strip()):
                lines = lines[1:]
            if not lines:
                return set()
            
            # Get base indentation from first line
            base_indent = len(lines[0]) - len(lines[0].lstrip())
            # Remove base indentation from all lines
            source = "\n".join(line[base_indent:] if len(line) > base_indent else line 
                             for line in lines)
            
            tree = ast.parse(source)
            imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        base_module = alias.name.split('.')[0]
                        imports.add(base_module)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:  # Handles 'from x import y'
                        base_module = node.module.split('.')[0]
                        imports.add(base_module)
                    
            return imports
        except (IOError, TypeError, SyntaxError):
            # If we can't get the source (e.g., built-in function)
            return set()

class Toolbox:
    """
    Manages a collection of tools that can be used by the agent.
    
    This class is implemented as a singleton to ensure that all tools
    are registered in the same toolbox, regardless of where they are
    defined in the code.
    
    The tools are stored in a dictionary mapping tool names to Tool objects.
    This allows for quick lookup when the agent needs to use a tool.
    
    Attributes:
        _instance: Class variable for singleton pattern
        tools: Dictionary mapping tool names to Tool objects
    """
    _instance: Optional['Toolbox'] = None
    tools: Dict[str, Tool]
    
    def __new__(cls) -> 'Toolbox':
        """
        Implements the singleton pattern.
        
        Returns:
            The single instance of Toolbox, creating it if it doesn't exist.
            This ensures all @register_tool decorators register to the same toolbox.
        """
        if cls._instance is None:
            cls._instance = super(Toolbox, cls).__new__(cls)
            cls._instance.tools = {}
        return cls._instance
    
    def add_tool(self, tool: Tool) -> None:
        """
        Register a new tool in the toolbox.
        
        Args:
            tool: The Tool object to register
            
        If a tool with the same name already exists, it will be overwritten.
        This allows for tool redefinition if needed.
        """
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        """
        Retrieve a tool by name.
        
        Args:
            name: The name of the tool to retrieve
            
        Returns:
            The Tool object if found, None otherwise.
            This matches Python's dictionary.get() behavior.
        """
        return self.tools.get(name)
    
    def get_required_imports(self) -> Set[str]:
        """
        Get all unique imports required by all registered tools.
        
        Returns:
            A set of module names that need to be imported for all tools.
        """
        imports = set()
        for tool in self.tools.values():
            imports.update(tool.required_imports)
        return imports

# Type hint overloads to properly handle both decorator usage patterns
@overload
def register_tool(func: Callable[P, R]) -> Callable[P, R]: ...

@overload
def register_tool(
    *, 
    name: Optional[str] = None, 
    description: Optional[str] = None
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...

def register_tool(
    func: Optional[Callable[P, R]] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None
) -> Union[Callable[P, R], Callable[[Callable[P, R]], Callable[P, R]]]:
    """
    Decorator to register a function as a tool.
    
    This decorator can be used in two ways:
    1. With no arguments: @register_tool
    2. With keyword arguments: @register_tool(name="...", description="...")
    
    The decorator preserves the original function's signature for type checking
    and simply registers it as a tool before returning it unchanged.
    
    Args:
        func: The function to decorate (when used as @register_tool)
        name: Optional custom name for the tool (defaults to function name)
        description: Optional description (defaults to function's docstring)
        
    Returns:
        The original function, unchanged but registered as a tool
        
    Example:
        @register_tool(description="Fetch webpage content")
        def fetch_webpage(url):
            '''Fetch and parse a webpage.'''
            import requests
            from bs4 import BeautifulSoup
            response = requests.get(url)
            return BeautifulSoup(response.text, 'html.parser')
    """
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        # Get tool name from argument or function name
        tool_name = name or fn.__name__
        # Get description from argument, docstring, or generate default
        tool_description = description or fn.__doc__ or f"Execute {tool_name}"
        
        # Register the tool in the singleton toolbox
        Toolbox().add_tool(Tool(
            name=tool_name,
            func=fn,
            description=tool_description
        ))
        # Return original function unchanged
        return fn
    
    # Handle both @register_tool and @register_tool() patterns
    if func is not None:
        return decorator(func)
    
    return decorator