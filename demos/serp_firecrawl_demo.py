"""Demo script showing SERP API integration with Firecrawl."""

import asyncio
import logging
from src.clients.serp_client import SerpClient
from src.clients.firecrawl_client import FirecrawlClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def demo_search_and_crawl():
    """Demonstrate searching with SERP API and crawling results with Firecrawl."""
    
    # Initialize clients
    serp_client = SerpClient()
    firecrawl_client = FirecrawlClient()
    
    try:
        # Example: Search for a specific topic
        logger.info("Searching for 'OpenAI GPT-4 documentation'...")
        search_results = await serp_client.search("OpenAI GPT-4 documentation", num_results=3)
        
        logger.info(f"Found {len(search_results)} results")
        logger.info(f"Monthly SERP API usage: {serp_client._monthly_searches}/{serp_client._monthly_limit}")
        
        # Process each result with Firecrawl
        for i, result in enumerate(search_results, 1):
            logger.info(f"\nProcessing result {i}:")
            logger.info(f"Title: {result['title']}")
            logger.info(f"URL: {result['link']}")
            logger.info(f"Snippet: {result['snippet']}")
            
            # Scrape the page content
            try:
                content = await firecrawl_client.scrape_url(result['link'])
                if content:
                    preview = content[:200] + "..." if len(content) > 200 else content
                    logger.info(f"Successfully scraped {len(content)} characters")
                    logger.info("Content preview:")
                    logger.info(preview)
                else:
                    logger.warning("No content returned from scraper")
            except Exception as e:
                logger.error(f"Failed to scrape {result['link']}: {str(e)}")
                continue
            
            logger.info("-" * 80)
            
    except Exception as e:
        logger.error(f"Demo failed: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(demo_search_and_crawl()) 