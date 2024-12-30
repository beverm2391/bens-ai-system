# AI Scripts

Helper scripts for AI operations.

## Scripts

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
Consult O1 for critical thinking and analysis.

```bash
# Get O1's analysis
./o1_consult.py "What are the implications of [design choice]?"
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