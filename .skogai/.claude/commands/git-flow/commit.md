---
description: Create a git commit with proper co-author attribution
allowed-tools: Bash(git add*), Bash(git status*), Bash(git commit*), Bash(git diff*)
---

## Context
- Current git status: !`git status --short`
- Current git diff (staged and unstaged): !`git diff HEAD`
- Current branch: !`git branch --show-current`
- Recent commits: !`git log --oneline -5`

## Task
Based on the changes above, create a single git commit:
1. Analyze all changes (both staged and unstaged)
2. Stage appropriate files with git add
3. Create a descriptive commit message
4. Always include co-author attribution:

🤖 Generated with [Claude Code](https://claude\.claude/code)

Co-Authored-By: Claude <noreply@anthropic.com>
