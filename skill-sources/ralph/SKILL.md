---
name: ralph
description: Queue processing with fresh context per phase. Processes N tasks from the queue, spawning isolated subagents to prevent context contamination. Supports batch filter and type filter modes. Triggers on "/ralph", "/ralph N", "process queue", "run pipeline tasks".
version: "1.0"
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, Agent
argument-hint: "N [--batch id] [--type process] — N = number of tasks to process"
---

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse arguments:
- N (required): number of tasks to process
- --batch [id]: process only tasks from specific batch
- --type [type]: process only tasks of a specific type (process, note, enrichment)

### Step 0: Read Vocabulary

Read `ops/derivation-manifest.md` (or fall back to `ops/derivation.md`) for domain vocabulary mapping. All output must use domain-native terms. If neither file exists, use universal terms.

**START NOW.** Process queue tasks.

---

## MANDATORY CONSTRAINT: SUBAGENT SPAWNING IS NOT OPTIONAL

**You MUST use the Agent tool to spawn a subagent for EVERY task. No exceptions.**

This is not a suggestion. This is not an optimization you can skip for "simple" tasks. The entire architecture depends on fresh context isolation per phase. Executing tasks inline in the lead session:
- Contaminates context (later tasks run on degraded attention)
- Skips the handoff protocol (learnings are not captured)
- Violates the ralph pattern (one phase per context window)

**If you catch yourself about to execute a task directly instead of spawning a subagent, STOP.** Call the Agent tool. Every time. For every task. Including create tasks. Including "simple" tasks.

The lead session's ONLY job is: read queue, spawn subagent, evaluate return, update queue, repeat.

---

## Phase Configuration

Each phase maps to specific Agent tool parameters. Use these EXACTLY when spawning subagents.

| Phase | Skill Invoked | Purpose |
|-------|---------------|---------|
| process | /extract, /structure, or /capture (based on task.granularity) | Extract notes from source material |
| create | /create | Write the {DOMAIN:note} file with schema validation |
| enrich | (inline enrichment) | Add content to existing {DOMAIN:note} |
| reflect | /reflect | Find connections, update {DOMAIN:topic map}s |
| reweave | /reweave | Update older {DOMAIN:note_plural} with new connections |
| verify | /verify | Description quality + schema + health checks |

---

## Step 1: Read Queue State

Read the queue file. Check these locations in order:
1. `ops/queue.yaml`
2. `ops/queue/queue.yaml`
3. `ops/queue/queue.json`

Parse the queue. Identify ALL pending tasks.

**Queue structure (v2 schema):**

The queue uses `current_phase` and `completed_phases` per task entry:

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

If the queue file does not exist or is empty, report: "Queue is empty. Use /seed or /pipeline to add sources."

## Step 2: Filter Tasks

Build a list of **actionable tasks** — tasks where `status == "pending"`. Order by position in the tasks array (first = highest priority).

Apply filters:
- If `--batch` specified: keep only tasks where `batch` matches
- If `--type` specified: keep only tasks where `type` matches (e.g., `--type process` finds process tasks, `--type note` finds note tasks)

The `phase_order` header defines the phase sequence:
- `note`: create -> reflect -> reweave -> verify
- `enrichment`: enrich -> reflect -> reweave -> verify

**For `type: "process"` tasks:**
Read `task.granularity` to determine which skill to invoke:
- `"extract"` → spawn /extract worker
- `"structure"` → spawn /structure worker
- `"capture"` → spawn /capture worker

## Step 3: Process Loop

Process up to N tasks (default 1). For each iteration:

### 3a. Select Next Task

Pick the first pending task from the filtered list. Read its metadata: `id`, `type`, `file`, `target`, `batch`, `current_phase`, `completed_phases`.

The `current_phase` determines which skill to invoke.

Report:
```
=== Processing task {i}/{N}: {id} — phase: {current_phase} ===
Target: {target}
File: {file}
```

### 3b. Build Subagent Prompt

Construct a prompt based on `current_phase`. Every prompt MUST include:
- Reference to the task file path (from queue's `file` field)
- The task identity (id, current_phase, target)
- The skill to invoke
- `ONE PHASE ONLY` constraint

**Phase-specific prompts:**

For **process** phase (type=process tasks only):
```
Read the task file at ops/queue/{FILE} for context.

You are processing task {ID} from the work queue.
Phase: process | Target: {TARGET}
Granularity: {GRANULARITY} (from task.granularity)

Run /{GRANULARITY_SKILL} on the source file referenced in the task file.
(granularity "extract" → /extract, "structure" → /structure, "capture" → /capture)
After processing: create per-note task files, update the queue with new entries
(1 entry per note with type: note, current_phase/completed_phases), output RALPH HANDOFF.
ONE PHASE ONLY. Do NOT run reflect or other phases.
```

For **create** phase:
```
Read the /create skill and the task file at ops/queue/{FILE}.

You are processing task {ID} from the work queue.
Phase: create | Target claim: {TARGET}

Follow the /create skill instructions for this task file.
ONE PHASE ONLY. Do NOT run reflect.
```

For **enrich** phase:
```
Read the task file at ops/queue/{FILE} for context.

You are processing task {ID} from the work queue.
Phase: enrich | Target: {TARGET}

The task file frontmatter specifies which existing {DOMAIN:note} to enrich (target_note)
and what to add (addition, source_lines).

Enrich the existing {DOMAIN:note}:
1. Read the target {DOMAIN:note} file
2. Read the source lines referenced in the task file
3. Integrate the new content into the existing {DOMAIN:note}:
   - Weave new detail into existing body (don't append a disconnected section)
   - Preserve the {DOMAIN:note}'s voice and structure
   - Update description in frontmatter if the addition materially changes scope
4. If enrichment causes the {DOMAIN:note} to cover multiple distinct claims,
   set post_enrich_action: split-recommended in the task file
5. If the title no longer fits after integration,
   set post_enrich_action: title-sharpen in the task file
6. If the {DOMAIN:note} now substantially overlaps another,
   set post_enrich_action: merge-candidate in the task file
7. Update the task file's ## Enrich section with what was changed and why
ONE PHASE ONLY. Do NOT run reflect.
```

For **reflect** phase:

**Build sibling list:** Query the queue for other claims in the same batch where `completed_phases` includes "create" (note already exists). Format as wiki links.

```
Read the task file at ops/queue/{FILE} for context.

You are processing task {ID} from the work queue.
Phase: reflect | Target: {TARGET}

OTHER CLAIMS FROM THIS BATCH (check connections to these alongside regular discovery):
{for each sibling in batch where completed_phases includes "create":}
- [[{SIBLING_TARGET}]]
{end for, or "None yet" if this is the first claim}

Run /reflect on: {TARGET}
Use dual discovery: {DOMAIN:topic map} exploration AND semantic search.
Add inline links where genuine connections exist — including sibling claims listed above.
Update relevant {DOMAIN:topic map} with this {DOMAIN:note}.
ONE PHASE ONLY. Do NOT run reweave.
```

For **reweave** phase:

**Same sibling list** as reflect (re-query queue for freshest state):

```
Read the task file at ops/queue/{FILE} for context.

You are processing task {ID} from the work queue.
Phase: reweave | Target: {TARGET}

OTHER CLAIMS FROM THIS BATCH:
{for each sibling in batch where completed_phases includes "create":}
- [[{SIBLING_TARGET}]]
{end for}

Run /reweave for: {TARGET}
This is the BACKWARD pass. Find OLDER {DOMAIN:note_plural} AND sibling claims
that should reference this {DOMAIN:note} but don't.
Add inline links FROM older {DOMAIN:note_plural} TO this {DOMAIN:note}.
ONE PHASE ONLY. Do NOT run verify.
```

For **verify** phase:
```
Read the task file at ops/queue/{FILE} for context.

You are processing task {ID} from the work queue.
Phase: verify | Target: {TARGET}

Run /verify on: {TARGET}
Combined verification: recite (cold-read prediction test), validate (schema check),
review (per-note health).
IMPORTANT: Recite runs FIRST — read only title+description, predict content,
THEN read full {DOMAIN:note}.
Final phase for this claim. ONE PHASE ONLY.
```

### 3c. Spawn Subagent (MANDATORY — NEVER SKIP)

Call the Agent tool with the constructed prompt:

```
Agent(
  prompt = {the constructed prompt from 3b},
  description = "{current_phase}: {short target}" (5 words max)
)
```

**REPEAT: You MUST call the Agent tool here.** Do NOT execute the prompt yourself. Do NOT "optimize" by running the task inline. The Agent tool call is the ONLY acceptable action at this step.

Wait for the subagent to complete and capture its return value.

### 3d. Evaluate Return

When the subagent returns:

1. **Look for RALPH HANDOFF block** — search for `=== RALPH HANDOFF` and `=== END HANDOFF ===` markers
2. **If handoff found:** Parse the Work Done, Learnings, and Queue Updates sections
3. **If handoff missing:** Log a warning but continue — the work was still completed
4. **Capture learnings:** If Learnings section has non-NONE entries, note them for the final report

### 3e. Update Queue (Phase Progression)

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

### 3f. Report Progress

```
=== Task {id} complete ({i}/{N}) ===
Phase: {current_phase} -> {next_phase or "done"}
```

If learnings were captured, show a brief summary.
If more unblocked tasks exist, show the next one.

### 3g. Re-filter Tasks

Before the next iteration, re-read the queue and re-filter tasks. Phase advancement may have changed eligibility (e.g., after completing a `create` phase, the task is now at `reflect` — if filtering by `--type reflect`, it becomes eligible).

---

## Step 4: Post-Batch Cross-Connect

After advancing a task to "done" (Step 3e), check if ALL tasks in that batch now have `status: "done"`. If yes and the batch has 2 or more completed claims:

1. **Collect all note paths** from completed batch tasks. For each claim task with `status: "done"`, read the task file's `## Create` section to find the created note path.

2. **Spawn ONE subagent** for cross-connect validation:
```
Agent(
  prompt = "You are running post-batch cross-connect validation for batch '{BATCH}'.

Notes created in this batch:
{list of ALL note titles + paths from completed batch tasks}

Verify sibling connections exist between batch notes. Add any that were missed
because sibling notes did not exist yet when the earlier claim's reflect ran.
Check backward link gaps. Output RALPH HANDOFF block when done.",
  description = "cross-connect: batch {BATCH}"
)
```

3. **Parse handoff block**, capture learnings. Include cross-connect results in the final report.

**Skip if:** batch has only 1 claim (no siblings) or tasks from the batch are still pending.

---

## Step 5: Final Report

After all iterations (or when no unblocked tasks remain):

```
--=={ ralph }==--

Processed: {count} tasks
  {breakdown by phase type}

Subagents spawned: {count} (MUST equal tasks processed)

Learnings captured:
  {list any friction, surprises, methodology insights, or "None"}

Queue state:
  Pending: {count}
  Done: {count}
  Phase distribution: {create: N, reflect: N, reweave: N, verify: N}

Next steps:
  {if more pending tasks}: Run /ralph {remaining} to continue
  {if batch complete}: Run /archive-batch {batch-id}
  {if queue empty}: All tasks processed
```

**Verification:** The "Subagents spawned" count MUST equal "Tasks processed." If it does not, the lead executed tasks inline — this is a process violation. Report it as an error.

Also output the RALPH HANDOFF block:

```
=== RALPH HANDOFF: orchestration ===
Target: queue processing

Work Done:
- Processed {count} tasks: {list of task IDs}
- Types: {breakdown by type}

Learnings:
- [Friction]: {description} | NONE
- [Surprise]: {description} | NONE
- [Methodology]: {description} | NONE
- [Process gap]: {description} | NONE

Queue Updates:
- Marked done: {list of completed task IDs}
=== END HANDOFF ===
```

---

## Error Recovery

**Subagent crash mid-phase:** The queue still shows `current_phase` at the failed phase. The task file confirms the corresponding section is empty. Re-running `/ralph` picks it up automatically — the task is still pending at that phase.

**Queue corruption:** If the queue file is malformed, report the error and stop. Do NOT attempt to fix it automatically.

**All tasks blocked:** Report which tasks are blocked and why. Suggest remediation.

**Empty queue:** Report "Queue is empty. Use /seed or /pipeline to add sources."

---

## Quality Gates

### Gate 1: Subagent Spawned
Every task MUST be processed via Agent tool. If the lead detects it executed a task inline, log this as an error and flag it in the final report.

### Gate 2: Handoff Present
Every subagent SHOULD return a RALPH HANDOFF block. If missing: log warning, mark task done, continue.

### Gate 3: Process Yield
For process tasks: if zero notes extracted, log as an observation. Do NOT retry automatically.

### Gate 4: Task File Updated
After each phase, the task file's corresponding section (Create, Reflect, Reweave, Verify) should be filled. If empty after subagent completes, log warning.

---

## Critical Constraints

**Never:**
- Execute tasks inline in the lead session (USE THE AGENT TOOL)
- Process more than one phase per subagent (context contamination)
- Retry failed tasks automatically without human input
- Skip queue phase advancement (breaks pipeline state)
- Process tasks that are not in pending status
- Run if queue file does not exist or is malformed

**Always:**
- Spawn a subagent via Agent tool for EVERY task (the lead ONLY orchestrates)
- Include sibling claim titles in reflect and reweave prompts
- Re-read queue after extract tasks (subagent adds new entries)
- Re-filter tasks between iterations (phase advancement creates new eligibility)
- Log learnings from handoff blocks
- Report failures clearly for human review
- Verify subagent count equals task count in final report
