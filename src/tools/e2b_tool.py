import os
import logging
from src.e2b.execute import execute_code

logger = logging.getLogger(__name__)

# Get debug level
debug_level = int(os.getenv("DEBUG_LEVEL", "0"))


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