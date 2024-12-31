"""
Robust Anthropic Claude client with streaming, token tracking, and full parameter support.
"""
from typing import AsyncIterator, Dict, List, Optional, Any, Union, Callable
import anthropic
from dataclasses import dataclass, field
from datetime import datetime
import os
import logging
import json

# Configure logging based on DEBUG_LEVEL
DEBUG_LEVEL = int(os.getenv("DEBUG_LEVEL", "0"))
logging.basicConfig(
    level=logging.DEBUG if DEBUG_LEVEL > 0 else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("anthropic_client")


@dataclass
class UsageStats:
    """Track API usage statistics"""
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_cost: float = 0.0
    requests: int = 0
    last_request: Optional[datetime] = None
    
    def add_request(self, prompt_tokens: int, completion_tokens: int, cost: float) -> None:
        """Record usage from a request"""
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_cost += cost
        self.requests += 1
        self.last_request = datetime.now()


class AnthropicClient:
    """
    Robust client for Anthropic's Claude API with streaming support and usage tracking.
    
    Features:
    - Async streaming by default
    - Full parameter support
    - Token and cost tracking
    - Usage statistics
    - Error handling
    - Debug output controlled by DEBUG_LEVEL env var
    - Tool use support for Claude 3.5
    """
    
    # Claude API pricing per 1k tokens (as of Dec 2023)
    PRICING = {
        "claude-3-sonnet-20240229": {"prompt": 0.008, "completion": 0.024},
        "claude-2.1": {"prompt": 0.008, "completion": 0.024},
        "claude-2.0": {"prompt": 0.008, "completion": 0.024},
        "claude-instant-1.2": {"prompt": 0.0008, "completion": 0.0024}
    }

    def __init__(
        self,
        api_key: str,
        model: str = "claude-3-sonnet-20240229",
        default_max_tokens: int = 1024,
    ):
        """
        Initialize the client.
        
        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-3-sonnet-20240229)
            default_max_tokens: Default maximum tokens for completions
        """
        if not api_key:
            raise ValueError("API key is required")
        if model not in self.PRICING:
            raise ValueError(f"Unsupported model: {model}. Must be one of {list(self.PRICING.keys())}")
            
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = model
        self.default_max_tokens = default_max_tokens
        self.stats = UsageStats()
        logger.debug(f"Initialized AnthropicClient with model={model}, default_max_tokens={default_max_tokens}")

    async def stream(
        self,
        prompt: str,
        *,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
        top_p: float = 1.0,
        top_k: Optional[int] = None,
        stop_sequences: Optional[List[str]] = None,
        system: Optional[Union[str, List[str]]] = None,
        metadata: Optional[Dict[str, str]] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_handlers: Optional[Dict[str, Callable]] = None,
    ) -> AsyncIterator[str]:
        """
        Stream a completion from Claude.
        
        Args:
            prompt: The prompt to complete
            max_tokens: Maximum tokens to generate (default: self.default_max_tokens)
            temperature: Sampling temperature (default: 1.0)
            top_p: Nucleus sampling parameter (default: 1.0)
            top_k: Top-k sampling parameter (default: None)
            stop_sequences: Sequences that will stop generation (default: None)
            system: System prompt(s) (default: None)
            metadata: Request metadata (default: None)
            tools: List of tool definitions in Claude's tool format (default: None)
            tool_handlers: Dict mapping tool names to their handler functions (default: None)
            
        Yields:
            Generated text chunks
            
        Raises:
            ValueError: For invalid parameters
            anthropic.APIError: For API errors
        """
        # Parameter validation
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        if temperature < 0 or temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")
        if top_p < 0 or top_p > 1:
            raise ValueError("top_p must be between 0 and 1")
        if tools and not tool_handlers:
            raise ValueError("tool_handlers must be provided when tools are specified")
        
        max_tokens = max_tokens or self.default_max_tokens
        
        # Build request parameters
        params = {
            "max_tokens": max_tokens,
            "messages": [{
                "role": "user",
                "content": [{
                    "type": "text",
                    "text": prompt
                }]
            }],
            "model": self.model,
            "temperature": temperature,
            "top_p": top_p,
            "stop_sequences": stop_sequences,
            "metadata": metadata,
            "stream": True
        }
        
        # Add tools if specified
        if tools:
            params["tools"] = tools
        
        # Only include optional parameters if set
        if top_k is not None:
            params["top_k"] = top_k
            
        if system is not None:
            if isinstance(system, str):
                params["system"] = system
            else:
                params["system"] = " ".join(system)
        
        logger.debug(
            f"Starting stream with: prompt_length={len(prompt)}, "
            f"max_tokens={max_tokens}, temperature={temperature}, "
            f"top_p={top_p}, top_k={top_k}, system={'set' if system else 'none'}, "
            f"tools={'set' if tools else 'none'}"
        )
        
        try:
            # Stream the response
            stream = self.client.messages.create(**params)
            
            prompt_tokens = 0
            completion_tokens = 0
            current_block_text = ""
            current_tool_call = None
            
            for chunk in stream:
                if DEBUG_LEVEL > 0:
                    logger.debug(f"Received chunk: {chunk}")
                
                if hasattr(chunk, 'type'):
                    if chunk.type == "message_start":
                        if hasattr(chunk.message, "usage"):
                            prompt_tokens = chunk.message.usage.input_tokens
                            logger.debug(f"Stream started, prompt_tokens={prompt_tokens}")
                            if DEBUG_LEVEL > 0:
                                logger.debug(f"Full message: {chunk.message}")
                    
                    elif chunk.type == "content_block_start":
                        if hasattr(chunk, "content_block") and chunk.content_block.type == "tool_use":
                            logger.debug(f"Starting tool use block: {chunk.content_block}")
                            current_tool_call = {
                                "id": chunk.content_block.id,
                                "name": chunk.content_block.name,
                                "parameters": {}
                            }
                    
                    elif chunk.type == "content_block_delta":
                        if hasattr(chunk.delta, "text"):
                            text = chunk.delta.text
                            current_block_text += text
                            completion_tokens += len(text.split())  # Approximate
                            if DEBUG_LEVEL > 0:
                                logger.debug(f"Received text: {len(text)} chars")
                            yield text
                        elif hasattr(chunk.delta, "partial_json"):
                            if current_tool_call:
                                # Accumulate JSON for tool parameters
                                current_tool_call["parameters_json"] = current_tool_call.get("parameters_json", "") + chunk.delta.partial_json
                                if DEBUG_LEVEL > 0:
                                    logger.debug(f"Accumulated tool parameters JSON: {current_tool_call['parameters_json']}")
                    
                    elif chunk.type == "content_block_stop":
                        if current_block_text:
                            logger.debug(f"Content block complete: {len(current_block_text)} chars")
                            current_block_text = ""
                        
                        if current_tool_call and "parameters_json" in current_tool_call:
                            # Parse and execute the tool call
                            try:
                                parameters = json.loads(current_tool_call["parameters_json"])
                                tool_name = current_tool_call["name"]
                                
                                if tool_handlers and tool_name in tool_handlers:
                                    logger.debug(f"Executing tool {tool_name} with parameters: {parameters}")
                                    try:
                                        result = tool_handlers[tool_name](**parameters)
                                        logger.debug(f"Tool {tool_name} execution result: {result}")
                                        
                                        # Send tool result back to Claude
                                        params["messages"].extend([
                                            {
                                                "role": "assistant",
                                                "content": [{
                                                    "type": "tool_calls",
                                                    "tool_calls": [{
                                                        "id": current_tool_call["id"],
                                                        "name": tool_name,
                                                        "parameters": parameters
                                                    }]
                                                }]
                                            },
                                            {
                                                "role": "tool",
                                                "content": [{
                                                    "type": "text",
                                                    "text": json.dumps(result)
                                                }],
                                                "tool_call_id": current_tool_call["id"]
                                            }
                                        ])
                                    except Exception as e:
                                        logger.error(f"Tool {tool_name} execution failed: {str(e)}")
                                        params["messages"].append({
                                            "role": "tool",
                                            "content": [{
                                                "type": "text",
                                                "text": json.dumps({"error": str(e)})
                                            }],
                                            "tool_call_id": current_tool_call["id"]
                                        })
                            except json.JSONDecodeError as e:
                                logger.error(f"Failed to parse tool parameters JSON: {str(e)}")
                            finally:
                                current_tool_call = None
                    
                    elif chunk.type == "message_delta":
                        if hasattr(chunk, "usage"):
                            completion_tokens = chunk.usage.output_tokens
                            logger.debug(f"Updated completion_tokens={completion_tokens}")
                    
                    elif chunk.type == "error":
                        error_msg = chunk.error.message if hasattr(chunk.error, "message") else str(chunk.error)
                        logger.error(f"Stream error: {error_msg}")
                        raise RuntimeError(f"Stream error: {error_msg}")
                    
                    # Ignore ping events and handle unknown events gracefully
                    elif chunk.type != "ping":
                        logger.debug(f"Unknown event type: {chunk.type}")
            
            # Update usage statistics
            cost = self._calculate_cost(prompt_tokens, completion_tokens)
            self.stats.add_request(prompt_tokens, completion_tokens, cost)
            logger.debug(
                f"Stream complete: prompt_tokens={prompt_tokens}, "
                f"completion_tokens={completion_tokens}, cost=${cost:.6f}"
            )
                
        except anthropic.BadRequestError as e:
            logger.error(f"Bad request error: {str(e)}")
            raise ValueError(f"Invalid request: {str(e)}") from e
        except anthropic.RateLimitError as e:
            logger.error(f"Rate limit error: {str(e)}")
            raise RuntimeError(f"Rate limit exceeded: {str(e)}") from e
        except anthropic.APIError as e:
            logger.error(f"API error: {str(e)}")
            raise RuntimeError(f"API error: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            raise RuntimeError(f"Unexpected error in AnthropicClient: {str(e)}") from e

    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for token usage"""
        pricing = self.PRICING[self.model]
        prompt_cost = (prompt_tokens / 1000) * pricing["prompt"]
        completion_cost = (completion_tokens / 1000) * pricing["completion"]
        total_cost = prompt_cost + completion_cost
        logger.debug(
            f"Cost calculation: prompt=${prompt_cost:.6f}, "
            f"completion=${completion_cost:.6f}, total=${total_cost:.6f}"
        )
        return total_cost

    @property
    def usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        stats = {
            "model": self.model,
            "prompt_tokens": self.stats.prompt_tokens,
            "completion_tokens": self.stats.completion_tokens,
            "total_tokens": self.stats.prompt_tokens + self.stats.completion_tokens,
            "total_cost": round(self.stats.total_cost, 6),
            "requests": self.stats.requests,
            "last_request": self.stats.last_request.isoformat() if self.stats.last_request else None
        }
        logger.debug(f"Current usage stats: {stats}")
        return stats 