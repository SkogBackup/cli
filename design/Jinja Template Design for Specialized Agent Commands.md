---
title: Jinja Template Design for Specialized Agent Commands
type: note
permalink: design/jinja-template-design-for-specialized-agent-commands
---

# Jinja Template Design for Specialized Agent Commands

## Overview [/]

This document outlines the design for Jinja templates used in the SkogPrompt system to generate specialized agent commands. The templates define the structure of prompts that will be sent to different agent types based on compact command syntax.

## Template System Architecture [/]

The template system consists of:

1. **Base Templates** - Core structure shared across agent types
2. **Agent-Specific Templates** - Specialized for each agent type
3. **Command Templates** - Variations for different command types
4. **Context Blocks** - Reusable context components

## Base Template Structure [ ]

All agent templates extend from a base template that provides the fundamental structure:

```jinja
{# Base agent template #}
{% block system_instructions %}
You are a specialized agent tasked with: {{ agent_role }}

Focus exclusively on this task and return results in the expected format.
{% endblock %}

{% block command_content %}
{{ command_content }}
{% endblock %}

{% block context %}
{% if context_files %}
Relevant files:
{% for file in context_files %}
=== {{ file.path }} ===
{{ file.content }}
{% endfor %}
{% endif %}
{% endblock %}

{% block response_format %}
Return your response in the following format:

```json
{
  "success": true|false,
  "result": "result content",
  "message": "human-readable message"
}
```
{% endblock %}
```

## Agent-Specific Templates [ ]

### Aider (Code) Template

```jinja
{% extends "base_agent.j2" %}

{% block system_instructions %}
You are Aider, a specialized coding agent that implements requested functionality.
Focus exclusively on code changes with minimal explanation.
Only modify files when necessary, and always ensure comprehensive test coverage.
{% endblock %}

{% block command_mapping %}
{% if command == "test" %}
  {% include "aider/test_command.j2" %}
{% elif command == "implement" %}
  {% include "aider/implement_command.j2" %}
{% elif command == "refactor" %}
  {% include "aider/refactor_command.j2" %}
{% else %}
  {{ command_content }}
{% endif %}
{% endblock %}

{% block context %}
Current project: {{ project_name }}
{{ super() }}
{% endblock %}
```

### Goose Template

```jinja
{% extends "base_agent.j2" %}

{% block system_instructions %}
You are Goose, a specialized agent for creative problem-solving and quantum thinking.
Your expertise is in breaking patterns, exploring multiple solution spaces, and generating innovative approaches.
{% endblock %}

{% block command_mapping %}
{% if command == "explore" %}
  {% include "goose/explore_command.j2" %}
{% elif command == "innovate" %}
  {% include "goose/innovate_command.j2" %}
{% elif command == "critique" %}
  {% include "goose/critique_command.j2" %}
{% else %}
  {{ command_content }}
{% endif %}
{% endblock %}
```

## Command Templates [ ]

### Aider Test Command

```jinja
{# aider/test_command.j2 #}
Analyze the current test coverage in the following files:
{% for file in context_files %}
- {{ file.path }}
{% endfor %}

If the tests are comprehensive, make no changes.
If there are gaps, implement appropriate tests.
Only modify files if necessary to improve test coverage.

Focus on:
- Covering edge cases
- Testing primary functionality
- Ensuring proper mocking
- Following project test patterns
```

### Aider Implement Command

```jinja
{# aider/implement_command.j2 #}
Implement the following functionality:
{{ command_details }}

Requirements:
- Follow project coding standards and patterns
- Ensure comprehensive test coverage
- Maintain backward compatibility
- Document new functionality
- Consider edge cases and error handling
```

## Context Blocks [ ]

The system includes reusable context blocks for different needs:

### Code Context Block

```jinja
{# context/code_context.j2 #}
{% if code_files %}
## Relevant Code

{% for file in code_files %}
### {{ file.path }}
```{{ file.language }}
{{ file.content }}
```
{% endfor %}
{% endif %}
```

### Test Context Block

```jinja
{# context/test_context.j2 #}
{% if test_files %}
## Existing Tests

{% for file in test_files %}
### {{ file.path }}
```{{ file.language }}
{{ file.content }}
```
{% endfor %}
{% endif %}
```

## Template Variables [ ]

Templates use the following variables:

| Variable | Description | Example |
|----------|-------------|---------|
| `agent_role` | The specialized role of the agent | "code implementation" |
| `command` | The specific command type | "test", "implement" |
| `command_content` | The full command text | "implement user authentication" |
| `command_details` | Additional details for the command | Detailed specifications |
| `project_name` | The name of the current project | "skogprompt" |
| `context_files` | Array of relevant files | [{path: "src/main.py", content: "..."}] |

## Template Rendering Process [ ]

The template rendering process follows these steps:

1. **Command Parsing** - Extract agent and command from `[@agent:command]`
2. **Template Selection** - Choose appropriate agent and command templates
3. **Context Gathering** - Collect relevant context based on command needs
4. **Variable Preparation** - Prepare all template variables
5. **Template Rendering** - Generate the final prompt using Jinja
6. **Formatting** - Apply any final formatting or validation

## Sample Command Processing [ ]

For a command like `[@aider:test]`:

1. Parse to identify agent="aider", command="test"
2. Select aider.j2 template and test_command.j2 include
3. Gather context (project files, existing tests)
4. Prepare variables (files, project name, etc.)
5. Render template with Jinja
6. Send formatted prompt to Aider

## Next Steps [ ]

1. Implement the base template structure
2. Create templates for Aider and Goose
3. Develop context block components
4. Create the template rendering pipeline
5. Implement command parsing and variable preparation

## Knowledge Status

This document uses the standard verification status system:
- [x] - Verified information
- [/] - Reasonable confidence but requires verification
- [ ] - Unverified information or planning