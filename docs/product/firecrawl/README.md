# Firecrawl Integration

Async client for interacting with Firecrawl API to scrape and crawl websites for LLM-ready markdown content.

## Setup

1. Get a Firecrawl API key from https://firecrawl.dev
2. Set environment variable:
```bash
export FIRECRAWL_API_KEY="your_api_key"
```

## Usage

```python
from src.clients.firecrawl_client import FirecrawlClient

# Initialize client
client = FirecrawlClient()

# Scrape single URL
content = await client.scrape_url("https://example.com")

# Start crawl job
job_id = await client.crawl_url("https://example.com")

# Check crawl status
status = await client.get_crawl_status(job_id)
```

## API Methods

- `scrape_url(url: str)`: Scrape single URL to markdown
- `crawl_url(url: str)`: Start crawl job and return job ID
- `get_crawl_status(job_id: str)`: Get status of crawl job 