---
title: SkogPrompt Templating System Design
type: note
permalink: design/skog-prompt-templating-system-design
---

# SkogPrompt Templating System Design

## Overview [/]

This document describes the detailed design for the SkogPrompt templating system, which forms the core of the dynamic prompt generation capabilities. The system is inspired by the Jinja templating capabilities seen in skogmcp but expanded to meet the specific needs of AI prompt generation.

## Core Components [ ]

### 1. Template Registry [PLACEHOLDER: Based on template_manager.py patterns]

The Template Registry is responsible for storing, retrieving, and managing templates within the system.

#### Key Functionality
- Template storage in filesystem or database
- Versioning of templates
- Categorization and tagging
- Template discovery and listing
- Template validation

#### Implementation Considerations
- Use a layered approach with filesystem as default backend
- Support optional integration with skogai-memory for persistent storage
- Implement a caching layer for performance
- Include validation hooks for template correctness

### 2. Template Engine [ ]

The Template Engine handles the parsing, rendering, and extension of templates.

#### Key Functionality
- Template parsing and syntax validation
- Variable substitution and expression evaluation
- Control structures (conditionals, loops)
- Template inheritance and inclusion
- Macros and reusable components
- Custom filters and extensions

#### Implementation Considerations
- Build on Jinja2 as the core engine
- Create a thin wrapper for SkogPrompt-specific features
- Implement a plugin system for extensions
- Include performance optimizations for frequently used templates

### 3. Context Providers [ ]

Context Providers supply the dynamic data used during template rendering.

#### Key Functionality
- System context (time, environment, etc.)
- User context (preferences, history, etc.)
- Repository context (project structure, files, etc.)
- Conversation context (chat history, previous interactions)
- Dynamic context (runtime information)

#### Implementation Considerations
- Implement a provider interface for extensibility
- Include standard providers out of the box
- Support lazy loading for expensive context
- Allow context composition and overlays

### 4. Rendering Pipeline [ ]

The Rendering Pipeline orchestrates the entire process from template selection to final output.

#### Key Functionality
- Template resolution and loading
- Context collection and preparation
- Template rendering with context
- Post-processing and formatting
- Output adaptation for target platforms

#### Implementation Considerations
- Design as a multi-stage pipeline with clear boundaries
- Support for synchronous and asynchronous rendering
- Implement hooks for customization at each stage
- Include comprehensive logging and debugging

## Data Flow

The data flow through the system follows these steps:

1. **Template Request**
   - Application requests a template by name/ID
   - Optional parameters specify rendering options

2. **Template Resolution**
   - Registry locates the requested template
   - Template is loaded and validated

3. **Context Collection**
   - System determines required context
   - Context providers are invoked to gather data
   - Context is validated and prepared

4. **Template Rendering**
   - Engine combines template with context
   - Variables are substituted and expressions evaluated
   - Control structures are processed
   - Included templates and macros are resolved

5. **Post-Processing**
   - Output is formatted according to requirements
   - Platform-specific adaptations are applied
   - Final validation ensures correctness

6. **Delivery**
   - Rendered prompt is returned to the caller
   - Optional caching for future requests

## Template Format [PLACEHOLDER: Based on observed examples]

Templates follow an extended Jinja2 syntax with additional features specific to prompt generation:

```jinja
# {{ template.name }} - v{{ template.version }}

{# Basic variable substitution #}
You are {{ agent.name }}, a {{ agent.role }} with the following capabilities:

{# Looping through collections #}
{% for capability in agent.capabilities %}
- {{ capability.name }}: {{ capability.description }}
{% endfor %}

{# Conditional sections #}
{% if context.repository %}
## Project Context
You are working with the {{ context.repository.name }} project, which contains:
{{ context.repository.description }}
{% endif %}

{# Custom prompt extensions #}
{% prompt_section "System Instructions" %}
Follow these instructions carefully:
1. Respond in a helpful, harmless, and honest manner
2. Acknowledge when you're uncertain
3. Focus on providing maximum value to the user
{% end_prompt_section %}

{# Dynamic content inclusion #}
{% include "standard_disclaimers.j2" %}

{# Format-specific sections #}
{% claude_only %}
This section only appears in Claude prompts.
{% end_claude_only %}
```

## Integration Interfaces [ ]

The templating system exposes several interfaces for integration:

### 1. Python API

```python
# Simple rendering
prompt = skogprompt.template.render("agent_system", 
                                    agent_name="Claude",
                                    capabilities=["writing", "analysis"])

# Advanced rendering with context providers
context = skogprompt.context.create()
context.add_provider(RepositoryContextProvider("/path/to/repo"))
context.add_provider(TimeContextProvider())
prompt = skogprompt.template.render_with_context("agent_system", context)

# Stream rendering for large templates
async for chunk in skogprompt.template.stream_render("large_template", context):
    process_chunk(chunk)
```

### 2. Command-Line Interface

```bash
# Render a template with parameters
skogprompt template render agent_system --param agent_name=Claude

# Create a new template
skogprompt template create my_template --from base_template

# List available templates
skogprompt template list --category system
```

### 3. Integration API

```python
# Register as a provider in another system
class TemplateProvider(BaseProvider):
    def provide(self, request):
        template_name = request.get("template")
        params = request.get("parameters", {})
        return skogprompt.template.render(template_name, **params)
```

## Extension Mechanisms [ ]

The system supports several extension points:

### 1. Custom Context Providers

Developers can create custom context providers by implementing the ContextProvider interface:

```python
class MyCustomContextProvider(ContextProvider):
    def collect(self, context):
        # Add custom data to the context
        context["my_custom_data"] = self.generate_data()
        return context
```

### 2. Template Extensions

Custom extensions can add new tags, filters, and functions to the template language:

```python
class MyExtension(Extension):
    def get_filters(self):
        return {
            "my_filter": self.my_filter,
        }
    
    def my_filter(self, value, arg=None):
        # Filter implementation
        return processed_value
```

### 3. Format Adapters

Format adapters can be created to handle specialized output formats:

```python
class OpenAIAdapter(FormatAdapter):
    def adapt(self, rendered_template, options=None):
        # Transform to OpenAI-specific format
        return {
            "model": options.get("model", "gpt-4"),
            "messages": self.split_into_messages(rendered_template)
        }
```

## Implementation Plan [ ]

The implementation will proceed in phases:

### Phase 1: Core Engine
- Implement basic Template Registry
- Create Template Engine wrapper around Jinja2
- Develop standard Context Providers
- Build simple Rendering Pipeline

### Phase 2: Extensions
- Implement custom template extensions
- Add format-specific adapters
- Create plugin system for extensibility
- Develop comprehensive testing suite

### Phase 3: Integration
- Build Command-Line Interface
- Implement Python API
- Develop integration points with SkogAI ecosystem
- Create documentation and examples

## Next Steps

The immediate next steps for this design are:

1. Review and validate the overall architecture
2. Create detailed interface specifications
3. Implement proof-of-concept for core components
4. Test with existing templates from skogmcp

## Knowledge Status

This document uses the standard verification status system:
- [x] - Verified information
- [/] - Reasonable confidence but requires verification
- [ ] - Unverified information or planning