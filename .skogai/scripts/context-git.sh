#!/usr/bin/env bash
set -e
.skogai/scripts/context-start.sh "git"
# git branch --show-current
# git status --porcelain
printf "## Git-Flow features\n"
git-flow feature
git-flow feature diff
printf "## Git-Status\n"
git status --short
printf "## Git-Diff Cached (or in other words: skogix changed this crap and want your input:\n"
git diff --cached
printf "## Git-Diff (or in other words: you did not commit claude! bad git hygiene! <3\n"
# git diff --stat
# git diff HEAD^ HEAD --full-index
.skogai/scripts/context-end.sh "git"
