---
name: archive-batch
description: Archive a completed processing batch. Verifies all tasks are done, resolves the archive folder from the queue, removes queue entries. Triggers on "/archive-batch", "/archive-batch [batch_id]", "archive this batch".
version: "1.0"
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
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

## Step 3: Remove Batch From Queue

Remove all entries for this batch from `ops/queue/queue.json` via a single `jq` call. Substitute the batch id (the source basename) for `<batch-id>`:

```bash
jq --arg batch "<batch-id>" \
   '.tasks |= map(select(.batch != $batch))' \
   ops/queue/queue.json > ops/queue/queue.json.tmp \
   && mv ops/queue/queue.json.tmp ops/queue/queue.json
```

## Step 4: Report

```
--=={ archive-batch }==--

Archived: {batch_id}
Archive folder: {ARCHIVE_DIR}

{DOMAIN:note_plural} produced: {claim_count}
Enrichments: {enrichment_count}

Created {DOMAIN:note_plural}:
- [[{title 1}]]
- [[{title 2}]]
- ...

Queue: {remaining_entry_count} entries remaining
```
