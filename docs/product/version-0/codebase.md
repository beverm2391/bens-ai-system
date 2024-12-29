# Codebase Structure

```
.
├── docs/
│   ├── product/              # Product documentation
│   │   └── version-0/        # Current version docs
│   ├── ai-system/            # AI architecture (abstract)
│   └── ben-only/            # Private planning docs
│
├── src/                      # Source code
│   ├── core/                # Core agent functionality
│   │   ├── memory.py        # Memory/context management
│   │   └── agent.py         # Main agent logic
│   │
│   ├── tools/               # Tool implementations
│   │   ├── files.py         # File operations
│   │   └── code_exec.py     # Code execution
│   │
│   └── interface/           # Interface layer
│       └── chat.py          # Text chat implementation
│
├── tests/                    # Tests mirror src structure
│   ├── core/
│   ├── tools/
│   └── interface/
│
└── scripts/                  # Utility scripts
    └── render_diagrams.py    # Mermaid renderer
```

Key principles:
- Flat where possible
- Clear separation of concerns
- Tests mirror source
- Documentation close to code 