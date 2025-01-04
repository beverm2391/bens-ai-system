"""
A code generation and execution agent that combines:
- Code generation using Together's Qwen model
- Secure code execution in a sandbox environment
- Tool injection for extensibility
- State management between executions
- Async support for both sync and async tools
"""
from openai import AsyncOpenAI
import asyncio
from time import perf_counter
from dotenv import load_dotenv
import os
import ast
import logging
from typing import Union, List, Any, Callable
from src.e2b.execute import execute_code
from src.clients.together_client import TogetherClient
from .toolbox import Tool, Toolbox

# Setup environment and logging
load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

class CodeAgent:
    """
    An agent that generates, validates, and executes Python code in response to natural language prompts.
    Supports both synchronous and asynchronous tools, maintains state between executions, and runs code
    in a secure sandbox environment.
    """
    def __init__(self, tools: List[Tool] = None, logging_level: int = logging.INFO):
        """
        Initialize the agent with optional tools and logging configuration.
        
        Args:
            tools: List of Tool objects that provide additional functionality
            logging_level: Logging level for debug output
        """
        self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.together_client = TogetherClient(model="Qwen/Qwen2.5-Coder-32B-Instruct")
        self.toolbox = Toolbox()  # Use singleton instance
        if tools:  # Add any additional tools
            for tool in tools:
                self.toolbox.add_tool(tool)
                
        # Allowed imports for generated code
        self.allowed_imports = [
            "requests", "os", "sys", "time", "datetime",
            "random", "math", "json", "bs4", "asyncio"
        ]
        self.logging_level = logging_level
        logger.setLevel(logging_level)
        self.state = {}  # Shared state between executions

    async def _wrap_sync_tool(self, func: Callable) -> Callable:
        """
        Wrap a tool function to make it async-compatible and update state with its result.
        
        Args:
            func: The tool function to wrap
            
        Returns:
            An async wrapper function that handles both sync and async tools
        """
        async def wrapper(*args, **kwargs):
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = await asyncio.to_thread(func, *args, **kwargs)
            self.state['result'] = result
            return result
        return wrapper

    def validate_code(self, code: Union[str, None]) -> tuple[bool, str]:
        """
        Validate generated code for security and syntax.
        
        Args:
            code: The code string to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        logger.debug(f"Validating code: {code}")
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
                        if base_module not in self.allowed_imports:
                            logger.warning(f"Import '{import_name}' is not allowed")
                            return False, f"Import '{import_name}' is not allowed"
            logger.debug("Code validation successful")
            return True, ""
        except SyntaxError as e:
            logger.error(f"Syntax error in code validation: {str(e)}")
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error in code validation: {str(e)}")
            return False, f"Validation error: {str(e)}"

    def system_prompt(self) -> str:
        """Generate the system prompt for code generation."""
        return f"""You are a Python code generator that outputs ONLY raw Python code.
IMPORTANT: DO NOT USE ANY MARKDOWN FORMATTING OR TRIPLE BACKTICKS.
DO NOT include the word 'python' or any other language identifier.
DO NOT add any explanatory text or comments.

Always start your response with the necessary imports from this allowed list: {self.allowed_imports}
For example, if using BeautifulSoup, start with 'from bs4 import BeautifulSoup'.

The code must be complete and self-contained in a single Python script.
Output only the raw Python code that would be in a .py file."""

    async def generate(self, prompt: str) -> str:
        """
        Generate Python code from a natural language prompt using the Qwen model.
        
        Args:
            prompt: Natural language description of the code to generate
            
        Returns:
            Generated Python code as a string
        """
        start_time = perf_counter()
        logger.info("Starting code generation")
        
        try:
            code = await self.together_client.chat_completion(
                messages=[
                    {"role": "system", "content": self.system_prompt()},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.7,
                max_tokens=1000,
            )
            logger.info(f"Code generated in {perf_counter() - start_time:0.2f} seconds")
            return code
        except Exception as e:
            logger.error(f"Error in code generation: {str(e)}")
            raise

    async def execute(self, code: str) -> Any:
        """
        Execute code in a secure sandbox with access to tools and state.
        
        Args:
            code: Python code to execute
            
        Returns:
            The result of the execution, if any
        """
        start_time = perf_counter()
        logger.debug("Starting code execution")
        
        # Create tool definitions for sandbox
        tool_setup = []
        for name, tool in self.toolbox.tools.items():
            if asyncio.iscoroutinefunction(tool.func):
                # Skip async tools for now
                continue
                
            # Get the function's source code if possible
            if hasattr(tool.func, '__code__'):
                tool_setup.append(f"""
def {name}(x, y):
    # {tool.description}
    return x {tool.func.__code__.co_code[0]} y
""")
            else:
                # For lambda functions, infer the operation
                sample_result = tool.func(1, 2)
                if sample_result == 3:
                    op = "+"
                elif sample_result == 2:
                    op = "*"
                elif sample_result == 0.5:
                    op = "/"
                else:
                    op = "-"
                tool_setup.append(f"""
def {name}(x, y):
    # {tool.description}
    return x {op} y
""")
        
        # Prepare state variables for sandbox
        state_setup = "\n".join([
            f"{k} = {repr(v)}"
            for k, v in self.state.items()
            if not callable(v)
        ])
        
        # Combine all code
        full_code = f"""
{state_setup}
{''.join(tool_setup)}
{code}
"""
        
        try:
            # Execute in sandbox
            stdout, stderr = execute_code(full_code)
            if stderr:
                raise ValueError(stderr)
                
            # Parse stdout to update state
            if stdout:
                # Extract variable assignments from stdout
                for line in stdout.split("\n"):
                    if "=" in line:
                        try:
                            var_name = line.split("=")[0].strip()
                            var_value = eval(line.split("=")[1].strip())
                            self.state[var_name] = var_value
                        except:
                            pass
                logger.debug(f"Execution output: {stdout}")
            
            logger.info(f"Code executed in {perf_counter() - start_time:0.2f} seconds")
            return stdout
            
        except Exception as e:
            logger.error(f"Error in code execution: {str(e)}")
            raise ValueError(f"Code execution error: {str(e)}")

    async def run(self, prompt: str) -> str:
        """
        Main entry point - generate, validate, and execute code from a prompt.
        
        Args:
            prompt: Natural language description of what to do
            
        Returns:
            A natural language response based on the code execution results
        """
        logger.info("Starting agent run")
        try:
            code = await self.generate(prompt)
            res, message = self.validate_code(code)
            if not res:
                raise ValueError(message)
                
            output = await self.execute(code)
            logger.debug("Generating final response")

            start_time = perf_counter()
            final_response = await self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant. Provide a clear, concise answer based on the code output.",
                    },
                    {
                        "role": "user",
                        "content": f"The original prompt was: {prompt}\nThe code output was: {output}\nPlease provide a clear answer based on this output.",
                    },
                ],
            )
            logger.info(f"Final response generated in {perf_counter() - start_time:0.2f} seconds")
            return final_response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error in agent run: {str(e)}")
            raise

# CLI interface
async def main(prompt: str):
    """CLI entry point for running the agent."""
    agent = CodeAgent()
    response = await agent.run(prompt)
    print(response)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Execute code based on a prompt")
    parser.add_argument("prompt", help="The prompt to generate and execute code for")
    args = parser.parse_args()
    
    asyncio.run(main(args.prompt))
