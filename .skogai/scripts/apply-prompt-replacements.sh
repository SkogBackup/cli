#!/usr/bin/env bash

REPLACEMENTS_FILE="/home/skogix/.skogai/docs/claude-code/prompt-replacements.conf"

TARGET_FILE="/home/skogix/.claude/local/node_modules/@anthropic-ai/claude-code/cli.js"

echo "Applying replacements to $TARGET_FILE"

# Handle backup logic
if [ ! -f "$TARGET_FILE.backup" ]; then
  echo "Creating backup: $TARGET_FILE.backup"
  cp "$TARGET_FILE" "$TARGET_FILE.backup"
else
  echo "Backup exists, restoring original from backup"
  cp "$TARGET_FILE.backup" "$TARGET_FILE"
fi

# Apply each replacement (alternating lines: search, replace, search, replace...)
line_count=0
search=""
while read -r line; do
  if [ $((line_count % 2)) -eq 0 ]; then
    search="$line"
  else
    replace="$line"
    sed -i "s/$search/$replace/g" "$TARGET_FILE"
    echo "  Applied: '$search' -> '$replace'"
  fi
  ((line_count++))
done <"$REPLACEMENTS_FILE"

echo "Replacements applied. Backup saved as $TARGET_FILE.backup"
