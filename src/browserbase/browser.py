"""
Browserbase client implementation for browser automation.
"""

import os
import logging
from typing import Optional
from playwright.sync_api import Playwright, sync_playwright
from browserbase import Browserbase

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BrowserbaseClient:
    def __init__(self, api_key: Optional[str] = None, project_id: Optional[str] = None):
        """Initialize Browserbase client.
        
        Args:
            api_key: Browserbase API key. If not provided, reads from BROWSERBASE_API_KEY env var
            project_id: Browserbase project ID. If not provided, reads from BROWSERBASE_PROJECT_ID env var
        """
        self.api_key = api_key or os.environ.get("BROWSERBASE_API_KEY")
        if not self.api_key:
            raise ValueError("Browserbase API key not provided and BROWSERBASE_API_KEY not set")
            
        self.project_id = project_id or os.environ.get("BROWSERBASE_PROJECT_ID")
        if not self.project_id:
            raise ValueError("Project ID not provided and BROWSERBASE_PROJECT_ID not set")
            
        logger.info("Initializing Browserbase client with project ID: %s", self.project_id)
        self.bb = Browserbase(api_key=self.api_key)
        
    def create_session(self) -> tuple[str, str]:
        """Create a new Browserbase session.
        
        Returns:
            Tuple of (session_id, replay_url)
        """
        logger.info("Creating new Browserbase session...")
        session = self.bb.sessions.create(project_id=self.project_id)
        logger.info("Session created with ID: %s", session.id)
        return session.id, f"https://browserbase.com/sessions/{session.id}"
        
    def run_playwright(self, callback) -> None:
        """Run Playwright automation in Browserbase session.
        
        Args:
            callback: Function that takes (playwright, page) arguments and performs automation
        """
        with sync_playwright() as playwright:
            # Create session
            logger.info("Creating Browserbase session...")
            session = self.bb.sessions.create(project_id=self.project_id)
            logger.info("Session created. Replay URL: https://browserbase.com/sessions/%s", session.id)
            
            # Connect to remote browser
            logger.info("Connecting to remote browser...")
            browser = playwright.chromium.connect_over_cdp(session.connect_url)
            context = browser.contexts[0]
            page = context.pages[0]
            logger.info("Connected to remote browser")
            
            try:
                # Run the callback with playwright and page
                logger.info("Running automation callback...")
                callback(playwright, page)
                logger.info("Automation completed successfully")
            except Exception as e:
                logger.error("Error during automation: %s", str(e))
                raise
            finally:
                # Cleanup
                logger.info("Cleaning up browser session...")
                page.close()
                browser.close()
                logger.info("Cleanup completed") 