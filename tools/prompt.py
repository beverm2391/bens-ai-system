#!/usr/bin/env python3
"""
Helper script for writing and running prompts with any script.
Usage:
    Write mode: python prompt.py write prompt.txt
    Execute mode: python prompt.py run prompt.txt target_script [args...]
"""
import sys
import os
from pathlib import Path

# Store prompts in ai-scripts/prompts
SCRIPT_DIR = Path(__file__).parent
PROMPTS_DIR = SCRIPT_DIR / "prompts"

def ensure_prompts_dir():
    """Create prompts directory if it doesn't exist."""
    PROMPTS_DIR.mkdir(exist_ok=True)

def write_prompt():
    """Write a prompt from stdin to file."""
    if len(sys.argv) != 3:
        print("Usage: python prompt.py write prompt.txt")
        sys.exit(1)
        
    filename = PROMPTS_DIR / sys.argv[2]
    print(f"Enter/paste your prompt. Press Ctrl-D (Unix) or Ctrl-Z (Windows) to save.")
    
    content = sys.stdin.read()
    
    ensure_prompts_dir()
    with open(filename, 'w') as f:
        f.write(content)
    print(f"\nPrompt saved to {filename}")

def run_prompt():
    """Run a prompt file through specified script."""
    if len(sys.argv) < 4:
        print("Usage: python prompt.py run prompt.txt target_script [args...]")
        sys.exit(1)
        
    prompt_file = PROMPTS_DIR / sys.argv[2]
    if not prompt_file.exists():
        print(f"Error: {prompt_file} not found")
        sys.exit(1)
    
    target_script = SCRIPT_DIR / sys.argv[3]
    if not target_script.exists():
        print(f"Error: {target_script} not found")
        sys.exit(1)
        
    # Any additional args after the script name
    extra_args = ' '.join(sys.argv[4:]) if len(sys.argv) > 4 else ''
    
    # Read prompt and pipe to target script
    cmd = f"cat {prompt_file} | python {target_script} {extra_args}"
    os.system(cmd)

def main():
    if len(sys.argv) < 2:
        print("Usage: python prompt.py [write|run] prompt.txt [target_script] [args...]")
        sys.exit(1)
        
    command = sys.argv[1]
    if command == "write":
        write_prompt()
    elif command == "run":
        run_prompt()
    else:
        print("Unknown command. Use 'write' or 'run'")
        sys.exit(1)

if __name__ == "__main__":
    main() 