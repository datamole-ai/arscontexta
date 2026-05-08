---
name: pipeline
description: End-to-end source processing -- seed, structure/capture, process all notes through connect/verify, archive. The full pipeline in one command. Triggers on "/pipeline", "/pipeline [file]", "process this end to end", "full pipeline".
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
Phase 4.6: Sync semantic index
    |
    v
Phase 5: Commit — single batch commit if in a git repo
    |
    v
Complete
```

/pipeline is the orchestrator. /seed is the entry point for Phase 1; /pipeline drives Phase 2, invokes /archive-batch for Phase 4, and produces the batch commit as Phase 5.

## Output Contract for Sub-skills

Every sub-skill (seed, structure, capture, connect, verify, archive-batch) emits a single fenced JSON block as its final chat message. The block is the canonical handoff and the only chat output. The orchestrator parses these fields:

- `status` — `"ok"` or `"error"`. On `"error"`, stop the pipeline and surface `error`.
- `batch` — must equal `<batch-id>`.
- `queue` — short human string for the user-facing progress line.
- `created` / `updated` (when present) — paths to include in the final report.
- `learnings` — array of `{category, description}` aggregated for the archive-folder learnings.md.

The orchestrator does NOT re-narrate the JSON. It surfaces a one-line status to the user and moves to the next phase.

### Compact Batch Manifest

After each sub-skill returns, persist its exact JSON object (without markdown fences) to `<archive_folder>/phase-outputs/<phase>.json`, then refresh the compact manifest:

```bash
mkdir -p "<archive_folder>/phase-outputs"
# write the parsed JSON object for the phase, then:
bash ops/scripts/batch-manifest.sh "<batch-id>"
```

Before invoking structure/capture, connect, verify, or archive-batch, refresh the same manifest. Phase skills use `<archive_folder>/batch-manifest.json` as their primary entry point, then read specific source, note, or map files only when needed for correctness. The manifest is durable recovery state: if a run fails, queue state plus `batch-manifest.json` plus `phase-outputs/*.json` must be enough to diagnose where it stopped.

---

## Phase 1: Seed

Use Skill tool to invoke /seed on the target file with the granularity flag to create the process task.

Parse the seed JSON Output Contract:
- `status` — must be `"ok"`; otherwise stop the pipeline and surface `error`.
- `batch`, `archive_folder`, `next_claim_start`, `granularity` — capture for downstream phases.
- `learnings` — collect for the final report.

Persist the seed JSON to `<archive_folder>/phase-outputs/seed.json`, then run `bash ops/scripts/batch-manifest.sh "<batch-id>"`.

Report one line: `Seeded: <batch>` (no JSON re-rendering, no per-field listing).

---

## Phase 2: Process Source (Granularity-Routed) and claims

Process the source via the appropriate producer, then drive each resulting note/enrichment through the phase sequence. Each sub-skill is self-owning: it updates its own entry in `ops/queue/queue.json` and emits its canonical JSON Output Contract to chat. The orchestrator parses each JSON object for `status`, `queue`, paths, and `learnings`, and holds the iteration state in memory.

### Phase 2.1: Invoke the producer

Use the Skill tool to invoke `/structure` or `/capture` (based on the process entry's `granularity` in `queue.json`) passing the batch id as argument:

- `<batch-id>` — the source basename, equal to the process entry's `id`.

Parse the producer's JSON:
- `status` — must be `"ok"`; otherwise stop and surface `error`.
- `created`, `updated`, `quarantined` — capture for the final report.
- `learnings` — collect.

Persist the producer JSON to `<archive_folder>/phase-outputs/structure.json` or `<archive_folder>/phase-outputs/capture.json`, then run `bash ops/scripts/batch-manifest.sh "<batch-id>"`.

### Phase 2.2: Sanity check

Confirm at least one new pending entry exists for `<batch-id>` via the deterministic state script:

```bash
bash ops/scripts/pipeline-state.sh "<batch-id>"
```

Read the JSON and parse `.by_status.pending` (or `.total`). If no pending entries exist, report `Processing produced zero notes` and stop.

### Phase 2.3: Drive the batch through connect, then verify

Two skill invocations total. Both batched skills self-discover their work lists from `ops/queue/queue.json` using the batch id. The orchestrator does not iterate.

#### Phase 2.3.1: Batched connect

Refresh the compact manifest immediately before invoking connect:

```bash
bash ops/scripts/batch-manifest.sh "<batch-id>"
```

Use the Skill tool to invoke `/connect` with the batch id as the only argument:
- `<batch-id>` — the source basename, equal to the process entry's `id`.

Parse the connect JSON:
- `status` — must be `"ok"`; otherwise stop and surface `error`.
- `qmd_queries`, `topic_maps_consulted`, `topic_maps_created`, `evidence` — for the report and audit trail.
- `learnings` — collect.

Persist the connect JSON to `<archive_folder>/phase-outputs/connect.json`, then run `bash ops/scripts/batch-manifest.sh "<batch-id>"`.

Report one line: `<batch-id>: connect done — <queue>`.

#### Phase 2.3.2: Batched verify

Refresh the compact manifest immediately before invoking verify:

```bash
bash ops/scripts/batch-manifest.sh "<batch-id>"
```

Use the Skill tool to invoke `/verify` with the same batch id.

Parse the verify JSON:
- `status` — must be `"ok"`; otherwise stop and surface `error`.
- `vault_scope` and `per_note` — capture failures for the report; do not re-narrate the per-note rows.
- `learnings` — collect.

Persist the verify JSON to `<archive_folder>/phase-outputs/verify.json`, then run `bash ops/scripts/batch-manifest.sh "<batch-id>"`.

Report one line: `<batch-id>: verify done — <queue>`.

The batched skills have already updated `queue.json` atomically by the time their JSON return lands. The orchestrator trusts the JSON signal and does not re-read the file mid-Phase 2.3.

---

## Phase 3: Verify Completion

Run the deterministic readiness check:

```bash
bash ops/scripts/archive-ready.sh "<batch-id>"
```

Parse the JSON. **If `.ready == false`:**
- Report `.blocking` entries — each carries `id`, `current_phase`, `status`.
- Do NOT proceed to archive.

**If `.ready == true`:** proceed to Phase 4.

---

## Phase 4: Archive Batch

Refresh the compact manifest immediately before invoking archive-batch:

```bash
bash ops/scripts/batch-manifest.sh "<batch-id>"
```

When all tasks for the batch are complete, use the Skill tool to invoke /archive-batch.

Parse the archive-batch JSON:
- `status` — must be `"ok"`; otherwise stop and surface `error`.
- `archive_folder`, `notes_produced`, `enrichments` — for the final report.
- `learnings` — collect.

---

## Phase 4.5: Write Learnings

After `/archive-batch` returns successfully, aggregate the `learnings` arrays collected from every phase's JSON Output Contract (seed → producer → connect → verify → archive-batch) and write a consolidated file at `<archive_folder>/learnings.md`.

Group entries by `category`:

```markdown
# Learnings — <batch_id>

## Friction
- <description>
- ...

## Surprise
- ...

## Methodology
- ...

## Process gap
- ...
```

Omit any category whose aggregated list is empty. If every category is empty across all phases, do not write the file.

---

## Phase 4.6: Sync semantic index

```bash
bash .claude/hooks/qmd-sync.sh
```

## Phase 5: Commit

After `/archive-batch` returns successfully, commit all batch artifacts in a single commit:

```bash
bash ops/scripts/commit-batch.sh "<batch-id>" "pipeline: <batch-id>"
```

Parse the JSON. The script returns `committed: true` and the commit hash when work was staged, or `committed: false` with a `reason` when the tree was already clean or the workspace is not a git repo. Capture `.commit` (the hash) for Phase 6's final report.

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
