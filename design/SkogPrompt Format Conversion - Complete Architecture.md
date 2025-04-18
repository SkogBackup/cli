---
title: SkogPrompt Format Conversion - Complete Architecture
type: note
permalink: design/skog-prompt-format-conversion-complete-architecture
---

# SkogPrompt Format Conversion - Complete Architecture

## Overview [/]

This document outlines the complete architecture for the format conversion system within SkogPrompt, inspired by the `/home/skogix/skogchat/scripts/convert` scripts. The system is designed to provide bidirectional conversion between different AI platform formats while preserving special message elements and metadata.

## Core Components [ ]

### 1. Format Registry [PLACEHOLDER: Based on file system patterns seen in convert directory]

The Format Registry maintains information about supported formats and their converters.

#### Key Functionality
- Registration of supported formats
- Discovery of format converters
- Format capabilities and limitations
- Validation rules for each format

#### Implementation Considerations
- Use a plugin architecture for extensibility
- Support automatic discovery of new formats
- Include metadata about format capabilities
- Implement version tracking for formats

### 2. Message Model [ ]

The Message Model provides a unified internal representation for chat messages across different formats.

#### Key Functionality
- Abstract representation of messages and conversations
- Support for different message types (user, system, assistant)
- Handling of special elements (tool calls, functions, etc.)
- Metadata preservation across conversions

#### Implementation Considerations
- Design for extensibility as new message types emerge
- Create a normalized internal format
- Include schema validation
- Support for custom properties

### 3. Format Converters [ ]

Format Converters transform between the internal message model and platform-specific formats.

#### Key Functionality
- Parsing platform-specific formats into internal model
- Rendering internal model to platform-specific formats
- Handling platform-specific features and limitations
- Error detection and recovery

#### Implementation Considerations
- Implement bidirectional conversion for each format
- Handle edge cases gracefully
- Include comprehensive validation
- Support for format-specific optimizations

### 4. Conversion Pipeline [ ]

The Conversion Pipeline orchestrates the entire conversion process.

#### Key Functionality
- Format detection and selection
- Pre-processing and validation
- Conversion execution
- Post-processing and validation
- Error handling and reporting

#### Implementation Considerations
- Design as a configurable pipeline
- Support for batch and streaming conversion
- Include hooks for custom processing
- Implement comprehensive logging

## Supported Formats [PLACEHOLDER: Based on observed scripts]

Initial support will include the following formats:

1. **Claude**
   - System messages at beginning
   - Human/Assistant turn-taking
   - Tool call support
   - Metadata handling

2. **OpenAI**
   - GPT-style message arrays
   - Function/tool calling conventions
   - System message support
   - Response formatting options

3. **SillyTavern**
   - Character-based formatting
   - History management
   - Special delimiters and markers
   - Metadata and tags

4. **Markdown**
   - Human-readable format
   - Special annotations for message types
   - Front matter for metadata
   - Conversion annotations

5. **JSON**
   - Standard format for programmatic use
   - Complete metadata preservation
   - Full structure representation
   - Compatibility with most systems

## Data Flow

The conversion flow follows these steps:

1. **Format Detection**
   - Input is analyzed to determine format
   - Format-specific parser is selected

2. **Parsing to Internal Model**
   - Format-specific parser converts to internal model
   - Validation ensures correctness
   - Metadata is preserved

3. **Transformation**
   - Optional transformations are applied
   - Message filtering or modification
   - Metadata adjustments

4. **Rendering to Target Format**
   - Target format converter is selected
   - Internal model is rendered to target format
   - Format-specific optimizations are applied

5. **Validation**
   - Output is validated for correctness
   - Format-specific rules are checked
   - Error reporting if issues are found

## Format-Specific Considerations

### Claude Format [/]

Claude uses a simple text-based format with clear role indicators:

```
Human: [Human message content]