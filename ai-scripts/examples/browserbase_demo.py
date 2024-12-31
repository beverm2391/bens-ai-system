"""
Demo script showing Browserbase + Playwright automation capabilities.
This script will:
1. Navigate to a website
2. Take a screenshot
3. Extract some data
4. Show interaction capabilities
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from playwright.sync_api import Page, Playwright
    # These variables are provided by browserbase_run.py
    page: Page
    playwright: Playwright

# Navigate to website
print("Navigating to Hacker News...")
page.goto("https://news.ycombinator.com")
print(f"Page title: {page.title()}")

# Take screenshot
print("\nTaking screenshot...")
page.screenshot(path="hn_screenshot.png")
print("Screenshot saved as hn_screenshot.png")

# Extract data
print("\nExtracting top stories...")
stories = page.query_selector_all(".titleline a")
for story in stories[:5]:  # First 5 stories
    title = story.inner_text()
    print(f"- {title}")

# Demonstrate interaction
print("\nDemonstrating interaction...")
# Go directly to HN search
page.goto("https://hn.algolia.com")
print(f"Navigated to search page: {page.title()}")

search = page.locator("#searchbox")
search.click()
search.fill("python")
search.press("Enter")

# Wait for results
print("\nWaiting for search results...")
page.wait_for_selector(".Story")
results = page.query_selector_all(".Story")
print(f"Found {len(results)} search results for 'python'")

print("\nDemo completed! Check the session replay URL above to see the automation in action.") 