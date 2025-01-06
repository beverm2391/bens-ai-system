"""
Code generation agent that uses Together's Qwen model for code and OpenAI for responses.
"""
from openai import AsyncOpenAI
import asyncio
from time import perf_counter
from dotenv import load_dotenv
import os
import ast
from src.e2b.execute import execute_code
from src.clients.together_client import TogetherClient
from typing import Union, List, Set, Dict, Any
import logging

load_dotenv()

logger = logging.getLogger(__name__)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")

class CodeAgent:
    def __init__(self, tools: List = None):
        self.openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.together_client = TogetherClient(model="Qwen/Qwen2.5-Coder-32B-Instruct")
        
        # Base allowed imports that are always available
        self.base_imports = {
            "os",
            "sys",
            "time",
            "datetime", 
            "random",
            "math",
            "json",
        }
        
        self.state: Dict[str, Any] = {}  # Shared state between executions
        self.logging_level = 1

    def validate_code(self, code: Union[str, None]) -> tuple[bool, str]:
        """Validates code for syntax and allowed imports."""
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

    def system_prompt(self):
        """Returns the system prompt for code generation."""
        return f"""You are a Python code generator that outputs ONLY raw Python code.
DO NOT USE ANY MARKDOWN FORMATTING OR TRIPLE BACKTICKS.
DO NOT include the word 'python' or any other language identifier.
DO NOT add any explanatory text or comments.

Always start your response with the necessary imports from this allowed list: {self.base_imports}
For example:
import math
result = math.prod([6, 7])
print(result)

The code must be complete and self-contained in a single Python script.
Output only the raw Python code that would be in a .py file."""

    async def generate(self, prompt: str) -> str:
        """Generates code from a prompt using Together's Qwen model."""
        if self.logging_level > 0:
            print(f"Generating code...")
        
        code = await self.together_client.chat_completion(
            messages=[
                {"role": "system", "content": self.system_prompt()},
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=1000,
        )
        
        return code

    async def execute(self, code: str) -> Any:
        """Executes code and updates state."""
        if self.logging_level > 1:
            print(f"Executing code...")

        # Prepare code with state
        state_setup = []
        for k, v in self.state.items():
            if not callable(v):
                state_setup.append(f"{k} = {repr(v)}")
        
        # Combine state setup with user code
        full_code = "\n".join(filter(None, [
            "\n".join(state_setup),  # First set up state
            code.strip()             # Then add user code
        ]))

        try:
            stdout, stderr = execute_code(full_code)
            if stderr:
                raise ValueError(f"Code execution error: {stderr}")

            # Parse stdout to update state
            # This is a simple approach - we look for assignment statements in the output
            if stdout:
                for line in stdout.split("\n"):
                    if "=" in line:
                        try:
                            var_name = line.split("=")[0].strip()
                            var_value = eval(line.split("=")[1].strip(), {}, {})
                            self.state[var_name] = var_value
                        except:
                            pass

            return stdout

        except Exception as e:
            logger.error(f"Error in code execution: {str(e)}")
            raise ValueError(f"Code execution error: {str(e)}")

    async def run(self, prompt: str) -> str:
        """Main entry point - generates, validates and executes code, then returns result."""
        code = await self.generate(prompt)
        res, message = self.validate_code(code)
        if not res:
            raise ValueError(message)
            
        output = await self.execute(code)
        
        # Use OpenAI to interpret the result
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
        
        return final_response.choices[0].message.content

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
