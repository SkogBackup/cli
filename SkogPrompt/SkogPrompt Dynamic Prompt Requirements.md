---
title: SkogPrompt Dynamic Prompt Requirements
type: note
permalink: skog-prompt/skog-prompt-dynamic-prompt-requirements
---

# SkogPrompt Dynamic Prompt Requirements

## Core Requirements

The SkogPrompt system needs to support the following types of prompts and features:

### Message Types
- **User Messages as Prompts** [x]
  - Support for converting user messages into formatted prompts
  - Include context-aware information when needed
  - Maintain message history and relationships

- **Assistant Messages as Prompts** [x]
  - Support for converting assistant responses into formatted prompts
  - Preserve styling and formatting from original responses
  - Include metadata about response types and purposes

### Prompt Formats
- **Dynamic Prompts with Variables** [x]
  - Support for template variables that can be filled at runtime
  - Allow for conditional sections based on variable values
  - Enable loops and other template logic for complex prompts
  - Support for referencing other template components

- **Regular Prompts with Fixed Text** [x]
  - Support for static prompt templates without variables
  - Optimize for performance with pre-compiled templates
  - Enable versioning of fixed prompts

- **System Prompts with Instructions** [x]
  - Special format for system-level instructions
  - Support for global instruction sets that apply across sessions
  - Allow for project-specific instruction overrides

### Feature Requirements
- **Persona Injection** [x]
  - Support for loading predefined personas from JSON files
  - Enable dynamic persona attributes that can be adjusted
  - Support mixing multiple personas for complex interactions
  - Allow persona traits to influence prompt generation

## Architecture Implications

These requirements influence the system architecture in several ways:

1. **Template Engine**
   - Must support Jinja2 for variable substitution and conditional logic
   - Needs to handle different template types (user, assistant, system)
   - Should support template inheritance and composition

2. **Context Management**
   - Must track conversation state for contextual prompts
   - Needs to efficiently store and retrieve relevant context
   - Should support different context strategies for different prompt types

3. **Format Conversion**
   - Must support bidirectional conversion between formats
   - Needs to preserve message attributes during conversion
   - Should handle special formatting for different model providers

4. **Persona Management**
   - Must provide a clean API for accessing persona attributes
   - Needs to support combining multiple personas
   - Should enable runtime modification of persona characteristics

## Integration Points

The dynamic prompt system must integrate with:

1. **Other SkogAI Tools**
   - Connect with memory components for conversation history
   - Interface with context generation tools for relevant context
   - Support task management for prompt-initiated actions

2. **External AI Providers**
   - Format prompts appropriately for different AI models
   - Handle provider-specific requirements and limitations
   - Support platform-specific features when available

3. **Specialized Agents**
   - Support minimal command syntax like [@agent:command]
   - Provide appropriate context gathering for specialized agents
   - Format responses from specialized agents for conversation integration

## Implementation Considerations

- Prioritize template-based approach for flexibility
- Focus on clean interfaces between components
- Optimize for minimal context required by specialized agents
- Design for extensibility as new use cases emerge
- Maintain backward compatibility with existing templates

---

This document outlines the core requirements for SkogPrompt's dynamic prompt generation system as identified in our architectural discussions. These requirements will guide the implementation approach and design decisions moving forward.