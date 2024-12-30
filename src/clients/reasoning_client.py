"""
OpenAI-based reasoning client with step-by-step thought process support.
"""
import json
from typing import Optional, Dict, List, Any, AsyncIterator
from .openai_client import OpenAIClient

class ReasoningClient:
    """Client for step-by-step reasoning using OpenAI."""
    
    # System prompts for different reasoning patterns
    STEP_BY_STEP_PROMPT = """
    Solve problems step by step:
    1. Break down the problem into smaller steps
    2. Think through each step carefully
    3. Show your reasoning for each step
    4. Combine steps to reach the final answer
    
    Format each step as:
    Step 1: [step description]
    Step 2: [step description]
    etc.
    """
    
    CHAIN_OF_THOUGHT_PROMPT = """
    Use chain-of-thought reasoning to solve problems:
    1. First, I consider... [initial thoughts]
    2. Then, I think about... [analysis]
    3. Because of this... [logical connections]
    4. Therefore... [conclusion]
    
    Always show your thinking process using words like "consider", "think", "because".
    """
    
    STRUCTURED_OUTPUT_PROMPT = """
    Provide reasoning in structured format:
    {
        "steps": [
            {"step": 1, "thought": "...", "reason": "..."},
            {"step": 2, "thought": "...", "reason": "..."}
        ],
        "conclusion": "..."
    }
    
    Format your entire response as valid JSON.
    """
    
    def __init__(
        self,
        api_key: str,
        model: str = "gpt-4",
        default_max_tokens: int = 1000,
        structured_output: bool = False
    ):
        """
        Initialize reasoning client.
        
        Args:
            api_key: OpenAI API key
            model: Model to use (default: gpt-4)
            default_max_tokens: Default max tokens (default: 1000)
            structured_output: Whether to return JSON structure (default: False)
        """
        self.client = OpenAIClient(
            api_key,
            model="gpt-4-1106-preview" if structured_output else model,
            default_max_tokens=default_max_tokens
        )
        self.structured_output = structured_output
        
    async def reason(
        self,
        prompt: str,
        *,
        steps: Optional[int] = None,
        chain_of_thought: bool = True,
        examples: Optional[List[Dict[str, str]]] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Generate step-by-step reasoning.
        
        Args:
            prompt: The problem/question to reason about
            steps: Number of reasoning steps (default: None)
            chain_of_thought: Use chain-of-thought prompting (default: True)
            examples: Few-shot examples (default: None)
            **kwargs: Additional parameters for OpenAI client
            
        Yields:
            Reasoning steps and conclusion
        """
        # Build system prompt
        system_prompts = []
        
        if steps:
            system_prompts.append(
                f"Break this down into exactly {steps} steps. "
                f"Format each step as 'Step 1:', 'Step 2:', etc. "
                "Be clear and concise at each step."
            )
        
        if chain_of_thought:
            system_prompts.append(self.CHAIN_OF_THOUGHT_PROMPT)
        else:
            system_prompts.append(self.STEP_BY_STEP_PROMPT)
            
        if self.structured_output:
            system_prompts.append(self.STRUCTURED_OUTPUT_PROMPT)
            kwargs["response_format"] = {"type": "json_object"}
            
        # Add few-shot examples if provided
        if examples:
            examples_text = "\n\n".join(
                f"Question: {ex['question']}\n"
                f"Reasoning: {ex['reasoning']}\n"
                f"Answer: {ex['answer']}"
                for ex in examples
            )
            system_prompts.append(f"Examples:\n{examples_text}")
            
        system = "\n\n".join(system_prompts)
        
        # Stream the response
        async for chunk in self.client.stream(prompt, system=system, **kwargs):
            yield chunk
            
    @property
    def usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics from underlying client."""
        return self.client.usage_stats 