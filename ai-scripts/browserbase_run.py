#!/usr/bin/env python3
"""
Run browser automation tasks using Browserbase and Playwright.

Example usage:
    # Run a script file
    ./browserbase_run.py script.py
    
    # Run with direct code
    ./browserbase_run.py -c "page.goto('https://example.com'); print(page.title())"
"""

import os
import sys
import argparse
from dotenv import load_dotenv
from src.browserbase import BrowserbaseClient

# Load environment variables
load_dotenv()

def run_script_file(script_path: str) -> None:
    """Run a Python script file containing browser automation code."""
    with open(script_path) as f:
        code = f.read()
        
    # Create function from code
    def automation(playwright, page):
        # Make playwright available to script
        exec(code, {"playwright": playwright, "page": page})
        
    client = BrowserbaseClient()
    client.run_playwright(automation)


def run_code(code: str) -> None:
    """Run browser automation code directly."""
    def automation(playwright, page):
        exec(code, {"playwright": playwright, "page": page})
        
    client = BrowserbaseClient()
    client.run_playwright(automation)


def main():
    parser = argparse.ArgumentParser(description="Run browser automation with Browserbase")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("script", nargs="?", help="Path to Python script file to run")
    group.add_argument("-c", "--code", help="Browser automation code to run")
    
    args = parser.parse_args()
    
    try:
        if args.script:
            run_script_file(args.script)
        else:
            run_code(args.code)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main() 