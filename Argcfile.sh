#!/usr/bin/env bash

set -e

# @describe SkogCLI src commands
# @meta version 1.0.0
# @meta dotenv .env
# @env LLM_OUTPUT=/dev/stdout The output path

# @cmd
# @arg args~  Capture all remaining args
run() {
  uv run skogcli "${argc_args[@]}"
}

# @cmd
install() { :; }

# @cmd
install::dev() { :; }

# @cmd
build() { :; }

# @cmd
clean() { :; }

# @cmd
format() { :; }

# @cmd
format::lint() { :; }

# @cmd
format::mypy() { :; }

eval "$(argc --argc-eval "$0" "$@")"
