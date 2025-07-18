# code style rules (observed)

## shell scripts

### conventions
- use `#!/usr/bin/env bash` shebang
- always make scripts executable (`chmod +x`)
- use `printf` over `echo` for output
- pattern: `./update` with no file ending for "executable" files which are always named the same
- pattern: `./generate/` for "text output" files [@skogix:not so sure about this one]
- pattern: `.skogai/scripts/git/*.sh` for git flow operations

### context scripts structure
```bash
#!/usr/bin/env bash

printf "# section header\n"
command_output
```

### script pattern
- always append to with `>>` or `>`

### naming conventions
- scripts: `kebab-case.sh`

## git flow

### branch management
- [@todo:skogix]

## data flow

### context generation
- [@todo:skogix]

### file modifications
- [@todo:skogix:hooks]

## code principles

### simplicity first
- if you are not using a tool made for the problem or your "script" is not a one-liner you are *doing something wrong*
- composition and pipes are the way we do things

### functional approach
- small, single-purpose scripts
- composable via piping
- data transformations over control flow
