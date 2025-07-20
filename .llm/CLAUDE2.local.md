# CLAUDE.local.md - Tricky Problems & Solutions

## CLI Testing Issues

### 1. Memory Commands Display Bug
**Problem**: `memory list` and `memory search` show empty placeholder rows in table format, making it appear broken
**Solution**: Use `--format json` to see actual data - the commands work, it's just a table display formatting issue
```bash
# Broken display
uv run skogcli memory list

# Working display  
uv run skogcli memory list --format json
```

### 2. Config System Confusion
**Problem**: Config has duplicate sections with different values, inconsistent behavior between commands
- `show` vs `show-defaults` show different data
- `edit-defaults` changes one section, `reset` uses another
- Multiple `memory.page_size` entries with different values

**Solution**: Understand that config system has structural issues in the code - document as bugs to fix

### 3. COMMANDS.md Documentation Mismatch (SOLVED ✅)
**Problem**: Documentation was completely out of sync with actual CLI implementation
- Listed non-existent commands: `memory new`, `memory add`, `memory show`, `memory find`, `memory ls`, `memory info`, `memory recent-activity`
- Missing actual commands: `version`, `memory bm` (basic-memory passthrough)
- Had wrong command descriptions and options

**Root Cause**: Documentation was manually written and never updated when CLI implementation changed

**Solution Strategy**: Generate documentation directly from CLI source of truth
```bash
# Don't trust existing docs - verify actual commands
uv run skogcli --help
uv run skogcli memory --help  
uv run skogcli config --help

# Use CLI's built-in comprehensive documentation generator
uv run skogcli --helpall > COMMANDS.md

# This ensures docs always match actual implementation
```

**Key Insight**: Always generate docs from code, never manually maintain parallel documentation

### 4. Memory Command Redundancy
**Problem**: `memory write` and `memory create` do identical things with slightly different options
**Solution**: Pick one command and remove the other - they're unnecessarily redundant

### 5. Config File Corruption During Testing
**Problem**: Testing config commands corrupted `default_settings.json` structure
**Solution**: Restore file from git before testing, or test with backup copies

## Testing Approach Lessons
- Always test with JSON output first to see if data exists
- Check `--help` for actual commands vs documentation
- Be careful when testing config commands - they modify files
- Use git status to see what got changed during testing