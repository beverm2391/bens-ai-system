# AI Scripts

Helper scripts for AI operations.

## Scripts

### prompt.py
Write and run prompts with any script. Prompts are stored in `ai-scripts/prompts/` for reuse.

```bash
# Write a prompt to file
./prompt.py write my_prompt.txt
# Then enter/paste your prompt and press Ctrl-D (Unix) or Ctrl-Z (Windows)

# Run a prompt with any script
./prompt.py run my_prompt.txt target_script.py [args...]

# Example with o1_consult.py
./prompt.py run analysis.txt o1_consult.py
```

### serp_search.py
Search the web using SERP API with optional content crawling.

```bash
# Basic search
./serp_search.py "your search query"

# Search with more results
./serp_search.py -n 10 "your search query"

# Search and crawl content
./serp_search.py -c "your search query"

# Save results to file
./serp_search.py -o results.json "your search query"

# Verbose output
./serp_search.py -v "your search query"
```

### firecrawl_search.py
Crawl and scrape websites using Firecrawl API.

```bash
# Scrape a single URL
./firecrawl_search.py scrape https://example.com

# Crawl a website
./firecrawl_search.py crawl https://example.com
```

### o1_consult.py
Consult O1 for critical thinking and analysis. Can read from stdin or command line. O1 can handle large contexts (up to 150k tokens) - always provide complete relevant information for best results.

```bash
# Direct query
./o1_consult.py "What are the implications of [design choice]?"

# Read from stdin (preferred for large contexts)
echo "Your prompt" | ./o1_consult.py

# Use with prompt.py for longer prompts (best practice)
./prompt.py run analysis.txt o1_consult.py
```

### update_dir.py
Update directory structure documentation.

```bash
# Update dir.md
./update_dir.py
```

### notify.py
Send macOS notifications from scripts or command line.

```bash
# Basic banner notification
./notify.py "Your message"

# Custom title and subtitle
./notify.py "Your message" "Custom Title" "Optional Subtitle"

# Modal alert dialog
./notify.py "Your message" "Alert Title" "Alert Subtitle" --alert
```

### exa_search.py
Perform semantic web searches using the Exa API.

Usage:
```bash
python exa_search.py <query> [num_results] [include_domains] [exclude_domains]
```

Arguments:
- query: Search query string
- num_results: (optional) Number of results to return (default: 10)
- include_domains: (optional) Comma-separated list of domains to include
- exclude_domains: (optional) Comma-separated list of domains to exclude

Example:
```bash
python exa_search.py "latest AI developments" 5 "techcrunch.com,wired.com"
```

Returns JSON with search results including content and highlights.

## Environment Setup

All scripts require:
1. Python 3.7+
2. Required API keys in environment
3. Project dependencies installed

## API Keys

Required environment variables:
- `SERP_API_KEY`: For web searches
- `FIRECRAWL_API_KEY`: For web crawling
- `O1_API_KEY`: For O1 consultation

## Best Practices

1. Use scripts for automation and consistency
2. Check rate limits and costs
3. Handle errors gracefully
4. Save outputs when needed 