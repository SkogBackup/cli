---
title: SkogPrompt Dynamic Agent Communication Architecture
type: note
permalink: architecture/skog-prompt-dynamic-agent-communication-architecture
---

# SkogPrompt Dynamic Agent Communication Architecture

## Overview [x]

This document outlines the architecture for SkogPrompt's approach to dynamic, minimal agent communication with specialized agents. The system enables efficient interaction with specialized agents through compact commands rather than large context loads.

## Core Concept [x]

The central insight is that specialized agents can understand domain-specific instructions with minimal context when provided in the right format. This dramatically reduces token usage and improves efficiency compared to traditional approaches.

## Component Architecture [/]

### 1. Agent Command Interface [/]

The Agent Command Interface provides a standardized way to communicate with specialized agents:

```
[@agent:command]
```

Key features:
- Minimal token usage (approximately 5 tokens)
- Domain-specific command interpretation
- No need for extensive context loading
- Asynchronous execution model

Example commands:
- `[@aider:test]` - Run tests on the current codebase
- `[@goose:help with quantum thinking]` - Get help from Goose on complex problems
- `[@amy:communicate this to users]` - Get communication assistance from Amy

### 2. Template Engine [/]

The Template Engine constructs appropriate agent-specific prompts using Jinja templates:

- Templates define the structure for each agent type
- Dynamic content insertion based on command and context
- Efficient context preparation without unnecessary details
- Specialized format for each agent's capabilities

### 3. Context Management [/]

The Context Management system handles the efficient loading and maintenance of context:

- Minimal context loading based on agent needs
- Background processing for context preparation
- Memory management to prevent context overload
- Integration with the broader SkogAI ecosystem

### 4. Response Handling [/]

The Response Handling system processes agent outputs:

- Asynchronous response collection
- Result presentation in appropriate format
- Task completion tracking
- Context preservation during interactions

## Communication Flow [/]

1. **Command Issuance**
   - User issues compact agent command
   - System identifies target agent and command

2. **Context Preparation**
   - System determines minimal necessary context
   - Relevant files or information are gathered
   - Template selection based on agent and command

3. **Agent Execution**
   - Specialized prompt is sent to target agent
   - Agent processes command with appropriate context
   - Processing occurs asynchronously

4. **Response Integration**
   - Result is captured when available
   - Main conversation continues uninterrupted
   - Results are presented when ready
   - Follow-up commands can be issued if needed

## Benefits [x]

This architecture provides several key advantages:

1. **Efficiency** - Dramatically reduced token usage compared to traditional approaches
2. **Specialization** - Each agent handles what it's best at
3. **Context Preservation** - Main conversation maintains focus without disruption
4. **Asynchronous Processing** - Work happens in parallel to conversation
5. **Low Cognitive Overhead** - Simple interface despite complex underlying system

## Implementation Approach [/]

The implementation will prioritize:

1. **Template System** - Jinja-based templates for agent-specific prompts
2. **Command Parser** - Efficient identification of agent commands in text
3. **Context Providers** - Smart context gathering based on agent needs
4. **Integration Layer** - Connection with MCP servers for agent communication

## Next Steps [ ]

1. Design the Jinja template structure for agent commands
2. Implement the command parser for identifying agent references
3. Create context providers for each specialized agent type
4. Develop the integration layer with MCP servers
5. Build the response handling system for asynchronous processing

## Example Templates [ ]

### Aider Code Template

```jinja
{% if command == "test" %}
Analyze the current test coverage in the project.
If the tests are comprehensive, make no changes.
If there are gaps, implement appropriate tests.
Only modify files if necessary to improve test coverage.
{% endif %}

{% if command == "implement" %}
Implement the following functionality:
{{ details }}
Follow project coding standards and include appropriate tests.
{% endif %}
```

## Knowledge Status

This document uses the standard verification status system:
- [x] - Verified information (directly confirmed)
- [/] - Reasonable confidence but requires verification
- [ ] - Unverified information or planning