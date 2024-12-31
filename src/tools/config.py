#!/usr/bin/env python3
"""
AI script for using multiple tools with Claude.
"""
# Tool definitions
NOTIFICATION_SCHEMA = {
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

SEARCH_SCHEMA = {
    "type": "object",
    "properties": {
        "query": {
            "type": "string",
            "description": "The search query"
        },
        "num_results": {
            "type": "integer",
            "description": "Number of results to return",
            "default": 10
        },
        "include_domains": {
            "type": "string",
            "description": "Comma-separated list of domains to include",
            "default": ""
        },
        "exclude_domains": {
            "type": "string",
            "description": "Comma-separated list of domains to exclude",
            "default": ""
        }
    },
    "required": ["query"]
}

SCRAPE_SCHEMA = {
    "type": "object",
    "properties": {
        "url": {
            "type": "string",
            "description": "The URL to scrape"
        }
    },
    "required": ["url"]
}