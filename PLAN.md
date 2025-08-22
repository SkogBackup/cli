# SkogCLI Script Subcommand Analysis Plan

## Overview
The script subcommand is a comprehensive script management system with ~1400 lines of code. It provides functionality for creating, managing, and running custom scripts.

## Analysis Areas

### 1. Command Structure & Organization
- 18 subcommands: list, run, create, edit, remove, info, code, batch, update-metadata, templates, export, transform, search, generate, import, import-file, copy
- Rich CLI interface with typer
- Autocompletion support for script names and templates

### 2. Core Functionality Assessment
**Template System:**
- Templates stored in `data/templates/{python,shell}/`
- Dynamic template discovery and selection
- Template-based script generation

**Script Management:**
- User vs global script directories
- Metadata tracking (JSON-based)
- File operations (create, edit, copy, remove)

**Script Execution:**
- Python module loading and execution
- Shell script execution with permissions
- Argument passing support

### 3. Configuration Dependencies
**Current issues to investigate:**
- Multiple environment variable dependencies (SKOGAI_*)
- Config setting fallbacks (`script.user_scripts_dir`, etc.)
- Directory creation and permission handling
- Potential conflicts with the config system we just fixed

### 4. Code Quality & Maintainability
**Areas to examine:**
- Error handling patterns
- Code duplication (especially directory/path resolution)
- Function complexity (some functions are 100+ lines)
- Test coverage gaps

### 5. Integration Points
- Settings module integration
- Rich console output
- File system operations
- Subprocess management

## Immediate Concerns
1. **Config Integration**: Does it properly use the cleaned config system?
2. **Error Recovery**: What happens when directories/configs are missing?
3. **Test Coverage**: Are the script operations properly tested?
4. **Security**: File permissions, shell injection risks
5. **Complexity**: Some commands (like `generate`, `batch`) are very complex

## Next Steps
1. Review config integration points
2. Check test coverage for script module
3. Identify refactoring opportunities
4. Plan incremental improvements following TDD approach

## Priority Issues
- Directory resolution complexity (multiple fallback paths) ✅ FIXED
- Large function sizes (need decomposition)
- Error handling inconsistencies
- Potential security concerns in subprocess execution

## Current Status ✅
- **Environment Variable Support**: Fixed test environment variable support in `get_user_scripts_dir()` and `get_metadata_file()`
- **Config Integration**: Verified script module works correctly with cleaned config system
- **Test Coverage**: All 10 script tests passing

## Refactoring Opportunities Identified

### 1. Large Functions That Need Decomposition
- `batch_process()` - 200+ lines, handles multiple commands
- `generate_script()` - 150+ lines, complex AI/template logic
- `search_scripts()` - 100+ lines, file search and formatting
- `transform_script()` - 80+ lines, regex transformation with backup

### 2. Code Duplication Patterns
- Directory permission checks (repeated in multiple commands)
- Editor launching logic (create, edit, copy commands)
- Metadata update patterns (scattered across commands)
- Script path resolution (user vs global)

### 3. Error Handling Inconsistencies
- Some functions use console.print() for errors, others raise exceptions
- Inconsistent permission error handling
- Missing error recovery in some edge cases

### 4. Security Concerns
- subprocess.run() calls with user input in script execution
- File permission handling in global vs user scripts
- Path traversal risks in script file operations

### 5. Template System Issues
- Template discovery logic is scattered
- No validation of template content
- Template customization is basic string replacement

## Recommended Refactoring Approach (TDD)
1. **Extract common utilities** - Create helper functions for repeated patterns
2. **Decompose large functions** - Break into smaller, testable units
3. **Standardize error handling** - Consistent patterns across commands
4. **Improve security** - Validate inputs, sanitize paths
5. **Enhance template system** - Better discovery and customization
