#!/bin/bash
# Ars Contexta — Seed (validate phase)
# Args: FILE GRANULARITY (--structure | --capture)
# Output: key=value lines (status, source_basename, archive_dir, next_claim_start,
#         line_count, content_format, filename_match=NONE | repeated for each match)
set -e

FILE="${1:-}"
GRAN_FLAG="${2:-}"

# Validate args
if [ -z "$FILE" ] || [ -z "$GRAN_FLAG" ]; then
  echo "ERROR: seed-validate.sh requires FILE and GRANULARITY (--structure|--capture)" >&2
  exit 1
fi
case "$GRAN_FLAG" in
  --structure) GRANULARITY="structure" ;;
  --capture)   GRANULARITY="capture" ;;
  *) echo "ERROR: granularity must be --structure or --capture (got: $GRAN_FLAG)" >&2; exit 1 ;;
esac
if [ ! -f "$FILE" ]; then
  echo "ERROR: file not found: $FILE" >&2
  exit 1
fi

# Compute basename, archive dir, line count, format
SOURCE_BASENAME=$(basename "$FILE" .md | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
DATE=$(date -u +%Y-%m-%d)
ARCHIVE_DIR="ops/queue/archive/${DATE}-${SOURCE_BASENAME}"
LINE_COUNT=$(wc -l < "$FILE" | tr -d ' ')
case "$FILE" in
  *.md) FORMAT="markdown" ;;
  *.txt) FORMAT="plaintext" ;;
  *.json) FORMAT="json" ;;
  *) FORMAT="unknown" ;;
esac

# Determine final source destination (move-from-inbox semantics)
if [[ "$FILE" == *"inbox/"* ]] || [[ "$FILE" == inbox/* ]]; then
  FINAL_SOURCE="${ARCHIVE_DIR}/$(basename "$FILE")"
else
  FINAL_SOURCE="$FILE"
fi

# Compute next claim start across queue + archive
QUEUE_MAX=0
if [ -f ops/queue/queue.json ]; then
  Q=$(grep -oE '[0-9]{3}\.md' ops/queue/queue.json 2>/dev/null | grep -oE '[0-9]{3}' | sort -n | tail -1 || true)
  [ -n "$Q" ] && QUEUE_MAX="$Q"
fi
ARCHIVE_MAX=0
A=$(find ops/queue/archive -name "*-[0-9][0-9][0-9].md" 2>/dev/null \
  | sed 's/.*-\([0-9][0-9][0-9]\)\.md/\1/' | sort -n | tail -1 || true)
[ -n "$A" ] && ARCHIVE_MAX="$A"
QUEUE_MAX_N=$((10#$QUEUE_MAX))
ARCHIVE_MAX_N=$((10#$ARCHIVE_MAX))
if [ "$QUEUE_MAX_N" -gt "$ARCHIVE_MAX_N" ]; then
  NEXT_CLAIM_START=$((QUEUE_MAX_N + 1))
else
  NEXT_CLAIM_START=$((ARCHIVE_MAX_N + 1))
fi

# Filename match: queue file references + archive folders
matches=""
if [ -f ops/queue/queue.json ] && grep -q "$SOURCE_BASENAME" ops/queue/queue.json 2>/dev/null; then
  matches="${matches}ops/queue/queue.json
"
fi
while IFS= read -r m; do
  [ -n "$m" ] && matches="${matches}${m}
"
done < <(find ops/queue/archive -maxdepth 1 -type d -name "*-${SOURCE_BASENAME}*" 2>/dev/null)

# Emit output
echo "status=ok"
echo "source_basename=${SOURCE_BASENAME}"
echo "final_source_dest=${FINAL_SOURCE}"
echo "archive_dir=${ARCHIVE_DIR}"
echo "next_claim_start=${NEXT_CLAIM_START}"
echo "line_count=${LINE_COUNT}"
echo "content_format=${FORMAT}"
echo "granularity=${GRANULARITY}"
if [ -z "$matches" ]; then
  echo "filename_match=NONE"
else
  while IFS= read -r m; do
    [ -n "$m" ] && echo "filename_match=${m}"
  done <<< "$matches"
fi

exit 0
