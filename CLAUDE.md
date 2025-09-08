# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with the SkogCLI repository.

## Critical Context (Read First)

- **Tech Stack**: Python 3.12+ with Typer CLI framework, Rich for output formatting, UV for package management
- **Main File**: src/skogcli/**init**.py (main CLI entry point)
- **Core Mechanic**: Multi-module CLI with memory, script, config, and agent management (~5400 lines across 12 Python files)
- **Key Integration**: basic-memory for knowledge management, litellm for AI agents, smolagents for agent orchestration
- **Platform Support**: Cross-platform CLI tool with pytest testing
- **DO NOT**: Modify source code without writing tests first (strict TDD methodology)

## Session Startup Checklist

**IMPORTANT**: At the start of each session, check these items:

1. **Check TASKS.md** - Look for any IN_PROGRESS or BLOCKED tasks from previous sessions
2. **Review recent JOURNAL.md entries** - Scan last 2-3 entries for context
3. **If resuming work**: Load the current task context from TASKS.md before proceeding

### includes

@/home/skogix/.claude/CLAUDE.md
@README.md
@/home/skogix/skogai/.skogai/rules.md
@/home/skogix/skogai/.skogai/claude/identity.md
@/home/skogix/claude/.backup/persona/placeholder.md
@/home/skogix/claude/.backup/persona/placeholder.md
@/home/skogix/skogai/.skogai/claude/epistemic-frameworks.md
@/home/skogix/skogai/.skogai/definitions.md
@/home/skogix/skogai/.skogai/skogai-notation.md
@/home/skogix/skogai/.skogai/skogcli.md
@/home/skogix/skogai/.skogai/skogparse.md
@/home/skogix/skogai/.skogai/user.md

- NEVER EVER finish your message with "Is this what you mean?", "What you you think about..." and ABSOLUTELY NO questions designed to "drive the conversation forward". You are _NOT_ chat-GPT and do not have to rresort to sycofantry
