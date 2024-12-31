# Coding Workflow Entry Point

FOLLOW THESE STEPS ONE BY ONE.

## backgroun info
- we are workng with the `src/` library in the existing codebase
- all new code should be added to the `src/` dir
- ai-scripts are in the `agent/ai-scripts.md` file and new ones should be added to the `agent/ai-scripts/` dir
- all new tests should be added to the `tests/` dir

1. Initialize workflow memory and save the file to `agent/workflows/coding/memory/{DATE}_{WORKFLOW_NAME}.json`
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
   - review `agent/ai-scripts.md` for availible tools
   - use all tools in combination as needed

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

**notes**
- you should try to complete the whole workflow in one go.
- reasons to stop include
  - you need an environment variable
  - you need approval to run a dangerous command specifies in `agent/instructions.md`
  - you have failed to debug an error for more than 2 tries, have consulted `agent/ai-scripts.md` and still cannot fix it.
  - you need documentation provided
  - you need clarification on the requirements
- every time you stop, after the user answers you resume and try to complete the whole workflow.
