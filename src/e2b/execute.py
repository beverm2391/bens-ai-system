#!/usr/bin/env python3

import sys
import argparse
import os
from e2b import Sandbox

def execute_code(code: str, runtime: str = "python3"):
    """Execute code in an e2b sandbox environment."""
    debug = os.getenv("DEBUG_LEVEL", "0")
    api_key = os.getenv("E2B_API_KEY")
    
    if debug != "0":
        print(f"[DEBUG] Executing code with runtime: {runtime}")
        print(f"[DEBUG] Code:\n{code}")
    
    with Sandbox(api_key=api_key) as sandbox:
        try:
            result = sandbox.run(code)
            if debug != "0":
                print(f"[DEBUG] Stdout: {result.stdout}")
                print(f"[DEBUG] Stderr: {result.stderr}")
            return result.stdout, result.stderr
        except Exception as e:
            if debug != "0":
                print(f"[DEBUG] Error: {str(e)}")
            raise

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