#!/usr/bin/env bash
set -e
.skogai/scripts/context-start.sh "definitions"
cat .skogai/docs/definitions.md
.skogai/scripts/context-end.sh "definitions"
