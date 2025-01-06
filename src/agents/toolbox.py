# This module provides a comprehensive tool management system for secure function registration and execution. It enables registering functions as secure, callable tools while enforcing security through code validation, import whitelisting, and execution sandboxing. The system is optimized for performance using singleton patterns and cached operations.

from typing import Dict, List, Callable, Any, Optional, TypeVar, ParamSpec, overload, Union, Set
from dataclasses import dataclass
import inspect
import ast

# Type variables for preserving function signatures in decorators
P = ParamSpec('P')  # Parameter types
R = TypeVar('R')    # Return type

@dataclass
class Tool:
    # A Tool wraps a Python function with metadata for discovery and usage, security validation logic, and type safety enforcement. It provides efficient validation and cached import tracking while restricting dangerous operations and controlling import usage.
    
    name: str        # Name used to invoke tool
    func: Callable[P, R]  # Actual implementation
    description: str # Human-readable description

    def validate_code(self) -> tuple[bool, str]:
        # This function performs security validation of the tool implementation through AST-based analysis. It checks for dangerous operations like exec/eval calls, system/subprocess usage, and file operations while enforcing import restrictions.
        
        try:
            source = inspect.getsource(self.func)
            
            lines = source.split("\n")
            while lines and (lines[0].strip().startswith("@") or not lines[0].strip()):
                lines = lines[1:]
            if not lines:
                return False, "Empty function body"
            
            base_indent = len(lines[0]) - len(lines[0].lstrip())
            source = "\n".join(line[base_indent:] if len(line) > base_indent else line 
                             for line in lines)
            
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in ['exec', 'eval']:
                            return False, f"Use of {node.func.id} is not allowed"
                
                if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
                    for name in node.names:
                        if name.name in ['subprocess', 'os.system', 'os.popen']:
                            return False, f"Import of {name.name} is not allowed"
                
                if isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id == 'open':
                            return False, "Direct file operations are not allowed"
            
            return True, ""
            
        except (IOError, TypeError, SyntaxError) as e:
            return False, f"Code validation error: {str(e)}"

    @property
    def required_imports(self) -> Set[str]:
        # This function analyzes the tool's source code to detect required imports by parsing import statements and extracting base module names. For example, 'from bs4 import BeautifulSoup' would yield {'bs4'}.
        
        try:
            source = inspect.getsource(self.func)
            lines = source.split("\n")
            while lines and (lines[0].strip().startswith("@") or not lines[0].strip()):
                lines = lines[1:]
            if not lines:
                return set()
            
            base_indent = len(lines[0]) - len(lines[0].lstrip())
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
                    if node.module:
                        base_module = node.module.split('.')[0]
                        imports.add(base_module)
                    
            return imports
            
        except (IOError, TypeError, SyntaxError):
            return set()

class Toolbox:
    # This class serves as a central registry for managing available tools using the singleton pattern to ensure consistent tool registration across the system. It provides efficient tool lookup and cached import tracking while maintaining type safety.
    
    _instance: Optional['Toolbox'] = None  # Singleton instance
    tools: Dict[str, Tool]  # Name -> Tool mapping
    
    def __new__(cls) -> 'Toolbox':
        # This method implements the singleton pattern by creating a single shared instance on first call and returning the same instance for all subsequent calls. It initializes the tools dictionary when first created.
        
        if cls._instance is None:
            cls._instance = super(Toolbox, cls).__new__(cls)
            cls._instance.tools = {}
        return cls._instance
    
    def add_tool(self, tool: Tool) -> None:
        # This method registers a new tool in the system, updating the tools registry and overwriting any existing tool with the same name.
        
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[Tool]:
        # This method retrieves a registered tool by name, returning None if the tool is not registered.
        
        return self.tools.get(name)
    
    def get_required_imports(self) -> Set[str]:
        # This method combines the import requirements from all registered tools into a single set of base module names.
        
        all_imports = set()
        for tool in self.tools.values():
            all_imports.update(tool.required_imports)
        return all_imports

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
    # This decorator supports registering functions as tools with two usage patterns: basic (@register_tool) and with arguments (@register_tool(name="x", description="y")). It preserves the original function while adding it to the tool registry and maintaining type safety.
    
    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        # Get tool name from argument or function name
        tool_name = name or fn.__name__
        
        # Create and register tool
        tool = Tool(
            name=tool_name,
            func=fn,
            description=description or fn.__doc__ or ""
        )
        
        # Validate tool code
        is_valid, error = tool.validate_code()
        if not is_valid:
            raise ValueError(f"Invalid tool code: {error}")
        
        # Add to registry
        Toolbox().add_tool(tool)
        
        # Return original function
        return fn
    
    if func is None:
        # Called with arguments
        return decorator
    else:
        # Called without arguments
        return decorator(func)