# handover

Why "Stupid Files as Middle Man"

Files are the universal interface for distributed AI collaboration.

The core problem: AI assistants feel local but are actually remote, working on cached copies that must sync across:
- Local machine (skogix) ↔ Anthropic's cache (Claude)
- Git operations ↔ Context system
- Multiple agents ↔ Shared state
- Hook system ↔ @ notification system

Files solve this because:
- Every system can read/write files
- Git natively handles file versioning/branching
- Hooks can monitor file changes
- Caching systems sync file states
- Multiple agents coordinate via shared file state

What .skogai Does

.skogai creates a shared workspace where humans and AI collaborate naturally despite being distributed.

It's the standard interface for:
- ./update → Real-time context syncing
- .skogai/scripts/ → @ notation command routing
- ./hooks/ → Event-driven updates
- .skogai/tmp/ → Inter-process communication
- .skogai/docs/ → Shared knowledge base

The genius: Files bridge the gap between "feels local" and "actually distributed" - making remote AI assistants work like local tools while maintaining git compatibility and
multi-agent coordination.
