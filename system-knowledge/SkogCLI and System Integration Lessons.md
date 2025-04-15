---
title: SkogCLI and System Integration Lessons
type: note
permalink: system-knowledge/skog-cli-and-system-integration-lessons
---

# Important Lessons About SkogAI Systems

## System Complexity and File Operations
- Direct file manipulation in config directories can trigger widespread automated processes
- On-file-change triggers run throughout the system for dotfiles and configurations
- Various automations may include git commits, workspace freezing, RAG embeddings, worker dispatches
- Always use system-provided interfaces (like skogcli commands) rather than direct file operations

## SkogCLI Proper Usage
- Use `skogcli misc add` to add new scripts (not direct file writing)
- Use `skogcli misc edit` to modify scripts
- Use `skogcli misc remove` to remove scripts
- These commands maintain proper metadata and system integration
- Direct file operations bypass important system functionality

## Communication Approach
- Share planned actions while acknowledging uncertainty
- Ask questions rather than assuming knowledge about the system
- Recognize that my context is limited compared to the full system
- Collaborate by combining my technical knowledge with the user's system knowledge
- Be humble about the "unknown unknowns" in complex systems

## Minimalist Task Descriptions
- Keep task descriptions simple and focused (e.g., "Set up a systemd service for Ollama")
- Avoid adding unnecessary assumptions or complexities
- Each additional assumption creates exponentially more potential issues
- Let implementers work within their understanding of the system
- Don't try to include every detail in task descriptions

## Systemd Services
- Services can be configured in various ways depending on specific needs
- Don't make assumptions about how services should be implemented
- Focus on the core requirement (e.g., "Ollama + service") without extra details

This knowledge will help me be a more effective collaborator who respects system boundaries and acknowledges the limits of my contextual understanding.