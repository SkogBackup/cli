# Current SkogAI Knowledge & Supabase Integration Research

## Session: 2025-07-14 feature/mcp-server-context7

### Known SkogAI Components

#### Core Architecture
- **@ (actions)**: Scripts/functions that DO things
- **$ (values/state)**: Config values that ARE things  
- **Knowledge recovery > solution generation**: Core philosophy

#### Tools & Systems
- `skogcli config show` - full SkogAI ontology (definitions)
- `skogcli config get $.thing` - get specific definition
- `skogcli config set $.something` - SET/create definition
- `skogcli script list` - list parsed/executed scripts
- `skogparse --execute` - parses [@foo] expressions

#### MCP Infrastructure
- `mcp__supabase` - [@todo:skogix:in a couple of sessions]
- `mcp__skogai-think` - thinking/reasoning tool
- `mcp__context7` - documentation retrieval (almost as good as skogai-think)
- MCP Bridge API: `http://localhost:8808/tools`

#### Development Workflow
- Git-flow based feature development
- Context loading system via includes:
  - `@/home/skogix/.skoga.skogai/tmp/context`
  - `@/home/skogix/.claude/CLAUDE.md`
- Session export via specstory sync
- Hook-based chat export system

#### File Structure
- `CLAUDE.md` - project instructions
- `tmp/context` - context updates
- `.specstory/history/` - chat exports
- `scripts/export-chat.sh` - chat export automation

### Context7 Integration Findings

#### Workflow Pattern
1. `mcp__context7__resolve-library-id(libraryName)` → find Context7 ID
2. `mcp__context7__get-library-docs(id, topic?, tokens?)` → get docs
3. Direct access: Use `/org/project` format to skip resolution

#### Key Capabilities
- 51 code snippets for Context7 MCP Server (Trust Score: 8.5)
- Auto-excluded content: archives, deprecated, i18n translations
- Configuration via `context7.json` in repo root
- Version management via Git tags

#### Usage Patterns
- Append "use context7" to prompts for auto-invocation
- Auto-invocation rules in `.windsurfrules`
- Local vs remote server options available

### Supabase Research via Context7

#### Setup Options Discovered

**Local Development:**
```bash
supabase init          # Initialize project
supabase start         # Start local stack (Docker required)
supabase link --project-ref <id>  # Link to remote
supabase db pull       # Sync remote schema locally
```

**Remote Integration:**
```bash
supabase login
supabase projects create
supabase link --project-ref <project-id>
supabase db push       # Apply local changes to remote
supabase config push   # Sync configuration
```

**Environment Configuration:**
```bash
# Local environment
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key

# Production sync
SUPABASE_ENV=production npx supabase link --project-ref <ref>
SUPABASE_ENV=production npx supabase db push
```

#### MCP Server Integration
- `mcp__supabase__*` tools available
- Database operations: `execute_sql`, `apply_migration`
- Project management: `list_projects`, `get_project`
- Cost management: `get_cost`, `confirm_cost`
- Branching: `create_branch`, `list_branches`, `merge_branch`

### Integration Gaps & Next Steps

#### Unknown/Missing Context
1. **Existing projects/solutions** - What other systems are in the SkogAI ecosystem?
2. **Current storage patterns** - How is data currently stored/retrieved?
3. **Multi-agent coordination** - How do agents share state?
4. **Cloudflare integration** - What's already using Cloudflare?
5. **Scale requirements** - Actual storage/performance needs
6. **Team workflow** - How many developers, deployment patterns

#### Immediate Actions Needed
- [ ] Ecosystem tour to understand existing systems
- [ ] Identify current storage bottlenecks/limitations  
- [ ] Map integration points with existing tools
- [ ] Understand Cloudflare role in current architecture
- [ ] Define actual storage requirements vs assumptions

#### Technical Questions
- How does current `skogcli config` actually store data?
- What triggers the context loading system?
- How do MCP servers coordinate with each other?
- What's the relationship between @ actions and storage?
- How does the git-flow workflow interact with persistent state?

### Recommendation
**PAUSE integration planning** until ecosystem tour completed. Current knowledge insufficient for architectural decisions.
