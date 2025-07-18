# .skogai

.skogai is a folder which SkogAI have in every project root and contains the "shared tools, knowledge and experience of everything SkogAI" 

## .skogai

./update updates ".skogai/tmp/context which gives claude the context needed via hooks

## startup checks

skogix will probably open with "hello claude". please help him out by stating the current context as well as checking so your context contains what you need - otherwise you MUST inform skogix so it can get fixed.

### context tags

these should be included and 

- `[$claude:context]` - context container
- `[$claude:context:readme]` - project overview and context baseline
- `[$claude:context:git]` - version control information/state
- `[$claude:context:user]` - users/skogix self-made profile and communication patterns
- `[$claude:context:skogix]` - users/skogix comments and FAQ section
- `[$claude:context:workspace]` - project file tree structure which shows the relevant files only
- `[$claude:context:definitions]` - definitions and terms specific to the project

each section should have `timestamp` to let claude reason about the "freshness" of the data as well
