---
name: archive-batch
description: Archive a completed processing batch. Verifies all tasks are done, moves task files to archive folder, generates batch summary, removes queue entries. Triggers on "/archive-batch", "/archive-batch [batch_id]", "archive this batch".
version: "1.0"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
argument-hint: "{batch_id} — batch to archive (required)"
---

## EXECUTE NOW

**Target: $ARGUMENTS**

The target MUST be a batch ID (the source basename used by /seed, e.g. `article`, `claude-md`). If no target provided, read the queue file, list batches where all tasks have `status: done`, and ask which to archive. If no archivable batches exist, report that and stop.

### Step 0: Read Vocabulary

Read `ops/derivation-manifest.md` (or fall back to `ops/derivation.md`) for domain vocabulary mapping. All output must use domain-native terms. If neither file exists, use universal terms.

**START NOW.** Archive the completed batch.

---

## Step 1: Locate Queue File

Find the queue file. Check in order:
1. `ops/queue.yaml`
2. `ops/queue/queue.yaml`
3. `ops/queue/queue.json`

If no queue file found:
```
ERROR: No queue file found. Checked:
  - ops/queue.yaml
  - ops/queue/queue.yaml
  - ops/queue/queue.json
```
Stop.

Read the queue file contents.

## Step 2: Find Batch Entries

Find all queue entries belonging to this batch. A queue entry belongs to the batch if:
- `id` equals `{batch_id}` (the extract task), OR
- `id` starts with `{batch_id}-` (claim and enrichment tasks like `{batch_id}-001`, `{batch_id}-002`)

If no entries found:
```
ERROR: No batch '{batch_id}' found in queue.
```
Stop.

Record the list of matching entries and their count.

## Step 3: Verify All Tasks Complete

Check that every entry for this batch has `status: done`.

If ANY entry does not have `status: done`:
```
ERROR: Batch '{batch_id}' has incomplete tasks.

Incomplete:
  - {id}: status={status}, current_phase={current_phase}
  - ...

Run /ralph --batch {batch_id} to continue processing.
```
Stop. Do not archive.

## Step 4: Locate Archive Folder

The archive folder should already exist from /seed. Search for it:

```bash
ls -d ops/queue/archive/*-{batch_id}/ 2>/dev/null
```

The pattern is `ops/queue/archive/{date}-{batch_id}/`.

- If found: use the existing folder
- If not found: create `ops/queue/archive/$(date -u +"%Y-%m-%d")-{batch_id}/`

Record the archive folder path as `ARCHIVE_DIR`.

## Step 5: Move Task Files

Move all task files for this batch from the queue directory to the archive folder:

```bash
mv ops/queue/{batch_id}.md "$ARCHIVE_DIR/"
mv ops/queue/{batch_id}-*.md "$ARCHIVE_DIR/" 2>/dev/null
```

The glob catches:
- `{batch_id}.md` — the extract task file
- `{batch_id}-001.md`, `{batch_id}-002.md`, etc. — claim/enrichment task files

If a file already exists in the archive folder (edge case from partial previous run), skip it and warn:
```
WARN: {filename} already exists in archive, skipping move.
```

Record the count of files moved.

## Step 6: Generate Batch Summary

Read each task file from its new location in the archive folder. Extract:

**From the extract task file (`{batch_id}.md`):**
- `source` field from frontmatter — the source file path
- `original_path` field from frontmatter — the original location before /seed moved it

**From claim/enrichment task files (`{batch_id}-NNN.md`):**
- `type` field from frontmatter — `claim` or `enrichment`
- Title from the `## Create` section or the first `#` heading
- Any content under `## Execution Notes` or `## Learnings` sections

Count claims (type == claim or type containing create/reflect/reweave/verify phases) and enrichments (type == enrichment) separately.

Write `{batch_id}-summary.md` to the archive folder:

```markdown
---
batch: {batch_id}
source: {source path from extract task}
archived: {ARCHIVE_DIR}
completed: {UTC timestamp}
---

# Batch Summary: {batch_id}

## Source
- File: {source filename}
- Original location: {original_path from extract task}
- Archived to: {ARCHIVE_DIR}

## Results
- {DOMAIN:note_plural} extracted: {count of claim tasks}
- Enrichments: {count of enrichment tasks}

## Created {DOMAIN:note_plural}
- [[{title from claim task 1}]]
- [[{title from claim task 2}]]
- ...

## Learnings
{Combined learnings from task execution notes, or "None captured."}
```

## Step 7: Remove Batch From Queue

Remove all entries for this batch from the queue file (both the extract entry and all claim/enrichment entries identified in Step 2).

Write the updated queue file back. If the queue is now empty of task entries, preserve the file with its schema header (phase_order definitions) intact — do not delete the queue file.

## Step 8: Report

```
--=={ archive-batch }==--

Archived: {batch_id}
Archive folder: {ARCHIVE_DIR}

{DOMAIN:note_plural} extracted: {claim_count}
Enrichments: {enrichment_count}
Task files moved: {files_moved_count}

Summary: {ARCHIVE_DIR}/{batch_id}-summary.md

Created {DOMAIN:note_plural}:
- [[{title 1}]]
- [[{title 2}]]
- ...

Queue: {remaining_entry_count} entries remaining
```

---

## Edge Cases

**No batch_id argument and no archivable batches:** Report "No archivable batches found. All batches have pending tasks or the queue is empty."

**Archive folder missing:** Create it. This handles manual queue manipulation or edge cases where /seed was run differently.

**Task files already in archive:** Skip the move, warn in output. This handles re-running /archive-batch after a partial failure.

**Empty queue after removal:** Keep the queue file with its schema header. Do not delete it.

**No derivation-manifest.md:** Use universal vocabulary for all output (same fallback as all pipeline skills).

---

## Critical Constraints

**never:**
- Archive a batch with incomplete tasks (no --force, no partial archiving)
- Delete the queue file even if empty after removal
- Proceed past Step 3 if any task is not done

**always:**
- Read vocabulary before producing any output
- Move task files before generating summary (summary reads from archive location)
- Preserve the queue file schema header when removing entries
- Report created {DOMAIN:note_plural} with wiki-link syntax in the summary and report
