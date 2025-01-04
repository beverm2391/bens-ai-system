"""Demo script showing SERP API integration with Firecrawl."""

import asyncio
import logging
from dotenv import load_dotenv
from src.clients.serp_client import SerpClient
from src.clients.firecrawl_client import FirecrawlClient, FirecrawlError
from src.clients.anthropic_client import AnthropicClient
from src.clients.openai_client import OpenAIClient
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class URLSchema(BaseModel):
    url: str = Field(description="The URL of the most relevant result")

async def demo_search_and_crawl():
    """Demonstrate searching with SERP API and crawling results with Firecrawl."""
    
    # Initialize clients
    serp_client = SerpClient()
    
    try:
        # Example: Search for a specific topic
        logger.info("Searching for 'Claude documentation'...")
        search_results = await serp_client.search("Claude documentation", num_results=3)
        
        logger.info(f"Found {len(search_results)} results")
        logger.info(f"Monthly SERP API usage: {serp_client._monthly_searches}/{serp_client._monthly_limit}")

        # pick the most relevant result asking claude
        prompt = f"return the url and only the url of the most relevant result with no other text"
        client = OpenAIClient()
        response = await client.extract(prompt, URLSchema)
        url = response.get("url")
        if not url:
            logger.error("No URL found in response")
            return
        
        logger.info(f"Most relevant result: {url}")

        # crawl the url
        firecrawl_client = FirecrawlClient()
        job_id = await firecrawl_client.crawl_url(url)
        logger.info(f"Crawl job started with ID: {job_id}")
        
        # Process each result with Firecrawl
        async with FirecrawlClient() as firecrawl_client:
            for i, result in enumerate(search_results, 1):
                logger.info(f"\nProcessing result {i}:")
                logger.info(f"Title: {result['title']}")
                logger.info(f"URL: {result['link']}")
                logger.info(f"Snippet: {result['snippet']}")
                
                # Scrape the page content
                try:
                    content = await firecrawl_client.scrape_url(result['link'])
                    if content and 'markdown' in content:
                        preview = content['markdown'][:200] + "..." if len(content['markdown']) > 200 else content['markdown']
                        logger.info(f"Successfully scraped {len(content['markdown'])} characters")
                        logger.info("Content preview:")
                        logger.info(preview)
                    else:
                        logger.warning(f"No markdown content in response: {content}")
                except FirecrawlError as e:
                    logger.error(f"Failed to scrape {result['link']}: {str(e)}")
                    continue
                except Exception as e:
                    logger.error(f"Unexpected error scraping {result['link']}: {str(e)}")
                    continue
                
                logger.info("-" * 80)
            
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(demo_search_and_crawl()) 