---
name: pipeline
description: End-to-end source processing -- seed, structure/capture, process all notes through reflect/verify, archive. The full pipeline in one command. Triggers on "/pipeline", "/pipeline [file]", "process this end to end", "full pipeline".
version: "1.0"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
argument-hint: " [file path] [--structure] [--capture]
---

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse immediately:
- Source file path: the file to process (required)
- If target is empty: list files in {DOMAIN:inbox}/ and ask which to process

**Granularity flag:**
- one of: --structure, --capture
- If no flag: present both options and ask user before proceeding

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`


**START NOW.** Run the full pipeline.

---

## Pipeline Overview

The pipeline orchestrates three phases. Each phase uses skill invocation. State lives in the queue file — the pipeline is stateless orchestration on top of stateful queue entries.

```
Source file
    |
    v
Phase 1: /seed --[granularity] — create process task, move source to archive
    |
    v
Phase 2: Granularity-based processing
    |
    v
Phase 4: /archive-batch — finalize the batch in queue.json and move artifacts to archive
    |
    v
Phase 4.5: Write learnings.md to the archive folder
    |
    v
Phase 5: Commit — single batch commit if in a git repo
    |
    v
Complete
```

/pipeline is the orchestrator. /seed is the entry point for Phase 1; /pipeline drives Phase 2, invokes /archive-batch for Phase 4, and produces the batch commit as Phase 5.

---

## Phase 1: Seed

Use Skill tool to invoke /seed on the target file with the granularity flag to create the process task.

**Capture from seed output:**
- **Batch ID**: the source basename
- **Archive folder path**: where the source was moved
- **next_claim_start**: the claim numbering start

Report: `$ Seeded: {source-name}`

---

## Phase 2: Process Source (Granularity-Routed) and claims

Process the source via the appropriate producer, then drive each resulting note/enrichment through the phase sequence. Each sub-skill is self-owning: it updates its own entry in `ops/queue/queue.json` and echoes its canonical output block to chat. The orchestrator parses the chat return for Status / Queue / Learnings and holds the iteration state in memory.

### Phase 2.1: Invoke the producer

Use the Skill tool to invoke `/structure` or `/capture` (based on the process entry's `granularity` in `queue.json`) passing the batch id as argument:

- `<batch-id>` — the source basename, equal to the process entry's `id`.

Parse the producer's chat return:
- **Status:** must be `ok`; otherwise stop the pipeline and surface the error.
- **Queue:** should read `marked <batch-id>: process -> done; created <N> note entries ...`.
- **Learnings:** capture non-NONE entries for the final report.

### Phase 2.1.5: Sync semantic index

After the producer reports `ok`, refresh the qmd index. Run:

```bash
bash .claude/hooks/qmd-sync.sh
```

### Phase 2.2: Re-read queue to discover new entries

Read `ops/queue/queue.json` ONCE. Filter entries where `batch == <batch-id>` and `status == "pending"`. Order by `id` ascending. This is the "work list" for the remainder of Phase 2. The pipeline does not re-read `queue.json` during the per-phase loop.

If the list is empty, report `Processing produced zero notes` and stop.

### Phase 2.3: Drive each entry through its phase sequence

For each entry in the work list (index `i`, total `N`):

Report:
```
=== Processing task {i}/{N}: {id} — {target} ===
```

Look up `phase_order` for the entry's `type` (`note` or `enrichment`) from the queue file header. The sequence is `[reflect, verify]` for both types.

For each phase in the sequence, in order:

1. **Invoke the phase skill** via the Skill tool, passing the entry's queue `id` as argument (e.g. `note-007`, `enrich-002`).
2. **Parse the chat return:**
   - Extract the `**Status:**` line. If not `ok`, stop the pipeline and surface the error with the current task id and phase.
   - Extract the `**Queue:**` line for the progress log.
   - Extract non-NONE Learnings entries and append them to the batch's Learnings accumulator.
3. **Report phase completion:**
   ```
   {id}: {phase} done — queue: {queue-line}
   ```

The sub-skill has already updated `queue.json` by the time its chat return lands. The orchestrator trusts the chat signal and does not re-read the file.

---

## Phase 3: Verify Completion

Re-read `ops/queue/queue.json` once. Count entries where `batch == <batch-id>` AND `status != "done"`.

**If any remain:**
- Report which tasks are incomplete and at which phase (from the queue).
- Show the specific task ids and their `current_phase`.
- Do NOT proceed to archive.

**If all done:** proceed to Phase 4.

---

## Phase 4: Archive Batch

When all tasks for the batch are complete, archive the batch by using Skill tool to invoke /archive-batch.

---

## Phase 4.5: Write Learnings

After `/archive-batch` returns successfully, write the accumulated Learnings to the batch's archive folder.

Resolve the archive folder from the queue's process entry.

Write `<archive_folder>/learnings.md` with the following shape:

```markdown
# Learnings — {batch_id}

## Friction
- {description}
- ...

## Surprise
- {description}
- ...

## Methodology
- {description}
- ...

## Process gap
- {description}
- ...
```

If a category has zero non-NONE entries, omit that section entirely. If all four categories are empty, do not write the file.

---

## Phase 5: Commit

After `/archive-batch` returns successfully, commit all batch artifacts in a single commit.

Capture the value for inclusion in Phase 6's final report.

---

## Phase 6: Final Report

```
--=={ pipeline }==--

Source: {source_file}
Batch: {batch_id}

Source processing:
  {DOMAIN:note_plural} produced: {N}
  Enrichments identified: {M}

Processing:
  {DOMAIN:note_plural} created: {N}
  Existing {DOMAIN:note_plural} enriched: {M}
  Connections added: {C}
  {DOMAIN:topic map}s updated: {T}

Quality:
  All verify checks: {PASS/FAIL count}

Archive: ops/queue/archive/{date}-{batch_id}/
Learnings file: ops/queue/archive/{date}-{batch_id}/learnings.md (omitted if no non-NONE learnings)

{DOMAIN:note_plural} created:
- [[claim title 1]]
- [[claim title 2]]
- ...

Files Modified:
- {DOMAIN:note_collection}/ ({N} new {DOMAIN:note_plural})
- ops/queue/archive/{date}-{batch_id}/ (archived)

Learnings (aggregated from all phases):
- [Friction]: {description} | NONE
- [Surprise]: {description} | NONE
- [Methodology]: {description} | NONE
- [Process gap]: {description} | NONE
```

---

## Error Handling

**Phase failure at any stage:**
1. Report the failure with context (which phase, which task, what error)
2. Show the current queue state for this batch
3. Do NOT attempt to continue automatically past failures

**The pipeline is resumable.** Queue state persists across sessions:
- /seed detects prior processing and asks whether to proceed
- /pipeline picks up from the last completed phase (queue is the source of truth)
- /archive-batch verifies completeness before archiving

**Seed failure:** If /seed fails (file not found, duplicate detected and user declines), stop the pipeline entirely.

**Processing failure:** If Phase 2 produces zero notes, report and stop. Do not proceed to an empty processing phase.

## Critical Constraints

**always:**
- Report progress at each phase boundary
- Verify all tasks are done before archiving
- Show the user what was created (list of {DOMAIN:note_plural})
- Suggest next steps if interrupted
- Use domain-native vocabulary from derivation manifest
