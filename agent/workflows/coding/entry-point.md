# Coding Workflow Entry Point

1. Initialize workflow memory
   ```python
   workflow_memory = {
       "phase": "requirements",
       "decisions": [],
       "changes": []
   }
   ```

2. Review requirements and constraints
   - Challenge complexity
   - Question assumptions
   - Use O1 for complex decisions:
     ```bash
     ./ai-scripts/o1_consult.py (custom prompt asking what you need)
     ```

3. Follow test-driven development
   - Write tests first
   - Implement code
   - Run all tests

4. Demo and review
   - Create demo script
   - Run demo
   - Get human review

5. Pre-commit
   - Update directory structure:
     ```bash
     ./ai-scripts/update_dir.py
     ```
   - Update memory file
   - Get final approval

## Scale Process
- Small changes: Direct implementation
- Medium changes: Basic testing + review
- Large changes: Full TDD + O1 consultation