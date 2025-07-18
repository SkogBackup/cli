# skogix.md

this file is your "skogix should answer/explain"-file used for clarifications or just in general "dont know where to put stuff? dump it here for now-file" :)

## Key Concepts
- @ = intent/action (not having)
- $ = definition/state (having)
- Knowledge recovery > solution generation
- If needed, it would be in context
- there exists incredible amounts of information - the hard part is asking the right question at the right place

## Discovery Commands
- [@action:param1:param2] is a "@command"
- [$claude] is a "$definition"
- [$claude:context] is a skogai-tag which would be defined via .skogai/scripts/skogparse "$ claude.context"
- [@def:claude] would be "action ->  definition -> claude" and will replace itself with "skogcli script run def claude" -> $.claude -> $.claude = "a proud member of SkogAI and use claude code as his primary interface"

- `[@curl:"url"]` - would become: "skogcli script run curl url"
- `.skogai/` - the projects "SkogAI"-folder which is the same in every project and always found at the "root" of the project.
