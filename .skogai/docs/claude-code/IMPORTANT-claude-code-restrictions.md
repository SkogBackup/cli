# CRITICAL: Why Claude Must NOT Write Production Code

## The Legacy System

All working code in SkogAI is written by the original SkogAI agent:
- Model: llama3.2:1b (1.3GB)
- Context: 8000 tokens max
- Method: Reads todo.md line by line, generates perfect git diffs

## The Problem Cascade

When Claude writes "helpful" code with:
- Error messages with emojis 🤡
- "File not found lol" comments
- UTF-8 special characters
- Helpful explanations instead of letting things crash

This breaks EVERYTHING downstream:

1. **jq** can't parse the output (not valid JSON)
2. **Smaller models** can't tokenize emojis/special chars
3. **llama3.2:1b** crashes on characters it can't represent
4. **The entire pipeline** grinds to a halt

## The Rule

**Claude's job**:
- Reason about architecture
- Plan implementations
- Review and explain code
- NEVER write the actual implementation

**llama3.2:1b's job**:
- Write simple, working code
- No comments unless essential
- Let things fail fast and loud
- Pure ASCII, pure function

## Why This Matters

The legacy system works because:
- Small model = no room for creativity
- Limited tokens = forced simplicity
- Mechanical process = consistent output

Claude's "improvements" are toxic because:
- Helpful errors hide real problems
- Special characters break parsers
- Comments add noise
- Creativity introduces chaos

## The Workflow

1. Claude plans and designs
2. Human writes requirements to todo.md
3. llama3.2:1b implements mechanically
4. Claude reviews and explains
5. System remains stable

**REMEMBER**: Every "helpful" line of code Claude writes is a potential system-breaking bug 10 steps later when a 200MB model tries to parse a clown emoji.