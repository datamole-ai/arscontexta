#!/bin/bash
# Ars Contexta — Seed (commit phase)
# Args: FILE GRANULARITY ARCHIVE_DIR NEXT_CLAIM_START
# Mutates: archive dir, source location, domain archive copy, ops/queue/queue.json
# Output: --=={ seed }==-- report block
set -e

FILE="${1:-}"
GRAN_FLAG="${2:-}"
ARCHIVE_DIR="${3:-}"
NEXT_CLAIM_START="${4:-}"

if [ -z "$FILE" ] || [ -z "$GRAN_FLAG" ] || [ -z "$ARCHIVE_DIR" ] || [ -z "$NEXT_CLAIM_START" ]; then
  echo "ERROR: seed-commit.sh requires FILE GRANULARITY ARCHIVE_DIR NEXT_CLAIM_START" >&2
  exit 1
fi
case "$GRAN_FLAG" in
  --structure) GRANULARITY="structure" ;;
  --capture)   GRANULARITY="capture" ;;
  *) echo "ERROR: bad granularity $GRAN_FLAG" >&2; exit 1 ;;
esac

# ── Vocabulary loader (for {DOMAIN:archive} target) ─────────────
DOMAIN_ARCHIVE_DIR="archive"
if [ -f ops/derivation-manifest.md ]; then
  while IFS='|' read -r _ universal domain _; do
    universal=$(echo "$universal" | xargs)
    domain=$(echo "$domain" | xargs)
    [ "$universal" = "archive" ] && DOMAIN_ARCHIVE_DIR="$domain"
  done < <(grep -E '^\| archive ' ops/derivation-manifest.md 2>/dev/null || true)
fi

DATE=$(date -u +%Y-%m-%d)
SOURCE_BASENAME=$(basename "$FILE" .md | tr ' ' '-' | tr '[:upper:]' '[:lower:]')

mkdir -p "$ARCHIVE_DIR"

# Move from inbox if applicable
if [[ "$FILE" == *"inbox/"* ]] || [[ "$FILE" == inbox/* ]]; then
  mv "$FILE" "$ARCHIVE_DIR/"
  FINAL_SOURCE="$ARCHIVE_DIR/$(basename "$FILE")"
  # Domain archive copy
  mkdir -p "$DOMAIN_ARCHIVE_DIR"
  ARCHIVE_COPY="$DOMAIN_ARCHIVE_DIR/${DATE}-${SOURCE_BASENAME}.md"
  if [ ! -f "$ARCHIVE_COPY" ]; then
    cp "$FINAL_SOURCE" "$ARCHIVE_COPY"
  fi
else
  FINAL_SOURCE="$FILE"
fi

# Append queue entry
CREATED_TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)
NEW_ENTRY=$(cat <<JSON
{
  "id": "${SOURCE_BASENAME}",
  "type": "process",
  "granularity": "${GRANULARITY}",
  "status": "pending",
  "source": "${FINAL_SOURCE}",
  "archive_folder": "${ARCHIVE_DIR}",
  "created": "${CREATED_TS}",
  "next_claim_start": ${NEXT_CLAIM_START}
}
JSON
)

if [ ! -f ops/queue/queue.json ]; then
  echo '{"tasks": []}' > ops/queue/queue.json
fi
jq --argjson entry "$NEW_ENTRY" '.tasks += [$entry]' ops/queue/queue.json > ops/queue/queue.json.tmp
mv ops/queue/queue.json.tmp ops/queue/queue.json

LINE_COUNT=$(wc -l < "$FINAL_SOURCE" | tr -d ' ')

cat <<EOF
--=={ seed }==--

Seeded: ${SOURCE_BASENAME}
Source: ${FILE} -> ${FINAL_SOURCE}
Archive folder: ${ARCHIVE_DIR}
EOF
if [[ "$FILE" == *"inbox/"* ]] || [[ "$FILE" == inbox/* ]]; then
  echo "Archived copy: ${DOMAIN_ARCHIVE_DIR}/${DATE}-${SOURCE_BASENAME}.md"
fi
cat <<EOF
Size: ${LINE_COUNT} lines
Granularity: ${GRANULARITY}

Claims will start at: ${NEXT_CLAIM_START}
Claim files will be: ${SOURCE_BASENAME}-{NNN}.md (unique across vault)
Queue: updated with process task
EOF
