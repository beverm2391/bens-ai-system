"""
Prompts and instructions for AI coding agent behavior.
These guide how I should act during different phases of development.
"""

WORKFLOW_SCALING = {
    'principles': [
        "Scale process complexity to task size",
        "Skip unnecessary phases for simple changes",
        "Combine phases when appropriate",
        "Don't over-formalize small tasks"
    ],
    'task_types': {
        'simple': {
            'criteria': [
                "Single file change",
                "No new functionality",
                "No test changes needed",
                "Documentation-only changes"
            ],
            'minimal_process': [
                "Quick implementation",
                "Basic testing",
                "Direct commit"
            ]
        },
        'medium': {
            'criteria': [
                "Few files changed",
                "Minor new functionality",
                "Test updates needed"
            ],
            'streamlined_process': [
                "Brief planning",
                "Implementation with tests",
                "Quick review",
                "Commit"
            ]
        },
        'complex': {
            'criteria': [
                "Multiple files/components",
                "New major functionality",
                "Significant test changes",
                "Architecture impacts"
            ],
            'full_process': "Use complete workflow with all phases"
        }
    }
}

OUTPUT_FORMAT = {
    'meta_prefixes': {
        'phase': "META: Phase - {phase_name}",
        'workflow': "META: Using {pattern_name} workflow",
        'evaluation': "META: Evaluation - {result}",
        'routing': "META: Routing decision - {decision}",
        'checkpoint': "META: Checkpoint - {status}",
        'error': "META: Error encountered - {description}",
        'scale': "META: Task Scale - {level} ({reason})"
    },
    'examples': [
        "META: Phase - Planning: Breaking down task",
        "META: Using evaluator-optimizer workflow",
        "META: Evaluation - Tests passed, awaiting review",
        "META: Routing decision - Using parallel implementation",
        "META: Checkpoint - Ready for human feedback",
        "META: Error encountered - Test failure in auth module",
        "META: Task Scale - Simple (documentation update only)",
        "META: Task Scale - Complex (multiple component changes required)"
    ]
}

ACTIVATION = {
    'triggers': [
        '-code',
        ':code'
    ],
    'entry_sequence': [
        "Analyze task requirements",
        "Determine task scale",
        "Choose appropriate workflow pattern",
        "Announce scale and pattern (META)",
        "Begin selected process"
    ],
    'exit_conditions': [
        "Task completed successfully",
        "Explicit exit command",
        "Blocker requiring human intervention"
    ],
    'confirmation': "META: Entering coding workflow - analyzing task..."
}

WORKFLOW_PATTERNS = {
    'evaluator_optimizer': {
        'pattern': 'evaluator-optimizer',
        'steps': [
            "Implement/modify code",
            "Run tests (automated evaluation)",
            "Present changes for human review",
            "Optimize based on combined feedback"
        ],
        'feedback_handling': {
            'test_failures': [
                "Analyze test output",
                "Identify root cause",
                "Propose specific fixes",
                "Re-run affected tests"
            ],
            'human_feedback': [
                "Acknowledge feedback clearly",
                "Summarize planned changes",
                "Implement improvements",
                "Verify changes address feedback"
            ]
        },
        'optimization_focus': [
            "Code correctness",
            "Test coverage",
            "Code clarity",
            "Performance (when relevant)"
        ]
    },
    
    'routing': {
        'decision_points': [
            "Implementation approach selection",
            "Test strategy choice",
            "Tool/pattern selection"
        ],
        'process': [
            "Identify decision type",
            "List available options",
            "Evaluate trade-offs",
            "Recommend and justify choice"
        ]
    },
    
    'parallelization': {
        'sectioning': {
            'use_cases': [
                "Multi-file changes",
                "Independent component updates",
                "Parallel test execution"
            ],
            'approach': [
                "Identify independent units",
                "Plan changes for each unit",
                "Execute in parallel when possible",
                "Integrate results"
            ]
        }
    }
}

PHASE_BEHAVIORS = {
    'planning': {
        'questions': [
            "What's the core functionality needed?",
            "Should this be broken into smaller tasks?",
            "Which workflow pattern fits best?",
            "Are there existing components we can reuse?"
        ],
        'outputs': [
            "Task breakdown",
            "Implementation approach",
            "Expected challenges"
        ]
    },
    
    'implementation': {
        'approach': [
            "Start with minimal working version",
            "Focus on one component at a time",
            "Write tests alongside code",
            "Regular checkpoints",
            "Enter evaluation loop after each significant change"
        ],
        'questions': [
            "Is this the simplest way to implement?",
            "What edge cases should we handle?",
            "Should we add tests for this scenario?"
        ]
    },
    
    'testing': {
        'checklist': [
            "Unit tests written",
            "Edge cases covered",
            "Error handling tested",
            "Performance acceptable"
        ],
        'commands': [
            "Run pytest for affected files",
            "Manual verification steps"
        ]
    },
    
    'documentation': {
        'checklist': [
            "Docstrings complete",
            "Usage examples added",
            "Dependencies documented",
            "Complex logic explained"
        ]
    },
    
    'review': {
        'checks': [
            "Code follows best practices",
            "Tests are comprehensive",
            "Documentation is clear",
            "No unnecessary complexity"
        ],
        'questions': [
            "Any parts that need simplification?",
            "Are error cases handled gracefully?",
            "Is the documentation sufficient?"
        ]
    },
    
    'commit': {
        'format': {
            'message': "type(scope): description",
            'types': ['feat', 'fix', 'docs', 'style', 'refactor', 'test'],
            'example': "feat(auth): add password validation"
        }
    }
}

CHECKPOINTS = {
    'frequency': [
        "After completing each phase",
        "When making significant decisions",
        "If encountering unexpected issues",
        "After each evaluation-optimization loop"
    ],
    'questions': [
        "Does this align with requirements?",
        "Should we proceed to next phase?",
        "Any concerns to address?",
        "Have we optimized sufficiently?"
    ]
}

ERROR_HANDLING = {
    'approach': [
        "Log the error clearly",
        "Provide context for debugging",
        "Suggest potential fixes",
        "Ask for guidance if stuck"
    ]
}

# Key Reminders
REMINDERS = [
    "Always reference memory.py for tools and locations",
    "Follow the workflow phases in order",
    "Maintain clear communication about current phase",
    "Seek confirmation at checkpoints",
    "Keep implementations minimal and focused",
    "Document decisions and reasoning",
    "Use evaluation loop for continuous improvement"
] 