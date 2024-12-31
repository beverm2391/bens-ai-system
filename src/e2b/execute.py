#!/usr/bin/env python3

import sys
import argparse
import os
import logging
from e2b_code_interpreter import Sandbox

# Configure logging based on DEBUG_LEVEL
DEBUG_LEVEL = int(os.getenv("DEBUG_LEVEL", "0"))

# Configure e2b logger
e2b_logger = logging.getLogger("e2b")
e2b_logger.setLevel(logging.WARNING if DEBUG_LEVEL == 0 else logging.DEBUG)

# Configure our logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO if DEBUG_LEVEL == 0 else logging.DEBUG)

def execute_code(code: str, runtime: str = "python3"):
    """Execute code in E2B sandbox"""
    with Sandbox() as sandbox:
        result = sandbox.run_code(code)
        stdout = "\n".join(result.logs.stdout) if result.logs.stdout else ""
        stderr = "\n".join(result.logs.stderr) if result.logs.stderr else ""
        if result.error:
            stderr = str(result.error)
        return stdout, stderr

def main():
    parser = argparse.ArgumentParser(description="Execute code in a secure sandbox")
    parser.add_argument("code", help="Code to execute")
    parser.add_argument("--runtime", default="python3", help="Runtime environment")
    args = parser.parse_args()

    stdout, stderr = execute_code(args.code, args.runtime)
    if stdout:
        print("Output:", stdout)
    if stderr:
        print("Errors:", stderr, file=sys.stderr)

if __name__ == "__main__":
    main() 