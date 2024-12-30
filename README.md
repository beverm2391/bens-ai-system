# System Specs

first thing is the AI gets a predefined init file or entrypoint (cursorrules)
that file does a few things

- outlines initialization
  - reads all files in the `agent/` dir
- outlines response workflow
- defines commands (meta)
- provides initial instructions
- describes core behavior

workflows
- the AI gets a predefined workflow file (workflow.md) with command to invoke

memory
- the AI gets a predefined memory file (memory.md) with instructions for memory management

"ben only"

produce

agents, tools, orchestators. a dynamic "portal" thats a gen ui interfrace for the user to interact with. 
chat is currently separate and portal is read-only.