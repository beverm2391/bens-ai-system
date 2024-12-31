#!/usr/bin/env python3

import sys
import argparse
from pathlib import Path
from e2b import Sandbox
import os

def execute_file(file_path: str, runtime: str = "python3"):
    """Execute code from a file in an e2b sandbox environment."""
    debug = os.getenv("DEBUG_LEVEL", "0")
    api_key = os.getenv("E2B_API_KEY")
    
    if debug != "0":
        print(f"[DEBUG] Executing file: {file_path}")
        print(f"[DEBUG] Runtime: {runtime}")
    
    try:
        code = Path(file_path).read_text()
        if debug != "0":
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
    except FileNotFoundError:
        if debug != "0":
            print(f"[DEBUG] File not found: {file_path}")
        raise

def main():
    parser = argparse.ArgumentParser(description="Execute code file in a secure sandbox")
    parser.add_argument("file", help="Path to code file")
    parser.add_argument("--runtime", default="python3", help="Runtime environment")
    args = parser.parse_args()

    stdout, stderr = execute_file(args.file, args.runtime)
    if stdout:
        print("Output:", stdout)
    if stderr:
        print("Errors:", stderr, file=sys.stderr)

if __name__ == "__main__":
    main() 