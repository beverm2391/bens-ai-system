"""
Tool for executing code in E2B sandbox
"""
import os
import time
import logging
from typing import Dict, Any
from src.e2b.execute import execute_code

logger = logging.getLogger(__name__)

def run_code(code: str, timeout: int = 30) -> Dict[str, Any]:
    """
    Execute code in E2B sandbox and return results with usage metrics
    
    Args:
        code: Python code to execute
        timeout: Execution timeout in seconds
        
    Returns:
        Dict containing execution results and usage metrics
    """
    start_time = time.time()
    
    try:
        stdout, stderr = execute_code(code)
        execution_time = time.time() - start_time
        
        # Track usage metrics
        usage = {
            "execution_seconds": execution_time,
            "code_length": len(code),
            "stdout_length": len(stdout),
            "stderr_length": len(stderr),
            # TODO: Implement memory tracking
            # "memory_mb": get_sandbox_memory_usage(),
            # TODO: Implement CPU tracking
            # "cpu_percent": get_sandbox_cpu_usage(),
            # TODO: Track imports used
            # "imports": extract_imports(code)
        }
        
        return {
            "stdout": stdout,
            "stderr": stderr,
            "success": not stderr,
            "usage": usage
        }
        
    except Exception as e:
        execution_time = time.time() - start_time
        logger.error(f"Code execution failed: {str(e)}")
        
        return {
            "stdout": "",
            "stderr": str(e),
            "success": False,
            "usage": {
                "execution_seconds": execution_time,
                "code_length": len(code),
                "stdout_length": 0,
                "stderr_length": len(str(e))
            }
        } 