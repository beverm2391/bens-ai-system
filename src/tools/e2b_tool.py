import os
import logging
from src.e2b.execute import execute_code

logger = logging.getLogger(__name__)

# Get debug level
debug_level = int(os.getenv("DEBUG_LEVEL", "0"))

E2B_SCHEMA = {
    "description": """
    Executes code in a secure sandbox environment using E2B.
    This tool should be used when you need to run code snippets safely.
    The code runs in an isolated environment with proper error handling.
    Supports Python 3 runtime by default.
    Returns both stdout and stderr from the execution, along with a success flag.
    Use this for testing code, performing calculations, or running experiments.
    Note: The tool will return empty strings for stdout/stderr if there is no output.
    """,
    "input_schema": {
        "type": "object",
        "properties": {
            "code": {
                "type": "string",
                "description": "The code string to execute"
            },
            "runtime": {
                "type": "string",
                "description": "Runtime environment to use",
                "default": "python3"
            }
        },
        "required": ["code"]
    }
}

def run_code(code: str, runtime: str = "python3") -> dict:
    """Execute code in E2B sandbox and return results."""
    if debug_level > 0:
        logger.debug(f"Code:\n{code}")
    
    try:
        if debug_level > 0:
            logger.info("Executing code...")
        
        stdout, stderr = execute_code(code, runtime)
        
        if debug_level > 0:
            logger.info("Execution successful")
        
        return {
            "stdout": stdout or "",
            "stderr": stderr or "",
            "success": not stderr,
            "output": f"Code output:\n{stdout}" if stdout else "No output"
        }
        
    except Exception as e:
        logger.error(f"Code execution failed: {str(e)}")
        return {
            "stdout": "",
            "stderr": str(e),
            "success": False,
            "output": f"Error: {str(e)}"
        } 