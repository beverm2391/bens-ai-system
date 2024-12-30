# Coding Workflow

## Entry Point
1. Review requirements and constraints
2. For complex decisions or architecture, consult O1:
   ```bash
   ./ai-scripts/o1_consult.py "What are the implications of [design choice]?"
   ```
3. Challenge unnecessary complexity
4. Create/update memory file for task
5. Follow test-driven development
6. Run tests and verify passing
7. Update directory structure:
   ```bash
   ./ai-scripts/update_dir.py
   ```
8. Get human review before committing

## Key Principles
- Use O1 consultation for:
  - Architecture decisions
  - Security implications
  - Performance considerations
  - Edge case analysis
  - Risk assessment
- Keep solutions simple
- Document decisions in memory
- Test thoroughly before review
- Keep directory structure current

## Process Scale
- Small changes: Direct implementation
- Medium changes: Basic testing + review
- Large changes: Full TDD + O1 consultation + thorough review