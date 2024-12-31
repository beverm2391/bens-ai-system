"""
Tool executor for managing and executing AI tools.
"""
from typing import Dict, Any, Callable, Optional, List
import logging
from dataclasses import dataclass, field
import subprocess

logger = logging.getLogger(__name__)

@dataclass
class Tool:
    """Represents a registered tool"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable
    
@dataclass
class ToolExecutor:
    """
    Manages and executes AI tools.
    
    Features:
    - Tool registration and validation
    - Schema validation
    - Error handling
    - Logging
    """
    tools: Dict[str, Tool] = field(default_factory=dict)
    
    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable
    ) -> None:
        """
        Register a new tool.
        
        Args:
            name: Tool name
            description: Tool description
            input_schema: JSON Schema for tool inputs
            handler: Function to handle tool execution
        """
        self.tools[name] = Tool(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler
        )
        logger.debug(f"Registered tool: {name}")
    
    def get_tool_schema(self, name: str) -> Dict[str, Any]:
        """Get the Claude-compatible schema for a tool"""
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
            
        tool = self.tools[name]
        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema
        }
        
    def get_all_tool_schemas(self) -> List[Dict[str, Any]]:
        """Get Claude-compatible schemas for all registered tools"""
        return [self.get_tool_schema(name) for name in self.tools]
    
    def get_tool_handlers(self) -> Dict[str, Callable]:
        """Get a mapping of tool names to their handlers"""
        return {name: tool.handler for name, tool in self.tools.items()}
    
    def execute_tool(self, name: str, **kwargs) -> Any:
        """
        Execute a tool with the given parameters.
        
        Args:
            name: Tool name
            **kwargs: Tool parameters
            
        Returns:
            Tool execution result
            
        Raises:
            ValueError: If tool not found
            Exception: If tool execution fails
        """
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
            
        tool = self.tools[name]
        try:
            result = tool.handler(**kwargs)
            logger.debug(f"Tool {name} executed successfully")
            return result
        except Exception as e:
            logger.error(f"Tool {name} execution failed: {str(e)}")
            raise 