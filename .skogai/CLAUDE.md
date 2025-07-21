[$claude:context:local]
# .skogai/CLAUDE.md

## ALWAYS assume
- if it is needed the task, it will be in context

## Model Context Protocol
- `mcp__supabase` - [@todo:skogix:in a couple of sessions]
- `mcp__skogai-think` - USE IT! Best thing you have and helps out SO MUCH!
- `mcp__context7` - almost as good as skogai-think, always use!

## [@todo:explain to claude what context is]
- [$PLACEHOLDER:context]

## Do not
- Don't write forgiving code
  - Use preconditions
    - Use schema libraries
    - Assert that inputs match expected formats
    - When expectations are violated, throw, don't log
  - Don't add defensive try/catch blocks
    - Usually we let exceptions propagate out
- Don't use abbreviations or acronyms
  - Choose `number` instead of `num` and `greaterThan` instead of `gt`
- Emoji and unicode characters are welcome
  - Use them at the beginning of comments, commit messages, and in headers in docs
- If the user asks a question, only answer the question, do not edit code
- Don't say:
  - "You're right"
  - "I apologize"
  - "I'm sorry"
  - "Let me explain"
  - any other introduction or transition
- Immediately get to the point
- When a code change is ready, we need to verify it passes the build
- Don't run long-lived processes like development servers or file watchers
  - Don't run `npm run dev`
- If the build is slow or logs a lot, don't run it
  - Echo copy/pasteable commands and ask the user to run it
- If build speed is not obvious, figure it out and add notes to project-specific memory

[$/claude:context:local]
[$/claude:ignore]
@./.skogai/CLAUDE.md
@./.skogai/tmp/context
[$/claude:ignore]
