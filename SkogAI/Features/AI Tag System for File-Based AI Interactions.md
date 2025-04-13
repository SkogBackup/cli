---
title: AI Tag System for File-Based AI Interactions
type: note
permalink: skog-ai/features/ai-tag-system-for-file-based-ai-interactions
---

# AI Tag System for File-Based AI Interactions

## Overview
The AI tag system is an elegant method for interacting with AI agents through standard text files and code. It uses comment syntax followed by special tags that trigger different behaviors.

## Tag Types

### `#AI` - Context Provider
- **Purpose**: Provides context or information for future commands
- **Behavior**: Doesn't execute anything immediately but informs future operations
- **Example**: `# Here's some important context about this function #AI`
- **Usage**: Leave these tags in places of interest to build context

### `#AI?` - Question/Conditional Tag
- **Purpose**: Gets information or sets up conditional logic
- **Behavior**: Evaluates conditions and takes appropriate action
- **Example**: `# if 1=1 replace this text with fizzbuzz in F# #AI?`
- **Usage**: Acts like "if statements" that evaluate when execution begins

### `#AI!` - Action Command
- **Purpose**: Executes an immediate action
- **Behavior**: Triggers processing and often replaces file content with results
- **Example**: `# Generate unit tests for this function #AI!`
- **Usage**: The first `#AI!` tag triggers execution of the entire sequence

## Implementation Details
- Lines *MUST* start with a language-appropriate comment character (`#`, `//`, `--`, etc.)
- The system parses files looking for these specific patterns
- Extremely efficient to parse compared to complex command languages
- Works across any text or code file regardless of programming language

## Workflow Pattern
1. Add context with `#AI` tags across files of interest (building knowledge)
2. Add conditional logic with `#AI?` tags (defining behavior rules)
3. Trigger execution with an `#AI!` tag (the "go" button)

## Examples

```python
# This function handles user authentication #AI
# if there are no test cases, generate some #AI?
# Create comprehensive documentation for this module #AI!
```

```javascript
// This uses an older API version #AI
// if API version < 3 then show deprecation warnings #AI?
// Update this code to use the latest API #AI!
```

## Benefits
- Seamless integration with existing code and workflows
- Language-agnostic implementation
- Extremely efficient parsing
- Natural progression from context to questions to actions
- File-based interface works with any editor or environment

This system essentially creates a "programming language" for AI interactions through simple file annotations, allowing for asynchronous, declarative, and context-aware AI operations.