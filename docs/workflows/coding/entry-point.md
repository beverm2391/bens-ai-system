# Entry Point

1. Check if workflow exists:
   - Look for memory file in `docs/workflows/coding/memory/{task_id}.json`
   - If exists, load and resume from current phase
   - If not, create new workflow memory

2. For new workflows:
   - Create memory file with format: `{timestamp}_{task_name}.json`
   - Initialize in requirements phase
   - Follow phase structure from workflow.md

3. For all workflows:
   - Analyze task scale (simple/medium/complex)
   - Use META prefixes for status updates
   - Follow current phase instructions
   - Update memory before phase transitions
   - Challenge complexity at every step

4. Exit conditions:
   - Task complete
   - Explicitly ended with `:end` or `:e`
   - Phase transition needed

Next step: Go to `docs/workflows/coding/workflow.md` for phase details