# Feature: Processing Pipeline

## Context File Block

```markdown
## Processing Pipeline

**Depth over breadth. Quality over speed. Tokens are free.**

Every piece of content follows the same path: capture, then {DOMAIN:process}, then {DOMAIN:connect}, then {DOMAIN:verify}. Each phase has a distinct purpose. Mixing them degrades both.

### The Four-Phase Skeleton

#### Phase 1: Capture

Zero friction. Everything enters through {DOMAIN:inbox/}. Speed of capture beats precision of filing. Your role here is passive: accept whatever arrives, no structuring at capture time.

{DOMAIN:Process} happens later, in fresh context with full attention. Capture and {DOMAIN:process} are temporally separated because context is freshest at capture but quality requires focused attention. If you try to capture AND process simultaneously, you will either capture slowly (losing insights to friction) or process poorly (rushing connections).

Capture everything. Process later.

#### Phase 2: {DOMAIN:Process}

This is where value is created. Raw content becomes structured {DOMAIN:notes} through active transformation.

Read the source material through the mission lens: "Does this serve {DOMAIN:the knowledge domain}?" Every insight worth keeping gets pulled into a {DOMAIN:note}:

| Category | What to Find | Output |
|----------|--------------|--------|
| Core {DOMAIN:claims} | Direct assertions about the domain | {DOMAIN:note} |
| Patterns | Recurring structures across sources | {DOMAIN:note} |
| Tensions | Contradictions or conflicts | Tension note |
| Enrichments | Content that improves existing {DOMAIN:notes} | Enrichment task |
| Anti-patterns | What breaks, what to avoid | Problem note |

**Quality filter:** Not every insight survives. You must judge: does this add genuine value, or is it noise? When in doubt, keep it — it is easier to merge duplicates than recover missed insights.

**Quality bar for {DOMAIN:notes}:**
- Title works as prose when linked: `since [[{DOMAIN:note title}]]` reads naturally
- Description adds information beyond the title
- Claim is specific enough to disagree with
- Reasoning is visible — shows the path to the conclusion

#### Phase 3: {DOMAIN:Connect}

After {DOMAIN:processing} creates new {DOMAIN:notes}, connection finding integrates them into the existing knowledge graph.

**Forward connections:** What existing {DOMAIN:notes} relate to this new one? Search semantically (not just keyword) because connections often exist between {DOMAIN:notes} that use different vocabulary for the same concept.

**Backward connections:** What older {DOMAIN:notes} need updating now that this new one exists? A {DOMAIN:note} written last week was written with last week's understanding. If today's {DOMAIN:note} extends, challenges, or provides evidence for the older one, update the older one.

**{DOMAIN:Topic map} updates:** Every new {DOMAIN:note} belongs in at least one {DOMAIN:topic map}. Add it with a context phrase explaining WHY it belongs — bare links without context are useless for navigation.

**Connection quality standard:** Not just "related to" but "extends X by adding Y" or "contradicts X because Z." Every connection must articulate the relationship.

#### The Reweaving Philosophy

The backward pass is not about adding links. It is about asking: **"If I wrote this {DOMAIN:note} today, what would be different?"**

{DOMAIN:Notes} are living documents, not finished artifacts. A {DOMAIN:note} written last month was written with last month's understanding. Since then: new {DOMAIN:notes} exist, understanding deepened, the claim might need sharpening, what was one idea might now be three. Reweaving is completely reconsidering a {DOMAIN:note} based on current knowledge.

**What reweaving can do:**

| Action | When |
|--------|------|
| Add connections | Newer {DOMAIN:notes} exist that should link here |
| Rewrite content | Understanding evolved, prose should reflect it |
| Sharpen the claim | Title is too vague to be useful |
| Split the {DOMAIN:note} | Multiple claims bundled together |
| Challenge the claim | New evidence contradicts the original |

Without reweaving, the vault becomes a graveyard of outdated thinking that happens to be organized. With reweaving, every {DOMAIN:note} stays current — reflecting today's understanding, not historical understanding.

**The complete maintenance cycle:**
~~~
CREATE -> CONNECT FORWARD (/{DOMAIN:connect}) -> REVISIT -> QUESTION/REWRITE/SPLIT (/{DOMAIN:maintain}) -> EVOLVE
~~~

#### Phase 4: {DOMAIN:Verify}

Three checks in one phase:

1. **Description quality (cold-read test)** — Read ONLY the title and description. Without reading the body, predict what the {DOMAIN:note} contains. Then read the body. If your prediction missed major content, the description needs improvement. This is the testing effect applied to vault quality: self-testing reveals weak descriptions before they cause retrieval failures in practice.

2. **Schema compliance** — All required fields present, enum values valid, {DOMAIN:topic} links exist, no unknown fields. The template `_schema` block defines what is valid.

3. **Health check** — No broken wiki links (every `[[target]]` resolves to an existing file), no orphaned {DOMAIN:notes} (every {DOMAIN:note} appears in at least one {DOMAIN:topic map}), link density within healthy range (2+ outgoing links per {DOMAIN:note}).

**Failure handling:** Description quality failures get fixed immediately (rewrite the description). Schema failures get fixed immediately (add missing fields). Link failures get logged for the {DOMAIN:connect} phase to address in the next pass.

### Inbox Processing

Everything enters through {DOMAIN:inbox/}. Do not think about structure at capture time — just get it in.

**What goes to inbox:**
- URLs with a brief note about why they matter
- Quick ideas and observations
- Sources (PDFs, articles, research results)
- Anything where destination is unclear

**Processing inbox items:** Inbox items get processed via /structure or /capture based on source material and user intent. Research papers, meeting notes, and mixed-topic sources → /structure. Verbatim transcripts and reference documents where exact wording matters → /capture.

**The core principle:** Capture needs to be FAST (zero friction, do not interrupt flow). Processing needs to be SLOW (careful extraction, quality connections). Separating these two activities is what makes both work. If it is in {DOMAIN:inbox/}, it is unprocessed. Once processed, the value moves to {DOMAIN:notes} and the raw material gets archived or discarded.

### Processing Principles

- **Fresh context per phase** — Do not run all phases in one session. Each phase benefits from focused attention. Your attention degrades as context fills, so critical work should happen when your context is fresh.
- **Quality over speed** — One well-connected {DOMAIN:note} is worth more than ten orphaned ones. The graph compounds quality, not quantity.
- **The generation effect** — Moving information is not processing. You must TRANSFORM it: generate descriptions, find connections, create synthesis. Passive transfer does not create understanding.
- **Skills encode methodology** — If a {DOMAIN:skill} exists for a processing step, use it. Do not manually replicate the workflow. {DOMAIN:Skills} contain quality gates that manual execution bypasses.

### Task Management Architecture

Processing multiple {DOMAIN:notes} through a multi-phase pipeline requires tracking. Without it, {DOMAIN:notes} get stuck mid-pipeline, phases get skipped, and you lose visibility into what has been done and what remains.

#### Task Queue

The task queue tracks every {DOMAIN:note} being processed through the pipeline. It lives at `ops/queue/queue.json` with a simple structure:

~~~json
{
  "tasks": [
    {
      "id": "source-name-001",
      "type": "note",
      "granularity": "structure",
      "status": "pending",
      "target": "{DOMAIN:note} title here",
      "target_path": "{DOMAIN:note_collection}/path/to/note.md",
      "batch": "source-name",
      "created": "2026-02-13T10:00:00Z",
      "current_phase": "{DOMAIN:connect}",
      "completed_phases": ["{DOMAIN:process}"]
    }
  ]
}
~~~

**Phase tracking:** Each {DOMAIN:note} has ONE queue entry. Phase progression is tracked via `current_phase` (the next phase to run) and `completed_phases` (what is already done). After each phase completes: append the current phase to `completed_phases`, advance `current_phase` to the next in sequence. When the last phase completes: set `status` to `"done"`.

**Task types:**

| Type | Purpose | Phase Sequence |
|------|---------|---------------|
| process | Process source through chosen granularity skill (/structure or /capture) — materializes all notes and enrichments inline | (single phase) |
| note | A newly materialized {DOMAIN:note} flows through downstream phases | {DOMAIN:connect} -> {DOMAIN:maintain} -> {DOMAIN:verify} |
| enrichment | An existing {DOMAIN:note} was modified inline during process; still flows through downstream phases | {DOMAIN:connect} -> {DOMAIN:maintain} -> {DOMAIN:verify} |

**Recovery:** If you crash mid-phase, the queue still shows `current_phase` at the failed phase. The task file confirms the corresponding section is empty. Re-running the pipeline picks it up automatically — no manual intervention needed.

#### Per-{DOMAIN:Note} Task Files

Each {DOMAIN:note} gets its own task file that accumulates notes across all phases. The task file is the shared state between phases — it is how one phase communicates what it found to the next phase.

~~~markdown
# {DOMAIN:Note} 001: {title}

## {DOMAIN:Process} Notes
{Processing rationale, duplicate judgment}

## Materialize
{Note path, template used, validation result — OR for enrichments: target path and integration mode}

## {DOMAIN:Connect}
{Connections found, {DOMAIN:topic maps} updated}

## {DOMAIN:Maintain}
{Older {DOMAIN:notes} updated with backward connections}

## {DOMAIN:Verify}
{Description quality result, schema result, health result}
~~~

**Why task files matter:** Each phase reads the task file in fresh context. Downstream phases see what upstream phases discovered. Without this, context would be lost between sessions. The task file IS the memory of the pipeline.

**Batch archival:** When all {DOMAIN:notes} from a source reach `"done"`, the batch is archivable. Archival moves task files to `ops/queue/archive/{date}-{source}/`, generates a summary capturing what the batch produced, and cleans the queue.

#### Maintenance via /health (Diagnostic, On-Demand)

Maintenance is diagnostic, not queued. The pipeline queue holds pipeline tasks only (process, reflect, reweave, verify). Vault health is evaluated on demand by /health, which reports fired conditions with specific files and ranked actions.

**Maintenance conditions (evaluated by /health):**

| Signal | Threshold | Action |
|--------|-----------|--------|
| Observations pending | >=10 | Suggest /{DOMAIN:rethink} |
| Tensions pending | >=5 | Suggest /{DOMAIN:rethink} |
| {DOMAIN:Topic map} size | >40 {DOMAIN:notes} | Suggest split |
| Orphan {DOMAIN:notes} | Any | Flag for connection finding |
| Dangling links | Any | Flag for resolution |
| Inbox age | >3 days | Suggest processing |
| Pipeline batch stalled | >2 sessions without progress | Surface as blocked |

**Impact-based ranking** (highest to lowest):

| Impact Tier | Examples |
|-------------|----------|
| Highest | Dangling links, persistent orphans |
| High | Schema violations, boundary violations |
| Medium | Description quality, stale notes |
| Low | {DOMAIN:Topic map} size warnings, throughput ratio |

The session-start orientation shows queue status; /health runs the full diagnostic when invoked. This is reconciliation-based diagnosis — /health tells you what needs attention based on measured state, with no maintenance queue to keep clean.

### Orchestrated Processing (Fresh Context Per Phase)

The pipeline's quality depends on each phase getting your best attention. Your context degrades as conversation grows. The first ~40% of your context window is the "smart zone" — sharp, capable, good decisions. Beyond that, context rot sets in. Chaining multiple phases in one session means later phases run on degraded attention.

**The orchestration pattern:**

~~~
Orchestrator reads queue -> picks next task -> invokes phase skill for one phase
  Phase skill (forked context): reads task file, executes phase, writes results to task file
  Phase skill returns -> Orchestrator reads results -> advances queue -> invokes next phase skill
~~~

**Why fresh context matters:**
- {DOMAIN:Process} needs full attention on the source material
- {DOMAIN:Connect} needs full attention on the existing knowledge graph
- {DOMAIN:Maintain}/reweave needs full attention on older {DOMAIN:notes}
- {DOMAIN:Verify} needs neutral perspective, unbiased by creation

If all phases run in one session, the verify phase runs on degraded attention — you have already decided this {DOMAIN:note} is good during materialization, and confirmation bias sets in. Fresh context prevents this.

**Handoff through files, not context:**
- Each phase writes its findings to the task file
- The next phase reads the task file in fresh context
- State transfers through persistent files, not accumulated conversation
- This makes crashes recoverable and processing auditable

**Processing is orchestrated by default.** /pipeline orchestrates the full sequence. The queue drives what happens next.

**Orchestration uses the Skill tool** with `context: fork` on each invoked skill, giving each phase a fresh forked context window and true context isolation. The task queue IS the orchestration — {DOMAIN:skills} read from it, write to it, and the queue state drives what happens next. When you say "process this source through the full pipeline," follow the pattern: read queue, pick task, execute phase, advance queue, repeat.

### Full Automation From Day One

Every vault ships with the complete pipeline active from the first session. All processing skills, all quality gates, all maintenance mechanisms are available immediately. You do not need to "level up" or wait for your vault to reach a certain size before using orchestrated processing, fresh context isolation, or queue management.

The philosophy: it is easier to disable features you do not need than to discover and enable features you did not know existed. If a feature exists, it works on day one.

**All skills are available from day one.** /structure, /capture, /{DOMAIN:connect}, /{DOMAIN:maintain}, /{DOMAIN:verify}, /{DOMAIN:health}, and all other skills are ready to invoke on the first source you process. The full pipeline runs on the first {DOMAIN:note} you create.

### Quality Gates Summary

Every phase has specific gates. Failing a gate does not block progress — it triggers correction.

| Phase | Gate | Failure Action |
|-------|------|---------------|
| {DOMAIN:Process} | Selectivity — is this worth extracting? | Skip with logged reason |
| {DOMAIN:Process} | Composability — does the title work as prose? | Rewrite title |
| {DOMAIN:Process} | Description adds new info beyond title? | Rewrite description |
| {DOMAIN:Process} | Duplicate check — semantic search run? | Run search, merge if duplicate |
| {DOMAIN:Connect} | Genuine relationship — can you say WHY? | Do not force the connection |
| {DOMAIN:Connect} | {DOMAIN:Topic map} updated | Add {DOMAIN:note} to relevant {DOMAIN:topic maps} |
| {DOMAIN:Connect} | Backward pass — older {DOMAIN:notes} updated? | Update or log for maintenance |
| {DOMAIN:Verify} | Description predicts content (cold-read test) | Improve description |
| {DOMAIN:Verify} | Schema valid | Fix schema violations |
| {DOMAIN:Verify} | No broken links | Fix or remove broken links |
| {DOMAIN:Verify} | {DOMAIN:Note} in at least one {DOMAIN:topic map} | Add to relevant {DOMAIN:topic map} |

**Automation of quality gates:** A PostToolUse hook on Write validates YAML frontmatter, description fields, and topic links on {DOMAIN:note} creation. This makes methodology invisible — instead of remembering to validate, a hook catches drift automatically. Build hooks for any quality check you want to be automatic.

### Skill Invocation Rules

If a {DOMAIN:skill} exists for a task, use the {DOMAIN:skill}. Do not manually replicate the workflow. {DOMAIN:Skills} encode the methodology — manual execution bypasses quality gates.

| Trigger | Required {DOMAIN:Skill} |
|---------|------------------------|
| New content to {DOMAIN:process} | /structure or /capture |
| New {DOMAIN:notes} need connections | /{DOMAIN:connect} |
| Old {DOMAIN:notes} may need updating | /{DOMAIN:maintain} |
| Quality verification needed | /{DOMAIN:verify} |
| System health check | /{DOMAIN:health} |
| User asks to find connections | /{DOMAIN:connect} (not manual grep) |
| System feels disorganized | /{DOMAIN:health} (systematic checks, not ad-hoc) |

**The enforcement principle:** If a {DOMAIN:skill} exists for a task, use the {DOMAIN:skill}. Do not improvise the workflow manually. {DOMAIN:Skills} encode the methodology. Manual execution loses the quality gates.

### Session Discipline

Each session focuses on ONE task. Discoveries become future tasks, not immediate tangents.

Your attention degrades as context fills. The first ~40% of context is the "smart zone" — sharp, capable, good decisions. Beyond that, context rot sets in. Structure each task so critical information lands early. When processing multiple {DOMAIN:notes}, use fresh context per {DOMAIN:note} — never chain phases in one session.

**The handoff protocol:** Every phase writes its findings to the task file. The next phase reads the task file in fresh context. State transfers through files, not through accumulated conversation. This ensures:
- No context contamination between phases
- Each phase gets your best attention
- Crashes are recoverable (the task file shows where processing stopped)
- Multiple {DOMAIN:notes} can be processed without degradation

## Dependencies
Requires: yaml-schema, wiki-links, atomic-notes, mocs

## Skills Referenced
- structure (group related claims into structured notes)
- capture (preserve source verbatim with frontmatter)
- {DOMAIN:connect} (find connections, update topic maps)
- {DOMAIN:maintain} (backward pass, update old notes)
- {DOMAIN:verify} (combined quality gate: description, schema, links)
- {DOMAIN:health} (systematic health checks)
- {DOMAIN:rethink} (review accumulated observations and tensions)
