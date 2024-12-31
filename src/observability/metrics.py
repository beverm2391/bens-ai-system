"""
Simple metrics tracking system using JSON files.
"""
import os
import json
import time
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class ToolMetrics:
    """Metrics for a single tool invocation"""
    tool_name: str
    start_time: str
    end_time: str
    latency_ms: float
    success: bool
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    usage: Dict[str, Any] = None  # Tool-specific usage data

@dataclass
class LLMMetrics:
    """Metrics for a LLM interaction"""
    model: str
    start_time: str
    end_time: str
    latency_ms: float
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    cost: float
    user_prompt: str
    assistant_response: str
    metadata: Dict[str, Any] = None

class MetricsTracker:
    """Tracks and stores metrics in JSON files"""
    
    def __init__(self, metrics_dir: str = "metrics"):
        self.metrics_dir = metrics_dir
        self.tool_metrics_file = os.path.join(metrics_dir, "tool_metrics.jsonl")
        self.llm_metrics_file = os.path.join(metrics_dir, "llm_metrics.jsonl")
        
        # Load cost config for LLM only
        cost_config_path = os.path.join("src", "observability", "cost_config.json")
        with open(cost_config_path) as f:
            config = json.load(f)
            self.llm_cost_config = config["llm"]
        
        # Create metrics directory if needed
        os.makedirs(metrics_dir, exist_ok=True)
        
        # Touch files to create if they don't exist
        for file in [self.tool_metrics_file, self.llm_metrics_file]:
            if not os.path.exists(file):
                with open(file, 'w') as f:
                    f.write("")
    
    def track_tool_usage(
        self,
        tool_name: str,
        start_time: float,
        success: bool,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        usage: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track metrics for a tool invocation"""
        end_time = time.time()
        
        metrics = ToolMetrics(
            tool_name=tool_name,
            start_time=datetime.fromtimestamp(start_time).isoformat(),
            end_time=datetime.fromtimestamp(end_time).isoformat(),
            latency_ms=(end_time - start_time) * 1000,
            success=success,
            error=error,
            metadata=metadata or {},
            usage=usage or {}
        )
        
        try:
            with open(self.tool_metrics_file, 'a') as f:
                f.write(json.dumps(asdict(metrics)) + '\n')
        except Exception as e:
            logger.error(f"Failed to write tool metrics: {e}")
    
    def _calculate_llm_cost(self, model: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for an LLM interaction"""
        if model in self.llm_cost_config:
            rates = self.llm_cost_config[model]
            input_cost = (prompt_tokens / 1000) * rates["input_tokens"]
            output_cost = (completion_tokens / 1000) * rates["output_tokens"]
            return input_cost + output_cost
        return 0.0
    
    def track_llm_interaction(
        self,
        model: str,
        start_time: float,
        prompt_tokens: int,
        completion_tokens: int,
        user_prompt: str,
        assistant_response: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Track metrics for an LLM interaction"""
        end_time = time.time()
        
        # Calculate cost based on token usage
        cost = self._calculate_llm_cost(model, prompt_tokens, completion_tokens)
        
        metrics = LLMMetrics(
            model=model,
            start_time=datetime.fromtimestamp(start_time).isoformat(),
            end_time=datetime.fromtimestamp(end_time).isoformat(),
            latency_ms=(end_time - start_time) * 1000,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            total_tokens=prompt_tokens + completion_tokens,
            cost=cost,
            user_prompt=user_prompt,
            assistant_response=assistant_response,
            metadata=metadata or {}
        )
        
        try:
            with open(self.llm_metrics_file, 'a') as f:
                f.write(json.dumps(asdict(metrics)) + '\n')
        except Exception as e:
            logger.error(f"Failed to write LLM metrics: {e}")
    
    def _parse_date_range(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Tuple[datetime, datetime]:
        """Parse date range strings into datetime objects"""
        now = datetime.now()
        
        if end_date:
            end = datetime.fromisoformat(end_date)
        else:
            end = now
            
        if start_date:
            start = datetime.fromisoformat(start_date)
        else:
            # Default to last 24 hours
            start = end - timedelta(days=1)
            
        return start, end
    
    def get_tool_metrics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get aggregated tool metrics for a date range"""
        start, end = self._parse_date_range(start_date, end_date)
        
        metrics = {
            "period": {
                "start": start.isoformat(),
                "end": end.isoformat()
            },
            "total_calls": 0,
            "success_rate": 0.0,
            "avg_latency_ms": 0.0,
            "by_tool": {}
        }
        
        try:
            with open(self.tool_metrics_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    
                    # Check if entry is within date range
                    entry_time = datetime.fromisoformat(data["start_time"])
                    if not (start <= entry_time <= end):
                        continue
                        
                    metrics["total_calls"] += 1
                    metrics["avg_latency_ms"] += data["latency_ms"]
                    
                    tool = data["tool_name"]
                    if tool not in metrics["by_tool"]:
                        metrics["by_tool"][tool] = {
                            "calls": 0,
                            "successes": 0,
                            "failures": 0,
                            "avg_latency_ms": 0.0,
                            "usage": {}
                        }
                    
                    tool_metrics = metrics["by_tool"][tool]
                    tool_metrics["calls"] += 1
                    if data["success"]:
                        tool_metrics["successes"] += 1
                    else:
                        tool_metrics["failures"] += 1
                    tool_metrics["avg_latency_ms"] += data["latency_ms"]
                    
                    # Aggregate usage data
                    if data.get("usage"):
                        for key, value in data["usage"].items():
                            if key not in tool_metrics["usage"]:
                                tool_metrics["usage"][key] = 0
                            tool_metrics["usage"][key] += value
            
            # Calculate averages
            if metrics["total_calls"] > 0:
                metrics["avg_latency_ms"] /= metrics["total_calls"]
                metrics["success_rate"] = sum(
                    t["successes"] for t in metrics["by_tool"].values()
                ) / metrics["total_calls"]
                
                for tool_metrics in metrics["by_tool"].values():
                    if tool_metrics["calls"] > 0:
                        tool_metrics["avg_latency_ms"] /= tool_metrics["calls"]
            
        except Exception as e:
            logger.error(f"Failed to read tool metrics: {e}")
        
        return metrics
    
    def get_llm_metrics(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get aggregated LLM metrics for a date range"""
        start, end = self._parse_date_range(start_date, end_date)
        
        metrics = {
            "period": {
                "start": start.isoformat(),
                "end": end.isoformat()
            },
            "total_interactions": 0,
            "total_cost": 0.0,
            "total_tokens": 0,
            "avg_latency_ms": 0.0,
            "by_model": {}
        }
        
        try:
            with open(self.llm_metrics_file, 'r') as f:
                for line in f:
                    if not line.strip():
                        continue
                    data = json.loads(line)
                    
                    # Check if entry is within date range
                    entry_time = datetime.fromisoformat(data["start_time"])
                    if not (start <= entry_time <= end):
                        continue
                    
                    metrics["total_interactions"] += 1
                    metrics["total_cost"] += data["cost"]
                    metrics["total_tokens"] += data["total_tokens"]
                    metrics["avg_latency_ms"] += data["latency_ms"]
                    
                    model = data["model"]
                    if model not in metrics["by_model"]:
                        metrics["by_model"][model] = {
                            "interactions": 0,
                            "total_cost": 0.0,
                            "total_tokens": 0,
                            "avg_latency_ms": 0.0
                        }
                    
                    model_metrics = metrics["by_model"][model]
                    model_metrics["interactions"] += 1
                    model_metrics["total_cost"] += data["cost"]
                    model_metrics["total_tokens"] += data["total_tokens"]
                    model_metrics["avg_latency_ms"] += data["latency_ms"]
            
            # Calculate averages
            if metrics["total_interactions"] > 0:
                metrics["avg_latency_ms"] /= metrics["total_interactions"]
                
                for model_metrics in metrics["by_model"].values():
                    if model_metrics["interactions"] > 0:
                        model_metrics["avg_latency_ms"] /= model_metrics["interactions"]
            
        except Exception as e:
            logger.error(f"Failed to read LLM metrics: {e}")
        
        return metrics 