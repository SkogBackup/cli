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

### 3. COMMANDS.md Documentation Mismatch
**Problem**: Documentation lists non-existent commands (`memory new`, `memory add`, `memory show`, etc.)
**Solution**: Check actual CLI with `--help` before trusting documentation
```bash
# Check actual commands
uv run skogcli memory --help
```

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