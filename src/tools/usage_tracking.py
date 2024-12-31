"""
Interfaces and types for tool usage tracking.
"""
from typing import Dict, Any, Protocol, runtime_checkable
from dataclasses import dataclass

@dataclass
class SearchUsage:
    """Usage metrics for search tools"""
    queries: int  # Number of queries made
    # TODO: Implement result tracking
    # results: int  # Number of results returned
    # TODO: Implement token tracking for queries
    # query_tokens: int  # Number of tokens in queries

@dataclass
class CodeExecutionUsage:
    """Usage metrics for code execution tools"""
    execution_seconds: float  # Time spent executing code
    # TODO: Implement memory tracking
    # memory_mb: float  # Memory usage in MB
    # TODO: Implement CPU tracking
    # cpu_percent: float  # CPU usage percentage

@runtime_checkable
class UsageTracker(Protocol):
    """Protocol for tools that track usage"""
    
    def get_usage(self) -> Dict[str, Any]:
        """Get usage metrics for the tool"""
        ... 