import asyncio
from dotenv import load_dotenv
from src.clients.notion_client_wrapper import NotionClient

# Load environment variables
load_dotenv()

async def create_test_page():
    client = NotionClient()
    
    # Create a blank page under root page
    page = await client.create_page(
        title="Test Page"  # Will default to root page as parent
    )
    
    print(f"Created page with ID: {page['id']}")
    return page

if __name__ == "__main__":
    asyncio.run(create_test_page()) 