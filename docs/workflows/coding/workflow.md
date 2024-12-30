# Development Workflow

## Core Principles
- Challenge and minimize requirements aggressively
- Once requirements are finalized, implementation must be robust
- Better to do fewer things extremely well
- Test everything that can be tested

## Technical Standards
- Debug levels via DEBUG_LEVEL env var
- Tests in /tests/{unit,integration}
- Demo scripts in /examples
- Must run demo and get review before commit
- Must run update_dir.py before commit

## Implementation Steps
1. Write tests first
2. Implement code
3. Run tests until passing
4. Create and run demo
5. Get human review
   - If disapproved: fix and return to step 3
   - If approved: proceed
6. Update directory structure
7. Update memory and commit 