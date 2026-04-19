---
name: archive-batch
description: Archive a completed processing batch. Verifies all tasks are done, moves task files to archive folder, generates batch summary, removes queue entries. Triggers on "/archive-batch", "/archive-batch [batch_id]", "archive this batch".
version: "1.0"
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
argument-hint: "{batch_id} — batch to archive (required)"
---

## EXECUTE NOW

**Target: $ARGUMENTS**

The target MUST be a batch ID (the source basename used by /seed, e.g. `article`, `claude-md`). If no target provided, read the queue file, list batches where all tasks have `status: done`, and ask which to archive. If no archivable batches exist, report that and stop.

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

## Queue File

!`cat ops/queue/queue.json`

**START NOW.** Archive the completed batch.

---

## Step 1: Find Batch Entries

Find all queue entries belonging to this batch. Based on the batch ID.

If no entries found, end immediately with: `ERROR: No batch '{batch_id}' found in queue.`

Record the list of matching entries and their count.

## Step 2: Verify All Tasks Complete

Check that every entry for this batch has `status: done`.

If ANY entry does not have `status: done`:
end immediately with: `ERROR: Batch '{batch_id}' has incomplete tasks.`.

## Step 3: Move Task Files

Move all task files for this batch from the queue directory to the archive folder:

ARCHIVE_DIR="ops/queue/archive/$(date -u +"%Y-%m-%d")-{batch_id}/"

```bash
mv ops/queue/{batch_id}.md "$ARCHIVE_DIR/"
mv ops/queue/{batch_id}-*.md "$ARCHIVE_DIR/" 2>/dev/null
```

## Step 4: Remove Batch From Queue

Remove all entries for this batch from the queue file.

Write the updated queue file back. If the queue is now empty of task entries, preserve the file with its schema header (phase_order definitions) intact — do not delete the queue file.

## Step 5: Report

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
