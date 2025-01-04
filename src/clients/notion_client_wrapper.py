# This cannot be named `notion_client.py` because it will conflict with the `notion_client` package

import os
from typing import Dict, Any, Optional, List, Literal, Union
from notion_client import AsyncClient
from dotenv import load_dotenv

load_dotenv()

NOTION_INTEGRATION_SECRET = os.getenv("NOTION_INTEGRATION_SECRET")
NOTION_ROOT_PAGE_ID = os.getenv("NOTION_ROOT_PAGE_ID")

if not NOTION_INTEGRATION_SECRET:
    raise ValueError("NOTION_INTEGRATION_SECRET is not set")
if not NOTION_ROOT_PAGE_ID:
    raise ValueError("NOTION_ROOT_PAGE_ID is not set")

class NotionClient:
    def __init__(self):
        self.client = AsyncClient(auth=NOTION_INTEGRATION_SECRET)
        self.root_page_id = NOTION_ROOT_PAGE_ID

    async def list_users(self):
        return await self.client.users.list()

    async def search_pages(self, query: str = "", filter: Dict = None) -> List[Dict]:
        """Search for pages in Notion workspace."""
        return await self.client.search(query=query, filter=filter).get("results", [])

    async def get_page(self, page_id: str) -> Dict:
        """Get a page by its ID."""
        return await self.client.pages.retrieve(page_id=page_id)

    async def create_page(
        self,
        title: str,
        parent_id: Optional[str] = None,
        parent_type: Literal["page", "database"] = "page",
        properties: Optional[Dict] = None,
        children: Optional[List] = None,
    ) -> Dict:
        """Create a new page under specified parent or root page.
        
        Args:
            title: Page title
            parent_id: ID of parent page/database. Defaults to root page if None
            parent_type: Type of parent ('page' or 'database')
            properties: Additional page properties
            children: Page content blocks
        """
        # Use root page as default parent if none specified
        if not parent_id:
            parent_id = self.root_page_id
            parent_type = "page"

        # Set up parent reference
        if parent_type == "database":
            parent = {"database_id": parent_id}
        else:
            parent = {"page_id": parent_id}

        page_data = {
            "parent": parent,
            "properties": {
                "title": {"title": [{"text": {"content": title}}]}
            }
        }

        if properties:
            page_data["properties"].update(properties)
        if children:
            page_data["children"] = children

        return await self.client.pages.create(**page_data)

    async def update_page(self, page_id: str, properties: Dict[str, Any]) -> Dict:
        """Update an existing page's properties."""
        return await self.client.pages.update(page_id=page_id, properties=properties)

    async def append_blocks(self, page_id: str, children: List[Dict]) -> Dict:
        """Append blocks to an existing page."""
        return await self.client.blocks.children.append(
            block_id=page_id, children=children
        )
