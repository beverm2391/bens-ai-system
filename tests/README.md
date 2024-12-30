# Test Suite Documentation

## Structure
```
tests/
├── unit/           # Unit tests with mocked dependencies
├── integration/    # Integration tests that may use multiple components
└── README.md       # This file
```

## Test Categories
We use pytest markers to categorize tests:

- `@pytest.mark.unit`: Unit tests that mock all external dependencies
- `@pytest.mark.integration`: Tests that verify multiple components work together
- `@pytest.mark.external`: Tests that make real API calls (costs money/resources)

## Running Tests

### Safe Development (No API Calls)
```bash
# Run all tests except external
pytest -m "not external"

# Run only unit tests
pytest -m unit

# Run only integration tests (no external)
pytest -m "integration and not external"
```

### External API Tests
```bash
# Run external tests (will prompt for confirmation)
pytest -m external -s

# Run all tests (will prompt for external)
pytest -s
```

### Specific Test Files
```bash
# Run specific test file
pytest tests/unit/test_serp_client_unit.py -v
```

## External API Safety
- Tests marked with `@pytest.mark.external` will prompt for confirmation
- Prompts can be bypassed by explicitly using `-m external`
- External tests are skipped by default with `not external` marker
- Always use `-s` flag when running external tests to allow input

## Best Practices
1. Always mark tests appropriately:
   - Unit tests: `@pytest.mark.unit`
   - Integration tests: `@pytest.mark.integration`
   - External API calls: `@pytest.mark.external`

2. Keep external API calls minimal:
   - Use mocks for development
   - Only run external tests when needed
   - Group external tests to minimize API usage

3. Test file naming:
   - Unit tests: `test_*_unit.py`
   - Integration tests: `test_*_integration.py`

4. Documentation:
   - Clear test descriptions in docstrings
   - Explain what's being tested
   - Note any special requirements 