---
description: Finish the current git-flow feature branch
allowed-tools: Bash(git*), Bash(git-flow*)
---

## Context
- Current branch: !`git branch --show-current`
- Git status: !`git status --short`
- Uncommitted changes: !`git diff --stat`

## Task
Finish the current git-flow feature branch by:
1. Check if there are uncommitted changes
2. If clean, run git-flow feature finish
3. If not clean, inform me what needs to be committed first