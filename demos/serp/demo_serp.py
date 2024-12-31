import os
import json
from src.tools.serp_tool import search, SERP_SCHEMA

def main():
    # Print the tool schema
    print("\nTool Schema:")
    print(json.dumps(SERP_SCHEMA, indent=2))
    
    # Example 1: Basic search
    print("\nExample 1: Basic search")
    try:
        results = search("latest AI developments")
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error: {e}")
        
    # Example 2: Search with domain filters
    print("\nExample 2: Search with domain filters")
    try:
        results = search(
            "AI news",
            num_results=5,
            include_domains="techcrunch.com,wired.com"
        )
        print(json.dumps(results, indent=2))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 