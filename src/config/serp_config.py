"""SERP API configuration."""

SERP_CONFIG = {
    # Search parameters
    "hl": "en",      # Language: English
    "gl": "us",      # Country: US
    "google_domain": "google.com",
    
    # Rate limiting
    "monthly_limit": 100,
    
    # Results formatting
    "safe": "active",  # Safe search
    "output": "json",  # Response format
} 