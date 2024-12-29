"""
Robust OpenAI client with streaming, token tracking, and full parameter support.
"""
import os
import logging
from typing import Optional, Dict, List, AsyncIterator, Union, Any
from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from openai.types.chat.chat_completion import Choice, ChatCompletionMessage
from openai.types.chat.chat_completion_chunk import ChoiceDelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug level from environment
DEBUG_LEVEL = int(os.getenv("DEBUG_LEVEL", "0"))

class UsageStats:
    """Track API usage and costs."""
    def __init__(self):
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.total_cost = 0.0
        self.requests = 0
        
    def add_request(self, prompt_tokens: int, completion_tokens: int, cost: float):
        """Record usage from a request."""
        self.prompt_tokens += prompt_tokens
        self.completion_tokens += completion_tokens
        self.total_cost += cost
        self.requests += 1
        
    @property
    def total_tokens(self) -> int:
        """Total tokens used."""
        return self.prompt_tokens + self.completion_tokens
        
    def __getitem__(self, key: str) -> Union[int, float]:
        """Allow dict-like access to stats."""
        if key == "prompt_tokens":
            return self.prompt_tokens
        elif key == "completion_tokens":
            return self.completion_tokens
        elif key == "total_tokens":
            return self.total_tokens
        elif key == "total_cost":
            return self.total_cost
        elif key == "requests":
            return self.requests
        raise KeyError(f"Invalid stat key: {key}")

class OpenAIClient:
    """Client for OpenAI's API with streaming and usage tracking."""
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        default_max_tokens: int = 1000,
        cost_per_1k_prompt: float = 0.03,
        cost_per_1k_completion: float = 0.06,
    ):
        """
        Initialize OpenAI client.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4)
            default_max_tokens: Default max tokens for completions
            cost_per_1k_prompt: Cost per 1k prompt tokens
            cost_per_1k_completion: Cost per 1k completion tokens
        """
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
        self.default_max_tokens = default_max_tokens
        self.cost_per_1k_prompt = cost_per_1k_prompt
        self.cost_per_1k_completion = cost_per_1k_completion
        self.stats = UsageStats()
        
        logger.debug(
            f"Initialized OpenAIClient with model={model}, "
            f"default_max_tokens={default_max_tokens}"
        )
        
    def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate cost for token usage."""
        prompt_cost = (prompt_tokens / 1000) * self.cost_per_1k_prompt
        completion_cost = (completion_tokens / 1000) * self.cost_per_1k_completion
        return prompt_cost + completion_cost
        
    @property
    def usage_stats(self) -> Dict[str, Union[int, float]]:
        """Get current usage statistics."""
        return {
            "prompt_tokens": self.stats.prompt_tokens,
            "completion_tokens": self.stats.completion_tokens,
            "total_tokens": self.stats.total_tokens,
            "total_cost": self.stats.total_cost,
            "requests": self.stats.requests,
        }
        
    async def stream(
        self,
        prompt: str,
        *,
        max_tokens: Optional[int] = None,
        temperature: float = 1.0,
        top_p: float = 1.0,
        n: int = 1,
        frequency_penalty: float = 0.0,
        presence_penalty: float = 0.0,
        stop: Optional[Union[str, List[str]]] = None,
        system: Optional[str] = None,
        logit_bias: Optional[Dict[str, float]] = None,
        user: Optional[str] = None,
        response_format: Optional[Dict[str, str]] = None,
        seed: Optional[int] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    ) -> AsyncIterator[str]:
        """
        Stream a chat completion from OpenAI.
        
        Args:
            prompt: The prompt to complete
            max_tokens: Maximum tokens to generate (default: self.default_max_tokens)
            temperature: Sampling temperature (default: 1.0)
            top_p: Nucleus sampling parameter (default: 1.0)
            n: Number of completions to generate (default: 1)
            frequency_penalty: Frequency penalty (default: 0.0)
            presence_penalty: Presence penalty (default: 0.0)
            stop: Stop sequences (default: None)
            system: System prompt (default: None)
            logit_bias: Token bias dictionary (default: None)
            user: User identifier (default: None)
            response_format: Response format (default: None)
            seed: Random seed (default: None)
            tools: Function calling tools (default: None)
            tool_choice: Tool choice (default: None)
            
        Yields:
            Generated text chunks
            
        Raises:
            ValueError: For invalid parameters
            openai.OpenAIError: For API errors
        """
        # Parameter validation
        if not prompt:
            raise ValueError("Prompt cannot be empty")
        if temperature < 0 or temperature > 2:
            raise ValueError("Temperature must be between 0 and 2")
        if top_p < 0 or top_p > 1:
            raise ValueError("top_p must be between 0 and 1")
        if n < 1:
            raise ValueError("n must be >= 1")
            
        max_tokens = max_tokens or self.default_max_tokens
        
        # Build messages
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        
        # Build request parameters
        params = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
            "n": n,
            "frequency_penalty": frequency_penalty,
            "presence_penalty": presence_penalty,
            "stream": True,
        }
        
        # Add optional parameters
        if stop:
            params["stop"] = stop if isinstance(stop, list) else [stop]
        if logit_bias:
            params["logit_bias"] = logit_bias
        if user:
            params["user"] = user
        if response_format:
            params["response_format"] = response_format
        if seed is not None:
            params["seed"] = seed
        if tools:
            params["tools"] = tools
        if tool_choice:
            params["tool_choice"] = tool_choice
            
        logger.debug(
            f"Starting stream with: prompt_length={len(prompt)}, "
            f"max_tokens={max_tokens}, temperature={temperature}, "
            f"top_p={top_p}, system={'set' if system else 'none'}"
        )
        
        try:
            # Get initial completion to get usage info
            initial_response = await self.client.chat.completions.create(
                **{**params, "stream": False}
            )
            
            # Extract usage info
            if hasattr(initial_response, "usage"):
                prompt_tokens = initial_response.usage.prompt_tokens
                completion_tokens = initial_response.usage.completion_tokens
            else:
                # Fallback to approximation
                prompt_tokens = len(" ".join(m["content"] for m in messages).split())
                completion_tokens = 0
            
            # Now stream the actual response
            stream: AsyncStream[ChatCompletionChunk] = await self.client.chat.completions.create(**params)
            
            async for chunk in stream:
                if DEBUG_LEVEL > 0:
                    logger.debug(f"Received chunk: {chunk}")
                    
                # Process each choice in the chunk
                for choice in chunk.choices:
                    if hasattr(choice, "delta") and choice.delta.content:
                        text = choice.delta.content
                        completion_tokens += len(text.split())  # Approximate
                        if DEBUG_LEVEL > 0:
                            logger.debug(f"Received text: {len(text)} chars")
                        yield text
                        
            # Update usage statistics
            cost = self._calculate_cost(prompt_tokens, completion_tokens)
            self.stats.add_request(prompt_tokens, completion_tokens, cost)
            logger.debug(
                f"Stream complete: prompt_tokens={prompt_tokens}, "
                f"completion_tokens={completion_tokens}, cost=${cost:.6f}"
            )
                
        except Exception as e:
            logger.error(f"Stream error: {str(e)}")
            raise 