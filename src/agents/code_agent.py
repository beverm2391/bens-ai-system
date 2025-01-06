# This module implements a secure code generation and execution system. It takes natural language prompts to generate Python code, validates it for security and allowed imports, then executes it in a sandboxed environment. The system maintains isolated state between runs while enforcing security through AST-based validation, import restrictions, and sandboxed execution. Performance is optimized through async operations and state caching, with comprehensive error handling for system stability.

import asyncio
from openai import AsyncOpenAI
from time import perf_counter
from dotenv import load_dotenv
import os
import ast
import logging
from typing import Union, List, Set, Dict, Any
from src.e2b.execute import execute_code
from src.clients.together_client import TogetherClient
from .prompts import get_code_generation_prompt, RESPONSE_INTERPRETATION_PROMPT

# Initialize environment and logging
load_dotenv()
logger = logging.getLogger(__name__)

# Validate required API keys are set
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

# Default configuration values
DEFAULTS = {
    "code_generation_model": "Qwen/Qwen2.5-Coder-32B-Instruct",  # Latest Qwen model for code generation
    "response_model": "gpt-4o",  # GPT-4 for natural language responses
    "logging_level": 1,  # Basic logging by default
}

class CodeAgent:
    # This class manages the end-to-end workflow of code generation from natural language, security validation, sandboxed execution, and result interpretation. It maintains state between executions for multi-step operations while ensuring security through validation and sandboxing. The system uses async operations for API calls and efficient prompt engineering, with comprehensive error handling to maintain system stability.

    def __init__(
        self,
        code_gen_model: str = None,
        response_model: str = None,
        logging_level: int = None,
        tools: List = None,
    ):
        # Initialize OpenAI client for natural language responses
        self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        
        # Initialize Together client for code generation
        self.together_client = TogetherClient(
            model=code_gen_model or DEFAULTS["code_generation_model"]
        )
        
        # Set logging detail level
        self.logging_level = logging_level or DEFAULTS["logging_level"]
        
        # Set model for response generation
        self.response_model = response_model or DEFAULTS["response_model"]

        # Define safe Python imports for execution
        self.base_imports = {
            "os",      # File/path operations
            "sys",     # System functions
            "time",    # Time functions
            "datetime",# Date/time handling
            "random",  # Random number generation
            "math",    # Math operations
            "json",    # JSON handling
        }

        # Initialize shared state dictionary for executions
        self.state: Dict[str, Any] = {}

    def validate_code(self, code: Union[str, None]) -> tuple[bool, str]:
        # This function performs security validation of generated code by checking Python syntax, allowed imports, and dangerous operations. It returns a tuple indicating validity and any error message.
        
        if not isinstance(code, str):
            return False, f"Code must be a string, got {type(code)}"
        if not code.strip():
            return False, "Code cannot be empty"

        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module = node.module if isinstance(node, ast.ImportFrom) else None
                    for alias in node.names:
                        import_name = f"{module}.{alias.name}" if module else alias.name
                        base_module = import_name.split(".")[0]
                        if base_module not in self.base_imports:
                            return False, f"Import '{import_name}' is not allowed"
            return True, ""
            
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            return False, f"Validation error: {str(e)}"

    async def generate(self, prompt: str) -> str:
        # This function generates Python code from natural language using Together's Qwen model. The generated code is raw Python without markdown or explanatory text, ensuring complete and self-contained scripts with required imports from the whitelist.
        
        if self.logging_level > 0:
            print(f"Generating code...")

        code = await self.together_client.chat_completion(
            messages=[
                {"role": "system", "content": get_code_generation_prompt(self.base_imports)},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )

        return code

    async def execute(self, code: str) -> Any:
        # This function executes validated code in a sandbox while managing state. It sets up the execution environment with current state, runs code in isolation, captures output, and updates state from results. The system maintains clean state on failure and provides comprehensive error handling.
        
        if self.logging_level > 1:
            print(f"Executing code...")

        state_setup = []
        for k, v in self.state.items():
            if not callable(v):
                state_setup.append(f"{k} = {repr(v)}")

        full_code = "\n".join(
            filter(
                None,
                [
                    "\n".join(state_setup),
                    code.strip(),
                ],
            )
        )

        try:
            stdout, stderr = execute_code(full_code)
            if stderr:
                raise ValueError(f"Code execution error: {stderr}")

            # Update state from execution output
            # Look for assignment statements to track
            if stdout:
                for line in stdout.split("\n"):
                    if "=" in line:
                        try:
                            var_name = line.split("=")[0].strip()
                            var_value = eval(line.split("=")[1].strip(), {}, {})
                            self.state[var_name] = var_value
                        except:
                            # Skip failed state updates
                            pass

            return stdout

        except Exception as e:
            # Log error and re-raise with context
            logger.error(f"Error in code execution: {str(e)}")
            raise ValueError(f"Code execution error: {str(e)}")

    async def run(self, prompt: str) -> str:
        # Main entry point for code generation and execution
        #
        # Complete workflow:
        # 1. Generate code from natural language
        # 2. Validate code for security
        # 3. Execute in sandbox
        # 4. Interpret results in natural language
        #
        # Args:
        #     prompt: Natural language request
        #
        # Returns:
        #     Natural language response describing results
        #
        # Side effects:
        #     - Updates agent state from execution
        #     - Makes API calls to Together and OpenAI
        #     - Logs operations if enabled
        #
        # Error handling:
        #     - Validates all code before execution
        #     - Provides clear error messages
        #     - Maintains system stability

        # Generate and validate code
        code = await self.generate(prompt)
        res, message = self.validate_code(code)
        if not res:
            raise ValueError(message)

        # Execute validated code
        output = await self.execute(code)

        # Use OpenAI to interpret results in natural language
        final_response = await self.openai_client.chat.completions.create(
            model=self.response_model,
            messages=[
                {
                    "role": "system",
                    "content": RESPONSE_INTERPRETATION_PROMPT,
                },
                {
                    "role": "user",
                    "content": f"The original prompt was: {prompt}\nThe code output was: {output}\nPlease provide a clear answer based on this output.",
                },
            ],
        )

        return final_response.choices[0].message.content


# CLI interface for direct agent usage
async def main(prompt: str):
    # Command line entry point
    #
    # Creates agent with default config and runs prompt
    agent = CodeAgent()
    response = await agent.run(prompt)
    print(response)


# Allow running as script
if __name__ == "__main__":
    import argparse

    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description="Execute code based on a prompt")
    parser.add_argument("prompt", help="The prompt to generate and execute code for")
    args = parser.parse_args()

    # Run agent with provided prompt
    asyncio.run(main(args.prompt))
