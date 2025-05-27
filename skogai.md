# SKOGAI Project Summary

*This document provides comprehensive information about the SKOGAI project for AI agents to understand its purpose, components, and functionality. It is designed to help AI systems quickly grasp the project's architecture and intended use when working with SKOGAI.*

## Project Overview

SKOGAI is a comprehensive knowledge management and AI agent interaction system. It provides a command-line interface (SkogCLI) for managing knowledge bases, configuring and interacting with AI agents, and extending functionality through custom scripts. The system is designed to help users efficiently organize information, retrieve knowledge, and leverage AI capabilities through a consistent interface.

## Key Components

### 1. Knowledge Management System

The `memory` component provides a sophisticated knowledge base management system. It allows users to:
- Create, read, update notes in a structured format
- Organize information in folders
- Search across knowledge content
- Tag and categorize information
- Track recent activity
- Synchronize knowledge between local files and a database

### 2. Agent Framework

The `agent` component enables interaction with AI agents. Features include:
- Creating and configuring agents with different models and system prompts
- Sending messages to agents and receiving responses
- Managing agent configurations
- Customizing agent behaviors through scripts

### 3. Script Management

The `script` module provides an extensibility framework for custom functionality:
- Creating, editing, running custom scripts (Python or shell)
- Importing and exporting scripts
- Generating scripts using AI
- Searching and transforming script content
- Using templates for script creation

### 4. Configuration Management

The `config` component allows users to customize system behavior:
- Viewing and editing configuration values
- Creating and restoring backups
- Managing chat history
- Resetting to default configurations

## Technical Architecture

### Data Structure

The system organizes knowledge in a hierarchical structure:
- Projects can contain multiple knowledge bases
- Knowledge is organized into folders
- Individual notes have titles, content, and metadata (tags, timestamps, etc.)

### Command Structure

SKOGAI uses a nested command structure following the pattern:
```
skogcli [component] [command] [arguments] [options]
```

For example:
```
skogcli memory search "project ideas" --title --after-date "1 week"
```

### Integration Points

- Database synchronization for knowledge persistence
- External editor integration for content creation
- AI model integration (supporting various models)
- File system integration for importing/exporting data

## Usage and Workflow

### Knowledge Management Workflow

1. **Creating Knowledge**: Users add notes to their knowledge base using commands like:
   ```
   skogcli memory create "My Note" notes --content "# My Note\n\nThis is my note content."
   ```

2. **Finding Information**: Users search across their knowledge base:
   ```
   skogcli memory search "project ideas"
   ```

3. **Browsing Recent Activity**: Users can see what's changed recently:
   ```
   skogcli memory list --timeframe 7d
   ```

4. **Synchronizing Knowledge**: Users sync knowledge with the database:
   ```
   skogcli memory sync
   ```

### Agent Interaction Workflow

1. **Creating an Agent**:
   ```
   skogcli agent create researcher --model gpt-4 --system "You are a helpful research assistant."
   ```

2. **Sending Messages to Agents**:
   ```
   skogcli agent send "What is the capital of France?" --agent researcher
   ```

3. **Managing Agent Configuration**:
   ```
   skogcli agent set model gpt-4-turbo --agent researcher
   ```

### Script Management Workflow

1. **Creating Scripts**:
   ```
   skogcli script create analyze_data --type python --description "Analyze data from notes"
   ```

2. **Running Scripts**:
   ```
   skogcli script run analyze_data --arg1 value1
   ```

3. **Generating Scripts with AI**:
   ```
   skogcli script generate data_processor "Process CSV data and extract key insights"
   ```

## APIs and Dependencies

The system likely integrates with several external components:

1. **LLM Provider APIs**: 
   - The agent functionality suggests integration with language model APIs (such as OpenAI's GPT models)
   - Support for different models indicates possible multi-provider support

2. **Database Systems**:
   - The sync functionality suggests a backend database for knowledge persistence
   - Project management features indicate structured data storage

3. **File System Integration**:
   - Local file management for notes and scripts
   - Import/export capabilities for data portability

4. **External Editors**:
   - Support for opening content in external editors
   - Integration with system's default editor through environment variables

## For AI Agents: Working with SKOGAI

When interacting with SKOGAI as an AI agent, consider:

1. **Command Structure**: SKOGAI uses a consistent command pattern of `skogcli [component] [command] [arguments] [options]`

2. **Knowledge Structure**: Information is organized in projects, folders, and notes with metadata

3. **Script Extensions**: The system is extensible through custom scripts that can be generated, edited, and executed

4. **Configuration Management**: System behavior can be customized through configuration parameters
