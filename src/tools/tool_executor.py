"""
Tool executor for managing and executing AI tools.
"""
from typing import Dict, Any, Callable, Optional, List
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import subprocess

logger = logging.getLogger(__name__)

@dataclass
class ToolLimits:
    """Limits and constraints for a tool"""
    max_calls: Optional[int] = None  # Maximum number of calls allowed
    calls_per_minute: Optional[int] = None  # Rate limit for calls per minute
    cooldown_seconds: Optional[int] = None  # Cooldown period between calls
    cost_per_call: float = 0.0  # Cost tracking if applicable
    reset_interval: Optional[str] = None  # When to reset maximums: 'hourly', 'daily', 'monthly', or None for never

@dataclass
class ToolUsage:
    """Tracks usage statistics for a tool"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    last_call_time: Optional[datetime] = None
    total_cost: float = 0.0
    call_times: List[datetime] = field(default_factory=list)
    last_reset: Optional[datetime] = field(default_factory=lambda: datetime.now())

    def reset(self) -> None:
        """Reset all usage statistics"""
        self.total_calls = 0
        self.successful_calls = 0
        self.failed_calls = 0
        self.total_cost = 0.0
        self.call_times.clear()
        self.last_reset = datetime.now()

    def should_reset(self, reset_interval: Optional[str]) -> bool:
        """Check if usage should be reset based on interval"""
        if not reset_interval or not self.last_reset:
            return False
            
        now = datetime.now()
        time_since_reset = now - self.last_reset
        
        if reset_interval == 'hourly':
            return time_since_reset >= timedelta(hours=1)
        elif reset_interval == 'daily':
            return time_since_reset >= timedelta(days=1)
        elif reset_interval == 'monthly':
            # Simple month check - could be more precise
            return time_since_reset >= timedelta(days=30)
        return False

@dataclass
class Tool:
    """Represents a registered tool"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    handler: Callable
    limits: ToolLimits = field(default_factory=ToolLimits)
    usage: ToolUsage = field(default_factory=ToolUsage)

    def check_and_reset(self) -> None:
        """Check if usage should be reset and do so if needed"""
        if self.usage.should_reset(self.limits.reset_interval):
            self.usage.reset()

@dataclass
class ToolExecutor:
    """
    Manages and executes AI tools.
    
    Features:
    - Tool registration and validation
    - Schema validation
    - Error handling
    - Usage tracking and limits
    - Rate limiting
    - Cost tracking
    - Automatic usage resets
    """
    tools: Dict[str, Tool] = field(default_factory=dict)
    
    def register_tool(
        self,
        name: str,
        description: str,
        input_schema: Dict[str, Any],
        handler: Callable,
        limits: Optional[ToolLimits] = None
    ) -> None:
        """
        Register a new tool.
        
        Args:
            name: Tool name
            description: Tool description
            input_schema: JSON Schema for tool inputs
            handler: Function to handle tool execution
            limits: Optional tool limits and constraints
        """
        self.tools[name] = Tool(
            name=name,
            description=description,
            input_schema=input_schema,
            handler=handler,
            limits=limits or ToolLimits()
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
    
    def get_tool_usage(self, name: str) -> ToolUsage:
        """Get usage statistics for a tool"""
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
        return self.tools[name].usage
    
    def get_all_tool_usage(self) -> Dict[str, ToolUsage]:
        """Get usage statistics for all tools"""
        return {name: tool.usage for name, tool in self.tools.items()}
    
    def reset_tool_usage(self, name: str) -> None:
        """Manually reset usage statistics for a tool"""
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
        self.tools[name].usage.reset()
    
    def reset_all_tool_usage(self) -> None:
        """Manually reset usage statistics for all tools"""
        for tool in self.tools.values():
            tool.usage.reset()
    
    def _check_tool_limits(self, tool: Tool) -> None:
        """Check if tool usage is within limits and handle resets"""
        # Check if usage should be reset
        tool.check_and_reset()
        
        limits = tool.limits
        usage = tool.usage
        
        # Check maximum calls
        if limits.max_calls and usage.total_calls >= limits.max_calls:
            raise Exception(f"Tool {tool.name} has reached maximum calls limit ({limits.max_calls})")
        
        # Check rate limit
        if limits.calls_per_minute:
            now = datetime.now()
            recent_calls = sum(1 for t in usage.call_times 
                             if now - t < timedelta(minutes=1))
            if recent_calls >= limits.calls_per_minute:
                raise Exception(f"Tool {tool.name} has exceeded rate limit ({limits.calls_per_minute}/min)")
        
        # Check cooldown
        if limits.cooldown_seconds and usage.last_call_time:
            time_since_last = datetime.now() - usage.last_call_time
            if time_since_last.total_seconds() < limits.cooldown_seconds:
                raise Exception(f"Tool {tool.name} is in cooldown ({limits.cooldown_seconds}s between calls)")
    
    def _update_tool_usage(self, tool: Tool, success: bool, cost: float = 0.0) -> None:
        """Update usage statistics for a tool"""
        now = datetime.now()
        tool.usage.total_calls += 1
        if success:
            tool.usage.successful_calls += 1
        else:
            tool.usage.failed_calls += 1
        tool.usage.last_call_time = now
        tool.usage.total_cost += cost
        tool.usage.call_times.append(now)
        
        # Cleanup old call times (keep last hour only)
        hour_ago = now - timedelta(hours=1)
        tool.usage.call_times = [t for t in tool.usage.call_times if t > hour_ago]
    
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
            Exception: If tool execution fails or limits are exceeded
        """
        if name not in self.tools:
            raise ValueError(f"Tool not found: {name}")
            
        tool = self.tools[name]
        
        try:
            # Check limits before execution
            self._check_tool_limits(tool)
            
            # Execute tool
            result = tool.handler(**kwargs)
            
            # Update usage stats
            cost = tool.limits.cost_per_call
            self._update_tool_usage(tool, success=True, cost=cost)
            
            logger.debug(f"Tool {name} executed successfully")
            return result
            
        except Exception as e:
            # Update usage stats
            self._update_tool_usage(tool, success=False)
            
            logger.error(f"Tool {name} execution failed: {str(e)}")
            raise 