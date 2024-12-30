# Directory Structure

```
.
├── ai-scripts/                # AI helper scripts
│   ├── README.md             # Scripts documentation
│   ├── o1_consult.py         # O1 consultation tool
│   └── update_dir.py         # Directory structure updater
├── docs/                     # Documentation
│   ├── memory.md            # AI system memory
│   ├── ben-only/            # Private documentation
│   └── product/             # Product documentation
│       ├── anthropic/       # Anthropic implementation
│       └── openai/          # OpenAI implementation
├── examples/                 # Example usage
│   ├── demo_anthropic.py
│   ├── demo_openai.py
│   └── demo_reasoning.py
├── src/                     # Source code
│   ├── clients/            # API clients
│   │   ├── anthropic_client.py
│   │   ├── openai_client.py
│   │   └── reasoning_client.py
│   ├── utils/             # Utilities
│   └── config/            # Configuration
├── tests/                  # Test suite
│   ├── integration/       # Integration tests
│   └── unit/             # Unit tests
├── requirements.txt       # Python dependencies
└── dir.md                # This file
