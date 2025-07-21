# Session Context

## Project State
- Branch: feature/config-defaults  
- Main issue: Failing tests due to TDD methodology falling out of context
- Key insight: Context management is critical for AI behavior consistency

## TDD Context Loss Issue
- Problem: TDD document was only in chat history, got truncated
- Symptom: Started modifying source code without following Red-Green-Refactor
- Solution: Added `.skogai/.claude/commands/tdd.md` to CLAUDE.md includes permanently
- Verification: `skogcli config get "$.claude.context:tdd"` returns the file path

## Current Failing Tests
- `test_get_metadata_file` - expects temp directory but gets real config path
- Root cause: Test sets config via subprocess but function reads env vars first
- Fix: Set `SKOGAI_SCRIPT_METADATA_DIR` environment variable directly in test

## SkogAI Tag System
- `[@action:params]` - dynamic execution (cannot be cached)
- `$definition` - stored state/cached results  
- Examples: `[@git:status]`, `[@claude:"prompt"]`
- Config system tracks context: `$.claude.context:tdd`

## Trust Issues Resolved
- Script-kiddie behavior: asking questions instead of reading code
- Professional approach: read tests completely, understand specifications
- TDD sequence: Red (write test) → Green (minimal implementation) → Refactor