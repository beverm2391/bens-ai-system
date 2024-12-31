"""
Tool execution and management.
"""
import time
from typing import Dict, Any, Optional, Callable

from src.observability.metrics import MetricsTracker

class ToolExecutor:
    """Manages and executes AI tools"""
    
    def __init__(self, metrics_dir: str = "metrics"):
        self.tools: Dict[str, Dict[str, Any]] = {}
        self.metrics = MetricsTracker(metrics_dir)
        self.invocation_counts: Dict[str, int] = {}
        self.invocation_limits: Dict[str, Optional[int]] = {}
    
    def register_tool(
        self,
        name: str,
        handler: Callable,
        input_schema: Dict[str, Any],
        max_invocations: Optional[int] = None
    ) -> None:
        """Register a new tool"""
        self.tools[name] = {
            "handler": handler,
            "input_schema": input_schema
        }
        self.invocation_counts[name] = 0
        self.invocation_limits[name] = max_invocations
    
    def execute_tool(
        self,
        name: str,
        params: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a registered tool"""
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
            
        # Check invocation limit
        if (limit := self.invocation_limits[name]) is not None:
            if self.invocation_counts[name] >= limit:
                raise RuntimeError(
                    f"Tool {name} has reached its invocation limit of {limit}"
                )
        
        start_time = time.time()
        success = True
        error = None
        usage = None
        
        try:
            result = self.tools[name]["handler"](**params)
            self.invocation_counts[name] += 1
            
            # Extract usage data if available
            if isinstance(result, dict):
                usage = result.get("usage")
            
        except Exception as e:
            success = False
            error = str(e)
            result = {"error": str(e)}
            
        # Track metrics
        self.metrics.track_tool_usage(
            tool_name=name,
            start_time=start_time,
            success=success,
            error=error,
            metadata=metadata,
            usage=usage
        )
        
        return result
    
    def get_metrics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get aggregated metrics for all tools"""
        return self.metrics.get_tool_metrics(
            start_date=start_date,
            end_date=end_date
        )
    
    def get_schema(self, name: str) -> Dict[str, Any]:
        """Get the input schema for a tool"""
        if name not in self.tools:
            raise ValueError(f"Tool {name} not found")
        return self.tools[name]["input_schema"] 