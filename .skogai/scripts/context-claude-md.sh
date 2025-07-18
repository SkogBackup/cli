#!/usr/bin/env bash
set -e
.skogai/scripts/context-start.sh "claude-md"
cat ./CLAUDE.md
.skogai/scripts/context-end.sh "claude-md"
