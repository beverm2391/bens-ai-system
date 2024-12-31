#!/usr/bin/env python3
"""
AI script for using multiple tools with Claude.
"""
# Tool definitions
"""
Tool schemas for Claude tools
"""

# Schema for E2B code execution
E2B_SCHEMA = {
    "description": """
    Executes code in a secure sandbox environment using E2B.
    This tool should be used when you need to run code snippets safely.
    The code runs in an isolated environment with proper error handling.
    Supports Python 3 runtime by default.
    Returns both stdout and stderr from the execution, along with a success flag.
    Use this for testing code, performing calculations, or running experiments.
    Note: The tool will return empty strings for stdout/stderr if there is no output.
    """,
    "type": "object",
    "properties": {
        "code": {
            "type": "string",
            "description": "Python code to execute"
        },
        "timeout": {
            "type": "integer",
            "description": "Timeout in seconds",
            "default": 30
        }
    },
    "required": ["code"]
}

# Schema for notifications
NOTIFICATION_SCHEMA = {
    "description": """
    Sends system notifications to the user.
    This tool should be used to notify the user about important events or updates.
    Supports both banner notifications (non-blocking) and alert dialogs (blocking).
    Use banner style for regular updates and alert style for critical information.
    """,
    "type": "object", 
    "properties": {
        "message": {
            "type": "string",
            "description": "The notification message to display to the user"
        },
        "title": {
            "type": "string", 
            "description": "The notification title",
            "default": "AI System"
        },
        "subtitle": {
            "type": "string",
            "description": "Optional subtitle text",
            "default": ""
        },
        "style": {
            "type": "string",
            "enum": ["alert", "banner"],
            "description": "Notification style - alert for modal dialog, banner for notification center",
            "default": "banner"
        }
    },
    "required": ["message"]
}

# Schema for SERP web search
SEARCH_SCHEMA = {
    "description": """
    Performs a web search using SERP API to find relevant web pages and information.
    This tool should be used when you need to search the internet for current information.
    Results include titles, snippets, and URLs of relevant web pages.
    Note that this makes a real API call and consumes credits, so use judiciously.
    """,
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "The search query string"
        },
        "num_results": {
            "type": "integer",
            "description": "Number of results to return",
            "default": 5
        }
    },
    "required": ["query"]
}

# Schema for web scraping
SCRAPE_SCHEMA = {
    "description": """
    Scrapes content from a single webpage using Firecrawl API.
    This tool should be used to extract content from a specific documentation page.
    Returns structured content including:
    - Page title and metadata
    - Main content sections
    - Code examples
    - Links
    Note: For crawling multiple pages, use the crawl_site tool instead.
    """,
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "description": "URL of the page to scrape"
        }
    },
    "required": ["url"]
}

# Schema for web crawling
CRAWL_SCHEMA = {
    "description": """
    Crawls an entire website starting from a URL using Firecrawl API.
    This tool should be used to extract documentation across multiple connected pages.
    Features:
    - Follows links to build content graph
    - Maintains site structure
    - Extracts content from all pages
    - Handles pagination and navigation
    Note: For single pages, use the scrape_page tool instead.
    """,
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "description": "Starting URL to crawl"
        },
        "timeout": {
            "type": "integer",
            "description": "Maximum time to wait for crawl completion in seconds",
            "default": 300
        }
    },
    "required": ["url"]
}

# Schema for O1 reasoning
O1_SCHEMA = {
    "description": """
    Uses O1 reasoning system to analyze problems and plan implementations.
    This tool provides structured, step-by-step reasoning about:
    - Algorithms and data structures
    - API design and interfaces
    - Error handling and edge cases
    - Performance considerations
    - Testing strategies
    
    Returns JSON-structured reasoning steps and conclusions.
    Use this tool when you need to plan a complex implementation.
    """,
    "type": "object",
    "properties": {
        "prompt": {
            "type": "string",
            "description": "The problem or implementation to reason about"
        },
        "steps": {
            "type": "integer",
            "description": "Number of reasoning steps",
            "default": 5,
            "minimum": 3,
            "maximum": 10
        }
    },
    "required": ["prompt"]
}