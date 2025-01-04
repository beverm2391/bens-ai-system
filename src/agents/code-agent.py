from openai import AsyncOpenAI
import asyncio
from time import perf_counter
from dotenv import load_dotenv
import os
import ast
from src.e2b.execute import execute_code
from typing import Union

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set")


class CodeAgent:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=OPENAI_API_KEY)
        self.allowed_imports = [
            "requests",
            "os",
            "sys",
            "time",
            "datetime",
            "random",
            "math",
            "json",
            "bs4",
        ]
        self.logging_level = 1

    def validate_code(self, code: Union[str, None]) -> tuple[bool, str]:
        if self.logging_level > 0:
            print(f"Validating code: {code}")
        if not isinstance(code, str):
            return False, f"Code must be a string, got {type(code)}"
        if not code.strip():
            return False, "Code cannot be empty"

        if self.logging_level > 0:
            print(f"Validating code...")
        try:
            tree = ast.parse(code)
            for node in ast.walk(tree):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    module = node.module if isinstance(node, ast.ImportFrom) else None
                    for alias in node.names:
                        import_name = f"{module}.{alias.name}" if module else alias.name
                        base_module = import_name.split(".")[0]
                        if base_module not in self.allowed_imports:
                            if self.logging_level > 0:
                                print(f"Import '{import_name}' is not allowed")
                            return False, f"Import '{import_name}' is not allowed"
            if self.logging_level > 0:
                print(f"Code is valid.")
            return True, ""
        except SyntaxError as e:
            if self.logging_level > 0:
                print(f"Syntax error: {str(e)}")
            return False, f"Syntax error: {str(e)}"
        except Exception as e:
            if self.logging_level > 0:
                print(f"Validation error: {str(e)}")
            return False, f"Validation error: {str(e)}"

    def system_prompt(self):
        return f"""You are a Python code generator that outputs ONLY raw Python code.
IMPORTANT: DO NOT USE ANY MARKDOWN FORMATTING OR TRIPLE BACKTICKS.
DO NOT include the word 'python' or any other language identifier.
DO NOT add any explanatory text or comments.

Always start your response with the necessary imports from this allowed list: {self.allowed_imports}
For example, if using BeautifulSoup, start with 'from bs4 import BeautifulSoup'.

The code must be complete and self-contained in a single Python script.
Output only the raw Python code that would be in a .py file."""

    async def generate(self, prompt: str):
        s = perf_counter()
        if self.logging_level > 0:
            print(f"Generating code...")
        response = await self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.system_prompt()},
                {"role": "user", "content": prompt},
            ],
        )
        if self.logging_level > 0:
            print(f"Code generated in {perf_counter() - s:0.2f} seconds.")
        return response.choices[0].message.content

    def execute(self, code: str):
        s = perf_counter()
        if self.logging_level > 1:
            print(f"Executing code...")
        stdout, stderr = execute_code(code)
        if stderr:
            raise ValueError(f"Code execution error: {stderr}")
        if self.logging_level > 1:
            print(f"Code executed in {perf_counter() - s:0.2f} seconds.")
        return stdout

    async def run(self, prompt: str):
        if self.logging_level > 0:
            print(f"Run initiated.")
        code = await self.generate(prompt)
        res, message = self.validate_code(code)
        if not res:
            raise ValueError(message)
        output = self.execute(code)
        if self.logging_level > 1:
            print(f"Using the output to answer the user's prompt...")

        s = perf_counter()
        final_response = await self.client.chat.completions.create(
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
        if self.logging_level > 1:
            print(f"Final response generated in {perf_counter() - s:0.2f} seconds.")
        return final_response.choices[0].message.content


async def main(prompt: str):
    agent = CodeAgent()
    response = await agent.run(prompt)
    print(response)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Execute code based on a prompt")
    parser.add_argument("prompt", help="The prompt to generate and execute code for")
    args = parser.parse_args()
    
    asyncio.run(main(args.prompt))
