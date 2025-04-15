---
title: SkogCLI Standards Checker Tool
type: note
permalink: docs/tools/skog-cli-standards-checker-tool
---

# SkogCLI Standards Checker Tool

This document outlines a standards checker tool for the SkogCLI project to ensure consistent adherence to project standards.

## Overview

The Standards Checker is a utility script that validates code and configuration against the defined standards in the SkogCLI project.

## Implementation Plan

The tool will be implemented as a Python script in the project's tools directory.

### 1. Script Structure

```python
#!/usr/bin/env python
"""
Standards Checker for SkogCLI.

This tool validates code and configuration against defined project standards.
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple

# Configuration for the standards checker
STANDARDS = {
    "naming": {
        "file_patterns": {
            "module_files": r"^[a-z][a-z0-9_]*\.py$",
            "test_files": r"^test_[a-z0-9_]+\.py$",
            "doc_files": r"^[A-Z][A-Za-z0-9-]*\.md$",
        },
        "code_patterns": {
            "functions": r"^[a-z][a-z0-9_]*$",
            "classes": r"^[A-Z][A-Za-z0-9]*$",
            "constants": r"^[A-Z][A-Z0-9_]*$",
            "variables": r"^[a-z][a-z0-9_]*$",
        }
    },
    "structure": {
        "required_files": [
            "settings.py",
            "memory.py",
            "__init__.py",
        ],
        "required_test_files": [
            "test_settings.py",
            "test_memory.py",
        ]
    },
    "documentation": {
        "required_docstring_patterns": {
            "public_functions": r'""".*?"""',
            "classes": r'""".*?"""',
        }
    }
}


def main():
    """Run the standards checker."""
    parser = argparse.ArgumentParser(description="Check project standards compliance")
    parser.add_argument("--path", default=".", help="Path to check (default: current directory)")
    parser.add_argument("--fix", action="store_true", help="Attempt to fix issues automatically")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show verbose output")
    args = parser.parse_args()
    
    project_path = Path(args.path).resolve()
    issues = check_standards(project_path, verbose=args.verbose)
    
    if args.fix:
        fix_issues(project_path, issues, verbose=args.verbose)
        # Re-check after fixing
        issues = check_standards(project_path, verbose=args.verbose)
    
    if issues:
        print(f"\n{len(issues)} standards issues found.")
        sys.exit(1)
    else:
        print("\nAll standards checks passed!")
        sys.exit(0)


def check_standards(project_path: Path, verbose: bool = False) -> List[Dict[str, Any]]:
    """
    Check the project against defined standards.
    
    Args:
        project_path: Path to the project root
        verbose: Whether to show verbose output
    
    Returns:
        List of issues found
    """
    issues = []
    
    if verbose:
        print(f"Checking standards in {project_path}")
    
    # Check file naming
    issues.extend(check_file_naming(project_path, verbose))
    
    # Check project structure
    issues.extend(check_project_structure(project_path, verbose))
    
    # Check code style
    issues.extend(check_code_style(project_path, verbose))
    
    # Check documentation
    issues.extend(check_documentation(project_path, verbose))
    
    return issues


def check_file_naming(project_path: Path, verbose: bool) -> List[Dict[str, Any]]:
    """Check file naming conventions."""
    issues = []
    
    if verbose:
        print("Checking file naming conventions...")
    
    src_path = project_path / "src" / "skogcli"
    test_path = project_path / "tests"
    docs_path = project_path / "docs"
    
    # Check Python module files
    for file_path in src_path.glob("*.py"):
        if not re.match(STANDARDS["naming"]["file_patterns"]["module_files"], file_path.name):
            issues.append({
                "type": "naming",
                "path": str(file_path),
                "message": f"Module file name '{file_path.name}' does not match pattern "
                          f"'{STANDARDS['naming']['file_patterns']['module_files']}'",
                "fixable": False,
            })
    
    # Check test files
    for file_path in test_path.glob("*.py"):
        if not file_path.name.startswith("__") and not re.match(
            STANDARDS["naming"]["file_patterns"]["test_files"], file_path.name
        ):
            issues.append({
                "type": "naming",
                "path": str(file_path),
                "message": f"Test file name '{file_path.name}' does not match pattern "
                          f"'{STANDARDS['naming']['file_patterns']['test_files']}'",
                "fixable": False,
            })
    
    # Check documentation files
    for file_path in docs_path.glob("*.md"):
        if not re.match(STANDARDS["naming"]["file_patterns"]["doc_files"], file_path.name):
            issues.append({
                "type": "naming",
                "path": str(file_path),
                "message": f"Documentation file name '{file_path.name}' does not match pattern "
                          f"'{STANDARDS['naming']['file_patterns']['doc_files']}'",
                "fixable": False,
            })
    
    return issues


def check_project_structure(project_path: Path, verbose: bool) -> List[Dict[str, Any]]:
    """Check project structure for required files."""
    issues = []
    
    if verbose:
        print("Checking project structure...")
    
    src_path = project_path / "src" / "skogcli"
    test_path = project_path / "tests"
    
    # Check required source files
    for required_file in STANDARDS["structure"]["required_files"]:
        file_path = src_path / required_file
        if not file_path.exists():
            issues.append({
                "type": "structure",
                "path": str(file_path),
                "message": f"Required file '{required_file}' is missing",
                "fixable": False,
            })
    
    # Check required test files
    for required_file in STANDARDS["structure"]["required_test_files"]:
        file_path = test_path / required_file
        if not file_path.exists():
            issues.append({
                "type": "structure",
                "path": str(file_path),
                "message": f"Required test file '{required_file}' is missing",
                "fixable": False,
            })
    
    return issues


def check_code_style(project_path: Path, verbose: bool) -> List[Dict[str, Any]]:
    """Check code style conventions in Python files."""
    issues = []
    
    if verbose:
        print("Checking code style...")
    
    src_path = project_path / "src" / "skogcli"
    
    for file_path in src_path.glob("**/*.py"):
        if file_path.name.startswith("__"):
            continue
        
        with open(file_path, "r") as f:
            content = f.read()
        
        # Very basic parsing to find definitions
        function_pattern = r"def\s+([a-zA-Z0-9_]+)\s*\("
        class_pattern = r"class\s+([a-zA-Z0-9_]+)\s*[\(:]"
        constant_pattern = r"^([A-Z][A-Z0-9_]*)\s*="
        
        # Check function names
        for function_name in re.findall(function_pattern, content):
            if not re.match(STANDARDS["naming"]["code_patterns"]["functions"], function_name):
                issues.append({
                    "type": "naming",
                    "path": str(file_path),
                    "message": f"Function name '{function_name}' does not match pattern "
                              f"'{STANDARDS['naming']['code_patterns']['functions']}'",
                    "fixable": False,
                })
        
        # Check class names
        for class_name in re.findall(class_pattern, content):
            if not re.match(STANDARDS["naming"]["code_patterns"]["classes"], class_name):
                issues.append({
                    "type": "naming",
                    "path": str(file_path),
                    "message": f"Class name '{class_name}' does not match pattern "
                              f"'{STANDARDS['naming']['code_patterns']['classes']}'",
                    "fixable": False,
                })
        
        # Check constant names
        for line in content.split("\n"):
            matches = re.match(constant_pattern, line.strip())
            if matches:
                constant_name = matches.group(1)
                if not re.match(STANDARDS["naming"]["code_patterns"]["constants"], constant_name):
                    issues.append({
                        "type": "naming",
                        "path": str(file_path),
                        "message": f"Constant name '{constant_name}' does not match pattern "
                                  f"'{STANDARDS['naming']['code_patterns']['constants']}'",
                        "fixable": False,
                    })
    
    return issues


def check_documentation(project_path: Path, verbose: bool) -> List[Dict[str, Any]]:
    """Check documentation standards."""
    issues = []
    
    if verbose:
        print("Checking documentation...")
    
    src_path = project_path / "src" / "skogcli"
    
    for file_path in src_path.glob("**/*.py"):
        if file_path.name.startswith("__"):
            continue
        
        with open(file_path, "r") as f:
            content = f.read()
        
        # Check for docstrings in public functions
        function_pattern = r"def\s+([a-zA-Z0-9_]+)\s*\([^)]*\):\s*\n\s*(['\"]"
        matches = re.findall(function_pattern, content)
        
        for function_name, quote_start in matches:
            if not function_name.startswith("_"):  # Public function
                if quote_start != '"' or not re.search(
                    r'def\s+' + re.escape(function_name) + r'\s*\([^)]*\):\s*\n\s*""".*?"""',
                    content, re.DOTALL
                ):
                    issues.append({
                        "type": "documentation",
                        "path": str(file_path),
                        "message": f"Public function '{function_name}' is missing a proper docstring",
                        "fixable": False,
                    })
        
        # Check for docstrings in classes
        class_pattern = r"class\s+([a-zA-Z0-9_]+)"
        for class_name in re.findall(class_pattern, content):
            if not re.search(
                r'class\s+' + re.escape(class_name) + r'.*?:\s*\n\s*""".*?"""',
                content, re.DOTALL
            ):
                issues.append({
                    "type": "documentation",
                    "path": str(file_path),
                    "message": f"Class '{class_name}' is missing a docstring",
                    "fixable": False,
                })
    
    return issues


def fix_issues(project_path: Path, issues: List[Dict[str, Any]], verbose: bool) -> None:
    """
    Attempt to automatically fix some issues.
    
    Args:
        project_path: Path to the project root
        issues: List of issues to fix
        verbose: Whether to show verbose output
    """
    if verbose:
        print("\nAttempting to fix issues...")
    
    fixable_issues = [issue for issue in issues if issue.get("fixable", False)]
    
    for issue in fixable_issues:
        if verbose:
            print(f"Fixing: {issue['message']}")
        
        # Implement fix logic here based on issue type
        # This would be expanded based on the types of fixable issues we identify
    
    if verbose:
        print(f"Fixed {len(fixable_issues)} of {len(issues)} issues.")


if __name__ == "__main__":
    main()
```

### 2. Usage Instructions

```bash
# Run the checker
python tools/standards_checker.py

# Run with verbose output
python tools/standards_checker.py -v

# Check a specific path
python tools/standards_checker.py --path src/skogcli

# Auto-fix issues if possible
python tools/standards_checker.py --fix
```

## Integration with Development Workflow

The standards checker can be integrated into the development workflow in several ways:

### 1. Pre-commit Hook

Add a pre-commit hook to run the standards checker before each commit:

```bash
#!/bin/sh
python tools/standards_checker.py
if [ $? -ne 0 ]; then
    echo "Standards check failed. Please fix the issues before committing."
    exit 1
fi
```

### 2. CI/CD Integration

Add the standards checker to the CI/CD pipeline to ensure all code adheres to standards:

```yaml
# In CI/CD configuration
jobs:
  standards:
    name: Standards Check
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Check standards
        run: python tools/standards_checker.py -v
```

### 3. Editor Integration

Configure common editors to run the standards checker:

- **VS Code**: Add a task in `.vscode/tasks.json`
- **PyCharm**: Add an External Tool configuration
- **Vim/Neovim**: Add a command binding

## Future Enhancements

1. **Add more checks**:
   - Import order validation
   - Line length validation
   - Command help text validation

2. **More automatic fixes**:
   - Format imports
   - Add missing docstrings templates
   - Rename files to match conventions

3. **Configuration file**:
   - Allow customizing standards via a configuration file
   - Support project-specific overrides

4. **Integration with existing tools**:
   - Leverage tools like flake8, pylint, and black
   - Consolidate reports from multiple tools

This standards checker will help ensure consistent adherence to project standards across the codebase, making maintenance easier and reducing the cognitive load for developers working on the project.