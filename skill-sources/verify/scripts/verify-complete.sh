#!/bin/bash
# Ars Contexta — Verify (complete phase)
# Args: BATCH_ID COMPLETED_IDS_JSON
# Mutates: ops/queue/queue.json — marks listed entries verify -> done
# Output: queue: marked N entries verify -> done
set -e

BATCH_ID="${1:-}"
COMPLETED_IDS_JSON="${2:-}"

if [ -z "$BATCH_ID" ] || [ -z "$COMPLETED_IDS_JSON" ]; then
  echo "ERROR: verify-complete.sh requires BATCH_ID and COMPLETED_IDS_JSON" >&2
  exit 1
fi
if [ ! -f ops/queue/queue.json ]; then
  echo "ERROR: ops/queue/queue.json not found" >&2
  exit 1
fi

NOW=$(date -u +%Y-%m-%dT%H:%M:%SZ)
COUNT=$(echo "$COMPLETED_IDS_JSON" | jq 'length')

jq --arg batch "$BATCH_ID" \
   --arg now "$NOW" \
   --argjson ids "$COMPLETED_IDS_JSON" \
   '(.tasks[] | select(.batch == $batch and (.id | IN($ids[])))) |=
    (.completed_phases += ["verify"] | .status = "done" | .current_phase = null | .completed = $now)' \
   ops/queue/queue.json > ops/queue/queue.json.tmp
mv ops/queue/queue.json.tmp ops/queue/queue.json

echo "queue: marked $COUNT entries verify -> done"
