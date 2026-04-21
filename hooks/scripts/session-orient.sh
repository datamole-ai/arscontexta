#!/bin/bash
# Ars Contexta — Session Orientation Hook
# Injects workspace structure, identity, and inbox maintenance signals at session start.

# Only run in Ars Contexta vaults
GUARD_DIR="$(cd "$(dirname "$0")" && pwd)"
"$GUARD_DIR/vaultguard.sh" || exit 0

# SessionStart provides session info as JSON on stdin.
# Read it before any echo statements.
INPUT=$(cat)
SESSION_ID=""
if command -v jq &>/dev/null; then
  SESSION_ID=$(echo "$INPUT" | jq -r '.session_id // empty')
else
  SESSION_ID=$(echo "$INPUT" | grep -o '"session_id":"[^"]*"' | head -1 | sed 's/"session_id":"//;s/"//')
fi

# Export session ID for later hooks
if [ -n "$CLAUDE_ENV_FILE" ] && [ -n "$SESSION_ID" ]; then
  echo "export CLAUDE_SESSION_ID='$SESSION_ID'" >> "$CLAUDE_ENV_FILE"
fi

# ── Context injection (stdout → conversation) ──────────────────

echo "## Workspace Structure"
echo ""

# Show directory tree (3 levels deep, markdown files only)
if command -v tree &> /dev/null; then
    tree -L 3 --charset ascii -I '.git|node_modules' -P '*.md' .
else
    find . -name "*.md" -not -path "./.git/*" -not -path "*/node_modules/*" -maxdepth 3 | sort | while read -r file; do
        depth=$(echo "$file" | tr -cd '/' | wc -c)
        indent=$(printf '%*s' "$((depth * 2))" '')
        basename=$(basename "$file")
        echo "${indent}${basename}"
    done
fi

echo ""
echo "---"
echo ""

# Persistent working memory (goals)
if [ -f self/goals.md ]; then
  cat self/goals.md
  echo ""
fi

# Identity
if [ -f self/identity.md ]; then
  cat self/identity.md self/methodology.md 2>/dev/null
  echo ""
fi

# Condition-based maintenance signals
INBOX_COUNT=$(ls -1 inbox/*.md 2>/dev/null | wc -l | tr -d ' ')

if [ "$INBOX_COUNT" -ge 3 ]; then
  echo "CONDITION: $INBOX_COUNT items in inbox. Consider /structure or /capture."
fi
