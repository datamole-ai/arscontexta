---
name: pipeline
description: End-to-end source processing -- seed, extract/structure/capture, process all notes through reflect/reweave/verify, archive. The full pipeline in one command. Triggers on "/pipeline", "/pipeline [file]", "process this end to end", "full pipeline".
version: "1.0"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
argument-hint: " [file path] [--extract] [--structure] [--capture]
---

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse immediately:
- Source file path: the file to process (required)
- If target is empty: list files in {DOMAIN:inbox}/ and ask which to process

**Granularity flag:**
- `--extract`: use /extract for Phase 2
- `--structure`: use /structure for Phase 2 (default if no flag given)
- `--capture`: use /capture for Phase 2
- If no flag: present three options and ask user before proceeding

### Step 0: Read Vocabulary

Read `ops/derivation-manifest.md` (or fall back to `ops/derivation.md`) for domain vocabulary mapping. All output must use domain-native terms. If neither file exists, use universal terms.

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
Phase 3: /archive-batch — move task files, generate summary
    |
    v
Complete
```

/pipeline is the orchestrator. /seed is the entry point for Phase 1; /pipeline drives Phase 2 and invokes /archive-batch for Phase 3.

---

## Phase 1: Seed

Use Skill tool to invoke /seed on the target file with the granularity flag to create the process task, check for duplicates, and move the source to its archive folder.

**Capture from seed output:**
- **Batch ID**: the source basename
- **Archive folder path**: where the source was moved
- **next_claim_start**: the claim numbering start

Report: `$ Seeded: {source-name}`

---

## Phase 2: Process Source (Granularity-Routed) and claims

Process the source via the appropriate skill based on granularity, extracting notes from the source and creating task entries in the queue.

### Phase 2 configuration

| Phase | Skill Invoked | Purpose |
|-------|---------------|---------|
| process | /extract, /structure, or /capture (based on task.granularity) | Extract notes from source material |
| create | /create | Write the {DOMAIN:note} file with schema validation |
| enrich | (inline enrichment) | Add content to existing {DOMAIN:note} |
| reflect | /reflect | Find connections, update {DOMAIN:topic map}s |
| reweave | /reweave | Update older {DOMAIN:note_plural} with new connections |
| verify | /verify | Description quality + schema + health checks |

### Phase 2.1 Queue State

Read the queue file. `ops/queue/queue.json`

Parse the queue. Identify ALL pending tasks.

### Queue Schema

```yaml
phase_order:
  note: [create, reflect, reweave, verify]
  enrichment: [enrich, reflect, reweave, verify]

tasks:
  - id: source-name
    type: process
    granularity: extract
    status: pending
    source: ops/queue/archive/2026-01-30-source/source.md
    file: source-name.md
    created: "2026-01-30T10:00:00Z"

  - id: note-010
    type: note
    status: pending
    target: "note title here"
    batch: source-name
    file: source-name-010.md
    current_phase: reflect
    completed_phases: [create]
```

If the queue file does not exist or is empty, report: "Queue is empty. Use /pipeline to add sources."

### Phase 2.2 Filter Tasks

Build a list of **actionable tasks** — tasks where `status == "pending"`. Order by position in the tasks array (first = highest priority).

The `phase_order` header defines the phase sequence:
- `note`: create -> reflect -> reweave -> verify
- `enrichment`: enrich -> reflect -> reweave -> verify

**For `type: "process"` tasks:**
Read `task.granularity` to determine which skill to invoke:
- `"extract"` → invoke /extract skill
- `"structure"` → invoke /structure skill
- `"capture"` → invoke /capture skill

### Phase 2.3 Loop

Process the filtered tasks in a loop. For each iteration:

### Phase 2.3.1 Select Next Task

Pick the first pending task from the filtered list. Read its queue metadata.

Report:
```
=== Processing task {i}/{N}: {id} — phase: {current_phase} ===
Target: {target}
File: {file}
```

### Phase 2.3.2 Invoke Skill

| Current Phase | Skill to invoke |
|-------|-----------------|
| process | /extract, /structure, /capture based on granularity|
| create | /create |
| enrich | /enrich |
| reflect | /{vocabulary.reflect} |
| reweave | /{vocabulary.reweave} |
| verify | /{vocabulary.verify} |

Use Skill tool to invoke the appropriate skill based on the task's `current_phase` and `granularity`.

Pass the `task.file` as argument to the skill.

### Phase 2.3.3 Evaluate Return

When the subagent returns:

1. **Look for HANDOFF block** — search for `=== HANDOFF:` and `=== END HANDOFF ===` markers
2. **Parse handoff block:** Parse the Work Done, Learnings, and Queue Updates sections
3. **Capture learnings:** If Learnings section has non-NONE entries, note them for the final report

### Phase 2.3.4 Update Queue (Phase Progression)

After evaluating the return, advance the task to the next phase.

**Phase progression logic:**

Look up `phase_order` from the queue header to determine the next phase. Find `current_phase` in the array. If there is a next phase, advance. If it is the last phase, mark done.

**If NOT the last phase** — advance to next:
- Set `current_phase` to the next phase in the sequence
- Append the completed phase to `completed_phases`

**If the last phase** (verify) — mark task done:
- Set `status: done`
- Set `completed` to current UTC timestamp
- Set `current_phase` to null
- Append the completed phase to `completed_phases`

**For process tasks ONLY:** Re-read the queue after marking done. The processing skill (/extract, /structure, or /capture) writes new task entries (1 entry per note/enrichment with `current_phase`/`completed_phases`) to the queue during execution. The lead must pick these up for subsequent iterations.

### Phase 2.3.6 Report Progress

```
=== Task {id} complete ({i}/{N}) ===
Phase: {current_phase} -> {next_phase or "done"}
```

If learnings were captured, show a brief summary.
If more unblocked tasks exist, show the next one.

### Phase 2.3.7 Re-filter Tasks

Before the next iteration, re-read the queue and re-filter tasks. Phase advancement may have changed eligibility.

---

## Phase 2.4: Post-Batch Cross-Connect

After advancing a task to "done" (Phase 2.3.4), check if ALL tasks in that batch now have `status: "done"`. If yes and the batch has 2 or more completed claims:

1. **Collect all note paths** from completed batch tasks. For each claim task with `status: "done"`, read the task file's `## Create` section to find the created note path.

2. **Do cross-connect validation**:

Notes created in this batch:
{list of ALL note titles + paths from completed batch tasks}

Verify sibling connections exist between batch notes. Add any that were missed
because sibling notes did not exist yet when the earlier claim's reflect ran.
Check backward link gaps.

**Skip if:** batch has only 1 claim (no siblings) or tasks from the batch are still pending.

---

## Phase 3: Verify Completion

After Phase 2 finishes, verify all tasks for this batch are done.

Check the queue: count tasks for this batch that are NOT done.

**If tasks remain pending:**
- Report which tasks are incomplete and at which phase
- Show the specific task IDs and their current_phase
- Do NOT proceed to archive

**If all tasks are done:** Proceed to Phase 4.

---

## Phase 4: Archive Batch

When all tasks for the batch are complete, archive the batch by using Skill tool to invoke /archive-batch.

---

## Phase 5: Final Report

```
--=={ pipeline }==--

Source: {source_file}
Batch: {batch_id}

Extraction:
  {DOMAIN:note_plural} extracted: {N}
  Enrichments identified: {M}

Processing:
  {DOMAIN:note_plural} created: {N}
  Existing {DOMAIN:note_plural} enriched: {M}
  Connections added: {C}
  {DOMAIN:topic map}s updated: {T}
  Older {DOMAIN:note_plural} updated via reweave: {R}

Quality:
  All verify checks: {PASS/FAIL count}

Archive: ops/queue/archive/{date}-{batch_id}/
Summary: {batch_id}-summary.md

{DOMAIN:note_plural} created:
- [[claim title 1]]
- [[claim title 2]]
- ...

Files Modified:
- {DOMAIN:note_collection}/ ({N} new {DOMAIN:note_plural})
- ops/queue/archive/{date}-{batch_id}/ (archived)

Learnings:
- [Friction]: {description} | NONE
- [Surprise]: {description} | NONE
- [Methodology]: {description} | NONE
- [Process gap]: {description} | NONE

Queue Updates:
- All tasks for batch {batch_id} marked done and archived
=== END HANDOFF ===
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

**Extract failure:** If Phase 2 extracts zero notes, report and stop. Do not proceed to an empty processing phase.

## Critical Constraints

**always:**
- Report progress at each phase boundary
- Verify all tasks are done before archiving
- Show the user what was created (list of {DOMAIN:note_plural})
- Suggest next steps if interrupted
- Use domain-native vocabulary from derivation manifest
