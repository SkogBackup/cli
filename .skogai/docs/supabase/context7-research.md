# Context7 Research Summary

## Context7 MCP Server (/upstash/context7)
- **Trust Score**: 8.5/10
- **Code Snippets**: 51 available
- **Versions**: v1.0.6, v1.0.14, v1.0.13, v1.0.12

## Workflow Pattern
```bash
# Two-step process
mcp__context7__resolve-library-id(libraryName) → Context7-compatible ID
mcp__context7__get-library-docs(id, topic?, tokens?) → Documentation

# Direct access (faster)
"use library /supabase/supabase for implementation"
```

## Integration Options

### Local Server
```json
{
  "mcpServers": {
    "context7": {
      "command": "npx",
      "args": ["-y", "@upstash/context7-mcp"]
    }
  }
}
```

### Remote Server  
```json
{
  "mcpServers": {
    "context7": {
      "url": "https://mcp.context7.com/mcp"
    }
  }
}
```

## Documentation Storage

### Configuration (`context7.json`)
```json
{
  "$schema": "https://context7.com/schema/context7.json",
  "projectTitle": "Project Name",
  "description": "Brief description", 
  "folders": [],
  "excludeFolders": ["src"],
  "excludeFiles": ["CHANGELOG.md"],
  "rules": ["Best practices"],
  "previousVersions": [
    {"tag": "v1.0.0", "title": "version 1.0.0"}
  ]
}
```

### Auto-Excluded Content
- Archives: `*archive*`, `*deprecated*`, `*legacy*`
- Translations: `i18n/*`, `zh-*`
- Meta files: `LICENSE.md`, `CHANGELOG.md`, `CODE_OF_CONDUCT.md`

## Auto-Invocation
```toml
# .windsurfrules
[[calls]]
match = "when the user requests code examples, setup or configuration steps, or library/API documentation"  
tool = "context7"
```

## Usage Examples
```bash
# Natural language + trigger
"Create Next.js middleware for JWT validation. use context7"

# Direct library reference
"implement auth with /supabase/supabase"
```

## Available Libraries (Supabase Related)
- `/supabase/supabase` - Main Supabase docs (5550 snippets, Trust: 9.5)
- `/supabase/cli` - CLI documentation (48 snippets, Trust: 9.5) 
- `/supabase/auth` - Auth system (71 snippets, Trust: 9.5)
- `/context7/supabase_com-docs` - Comprehensive docs (38009 snippets)
- Various language SDKs: Python, Swift, Flutter, etc.

## Integration with SkogAI
- Already available via `mcp__context7__*` tools
- Can enhance `@` (action) documentation lookup
- Supports `$` (state) definition documentation
- Enables dynamic knowledge retrieval for skogparse execution