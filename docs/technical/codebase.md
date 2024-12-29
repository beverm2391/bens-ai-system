# Codebase Structure

```
.
├── docs/
│   ├── technical/           # Technical documentation
│   │   ├── codebase.md     # Codebase structure
│   │   └── conventions.md   # Code conventions
│   │
│   ├── product/            # Product documentation
│   │   └── version-0/      # Current version docs
│   │       ├── architecture.md
│   │       └── mvp.md
│   │
│   ├── ai-system/          # AI architecture (abstract)
│   └── ben-only/           # Private planning docs
│
├── src/                    # Source code
│   ├── core/              
│   │   ├── memory.py      
│   │   └── agent.py       
│   ├── tools/             
│   │   ├── files.py       
│   │   └── code_exec.py   
│   └── interface/         
│       └── chat.py        
│
├── tests/                  
└── scripts/                
```

Key principles:
- Flat where possible
- Clear separation of concerns
- Tests mirror source
- Documentation close to code 