"""
Main entry point for agent system
"""
import sys
from agent.core import Agent

def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python main.py <prompt>")
        sys.exit(1)

    prompt = " ".join(sys.argv[1:])
    agent = Agent()
    response = agent.process_command(prompt)
    print(response)

if __name__ == "__main__":
    main() 