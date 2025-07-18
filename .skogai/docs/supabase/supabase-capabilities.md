# Supabase Capabilities Research

## Setup Approaches

### Local Development
```bash
# Basic setup
supabase init                     # Initialize project
supabase start                    # Start local stack (Docker)
supabase link --project-ref <id>  # Link to remote

# Schema management
supabase db pull                  # Pull remote schema
supabase db push                  # Push local changes
supabase db diff                  # Generate migration
```

### Remote Production
```bash
# Authentication & setup
supabase login
supabase projects create
supabase link --project-ref <project-id>

# Configuration sync
SUPABASE_ENV=production supabase config push
SUPABASE_ENV=production supabase db push
```

### Environment Variables
```bash
# Local development
SUPABASE_URL=your-supabase-url
SUPABASE_ANON_KEY=your-supabase-anon-key

# Production/staging
SUPABASE_ENV=production
```

## Available MCP Tools

### Project Management
- `mcp__supabase__list_projects` - List all projects
- `mcp__supabase__get_project` - Get project details
- `mcp__supabase__create_project` - Create new project
- `mcp__supabase__pause_project` - Pause project
- `mcp__supabase__restore_project` - Restore project

### Database Operations
- `mcp__supabase__execute_sql` - Run SQL queries
- `mcp__supabase__apply_migration` - Apply DDL migrations
- `mcp__supabase__list_tables` - List database tables
- `mcp__supabase__list_migrations` - List migration history

### Branching & Development
- `mcp__supabase__create_branch` - Create development branch
- `mcp__supabase__list_branches` - List all branches
- `mcp__supabase__merge_branch` - Merge branch to production
- `mcp__supabase__delete_branch` - Delete branch
- `mcp__supabase__reset_branch` - Reset branch migrations
- `mcp__supabase__rebase_branch` - Rebase on production

### Cost Management
- `mcp__supabase__get_cost` - Get creation costs
- `mcp__supabase__confirm_cost` - Confirm cost acceptance

### Monitoring & Admin
- `mcp__supabase__get_logs` - Fetch service logs
- `mcp__supabase__get_advisors` - Security/performance advisors
- `mcp__supabase__get_project_url` - Get API URL
- `mcp__supabase__get_anon_key` - Get anonymous key

### Edge Functions
- `mcp__supabase__list_edge_functions` - List functions
- `mcp__supabase__deploy_edge_function` - Deploy function

### Type Generation
- `mcp__supabase__generate_typescript_types` - Generate types

## CLI Installation Options

### npm/yarn
```bash
npm install supabase --save-dev
yarn add supabase --dev
```

### System Package Managers
```bash
# macOS
brew install supabase/tap/supabase

# Linux
sudo dpkg -i supabase_linux_amd64.deb
sudo rpm -i supabase_linux_amd64.rpm

# Windows  
scoop bucket add supabase https://github.com/supabase/scoop-bucket.git
scoop install supabase
```

### Go Install
```bash
go install github.com/supabase/cli@latest
```

## Key Features for SkogAI Integration

### Real-time Capabilities
- WebSocket subscriptions for live data
- Real-time collaboration support
- Event-driven updates

### Authentication & Security
- Row Level Security (RLS)
- Anonymous access for development
- Service role for system operations
- Third-party auth providers

### Edge Functions
- Deno-based serverless functions
- Custom business logic
- Database triggers
- Webhook handling

### Storage
- File upload/download
- Image transformations
- CDN integration
- Bucket management

### Database Features
- PostgreSQL with extensions
- Full-text search
- JSON/JSONB support
- Triggers and functions
- Connection pooling

## Development Workflow Integration

### Git-flow Compatible
```bash
# Feature branch workflow
git flow feature start database-schema
supabase migration new add_new_table
# Edit migration file
supabase db reset  # Test migration
git flow feature finish database-schema
```

### Environment Management
```bash
# Development
supabase start

# Staging branch
supabase create_branch staging
supabase link --project-ref staging-ref

# Production
supabase link --project-ref production-ref
supabase db push
```

## Configuration Files

### config.toml
```toml
[api]
port = 54321

[db]
port = 54322

[auth]
enable_anonymous_sign_ins = true

[auth.external.github]
enabled = true
client_id = "env(GITHUB_CLIENT_ID)"
secret = "env(GITHUB_SECRET)"
```

### Environment Files
```bash
# .env.local
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=eyJ...

# .env.production  
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
```