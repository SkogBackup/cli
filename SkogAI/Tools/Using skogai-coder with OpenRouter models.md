---
title: Using skogai-coder with OpenRouter models
type: note
permalink: skog-ai/tools/using-skogai-coder-with-open-router-models
---

# Using skogai-coder with OpenRouter Models

## Overview

The `skogai-coder` tool is a powerful MCP service that allows generating code without cluttering the main conversation context. It excels at handling implementation details separately, keeping the main conversation focused and clean.

## Key Features

- Creates or modifies code files directly without adding the code to the conversation context
- Supports various AI models, including OpenRouter models
- Maintains a clean separation between conversation and implementation

## Usage Pattern

```
mcp__skogai-coder__aider_ai_code
Parameters:
- ai_coding_prompt: The task description for code generation
- relative_editable_files: Files that can be created or modified
- relative_readonly_files: Files that provide context but shouldn't be changed
- model: The AI model to use (optional)
```

## Working with OpenRouter Models

When using OpenRouter models with skogai-coder:

1. First list available models to find the one you need:
   ```
   mcp__skogai-coder__list_models
   Parameters:
     - substring: Optional filter to narrow down model list
   ```

2. Use the full OpenRouter model path when specifying the model:
   ```
   model: "openrouter/anthropic/claude-3.7-sonnet"
   ```

3. The OpenRouter models follow the pattern:
   ```
   openrouter/provider/model-name
   ```

## Example Models

Some of the recommended OpenRouter models:

- **Claude models**: `openrouter/anthropic/claude-3.7-sonnet`, `openrouter/anthropic/claude-3-opus`
- **Llama models**: `openrouter/meta-llama/llama-3-70b-instruct`
- **Code-specialized models**: `openrouter/deepseek/deepseek-coder`, `openrouter/qwen/qwen-2.5-coder-32b-instruct`

## Best Practices

1. Always specify the file path correctly in `relative_editable_files`
2. Provide enough context with `relative_readonly_files` for the model to understand the codebase
3. Write clear, specific prompts for best results
4. Check results after code generation by viewing the file and testing functionality

## Example

```python
<function_calls>
<invoke name="mcp__skogai-coder__aider_ai_code">
<parameter name="ai_coding_prompt">Create a Python function to analyze data from JSON files