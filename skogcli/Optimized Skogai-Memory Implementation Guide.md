---
title: Optimized Skogai-Memory Implementation Guide
type: note
permalink: development/optimized-skogai-memory-implementation-guide
---

# Optimized Skogai-Memory Implementation Guide

This document outlines a streamlined approach to implementing the skogai-memory extension with a simplified command structure that maintains all functionality while improving usability.

## Proposed Command Structure

### 1. `note` Command (Unified CRUD Operations)

```typescript
// Function signature
function note(operation: "create" | "read" | "update" | "delete", params: NoteParams): NoteResult

// Parameter interface
interface NoteParams {
  // Common parameters
  identifier?: string;     // Required for read, update, delete (title or permalink)
  
  // For create/update
  title?: string;          // Required for create
  content?: string;        // Required for create/update
  folder?: string;         // Required for create
  tags?: string[];         // Optional
  
  // Pagination (for read)
  page?: number;           // Optional, defaults to 1
  page_size?: number;      // Optional, defaults to 10
  
  // For raw content reading
  raw?: boolean;           // Optional, if true treats the note as raw content
}

// Result interface
interface NoteResult {
  success: boolean;
  message: string;
  data?: {
    content?: string;
    metadata?: {
      title: string;
      folder: string;
      tags?: string[];
      permalink: string;
      checksum: string;
      created_at: string;
      updated_at: string;
    }
  }
}
```

**Implementation Notes:**
- This unified command replaces `write_note`, `read_note`, `read_content`, and `delete_note`
- The `raw` parameter determines whether to treat the content as formatted markdown or raw content
- Pagination parameters are only used for read operations
- Comprehensive error handling should provide clear feedback on missing required parameters

### 2. `search` Command (Simplified)

```typescript
// Function signature
function search(query: string, options?: SearchOptions): SearchResult

// Options interface
interface SearchOptions {
  search_type?: "text" | "semantic" | "hybrid";  // Defaults to "hybrid"
  content_types?: string[];                      // Filter by content types
  entity_types?: string[];                       // Filter by entity types if applicable
  date_range?: {
    after?: string;                              // ISO date or natural language
    before?: string;                             // ISO date or natural language
  };
  page?: number;                                 // Default: 1
  page_size?: number;                            // Default: 10
}

// Result interface
interface SearchResult {
  hits: Array<{
    title: string;
    permalink: string;
    snippet: string;
    score: number;
    created_at: string;
    updated_at: string;
  }>;
  total: number;
  page: number;
  page_count: number;
}
```

**Implementation Notes:**
- Simplified from the current `search_notes` with more intuitive parameter names
- Adds a date range concept rather than just "after_date"
- Defaults to a hybrid search approach (combining text and semantic)

### 3. `context` Command (Combined Contextual Retrieval)

```typescript
// Function signature
function context(options?: ContextOptions): ContextResult

// Options interface
interface ContextOptions {
  mode: "uri" | "recent" | "related";             // Default: "recent"
  uri?: string;                                   // Required for uri mode
  timeframe?: string;                             // Natural language or standard format
  content_types?: string[];                       // Filter by content types
  reference_content?: string;                     // Text to find related content for
  depth?: number;                                 // Default: 1
  max_related?: number;                           // Default: 10
  page?: number;                                  // Default: 1
  page_size?: number;                             // Default: 10
}

// Result interface
interface ContextResult {
  items: Array<{
    title: string;
    permalink: string;
    content: string;
    created_at: string;
    updated_at: string;
    relevance?: number;                           // Only for related mode
  }>;
  total: number;
  context_summary?: string;                       // Optional natural language summary
}
```

**Implementation Notes:**
- Combines functionality from `build_context` and `recent_activity`
- Adds a new "related" mode that can find content related to provided reference text
- The `mode` parameter determines which other parameters are required
- Timeframe supports natural language (e.g., "2 days ago", "last week") or standard formats (e.g., "7d")

### 4. `canvas` Command (Simplified Parameters)

```typescript
// Function signature
function canvas(title: string, folder: string, elements: CanvasElements): CanvasResult

// Elements interface
interface CanvasElements {
  nodes: Array<{
    id: string;
    type: "text" | "file" | "link" | "image";
    content: string;
    position: { x: number, y: number };
    size?: { width: number, height: number };
    color?: string;
  }>;
  edges: Array<{
    from: string;        // Node ID
    to: string;          // Node ID
    label?: string;
    style?: "solid" | "dashed" | "dotted";
    color?: string;
  }>;
}

// Result interface
interface CanvasResult {
  success: boolean;
  file_path: string;
  permalink: string;
}
```

**Implementation Notes:**
- Maintains core canvas functionality but with more intuitive parameter structure
- Simplifies node and edge definitions
- Provides sensible defaults for optional styling parameters

### 5. `info` Command (System Information)

```typescript
// Function signature
function info(): SystemInfo

// Result interface
interface SystemInfo {
  stats: {
    total_notes: number;
    total_folders: number;
    storage_used: string;
    last_updated: string;
  };
  capabilities: string[];
  version: string;
}
```

**Implementation Notes:**
- Maintains the existing functionality of `project_info`
- Adds version information and explicit capabilities list
- Keeps the command simple with no required parameters

## Migration Strategy

1. **Implement New Commands**: Build the new command structure while maintaining backward compatibility with the original commands
2. **Deprecation Warnings**: Add deprecation notices to old commands that inform users of the new alternatives
3. **Documentation**: Create comprehensive documentation for the new command structure with examples
4. **Gradual Phase-Out**: Eventually phase out the old commands after sufficient adoption of the new structure

## Best Practices for Integration

1. **Consistent Error Handling**: Provide clear, actionable error messages
2. **Sensible Defaults**: All optional parameters should have reasonable default values
3. **Progressive Disclosure**: Make basic operations simple while allowing advanced options
4. **Type Safety**: Use strong typing to prevent runtime errors
5. **Command Discoverability**: Implement help/info mechanisms to make commands and their options discoverable

## Future Enhancements

1. **Bulk Operations**: Add support for batch processing multiple notes
2. **Templating**: Support note templates for consistent content creation
3. **Versioning**: Track content versions and changes
4. **Collaborative Features**: Add collaboration capabilities with permissions
5. **Enhanced Analytics**: Provide insights on knowledge base usage and growth

This implementation guide should provide a clear roadmap for developing a more intuitive and powerful interface to the skogai-memory extension while maintaining all existing functionality.