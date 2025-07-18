Plan: Add New Context Section Process

Based on the existing context system architecture, here's the standardized process for adding a new context section:

Steps to Add a New Context Section

1. Create context script - Create .skogai/scripts/context-{name}.sh with:
  - .skogai/scripts/context-start.sh "{name}" - Adds [@claude:context:{name}](generated: timestamp)
  - Content generation logic (cat file, run command, etc.)
  - .skogai/scripts/context-end.sh "{name}" - Adds [@/claude:context:{name}]
2. Add to update script - Edit .skogai/scripts/update to include:
  - .skogai/scripts/context-{name}.sh >>tmp/context in the desired order
3. Update README.md baseline - Add new tag to Expected Context Tags:
  - [@claude:context:{name}] - Description of what this section contains
4. Test the integration - Run ./update to verify:
  - New section appears in context with timestamp
  - All expected sections still present
  - Context system remains functional
5. Commit changes - Add the new script and updated files to git

Example Structure Pattern:

# scripts/context-example.sh
#!/usr/bin/env bash
.skogai/scripts/context-start.sh "example" 
echo "Example content here"
.skogai/scripts/context-end.sh "example"

This follows the modular pattern where each context section is self-contained and the update script orchestrates the assembly. The README.md serves as the single source of truth for 
what constitutes complete context.
