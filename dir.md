# Directory Structure

```
.
├── .cursorrules
├── README.md
├── ai-scripts
│   ├── README.md
│   ├── exa_search.py
│   ├── firecrawl_search.py
│   ├── notify.py
│   ├── o1_consult.py
│   ├── serp_search.py
│   └── update_dir.py
├── bens_ai_system.egg-info
│   ├── PKG-INFO
│   ├── SOURCES.txt
│   ├── dependency_links.txt
│   ├── requires.txt
│   └── top_level.txt
├── conftest.py
├── demos
│   └── serp_firecrawl_demo.py
├── dir.md
├── docs
│   ├── agents
│   ├── ai-system
│   │   ├── diagrams
│   │   │   ├── anthropic-patterns.md
│   │   │   ├── combined-system.md
│   │   │   └── top-down-overview.md
│   │   └── vision.md
│   ├── ben-only
│   │   ├── command-execution.md
│   │   ├── mission.md
│   │   └── rules-for-reflection.md
│   ├── external
│   │   └── building-effective-agents.md
│   ├── memory.md
│   ├── product
│   │   ├── anthropic
│   │   │   ├── architecture.md
│   │   │   └── mvp.md
│   │   ├── codebase.md
│   │   ├── conventions.md
│   │   ├── firecrawl
│   │   │   └── README.md
│   │   └── openai
│   │   │   └── README.md
│   ├── setup.md
│   ├── technical
│   │   └── conventions.md
│   └── workflows
│   │   └── coding
│   │   │   ├── entry-point.md
│   │   │   ├── memory
│   │   │   │   ├── 20231229_claude_integration.json
│   │   │   │   ├── 20231229_openai.json
│   │   │   │   └── 20231229_openai_reasoning.json
│   │   │   └── workflow.md
├── examples
│   ├── demo_anthropic_client.py
│   ├── demo_openai_client.py
│   ├── demo_reasoning_client.py
│   └── exa_search_demo.py
├── outputs
├── pytest.ini
├── scripts
│   └── render_diagrams.py
├── setup.py
├── src
│   ├── __init__.py
│   ├── agent
│   │   ├── __init__.py
│   │   └── core.py
│   ├── clients
│   │   ├── __init__.py
│   │   ├── anthropic_client.py
│   │   ├── exa_client.py
│   │   ├── firecrawl_client.py
│   │   ├── notification_client.py
│   │   ├── openai_client.py
│   │   ├── reasoning_client.py
│   │   └── serp_client.py
│   ├── config
│   │   └── serp_config.py
│   ├── main.py
│   └── tests
│   │   ├── integration
│   │   └── unit
├── tests
│   ├── README.md
│   ├── integration
│   │   ├── test_anthropic_client.py
│   │   ├── test_exa_client_integration.py
│   │   ├── test_firecrawl_client.py
│   │   ├── test_firecrawl_integration.py
│   │   ├── test_openai_client.py
│   │   ├── test_reasoning_client.py
│   │   ├── test_serp_client.py
│   │   └── test_serp_client_integration.py
│   └── unit
│   │   ├── test_anthropic_client.py
│   │   ├── test_exa_client.py
│   │   ├── test_firecrawl_client.py
│   │   └── test_serp_client_unit.py
├── todo.md
```