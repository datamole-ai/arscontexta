#!/usr/bin/env bash
# batch-manifest.sh - write a compact manifest for one pipeline batch.
# Args: BATCH_ID (required)
# Output: the manifest JSON. Also writes it to
# ops/queue/archive/<date>-<batch>/batch-manifest.json.

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

frontmatter_value() {
  local key="$1"
  local file="$2"

  awk -v key="$key" '
    NR == 1 && $0 == "---" { in_fm=1; next }
    in_fm && $0 == "---" { exit }
    in_fm {
      line=$0
      pattern="^" key ":[[:space:]]*"
      if (line ~ pattern) {
        sub(pattern, "", line)
        gsub(/^["'\''[:space:]]+|["'\''[:space:]]+$/, "", line)
        print line
        exit
      }
    }
  ' "$file"
}

first_heading() {
  local file="$1"

  awk '
    /^# / {
      sub(/^# /, "")
      print
      exit
    }
  ' "$file"
}

has_moc_content_type() {
  local file="$1"

  awk '
    NR == 1 && $0 == "---" { in_fm=1; next }
    in_fm && $0 == "---" { exit }
    in_fm && $0 ~ /^content_type:[[:space:]]*"?moc"?[[:space:]]*$/ { found=1 }
    END { exit found ? 0 : 1 }
  ' "$file"
}

json_array_add() {
  local array_json="$1"
  local object_json="$2"

  jq --argjson item "$object_json" '. + [$item]' <<<"$array_json"
}

process_entry=$(jq -c --arg b "$BATCH_ID" '
  [.tasks[] | select(.id == $b and .type == "process")] | first // null
' "$QUEUE")

if [ "$process_entry" = "null" ]; then
  jq -n --arg b "$BATCH_ID" '{ok:false,batch:$b,error:"process entry not found"}'
  exit 2
fi

archive_folder=$(jq -r '.archive_folder // empty' <<<"$process_entry")
if [ -z "$archive_folder" ]; then
  archive_folder=$(find ops/queue/archive -mindepth 1 -maxdepth 1 -type d -name "*-${BATCH_ID}" 2>/dev/null | head -n 1)
fi

if [ -z "$archive_folder" ]; then
  jq -n --arg b "$BATCH_ID" '{ok:false,batch:$b,error:"archive_folder not found"}'
  exit 2
fi

mkdir -p "$archive_folder"
manifest_path="$archive_folder/batch-manifest.json"

queue_snapshot=$(jq --arg b "$BATCH_ID" '
  [.tasks[] | select(.batch == $b or (.id == $b and .type == "process"))] as $tasks
  | {
      tasks: $tasks,
      by_status: (
        $tasks
        | group_by(.status // "none")
        | map({key:(.[0].status // "none"), value:length})
        | from_entries
      ),
      by_phase: (
        $tasks
        | group_by(.current_phase // "none")
        | map({key:(.[0].current_phase // "none"), value:length})
        | from_entries
      )
    }
' "$QUEUE")

notes_json='[]'
while IFS= read -r task; do
  target_path=$(jq -r '.target_path // empty' <<<"$task")
  [ -n "$target_path" ] || continue
  [ -f "$target_path" ] || continue

  title=$(first_heading "$target_path")
  [ -n "$title" ] || title=$(basename "$target_path" .md)
  description=$(frontmatter_value description "$target_path")

  note_json=$(jq -n \
    --arg id "$(jq -r '.id // ""' <<<"$task")" \
    --arg type "$(jq -r '.type // ""' <<<"$task")" \
    --arg granularity "$(jq -r '.granularity // ""' <<<"$task")" \
    --arg target "$(jq -r '.target // ""' <<<"$task")" \
    --arg path "$target_path" \
    --arg title "$title" \
    --arg description "$description" \
    --argjson semantic_neighbors "$(jq '.semantic_neighbors // []' <<<"$task")" \
    '{
      id: $id,
      type: $type,
      granularity: $granularity,
      target: (if $target == "" then $title else $target end),
      path: $path,
      title: $title,
      description: $description,
      semantic_neighbors: $semantic_neighbors
    }')
  notes_json=$(json_array_add "$notes_json" "$note_json")
done < <(jq -c --arg b "$BATCH_ID" '.tasks[] | select(.batch == $b and .type != "process")' "$QUEUE")

NOTE_COLLECTION_DIR="$(manifest_value note_collection)"
[ -n "$NOTE_COLLECTION_DIR" ] || NOTE_COLLECTION_DIR="notes"

maps_json='[]'
if [ -d "$NOTE_COLLECTION_DIR" ]; then
  while IFS= read -r -d '' file; do
    if has_moc_content_type "$file"; then
      title=$(first_heading "$file")
      [ -n "$title" ] || title=$(basename "$file" .md)
      description=$(frontmatter_value description "$file")
      link_count=$(grep -c '^- \[\[' "$file" 2>/dev/null || true)
      [ -n "$link_count" ] || link_count=0
      map_json=$(jq -n \
        --arg path "$file" \
        --arg title "$title" \
        --arg description "$description" \
        --argjson link_count "$link_count" \
        '{path:$path,title:$title,description:$description,link_count:$link_count}')
      maps_json=$(json_array_add "$maps_json" "$map_json")
    fi
  done < <(find "$NOTE_COLLECTION_DIR" -name "*.md" -type f -print0)
fi

phase_outputs='{}'
phase_outputs_dir="$archive_folder/phase-outputs"
if [ -d "$phase_outputs_dir" ]; then
  while IFS= read -r -d '' file; do
    if jq empty "$file" 2>/dev/null; then
      key=$(basename "$file" .json)
      phase_outputs=$(jq --arg key "$key" --slurpfile doc "$file" \
        '. + {($key): $doc[0]}' <<<"$phase_outputs")
    fi
  done < <(find "$phase_outputs_dir" -maxdepth 1 -name "*.json" -type f -print0)
fi

generated_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)

jq -n \
  --argjson process "$process_entry" \
  --argjson queue "$queue_snapshot" \
  --argjson notes "$notes_json" \
  --argjson maps "$maps_json" \
  --argjson phase_outputs "$phase_outputs" \
  --arg batch "$BATCH_ID" \
  --arg generated_at "$generated_at" \
  --arg manifest_path "$manifest_path" \
  --arg source "$(jq -r '.source // empty' <<<"$process_entry")" \
  --arg archive_folder "$archive_folder" \
  --arg note_collection "$NOTE_COLLECTION_DIR" \
  '{
    ok: true,
    schema_version: 1,
    generated_at: $generated_at,
    batch: $batch,
    manifest_path: $manifest_path,
    source: (if $source == "" then null else $source end),
    archive_folder: $archive_folder,
    note_collection: $note_collection,
    process: $process,
    queue: $queue,
    notes: $notes,
    existing_maps: $maps,
    semantic_neighbors: [
      $notes[]
      | select((.semantic_neighbors | length) > 0)
      | {id, title, path, semantic_neighbors}
    ],
    phase_outputs: $phase_outputs
  }' > "$manifest_path.tmp"

mv "$manifest_path.tmp" "$manifest_path"
cat "$manifest_path"
