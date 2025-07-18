#!/usr/bin/env bash
.skogai/scripts/context-start.sh "user"
cat .skogai/docs/user.md
.skogai/scripts/context-end.sh "user"
.skogai/scripts/context-start.sh "skogix"
cat .skogai/docs/skogix.md
.skogai/scripts/context-end.sh "skogix"
