"""
Robust Together AI client with streaming, token tracking, and full parameter support.
"""
from typing import Optional, List, Dict, Any, AsyncIterator, Union
import os
import logging
from dataclasses import dataclass
from datetime import datetime
from together import Together
from dotenv import load_dotenv

# Configure logging based on DEBUG_LEVEL
DEBUG_LEVEL = int(os.getenv("DEBUG_LEVEL", "0"))
logging.basicConfig(
    level=logging.DEBUG if DEBUG_LEVEL > 0 else logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("together_client")

load_dotenv()

TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")
if not TOGETHER_API_KEY:
    raise ValueError("TOGETHER_API_KEY environment variable is not set")

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

class TogetherClient:
    """
    Robust client for Together AI with streaming support and usage tracking.
    
    Features:
    - Async streaming by default
    - Full parameter support
    - Token and cost tracking
    - Usage statistics
    - Error handling
    - Debug output controlled by DEBUG_LEVEL env var
    """
    
    # Together API pricing per 1k tokens (as of March 2024)
    PRICING = {
        "meta-llama/Llama-3.3-70B-Instruct-Turbo": {"prompt": 0.0009, "completion": 0.0009},
        "Qwen/Qwen2.5-Coder-32B-Instruct": {"prompt": 0.0007, "completion": 0.0007},
    }

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        default_max_tokens: int = 1024,
    ):
        """
        Initialize the client.
        
        Args:
            api_key: Together API key
            model: Model to use
            default_max_tokens: Default maximum tokens for completions
        """
        if not api_key and not TOGETHER_API_KEY:
            raise ValueError("API key is required")
        if model not in self.PRICING:
            raise ValueError(f"Unsupported model: {model}. Must be one of {list(self.PRICING.keys())}")
            
        self.api_key = api_key or TOGETHER_API_KEY
        self.client = Together(api_key=self.api_key)
        self.model = model
        self.default_max_tokens = default_max_tokens
        self.stats = UsageStats()
        logger.debug(f"Initialized TogetherClient with model={model}, default_max_tokens={default_max_tokens}")

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        *,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        top_p: float = 1.0,
        top_k: Optional[int] = None,
        repetition_penalty: Optional[float] = None,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
    ) -> Union[str, AsyncIterator[str]]:
        """
        Get a chat completion from Together AI.
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use (defaults to instance default)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            top_p: Nucleus sampling parameter (0-1)
            top_k: Top-k sampling parameter
            repetition_penalty: Penalty for token repetition
            stop: Stop sequences
            stream: Whether to stream the response
            
        Returns:
            Generated text or async iterator of text chunks if streaming
            
        Raises:
            ValueError: For invalid parameters
            RuntimeError: For API errors
        """
        # Parameter validation
        if not messages:
            raise ValueError("Messages cannot be empty")
        if temperature < 0 or temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")
        if top_p < 0 or top_p > 1:
            raise ValueError("top_p must be between 0 and 1")
            
        model = model or self.model
        max_tokens = max_tokens or self.default_max_tokens
        
        # Build request parameters
        params = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "top_p": top_p,
            "stream": stream,
        }
        
        # Add optional parameters
        if top_k is not None:
            params["top_k"] = top_k
        if repetition_penalty is not None:
            params["repetition_penalty"] = repetition_penalty
        if stop:
            params["stop"] = stop if isinstance(stop, list) else [stop]
            
        logger.debug(
            f"Starting chat completion with: messages_count={len(messages)}, "
            f"model={model}, max_tokens={max_tokens}, temperature={temperature}, "
            f"top_p={top_p}, stream={stream}"
        )
        
        try:
            if stream:
                async def stream_response():
                    stream = self.client.chat.completions.create(**params)
                    prompt_tokens = len(" ".join(m["content"] for m in messages).split())
                    completion_tokens = 0
                    
                    for chunk in stream:
                        if chunk.choices[0].delta.content:
                            text = chunk.choices[0].delta.content
                            completion_tokens += len(text.split())  # Approximate
                            if DEBUG_LEVEL > 0:
                                logger.debug(f"Received chunk: {len(text)} chars")
                            yield text
                    
                    # Update usage statistics after streaming
                    cost = self._calculate_cost(prompt_tokens, completion_tokens)
                    self.stats.add_request(prompt_tokens, completion_tokens, cost)
                    logger.debug(
                        f"Stream complete: prompt_tokens={prompt_tokens}, "
                        f"completion_tokens={completion_tokens}, cost=${cost:.6f}"
                    )
                    
                return stream_response()
            else:
                response = self.client.chat.completions.create(**params)
                
                # Extract usage info
                if hasattr(response, "usage"):
                    prompt_tokens = response.usage.prompt_tokens
                    completion_tokens = response.usage.completion_tokens
                else:
                    # Fallback to approximation
                    prompt_tokens = len(" ".join(m["content"] for m in messages).split())
                    completion_tokens = len(response.choices[0].message.content.split())
                
                cost = self._calculate_cost(prompt_tokens, completion_tokens)
                self.stats.add_request(prompt_tokens, completion_tokens, cost)
                logger.debug(
                    f"Completion complete: prompt_tokens={prompt_tokens}, "
                    f"completion_tokens={completion_tokens}, cost=${cost:.6f}"
                )
                return response.choices[0].message.content
                
        except Exception as e:
            logger.error(f"Chat completion error: {str(e)}")
            raise RuntimeError(f"Together API error: {str(e)}")

    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            response = self.client.models.list()
            return response  # Response is already a list
        except Exception as e:
            logger.error(f"Failed to get models: {str(e)}")
            raise RuntimeError(f"Together API error: {str(e)}")

    async def completion(
        self,
        prompt: str,
        **kwargs
    ) -> Union[str, AsyncIterator[str]]:
        """
        Get a text completion from Together AI.
        
        Args:
            prompt: Text prompt to complete
            **kwargs: Additional arguments passed to chat_completion
            
        Returns:
            Generated text or async iterator of text chunks if streaming
        """
        messages = [{"role": "user", "content": prompt}]
        return await self.chat_completion(messages=messages, **kwargs)

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