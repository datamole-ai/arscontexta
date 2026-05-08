---
name: archive-batch
description: Archive a completed processing batch. Verifies all tasks are done, resolves the archive folder from the queue, removes queue entries. Triggers on "/archive-batch", "/archive-batch [batch_id]", "archive this batch".
version: "1.0"
context: fork
model: haiku
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

## EXECUTE NOW

**Target: $ARGUMENTS**

The target MUST be a batch ID (the source basename used by /seed, e.g. `article`, `claude-md`). If no target provided, read the queue file, list batches where all tasks have `status: done`, and ask which to archive. If no archivable batches exist, report that and stop.

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

## Compact Batch Manifest

Before removing queue entries, build/read the compact batch manifest with `ops/scripts/batch-manifest.sh`. Use it for `archive_folder`, produced note titles, enrichment titles, and removal counts instead of loading the whole queue into context.

**START NOW.** Archive the completed batch.

---

## Step 1: Check Batch Readiness

Run the deterministic readiness check in one Bash turn:

```bash
bash ops/scripts/archive-ready.sh "<batch-id>"
```

Parse the JSON:

- `.total == 0` (no entries for this batch) — end immediately with `ERROR: No batch '{batch_id}' found in queue.`
- `.ready == false` — end immediately with `ERROR: Batch '{batch_id}' has incomplete tasks.` and report `.blocking` (each entry carries `id`, `current_phase`, `status`).
- `.ready == true` — proceed to Step 2.

Build the compact manifest before queue removal:

```bash
MANIFEST_JSON=$(bash ops/scripts/batch-manifest.sh "<batch-id>")
MANIFEST_PATH=$(printf '%s' "$MANIFEST_JSON" | jq -r '.manifest_path')
```

Use `MANIFEST_PATH` to populate the Output Contract after removal:
- `archive_folder`: `.archive_folder`
- removed count: `.queue.tasks | length`
- `notes_produced`: `.notes[] | select(.type == "note") | .title`
- `enrichments`: `.notes[] | select(.type == "enrichment") | .title`

## Step 2: Remove Batch From Queue

Remove all entries for this batch from `ops/queue/queue.json` via a single `jq` call. Substitute the batch id (the source basename) for `<batch-id>`:

```bash
jq --arg batch "<batch-id>" \
   '.tasks |= map(select(.batch != $batch and ((.id == $batch and .type == "process") | not)))' \
   ops/queue/queue.json > ops/queue/queue.json.tmp \
   && mv ops/queue/queue.json.tmp ops/queue/queue.json
```

**Do not re-read after update.** A zero-exit on the `jq | mv` chain means the file was rewritten. Do NOT follow up with `jq` reads to "inspect" what was removed — it adds tokens but provides nothing the skill consumes before emitting the report.

## Step 3: Output Contract

Emit a single fenced JSON block as the final chat message. No prose, no headings, no progress narration.

```json
{
  "skill": "archive-batch",
  "status": "ok",
  "batch": "<batch-id>",
  "queue": "removed <N> entries",
  "archive_folder": "<ops/queue/archive/...>",
  "notes_produced": ["<title>", "..."],
  "enrichments": ["<title>", "..."],
  "warnings": [],
  "learnings": []
}
```

On error: `"status": "error"`, `"error": "<short>"`, leave `queue.json` unchanged.
