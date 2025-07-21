# Remove .config Directory References

## Feature Goal
Remove all references to .config directory from SkogCLI codebase and use only:
- Environment variables (SKOGAI_*)
- src/data/default_settings.json for configuration

## Requirements
Based on previous conversation:
1. No .config directory usage
2. No code fallback - throw error if src/data/default_settings.json missing
3. Environment variables override file-based settings
4. Remove all .config references from code and docs

## Current .config References Found
- `tests/test_config.py:20` - test setup creates .config/skogcli
- `README.md:49` - mentions ~/.config/skogcli/config.json
- `CLAUDE.md:90` - same as README.md
- `src/skogcli/settings.py:47` - fallback to ~/.config path
- `src/skogcli/data/default_settings.json` - various config paths point to skogai/config

## Test Cases to Write (RED Phase)
1. Configuration should load from src/data/default_settings.json
2. Environment variables should override file settings
3. Should throw error if default_settings.json is missing
4. No .config directory should be created or referenced
5. Config commands should work with new system

## Implementation Plan (GREEN Phase)
1. Update settings.py to remove .config fallback
2. Update test fixtures to use src/data paths
3. Update documentation references
4. Update default_settings.json paths if needed

## Notes
- Following TDD methodology from .skogai/.claude/commands/tdd.md
- Current branch: feature/tmp
- Clean state restored after previous attempt