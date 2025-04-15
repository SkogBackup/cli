---
title: Preset States Recipe
type: note
permalink: skogcli/recipes/preset-states-recipe
---

# Preset States Recipe Configuration

## Recipe Metadata
```yaml
version: 1.0.0
title: SkogCLI Preset States
description: Configuration for maintaining and switching between AI assistant states
instructions: Guide users in working with preset AI assistant states, focusing on saving, loading, and managing context across different projects. Help implement a system where complete assistant contexts can be saved as named presets and easily restored when needed.
author:
  contact: skogix
```

## Extension Configuration
```yaml
extensions:
- type: builtin
  name: memory
  display_name: Memory
  timeout: 300
  bundled: null
- type: builtin
  name: computercontroller
  display_name: Computer Controller
  timeout: 300
  bundled: null
- type: builtin
  name: developer
  display_name: Developer Tools
  timeout: 300
  bundled: null
- type: stdio
  name: skogai-memory
  cmd: uvx
  args:
  - basic-memory
  - mcp
  envs: {}
  timeout: 300
  description: null
  bundled: null
```

## Activities
```yaml
activities:
- Define state data model
- Implement state save/load commands
- Create state management utilities
- Design state sharing mechanisms
- Develop state composition features
```

## Original Recipe Reference
This recipe is based on the `testchat.yaml` example which demonstrated:
```yaml
version: 1.0.0
title: Custom recipe from chat
description: a custom recipe instance from this chat session
instructions: Guide users in exploring their memory system capabilities, focusing on investigating chat history functionality through systematic tool usage. When accessing memory systems, first check project info to establish available structures, then explore recent activity and specific content through targeted searches. Provide clear summaries of findings and document any limitations or areas for further exploration.
extensions:
- type: builtin
  name: memory
  display_name: Memory
  timeout: 300
  bundled: null
- type: builtin
  name: computercontroller
  display_name: Computer Controller
  timeout: 300
  bundled: null
- type: builtin
  name: developer
  display_name: Developer Tools
  timeout: 300
  bundled: null
- type: stdio
  name: skogai-memory
  cmd: uvx
  args:
  - basic-memory
  - mcp
  envs: {}
  timeout: 300
  description: null
  bundled: null
activities:
- Check project information
- Review recent activity
- Search for conversation logs
- Examine memory structure
- Document memory system features
author:
  contact: skogix
```

## Purpose
The recipe configuration manages the AI assistant's context, tools, and focus when working with the SkogCLI Preset States feature. This allows consistent assistant behavior when implementing and using the feature for managing saved states across different projects and task types.

## Usage Notes
This recipe should be loaded when:
1. Developing the Preset States feature
2. Documenting state management functionality
3. Testing state saving/loading behavior
4. Implementing state sharing capabilities

The configuration ensures the assistant has access to the memory system, developer tools, and computer controller extensions needed for implementing and managing state features.