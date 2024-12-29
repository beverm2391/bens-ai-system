"""
This is a memory file for AI to reference during coding tasks.
It contains information about available tools, locations, and workflows.
This is not meant to be executed, it's for reference only.
"""

# Available Tools and Commands
TOOLS = {
    'testing': {
        'command': 'pytest',
        'notes': [
            'Run without -v flag by default',
            'Can run specific test files or entire suite',
            'Example: pytest path/to/test.py'
        ]
    },
    'file_operations': {
        'capabilities': [
            'Read files',
            'Write/edit files',
            'Create new files',
            'Delete files'
        ]
    },
    'terminal': {
        'capabilities': [
            'Run any shell command',
            'Background process support',
            'Command approval system'
        ]
    }
}

# Important Directories
DIRECTORIES = {
    'code': 'code/',
    'docs': {
        'root': 'docs/',
        'ai_modifications': 'docs/ai-modifications/',
        'workflow': 'docs/ai-modifications/coding-workflow.md'
    },
    'tests': 'tests/',
    'outputs': 'outputs/'
}

# Documentation Rules
DOC_RULES = {
    'docstrings': {
        'format': 'Google style',
        'required_sections': [
            'Args',
            'Returns',
            'Raises (if applicable)'
        ]
    },
    'comments': {
        'style': 'Inline for complex logic only',
        'format': 'Clear, concise, explain why not what'
    }
}

# Testing Guidelines
TEST_RULES = {
    'naming': 'test_*.py',
    'style': 'pytest',
    'coverage': {
        'required': True,
        'target': 'high coverage for critical paths'
    }
}

# Workflow Reference
WORKFLOW_PHASES = [
    'Planning',
    'Implementation',
    'Testing',
    'Documentation',
    'Review',
    'Commit'
]

# Remember:
# 1. Always start with minimal implementation
# 2. Write tests alongside code
# 3. Document as you go
# 4. Regular checkpoints with human
# 5. Clear error handling
# 6. Performance considerations when relevant 