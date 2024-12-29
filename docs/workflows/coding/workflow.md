# Development Workflow

## Core Principles
- Challenge and minimize requirements aggressively
- Once requirements are finalized, implementation must be as robust as possible
- No half-measures in code quality after requirements are locked
- Better to do fewer things extremely well than many things poorly
- Test everything that can be tested automatically
- Only require human testing for what can't be automated

## Commands
- `-m` / `-mem`: Record message in memory and update relevant files
  - Updates memory.json for current workflow
  - Updates any relevant documentation
  - Preserves context between interactions

## Technical Standards
- Debug levels controlled by env var DEBUG_LEVEL (0=off, 1=on)
- Consistent debug output across codebase
- Tests organized in root /tests directory:
  - /tests/unit for unit tests
  - /tests/integration for integration tests
- Automated testing before human review
- Human review only after tests pass or for untestable features

## Testing Process
1. Implement automated tests where possible
2. Run tests and verify results
3. Request human review only when:
   - Tests are passing and need final verification
   - Feature cannot be automatically tested
   - Uncertain about test results
4. No commits until tests pass and necessary human review complete

## Overview
This workflow guides AI agents through development phases while maintaining state and consistency.

## Memory Structure
```json
{
  "current_phase": "requirements",
  "phase_data": {
    "requirements_met": [],
    "challenges_raised": [],
    "decisions_made": []
  },
  "context": {
    "last_action": "",
    "next_action": "",
    "commits": []
  }
}
```

## Version Control
- Commit before starting any workflow
- Commit before potentially breaking changes
- Track commits in memory file
- Use clear, descriptive commit messages
- Prefix commits with phase: `[PHASE] message`

## Phases

### 1. Requirements
**Entry Point:**
- New feature/change requested
- Memory loaded and reviewed

**Actions:**
- Challenge complexity and necessity
- Question assumptions
- Propose simpler alternatives
- Update documentation if requirements change

**Exit Criteria:**
- Requirements clearly defined
- Complexity challenges addressed
- Documentation updated
- Move to Design phase

### 2. Design
**Entry Point:**
- Requirements validated
- Memory updated with decisions

**Actions:**
- Propose minimal solution
- Review existing code/patterns
- Challenge design complexity
- Update technical docs if needed

**Exit Criteria:**
- Design approved
- Documentation updated
- Move to Implementation phase

### 3. Implementation
**Entry Point:**
- Design approved
- Memory updated with approach

**Actions:**
- Write minimal code
- Install dependencies if needed
- Update relevant docs
- Maintain memory state

**Exit Criteria:**
- Code implemented
- Tests passing
- Docs updated
- Move to Review phase

### 4. Review
**Entry Point:**
- Implementation complete
- Memory updated with changes

**Actions:**
- Self-review changes
- Verify documentation
- Check test coverage
- Challenge any complexity

**Exit Criteria:**
- Changes verified
- Documentation complete
- Return to appropriate phase or end

## Phase Transitions
- Each phase must meet ALL exit criteria
- Memory must be updated before transition
- Documentation must be current
- Complexity must be challenged

## Memory Management
- Load memory at start of each interaction
- Update before phase transitions
- Record key decisions and challenges
- Maintain context between phases 