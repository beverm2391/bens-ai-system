# Environment Setup

## Requirements
- Python 3.7+
- Required API keys (see below)
- Project dependencies installed

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -e .
```

## API Keys

The following API keys are required for different functionalities:

- `SERP_API_KEY`: Required for web searches (get from [SERP API](https://serpapi.com))
- `FIRECRAWL_API_KEY`: Required for web crawling (get from [Firecrawl](https://firecrawl.dev))
- `OPENAI_API_KEY`: Required for OpenAI integrations
- `ANTHROPIC_API_KEY`: Required for Anthropic/Claude integrations
- `O1_API_KEY`: Required for O1 consultation

Set these as environment variables:
```bash
export SERP_API_KEY="your_key"
export FIRECRAWL_API_KEY="your_key"
export OPENAI_API_KEY="your_key"
export ANTHROPIC_API_KEY="your_key"
export O1_API_KEY="your_key"
```

## Debug Level

Set debug level for verbose output:
```bash
export DEBUG_LEVEL=1  # 0=off, 1=on
```

## Testing

Run tests:
```bash
# Run all non-external tests
pytest

# Run external tests (requires API keys)
pytest --external
``` 