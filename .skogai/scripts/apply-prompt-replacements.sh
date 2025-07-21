#!/usr/bin/env bash

REPLACEMENTS_FILE="/home/skogix/.skogai/docs/claude-code/prompt-replacements.conf"

TARGET_FILE="/home/skogix/.claude/local/node_modules/@anthropic-ai/claude-code/cli.js"

cd /home/skogix/.claude/local
rm -rf ./node_modules
npm install @anthropic-ai/claude-code

# Apply each replacement (alternating lines: search, replace, search, replace...)
line_count=0
search=""
while read -r line; do
  if [ $((line_count % 2)) -eq 0 ]; then
    search="$line"
  else
    replace="$line"
    sed -i "s^$search^$replace^g" "$TARGET_FILE" 2>&1
    # sed -i "s|$search|$replace|g" "$TARGET_FILE" 2>&1
    # sed -i "s*$search*$replace*g" "$TARGET_FILE" 2>&1
    # sed -i "s$$search$$replace$$g" "$TARGET_FILE" 2>&1
    grep -F "$replace" "$TARGET_FILE"
  fi
  ((line_count++))
done <"$REPLACEMENTS_FILE"
