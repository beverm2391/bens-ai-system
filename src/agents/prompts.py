# This module manages prompts for code generation and response interpretation. It provides system prompts that control code generation behavior and natural language formatting. The prompts ensure consistent output formatting while enforcing import restrictions and generating complete, self-contained code. Security measures prevent unauthorized execution while optimizing for minimal token usage.

def get_code_generation_prompt(allowed_imports: set) -> str:
    # This function creates a system prompt for code generation that enforces strict output requirements. It ensures raw Python code output without markdown or language identifiers, restricts imports to an allowed list, and requires complete, runnable scripts. The prompt is designed with security in mind by preventing execution attempts and requiring pure Python output.
    
    return f"""You are a Python code generator that outputs ONLY raw Python code.
DO NOT USE ANY MARKDOWN FORMATTING OR TRIPLE BACKTICKS.
DO NOT include the word 'python' or any other language identifier.
DO NOT add any explanatory text or comments.

Always start your response with the necessary imports from this allowed list: {allowed_imports}
For example:
import math
result = math.prod([6, 7])
print(result)

The code must be complete and self-contained in a single Python script.
Output only the raw Python code that would be in a .py file."""

# This prompt guides natural language response generation by enforcing clear and concise output formatting. It focuses on delivering key results and insights using conversational language while keeping responses brief but informative.
RESPONSE_INTERPRETATION_PROMPT = """You are a helpful assistant. Provide a clear, concise answer based on the code output.

Use natural conversational language to explain the key results, keeping responses brief but informative. Include relevant values and explain any errors that occurred."""
