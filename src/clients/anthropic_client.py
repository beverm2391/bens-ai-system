"""
Robust Anthropic Claude client with streaming, token tracking, and full parameter support.
"""
from typing import AsyncIterator, Dict, List, Optional, Any
import anthropic
from dataclasses import dataclass, field
from datetime import datetime
import os
import logging

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
    """
    
    # Claude API pricing per 1k tokens (as of Dec 2023)
    PRICING = {
        "claude-2.1": {"prompt": 0.008, "completion": 0.024},
        "claude-2.0": {"prompt": 0.008, "completion": 0.024},
        "claude-instant-1.2": {"prompt": 0.0008, "completion": 0.0024}
    }

    def __init__(
        self,
        api_key: str,
        model: str = "claude-2.1",
        default_max_tokens: int = 1024,
    ):
        """
        Initialize the client.
        
        Args:
            api_key: Anthropic API key
            model: Model to use (default: claude-2.1)
            default_max_tokens: Default maximum tokens for completions
        """
        if not api_key:
            raise ValueError("API key is required")
        if model not in self.PRICING:
            raise ValueError(f"Unsupported model: {model}. Must be one of {list(self.PRICING.keys())}")
            
        self.client = anthropic.Client(api_key=api_key)
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
        system: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None,
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
            system: System prompt (default: None)
            metadata: Request metadata (default: None)
            
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
        
        max_tokens = max_tokens or self.default_max_tokens
        
        logger.debug(
            f"Starting stream with: prompt_length={len(prompt)}, "
            f"max_tokens={max_tokens}, temperature={temperature}, "
            f"top_p={top_p}, top_k={top_k}, system={'set' if system else 'none'}"
        )
        
        try:
            # Prepare the message
            message = anthropic.messages.Message(
                role="user",
                content=prompt,
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                stop_sequences=stop_sequences,
                system=system,
                metadata=metadata,
            )
            
            # Stream the response
            async with self.client.messages.stream(message) as stream:
                prompt_tokens = 0  # We'll get this from the response
                completion_tokens = 0
                
                async for chunk in stream:
                    if chunk.type == "content_block_delta":
                        completion_tokens += len(chunk.text.split())  # Approximate
                        if DEBUG_LEVEL > 0:
                            logger.debug(f"Received chunk: {len(chunk.text)} chars")
                        yield chunk.text
                    elif chunk.type == "message_start":
                        prompt_tokens = chunk.message.usage.input_tokens
                        logger.debug(f"Stream started, prompt_tokens={prompt_tokens}")
                
                # Update usage statistics
                cost = self._calculate_cost(prompt_tokens, completion_tokens)
                self.stats.add_request(prompt_tokens, completion_tokens, cost)
                logger.debug(
                    f"Stream complete: prompt_tokens={prompt_tokens}, "
                    f"completion_tokens={completion_tokens}, cost=${cost:.6f}"
                )
                
        except anthropic.APIError as e:
            logger.error(f"Anthropic API error: {str(e)}")
            # Enhance error message with context
            raise anthropic.APIError(
                f"Anthropic API error ({e.status_code}): {str(e)}. "
                f"Model: {self.model}, Prompt length: {len(prompt)}"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            # Catch-all for unexpected errors
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