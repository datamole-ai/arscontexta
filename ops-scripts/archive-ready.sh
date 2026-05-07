#!/usr/bin/env bash
# archive-ready.sh — check whether all batch entries are done.
# Args: BATCH_ID (required)
# Output: a single-line JSON object on stdout.
# Exit: 0 always when output is JSON. Errors are reported in the JSON.

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
  [.tasks[] | select(.batch == $b or (.id == $b and .type == "process"))] | length
' "$QUEUE")

if [ "$total" = "0" ]; then
  jq -n --arg b "$BATCH_ID" \
    '{ok:true,batch:$b,ready:false,reason:"no batch entries in queue",blocking:[],total:0,warnings:[]}'
  exit 0
fi

blocking=$(jq -c --arg b "$BATCH_ID" '
  [.tasks[]
   | select((.batch == $b or (.id == $b and .type == "process")) and .status != "done")
   | {id, type, current_phase, status, target_path: (.target_path // null)}]
' "$QUEUE")
blocking_count=$(echo "$blocking" | jq 'length')

if [ "$blocking_count" = "0" ]; then
  ready=true
else
  ready=false
fi

jq -n \
  --arg b "$BATCH_ID" \
  --argjson ready "$ready" \
  --argjson blocking "$blocking" \
  --argjson total "$total" \
  '{ok:true,batch:$b,ready:$ready,blocking:$blocking,total:$total,warnings:[]}'
