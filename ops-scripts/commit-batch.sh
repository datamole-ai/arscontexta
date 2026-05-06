#!/usr/bin/env bash
# commit-batch.sh — commit the artifacts produced by a pipeline run.
# Args: BATCH_ID (required), MESSAGE (optional — defaults to "batch: <id>")
# Assumption: the pipeline is the only writer in this working tree during a
# run, so `git add -A` captures exactly the batch's artifacts. Run after
# /archive-batch and the learnings write.
# Output: single-line JSON. Exit: 0 on success or "no changes"; nonzero on
# git failure.

set -u

BATCH_ID="${1:-}"
MESSAGE="${2:-batch: ${BATCH_ID:-unknown}}"

if [ -z "$BATCH_ID" ]; then
  echo '{"ok":false,"error":"BATCH_ID required"}'
  exit 2
fi

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  jq -n --arg b "$BATCH_ID" \
    '{ok:true, batch:$b, committed:false, reason:"not a git repo", commit:null, warnings:["not a git repo"]}'
  exit 0
fi

# Stage every working-tree change. Pipeline is the sole writer during a run.
if ! git add -A 2>/dev/null; then
  jq -n --arg b "$BATCH_ID" '{ok:false, batch:$b, error:"git add failed"}'
  exit 1
fi

# Anything to commit?
if git diff --cached --quiet 2>/dev/null; then
  jq -n --arg b "$BATCH_ID" \
    '{ok:true, batch:$b, committed:false, reason:"no staged changes", commit:null, warnings:[]}'
  exit 0
fi

# Commit. Capture stderr for diagnostics on failure.
commit_err=$(git commit -m "$MESSAGE" 2>&1 1>/dev/null) || {
  jq -n --arg b "$BATCH_ID" --arg err "$commit_err" --arg m "$MESSAGE" \
    '{ok:false, batch:$b, error:"git commit failed", detail:$err, message:$m}'
  exit 1
}

hash=$(git rev-parse HEAD 2>/dev/null || echo "")
short=$(git rev-parse --short HEAD 2>/dev/null || echo "")
porcelain_count=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
[ "$porcelain_count" = "0" ] && tree_status="clean" || tree_status="dirty"

jq -n \
  --arg batch "$BATCH_ID" \
  --arg hash "$hash" \
  --arg short "$short" \
  --arg msg "$MESSAGE" \
  --arg status "$tree_status" \
  '{ok:true, batch:$batch, committed:true, commit:$hash, short:$short, message:$msg, tree_status:$status, warnings:[]}'
