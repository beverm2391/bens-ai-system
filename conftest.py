"""Pytest configuration and shared fixtures."""

import pytest
import sys

def pytest_runtest_setup(item):
    """Called before each test is run."""
    # Check if test is marked as external
    if any(mark.name == 'external' for mark in item.iter_markers()):
        # Only prompt if not explicitly running external tests
        if '-m' not in sys.argv or 'external' not in sys.argv:
            print(f"\nWarning: Test '{item.name}' will make external API calls that may incur costs.")
            response = input("Do you want to continue? [y/N] ")
            if response.lower() != 'y':
                pytest.skip("Test skipped to avoid external API calls") 