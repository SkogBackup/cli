---
title: SkogPrompt Integration with Template-Based Prompt Generation
type: note
permalink: architecture/skog-prompt-integration-with-template-based-prompt-generation
---

# SkogPrompt Integration with Template-Based Prompt Generation

## Overview [/]

This document outlines the architectural approach for integrating the SkogPrompt system with template-based prompt generation capabilities, specifically focusing on merging the Jinja templating system from skogmcp with SkogPrompt's core functionality.

## Current Components [/]

### SkogPrompt Core [x]
- Basic Python package structure with `skogprompt` module
- Main functionality runs prompts through `gptme` and saves output to files
- Comprehensive unit tests for the core functionality
- Chat conversion utility (`chat_to_json.py`) for handling AI conversation formats

### SkogMCP Jinja Templating [/]
- Template examples in `/home/skogix/skogmcp/jinja-examples/`
- Template manager script (`template_manager.py`) for creating and managing templates
- Support for various template features (basic templates, control flow, macros, inheritance)

### Unified Prompt Script [/]
- Script (`/home/skogix/skogchat/scripts/base/prompts/unified-prompt.sh`)
- Creates standard history and system files for different personas (Claude, Dot, Goose, Amy)
- Builds persona-specific prompts including timestamp and context
- Copies final prompt to clipboard for use

## Integration Architecture [ ]

The proposed integration architecture focuses on creating a unified system that leverages the strengths of both template-based prompt generation and dynamic prompt management.

### Core Components

1. **Template Engine** [PLACEHOLDER: Based on skogmcp Jinja implementation]
   - Template storage and management
   - Support for template inheritance and includes
   - Custom extensions for prompt-specific functionality
   - Validation mechanisms for template correctness

2. **Prompt Generation System** [ ]
   - Context collection (time, repository, history)
   - Variable management for template rendering
   - Support for different prompt formats (Claude, OpenAI, etc.)
   - Extension points for specialized prompt types

3. **Format Conversion Layer** [ ]
   - Convert between different AI platform formats
   - Support for bidirectional conversion
   - Preservation of special elements (system messages, tool calls)
   - Metadata management across conversions

4. **Integration API** [ ]
   - Clean interfaces for invoking templated prompts
   - Stream processing for real-time prompt generation
   - Hooks for pre/post-processing prompt content
   - Integration with broader SkogAI ecosystem

## Key Design Principles

1. **Separation of Concerns** [/]
   - Templates define structure and placeholders
   - Context providers supply dynamic content
   - Rendering engine combines them at runtime
   - Format handlers adapt the output for specific platforms

2. **Extensibility** [ ]
   - Plugin architecture for template extensions
   - Custom context providers for specialized content
   - Format adapters for new AI platforms
   - Custom rendering strategies for complex scenarios

3. **Consistency** [/]
   - Unified approach to template management
   - Standardized context collection
   - Common patterns across different prompt types
   - Consistent error handling and validation

4. **Integration with Ecosystem** [ ]
   - Use skogai-memory for template storage
   - Leverage skogai-context for repository information
   - Follow verification status system for documentation
   - Maintain clean boundaries between components

## Implementation Approach

### Phase 1: Foundation Integration

1. **Template Engine Implementation** [ ]
   - Port the template manager functionality from skogmcp
   - Create a unified template storage structure
   - Implement basic template rendering
   - Add validation for template correctness

2. **Context Collection** [ ]
   - Create providers for standard context (time, user, etc.)
   - Implement repository context collection
   - Add history tracking for conversation context
   - Design the context registry for extension

3. **Basic Format Support** [ ]
   - Implement standard formats (Claude, OpenAI)
   - Create the conversion architecture
   - Add validation for format correctness
   - Build initial command-line interface

### Phase 2: Advanced Features

1. **Dynamic Prompt Generation** [ ]
   - Real-time context injection
   - Conditional prompt sections
   - Advanced template inheritance
   - Context-aware formatting

2. **Integration APIs** [ ]
   - Python API for programmatic access
   - CLI for command-line operations
   - Web API for remote access
   - Inter-process communication for system integration

3. **Ecosystem Integration** [ ]
   - Template storage in skogai-memory
   - Context collection via skogai-context
   - Task tracking with skogai-todo
   - Planning integration with skogai-planning

## Examples [PLACEHOLDER: Initial concepts pending validation]

### Basic Template Example
```jinja
# {{ agent_name }} System Prompt

You are {{ agent_name }}, an AI assistant with the following characteristics:
{% for trait in traits %}
- {{ trait }}
{% endfor %}

## Key Information:
- Current time: {{ current_time }}
- User: {{ user_name }}
{% if context %}
- Context: {{ context }}
{% endif %}
```

### Usage Example
```python
prompt = skogprompt.template.render(
    "claude_system",
    agent_name="Claude",
    traits=["helpful", "harmless", "honest"],
    user_name="Skogix",
    context=repo_context
)
```

## Next Steps

The immediate focus for implementation should be:

1. Create detailed design for the template engine component
2. Document the context collection architecture
3. Define the format conversion specification
4. Establish the integration points with existing code
5. Create a prototype implementation of the core components

## Knowledge Status

This document uses the standard verification status system:
- [x] - Verified information
- [/] - Reasonable confidence but requires verification
- [ ] - Unverified information or planning