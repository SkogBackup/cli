---
title: SkogPrompt Tools Guide
type: note
permalink: documentation/skog-prompt-tools-guide
---

# SkogPrompt Tools Guide

This document provides comprehensive guidance on the SkogPrompt suite of tools designed to enhance architectural design and documentation capabilities.

## Overview

The SkogPrompt ecosystem consists of four primary tools:

1. **skogai-context** - For efficient project understanding and code navigation
2. **skogai-memory** - For knowledge persistence and documentation
3. **skogai-todo** - For task management and tracking
4. **skogai-planning** - For structured development planning

These tools work together to provide a comprehensive environment for architectural design and documentation without requiring deep implementation details.

## skogai-context

The context module provides efficient access to project structure and code without requiring direct file access.

### Key Components

- **lc-project-context** - Generates a structured repository overview including directory tree and file status
- **lc-get-files** - Retrieves complete contents of specified files
- **lc-code-outlines** - Provides high-level overview of code structure showing key definitions
- **lc-get-implementations** - Retrieves specific code implementations from outlines
- **lc-list-modified-files** - Shows files that have changed since a given timestamp

### Best Practices

- Use lc-project-context for initial understanding of repository structure
- Prefer lc-get-files for file content analysis over direct file access tools
- Use lc-code-outlines to understand code structure without implementation details
- Always check for modified files before updating documentation

## skogai-memory

The memory module provides persistent knowledge storage and retrieval across sessions.

### Key Functions

- **project_info** - Provides statistics about the memory project
- **recent_activity** - Shows recently created or modified notes
- **search_notes** - Finds relevant content across the knowledge base
- **read_note** - Retrieves specific notes by title or permalink
- **write_note** - Creates or updates markdown notes with semantic content
- **build_context** - Generates context from memory URIs for natural conversations

### Documentation Approach

The memory system supports the verification status system and placeholder approach:

- **Verification Status**
  - `[x]` - Hard verification by user, confirmed correct
  - `[/]` - Reasonable confidence but verify in critical contexts
  - `[ ]` - No verification, considered planning/suggestion
  - `[s]` - Waiting for user input

- **Placeholder Format**
  - `[PLACEHOLDER: reasoning based on context]` - Indicates uncertain information
  - `[TODO: specific task description]` - Marks explicit action items

This approach creates clear knowledge boundaries and distinguishes between verified information and assumptions.

## skogai-todo

The todo module provides structured task management for implementation tracking.

### Key Functions

- **task_create** - Creates new tasks with detailed information
- **task_list** - Lists tasks with optional filters
- **task_update** - Updates existing task properties
- **task_get** - Retrieves specific task details
- **task_delete** - Removes tasks from the system

### Task Structure

Each task contains:
- **Name** - Brief description of the task
- **Description** - Detailed explanation of requirements
- **Tags** - Categorization labels
- **Priority** - Importance level (low, medium, high)
- **Status** - Current state (active, completed, archived)
- **Progress** - Optional notes on current progress
- **Due Date** - Optional deadline

## skogai-planning

The planning module provides a structured approach to development planning.

### Key Functions

- **start_planning** - Initiates a new planning session with a goal
- **save_plan** - Stores the current implementation plan
- **add_todo** - Creates new planning tasks with complexity ratings
- **get_todos** - Retrieves all tasks in the current plan
- **update_todo_status** - Tracks task completion
- **remove_todo** - Removes tasks from the plan

### Planning Workflow

1. Start with a high-level goal
2. Document the objective, components, approach, and success metrics
3. Break down implementation into specific todos with detailed descriptions
4. Assign complexity scores (0-10) to each task
5. Track completion status as implementation progresses

## Integrated Workflow

These tools are designed to work together for a comprehensive architectural design experience:

1. **Understanding Phase**
   - Use skogai-context to understand project structure
   - Reference skogai-memory for existing documentation
   - Review skogai-todo for current tasks

2. **Planning Phase**
   - Use skogai-planning to structure architectural goals
   - Break down into manageable components
   - Define complexity and dependencies

3. **Documentation Phase**
   - Document architectural decisions in skogai-memory
   - Use verification status to track certainty
   - Connect documentation to implementation tasks

4. **Implementation Tracking**
   - Track progress with skogai-todo
   - Monitor file changes with skogai-context
   - Update documentation in skogai-memory

## Best Practices

- **Tool Prioritization**:
  1. Use skogai-context tools first for file operations
  2. Use BatchTool for multiple operations
  3. Fall back to basic tools only if specifically needed

- **Documentation Principles**:
  - Maintain clear verification status in all documentation
  - Use placeholders to indicate uncertainty
  - Focus on architectural concepts over implementation details
  - Create clear knowledge boundaries

- **Memory Management**:
  - Categorize notes logically by folder
  - Use consistent tagging for searchability
  - Maintain knowledge persistence across sessions
  - Update verification status as certainty improves

By leveraging these tools effectively, architects can maintain high-level understanding of systems without requiring implementation details, focusing on design patterns, interfaces, and architectural principles.