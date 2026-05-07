#!/usr/bin/env bash
# commit-batch.sh - commit the artifacts produced by a pipeline run.
# Args: BATCH_ID (required), MESSAGE (optional — defaults to "batch: <id>")
# Stages pipeline-owned paths only; unrelated workspace and inbox changes are
# left untouched. Run after /archive-batch and the learnings write.
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

manifest_value() {
  local key="$1"
  [ -f ops/derivation-manifest.md ] || return 1

  awk -v key="$key" '
    /^[[:space:]]*vocabulary:[[:space:]]*$/ { in_vocab=1; next }
    in_vocab && /^[^[:space:]#][^:]*:/ { in_vocab=0 }
    in_vocab {
      line=$0
      sub(/[[:space:]]+#.*/, "", line)
      pattern="^[[:space:]]*" key "[[:space:]]*:"
      if (line ~ pattern) {
        sub(pattern "[[:space:]]*", "", line)
        gsub(/^[[:space:]"'\''"]+|[[:space:]"'\''"]+$/, "", line)
        print line
        exit
      }
    }
  ' ops/derivation-manifest.md
}

NOTE_COLLECTION_DIR="$(manifest_value note_collection)"
[ -n "$NOTE_COLLECTION_DIR" ] || NOTE_COLLECTION_DIR="notes"
DOMAIN_ARCHIVE_DIR="$(manifest_value archive)"
[ -n "$DOMAIN_ARCHIVE_DIR" ] || DOMAIN_ARCHIVE_DIR="archive"
INBOX_DIR="$(manifest_value inbox)"
[ -n "$INBOX_DIR" ] || INBOX_DIR="inbox"

stage_paths=()
archive_folders=()
source_basenames=()

add_stage_path() {
  local path="$1"
  [ -n "$path" ] || return 0

  if [ -e "$path" ] || git ls-files --error-unmatch "$path" >/dev/null 2>&1; then
    stage_paths+=("$path")
  fi
}

add_stage_path "ops/queue/queue.json"
add_stage_path "$NOTE_COLLECTION_DIR"
add_stage_path "ops/observations"
add_stage_path "ops/tensions"
add_stage_path "ops/quarantine"

if [ -d ops/queue/archive ]; then
  while IFS= read -r -d '' dir; do
    case "$(basename "$dir")" in
      *-"$BATCH_ID")
        archive_folders+=("$dir")
        add_stage_path "$dir"
        ;;
    esac
  done < <(find ops/queue/archive -mindepth 1 -maxdepth 1 -type d -print0)
fi

for dir in "${archive_folders[@]}"; do
  while IFS= read -r -d '' file; do
    source_basenames+=("$(basename "$file")")
  done < <(find "$dir" -maxdepth 1 -type f -print0)
done

if [ -d "$DOMAIN_ARCHIVE_DIR" ]; then
  while IFS= read -r -d '' file; do
    case "$(basename "$file")" in
      *-"$BATCH_ID".*) add_stage_path "$file" ;;
    esac
  done < <(find "$DOMAIN_ARCHIVE_DIR" -maxdepth 1 -type f -print0)
fi

# If seed moved a tracked inbox source into the batch archive, stage only that
# source deletion, not the whole inbox.
if [ "${#source_basenames[@]}" -gt 0 ]; then
  while IFS= read -r line; do
    status="${line:0:2}"
    path="${line:3}"
    case "$status" in
      D*|*D)
        case "$path" in
          "$INBOX_DIR"/*|*/"$INBOX_DIR"/*)
            base="$(basename "$path")"
            for source_base in "${source_basenames[@]}"; do
              [ "$base" = "$source_base" ] && add_stage_path "$path"
            done
            ;;
        esac
        ;;
    esac
  done < <(git status --porcelain)
fi

if [ "${#stage_paths[@]}" -gt 0 ]; then
  add_err=$(git add -A -- "${stage_paths[@]}" 2>&1) || {
    jq -n --arg b "$BATCH_ID" --arg err "$add_err" \
      '{ok:false, batch:$b, error:"git add failed", detail:$err}'
    exit 1
  }
fi

# Anything to commit?
if [ "${#stage_paths[@]}" = "0" ] || git diff --cached --quiet -- "${stage_paths[@]}" 2>/dev/null; then
  dirty_count=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  warnings='[]'
  if [ "$dirty_count" != "0" ]; then
    warnings=$(jq -n --argjson n "$dirty_count" \
      '["left " + ($n|tostring) + " non-batch path(s) uncommitted"]')
  fi
  jq -n --arg b "$BATCH_ID" \
    --argjson warnings "$warnings" \
    '{ok:true, batch:$b, committed:false, reason:"no batch changes", commit:null, warnings:$warnings}'
  exit 0
fi

# Commit. Capture stderr for diagnostics on failure.
commit_err=$(git commit -m "$MESSAGE" -- "${stage_paths[@]}" 2>&1 1>/dev/null) || {
  jq -n --arg b "$BATCH_ID" --arg err "$commit_err" --arg m "$MESSAGE" \
    '{ok:false, batch:$b, error:"git commit failed", detail:$err, message:$m}'
  exit 1
}

hash=$(git rev-parse HEAD 2>/dev/null || echo "")
short=$(git rev-parse --short HEAD 2>/dev/null || echo "")
porcelain_count=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
[ "$porcelain_count" = "0" ] && tree_status="clean" || tree_status="dirty"
warnings='[]'
if [ "$porcelain_count" != "0" ]; then
  warnings=$(jq -n --argjson n "$porcelain_count" \
    '["left " + ($n|tostring) + " non-batch path(s) uncommitted"]')
fi

jq -n \
  --arg batch "$BATCH_ID" \
  --arg hash "$hash" \
  --arg short "$short" \
  --arg msg "$MESSAGE" \
  --arg status "$tree_status" \
  --argjson warnings "$warnings" \
  '{ok:true, batch:$batch, committed:true, commit:$hash, short:$short, message:$msg, tree_status:$status, warnings:$warnings}'
