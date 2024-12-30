from setuptools import setup, find_packages

setup(
    name="bens-ai-system",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "google-search-results",  # SERP API
        "aiohttp",               # Async HTTP
        "pytest",                # Testing
        "pytest-asyncio",        # Async testing
    ],
) 