---
title: Recommended Additions to Global CLAUDE.md
type: note
permalink: configuration/recommended-additions-to-global-claude-md
---

# Recommended Additions to Global CLAUDE.md

The following section should be added to the global CLAUDE.md file to provide comprehensive guidance on SkogPrompt tools usage.

```markdown
## SkogPrompt Tools Guide

### Tool Overview

The SkogPrompt ecosystem includes four integrated tools that enhance architectural design capabilities:

1. **skogai-context** - Efficient project understanding without implementation details
2. **skogai-memory** - Knowledge persistence and documentation
3. **skogai-todo** - Task management with architectural focus
4. **skogai-planning** - Structured development planning

### Tool Prioritization

When working with files, ALWAYS prioritize in this order:

1. Use skogai-context tools first for all file operations
   - `lc-project-context` for repository structure
   - `lc-get-files` for file contents
   - `lc-code-outlines` for code structure
   - `lc-get-implementations` for specific implementations
   - `lc-list-modified-files` for tracking changes

2. Use BatchTool for multiple operations
3. Fall back to basic tools only if specifically requested

### Documentation Approach with skogai-memory

When documenting with skogai-memory, always use the verification status system:

- `[x]` - Hard verification by user, confirmed correct
- `[/]` - Reasonable confidence but verify in critical contexts
- `[ ]` - No verification, considered planning/suggestion
- `[s]` - Waiting for user input

Use placeholders to indicate uncertainty: `[PLACEHOLDER: reasoning based on context]`

### Task Management with skogai-todo

For architectural tasks:
- Assign clear priorities based on architectural impact
- Use consistent tags for categorization
- Include detailed descriptions of requirements
- Track progress with status updates

### Planning with skogai-planning

For architectural planning:
- Start with high-level architectural goals
- Break down into components with clear interfaces
- Assign complexity scores (0-10) based on architectural challenge
- Track implementation progress
- Document architectural decisions throughout

### Integrated Workflow

For optimal results, combine tools in this workflow:
1. Understand project context with skogai-context
2. Reference and update knowledge with skogai-memory
3. Plan implementation with skogai-planning
4. Track tasks with skogai-todo
5. Monitor changes with skogai-context

This integrated approach maintains architectural focus without requiring implementation details.
```

This addition provides a comprehensive reference for effectively using SkogPrompt tools while maintaining focus on architectural concepts over implementation details.