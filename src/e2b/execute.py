#!/usr/bin/env python3

import sys
import argparse
import os
from e2b_code_interpreter import Sandbox

def execute_code(code: str, runtime: str = "python3"):
    """Execute code in an e2b sandbox environment."""
    debug = os.getenv("DEBUG_LEVEL", "0")
    api_key = os.getenv("E2B_API_KEY")
    
    if debug != "0":
        print(f"[DEBUG] Executing code with runtime: {runtime}")
        print(f"[DEBUG] Code:\n{code}")
    
    with Sandbox(api_key=api_key) as sandbox:
        try:
            result = sandbox.run_code(code)
            if debug != "0":
                print(f"[DEBUG] Result type: {type(result)}")
                print(f"[DEBUG] Result dir: {dir(result)}")
                print(f"[DEBUG] Result vars: {vars(result)}")
                if result.error:
                    print(f"[DEBUG] Error type: {type(result.error)}")
                    print(f"[DEBUG] Error dir: {dir(result.error)}")
                    print(f"[DEBUG] Error str: {str(result.error)}")
            stdout = "\n".join(result.logs.stdout) if result.logs.stdout else ""
            stderr = "\n".join(result.logs.stderr) if result.logs.stderr else ""
            if result.error:
                stderr = str(result.error)
            if debug != "0":
                print(f"[DEBUG] Stdout: {stdout}")
                print(f"[DEBUG] Stderr: {stderr}")
            return stdout, stderr
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