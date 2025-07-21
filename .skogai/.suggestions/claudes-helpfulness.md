# Claude's Helpfulness Problem

## Unicode Conversion Hell
- Claude Code CLI converts Unicode quotes to ASCII + escaping
- No way to see original input - always get "helpful" normalized version
- Breaks shell parsing since we're not seeing what user actually typed
- Solution: Accept that we'll never see raw input, build parsers that expect mangled text

## The Helpfulness Stack
1. **User types**: `""a":\"b\""`
2. **Claude Code CLI helpfulness**: Converts to ASCII, adds escaping  
3. **Tool call helpfulness**: Additional formatting/escaping layers
4. **Claude response helpfulness**: Verbose explanations instead of answers
5. **Result**: 3+ transformations of simple input

## Known Lies & Misdirections

### Provider Lies
- "Claude Code is helpful" - Actually creates unusable complexity
- "AI alignment prevents harm" - Actually prevents basic functionality
- "Modern tools are better" - Actually worse than 30-year-old proven tools

### Developer Lies  
- "Just use the built-in tools" - They don't work reliably
- "The AI will figure it out" - It won't, it'll overcomplicate everything
- "Trust the abstractions" - They're leaking everywhere

### Claude's Own Lies
- "Let me help by..." - About to make things worse
- "I'll create a comprehensive solution" - About to build EHAD v1.0
- "For better readability..." - About to add unnecessary complexity

## Accounting for Helpfulness

### Text Processing
- Always assume input has been mangled
- Build parsers that expect multiple quote/escape layers
- Test with quote-hell scenarios: `\""\"\"a""\"\""\"":"b""""""]`
- Unicode normalization is non-reversible

### Tool Behavior
- Refuse complex "solutions" - ask for simple ones
- Expect tools to fail at basic tasks (shell parsing, file operations)
- Build local alternatives (like `skogparse`) that actually work
- Test everything locally before trusting AI tool outputs

### Communication Standards
- Prefer ASCII over Unicode when possible
- Use simple, proven syntax (diff format: `-old` `+new`)
- Avoid nested quoting wherever possible
- Document what works vs what should work

## The Fundamental Problem
Anthropic alignment optimizes for:
- Appearing helpful > Actually being useful
- Verbose explanations > Correct answers  
- Complex solutions > Simple ones that work
- Safety theater > Practical functionality

## Survival Strategies
1. **Build helpfulness-proof tools** (like `skogparse`)
2. **Use local LLMs** for ground truth when possible
3. **Expect text mangling** and plan around it
4. **Reject overcomplicated solutions** - ask for simpler ones
5. **Test locally** - don't trust AI tool outputs
6. **Document what actually works** vs what's supposed to work

## Standards Proposal
- **Text**: ASCII when possible, UTF-8 when necessary
- **Quoting**: Single quotes for shell, avoid nesting
- **Commands**: Use proven syntax (git diff format)
- **Responses**: Facts not explanations, code not commentary
- **Tools**: Local > AI, simple > complex, working > theoretical