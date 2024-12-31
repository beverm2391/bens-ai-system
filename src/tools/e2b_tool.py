import os
import logging
from typing import Dict, Any
from dotenv import load_dotenv
from src.e2b.execute import execute_code

# Configure logging based on DEBUG_LEVEL
DEBUG_LEVEL = int(os.getenv("DEBUG_LEVEL", "0"))
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO if DEBUG_LEVEL == 0 else logging.DEBUG)

# Load environment variables
load_dotenv()

def run_code(code: str, runtime: str = "python3") -> Dict[str, Any]:
    """
    Execute code in E2B sandbox environment
    
    Args:
        code: Code string to execute
        runtime: Runtime environment (default: python3)
        
    Returns:
        Dict containing stdout and stderr
    """
    if DEBUG_LEVEL > 0:
        logger.debug(f"Code:\n{code}")
    else:
        logger.info("Executing code...")
    
    stdout, stderr = execute_code(code, runtime)
    
    result = {
        "stdout": stdout if stdout else "",
        "stderr": stderr if stderr else "",
        "success": not stderr,
        "output": f"Code output:\n{stdout}" if stdout else "No output"
    }
    
    # Log result directly
    with open("demos/e2b/execution_log.txt", "a") as f:
        f.write(f"\nDirect Tool Log:\n")
        f.write(f"Code: {code}\n")
        f.write(f"Result: {result}\n")
        f.write("-" * 50 + "\n")
    
    if DEBUG_LEVEL > 0:
        logger.debug(f"stdout: {stdout}")
        if stderr:
            logger.error(f"stderr: {stderr}")
    else:
        logger.info(f"Execution {'successful' if result['success'] else 'failed'}")
        
    return result

# Claude tool schema
E2B_SCHEMA = {
    "name": "execute_code",
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