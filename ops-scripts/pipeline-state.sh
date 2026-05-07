#!/usr/bin/env bash
# pipeline-state.sh — return a deterministic snapshot of pipeline state.
# Args: BATCH_ID (required)
# Output: a single-line JSON object on stdout.
# Exit: 0 on normal output (including warnings); 2 on a hard error (missing
# arguments or queue file). Hard errors still emit JSON on stdout describing
# the failure.

set -u

BATCH_ID="${1:-}"
if [ -z "$BATCH_ID" ]; then
  echo '{"ok":false,"error":"BATCH_ID required"}'
  exit 2
fi

QUEUE="ops/queue/queue.json"
if [ ! -f "$QUEUE" ]; then
  jq -n --arg b "$BATCH_ID" '{ok:false,batch:$b,error:"ops/queue/queue.json not found"}'
  exit 2
fi

if ! jq empty "$QUEUE" 2>/dev/null; then
  jq -n --arg b "$BATCH_ID" '{ok:false,batch:$b,error:"queue.json is not valid JSON"}'
  exit 2
fi

total=$(jq --arg b "$BATCH_ID" '
  [.tasks[] | select(.batch == $b and .type != "process")] | length
' "$QUEUE")
by_phase=$(jq --arg b "$BATCH_ID" '
  [.tasks[] | select(.batch == $b and .type != "process")]
  | group_by(.current_phase // "none")
  | map({key:(.[0].current_phase // "none"), value:length})
  | from_entries
' "$QUEUE")
by_status=$(jq --arg b "$BATCH_ID" '
  [.tasks[] | select(.batch == $b and .type != "process")]
  | group_by(.status)
  | map({key:(.[0].status), value:length})
  | from_entries
' "$QUEUE")
process_entry=$(jq -c --arg b "$BATCH_ID" '
  [.tasks[] | select(.id == $b and .type == "process")] | first // null
' "$QUEUE")
archive_folder=$(echo "$process_entry" | jq -r '.archive_folder // empty')
source_path=$(echo "$process_entry" | jq -r '.source // empty')
granularity=$(echo "$process_entry" | jq -r '.granularity // empty')

# Git state (best-effort — vault may not be a repo)
warnings='[]'
if git rev-parse --git-dir >/dev/null 2>&1; then
  branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")
  if git diff --quiet 2>/dev/null && git diff --cached --quiet 2>/dev/null; then
    dirty="false"
  else
    dirty="true"
  fi
  changed=$(git status --porcelain 2>/dev/null \
    | awk '{ for (i=2; i<=NF; i++) printf "%s%s", $i, (i==NF?ORS:" ") }' \
    | jq -R -s -c 'split("\n") | map(select(. != ""))')
  git_obj=$(jq -n --arg branch "$branch" --argjson dirty "$dirty" --argjson changed "$changed" \
    '{branch:$branch,dirty:$dirty,changed:$changed}')
else
  git_obj='null'
  warnings='["not a git repo"]'
fi

jq -n \
  --arg batch "$BATCH_ID" \
  --argjson total "$total" \
  --argjson by_phase "$by_phase" \
  --argjson by_status "$by_status" \
  --arg archive "$archive_folder" \
  --arg source "$source_path" \
  --arg gran "$granularity" \
  --argjson git "$git_obj" \
  --argjson warnings "$warnings" \
  '{
    ok: true,
    batch: $batch,
    total: $total,
    by_phase: $by_phase,
    by_status: $by_status,
    archive_folder: (if $archive == "" then null else $archive end),
    source: (if $source == "" then null else $source end),
    granularity: (if $gran == "" then null else $gran end),
    git: $git,
    warnings: $warnings
  }'
