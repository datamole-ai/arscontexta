---
name: connect
description: Internal pipeline skill — runs forward connection-finding, topic-map updates, sibling cross-linking, and per-note reconsideration across all notes in a batch in one pass. Invoked by /pipeline as a subagent; do not invoke directly.
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

### Task Queue

Current task queue:
!`cat ops/queue/queue.json`

## Granularity-Aware Processing

After reading the target {vocabulary.note}, check its `granularity` frontmatter field. Adjust connection-finding depth:

- **`structure`**: Forward connections at both topic and section level — the {vocabulary.note} as a whole connects to topics, but individual sections may connect to specific existing {vocabulary.note_plural}. Backward connections to {vocabulary.note_plural} relating to any sub-claim. {vocabulary.topic_map} placement with context phrases explaining WHY the {vocabulary.note} belongs.
- **`capture`**: Lighter treatment — scan verbatim content for references to existing topics and {vocabulary.note_plural}. Add wikilinks ONLY outside the fenced block (in Relevant Notes and Topics footer sections). **NEVER modify content inside the fenced block.** {vocabulary.topic_map} placement.

**Connection behavior:** Full dual discovery (MOC + semantic search). Evaluate every candidate. Multiple passes. Synthesis opportunity detection. Bidirectional link evaluation for all connections.

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse the batch id from arguments (e.g. `my-source`). If no argument is provided, end immediately with: report `ERROR: connect requires batch id`.

### Work-list discovery

Read the queue and find every pending entry for this batch awaiting connect:

```bash
BATCH_ID="$ARGUMENTS"
jq --arg batch "$BATCH_ID" \
   '[.tasks[] | select(.batch == $batch and .status == "pending" and .current_phase == "connect")]' \
   ops/queue/queue.json
```

If the work list is empty, end immediately with `Status: ok`, `Queue: no entries to advance`, and an empty per-note results section.

For each work-list entry, the relevant fields are:
- `id` — queue id (e.g. `note-007`, `enrich-002`)
- `target_path` — path to the {vocabulary.note}
- `granularity` — routes connection-finding depth (`structure` | `capture`)
- `type` — `note` or `enrichment`

All subsequent references to "the {vocabulary.note}" inside per-note steps use the entry's `target_path`. Where this skill says "for each note" it means iterating the work list in queue id order.

**START NOW.** Reference below explains methodology — use to guide, not as output.

---

# Connect

Find connections, weave the knowledge graph, update {vocabulary.topic_map_plural}. This is the forward-connection phase of the processing pipeline.

## Philosophy

**The network IS the knowledge.**

Individual {vocabulary.note_plural} are less valuable than their relationships. A {vocabulary.note} with fifteen incoming links is an intersection of fifteen lines of thought. Connections create compound value as the vault grows.

This is not keyword matching. This is semantic judgment — understanding what {vocabulary.note_plural} MEAN to determine how they relate. A {vocabulary.note} about "friction in systems" might deeply connect to "verification approaches" even though they share no words. You are building a traversable knowledge graph, not tagging documents.

**Quality over speed. Explicit over vague.**

Every connection must pass the articulation test: can you say WHY these {vocabulary.note_plural} connect? "Related" is not a relationship. "Extends X by adding Y" or "contradicts X because Z" is a relationship.

Bad connections pollute the graph. They create noise that makes real connections harder to find. When uncertain, do not connect.

## Fabrication Guardrail

Do not add context, motivation, rationale, mechanism explanations, or implication statements that are not in one of:
- the source material cited in the {vocabulary.note}'s footer,
- a linked neighbor {vocabulary.note},
- the vault's stable reference material (identity files, methodology, {vocabulary.topic_map_plural}).

When tempted to explain, either link a neighbor that already explains, or flag the gap for attention. Model-derived framing that looks plausible is still fabrication; once committed to the graph it becomes indistinguishable from attested claims and compounds through later reconsiderations.

## Workflow

Cross-cutting pass. Order is fixed: shared discovery first, then per-note evaluation and linking, then per-note reconsideration. Mutations only happen in Steps 6-9. Steps 1-5 read and plan.

### Step 1: Understand each note (per-note)

For each entry in the work list, do the following on the entry's `target_path`:

Before searching for connections, deeply understand the source material.

For each {vocabulary.note} you are connecting:
1. Read the full {vocabulary.note}, not just title and description
2. Identify the core claim and supporting reasoning
3. Note key concepts, mechanisms, implications
4. Ask: what questions does this answer? What questions does it raise?

**What you are looking for:**
- The central argument (what is being claimed?)
- The mechanism (why/how does this work?)
- The implications (what follows from this?)
- The scope (when does this apply? When not?)
- The tensions (what might contradict this?)

Read the {vocabulary.note}'s body and footer for context. **Two sources are authoritative priors — not hints to verify, but starting points to extend:**

1. The note's `Topics:` footer — every {vocabulary.topic_map} listed there was chosen by the producer phase; those topic maps and their members are in scope by default.
2. The queue entry's `semantic_neighbors` field (when present) — qmd results structure already gathered while routing this cluster. Treat each entry as a candidate connection that has already passed semantic-similarity threshold.

Connect's job is to **extend** these priors — find what structure could not have seen (sibling notes created in this batch, neighbors with shared mechanism but unshared vocabulary, recently-added notes outside structure's view) — not to re-derive them.

### Step 2: Aggregate discovery candidates (shared)

Build the candidate set in this order:

1. **Seed from priors (no search needed).** For each note in the work list, add its Topics-footer entries and its queue entry's `semantic_neighbors` directly to the candidate set. These are already validated — they enter Step 4 as candidates without re-derivation.
2. **Extract gap-fill targets.** For each note, identify concepts mentioned in the body but not represented in the priors. These become the qmd/grep query set in Step 3.
3. **Deduplicate semantically across notes.** If two notes pointed at the same gap concept, that's one query, not two.

The output of this step is the input to Step 3: priors that flow straight through (no search), plus a smaller set of gap-fill queries to issue.

### Step 3: Fill gaps via dual discovery (shared)

Step 2's priors are already in the candidate set. Step 3 runs ONE consolidated pass to fill the gaps Step 2 identified. Use dual discovery: {vocabulary.topic_map} exploration AND semantic search in parallel. These are complementary, not sequential. **qmd and grep are gap-filling — not primary discovery — when priors have already supplied candidates.**

**Primary discovery (run in parallel):**

**Path 1: {vocabulary.topic_map} Exploration** — curated navigation

Read every {vocabulary.topic_map} listed in any work-list note's Topics footer (these are mandatory; the producer phase already chose them):

- Follow curated links in Core Ideas — these are human/agent-curated connections
- Note what is already connected to similar concepts
- Check Tensions and Gaps for context

{vocabulary.topic_map_plural} tell you what thinking exists and how it is organized. Someone already decided what matters for this topic.

**Path 2: Semantic Search** — find what priors and {vocabulary.topic_map_plural} miss

Use `qmd query` via Bash (hybrid search with auto-expansion + reranking) for the gap-fill query set from Step 2. Skip queries that would re-derive what `semantic_neighbors` or Topics-footer entries already cover — issue one query per unique gap concept, not one query per note:

```bash
qmd query "[aggregated core concept or mechanism]" --collection {vocabulary.qmd_collection} -n 15
```

Evaluate results by relevance — read any result where title or snippet suggests genuine connection. Semantic search finds {vocabulary.note_plural} that share MEANING even when vocabulary differs. A {vocabulary.note} about "iteration cycles" might connect to "learning from friction" despite sharing no words.

**Secondary discovery (after primary):**

**Keyword Search**

For specific terms and exact matches:
```bash
grep -r "term" {vocabulary.note_collection}/ --include="*.md"
```

Use grep when:
- You know the exact words that should appear
- Searching for specific terminology or phrases
- Finding all uses of a named concept
- The vocabulary is stable and predictable

**Description Scan**

Use ripgrep to scan {vocabulary.note} frontmatter descriptions for edge cases:
- Does this extend the source {vocabulary.note}?
- Does this contradict or create tension?
- Does this provide evidence or examples?

Flag candidates with a reason (not just "related").

**Link Following**

From promising candidates, follow their existing links:
- What do THEY connect to?
- Are there clusters of related {vocabulary.note_plural}?
- Do chains emerge that any source {vocabulary.note} should join?

This is graph traversal. You are exploring the neighborhood once for the whole batch.

### Step 4: Build the candidate-connection map (shared)

For each note in the work list, filter Step 3's results down to the candidates relevant to that note's claim. The output is a map `{note-id → [candidate connection, ...]}` with each candidate tagged by source (which discovery path surfaced it) and any preliminary relationship hint. Step 4 produces structure, not text — no files mutate yet.

### Step 5: Evaluate connections per note (per-note)

For each note, evaluate its candidate-connection map from Step 4. Apply the articulation test to each candidate.

**The Articulation Test:**

Complete this sentence:
> [[note A]] connects to [[note B]] because [specific reason]

If you cannot fill in [specific reason] with something substantive, the connection fails.

**Valid Relationship Types:**

| Relationship | Signal | Example |
|-------------|--------|---------|
| extends | adds dimension | "extends [[X]] by adding temporal aspect" |
| grounds | provides foundation | "this works because [[Y]] establishes..." |
| contradicts | creates tension | "conflicts with [[Z]] because..." |
| exemplifies | concrete instance | "demonstrates [[W]] in practice" |
| synthesizes | combines insights | "emerges from combining [[A]] and [[B]]" |
| enables | unlocks possibility | "makes [[C]] actionable by providing..." |

**Reject if:**
- The connection is "related" without specifics
- You found it through keyword matching alone with no semantic depth
- Linking would confuse more than clarify
- The relationship is too obvious to be useful

**Agent Traversal Check:**

Ask: **"If an agent follows this link, what do they gain?"**

| Agent Benefit | Keep Link |
|---------------|-----------|
| Provides reasoning foundation (why something works) | YES |
| Offers implementation pattern (how to do it) | YES |
| Surfaces tension to consider (trade-off awareness) | YES |
| Gives concrete example (grounds abstraction) | YES |
| Just "related topic" with no decision value | NO |

The vault is built for agent traversal. Every connection should help an agent DECIDE or UNDERSTAND something. Connections that exist only because they feel "interesting" without operational value are noise.

### Step 6: Topic-map management (shared)

Identify every {vocabulary.topic_map} the batch's notes belong to. For new MOCs, create them once. For existing MOCs, apply all batch additions in one pass. {vocabulary.topic_map_plural} are synthesis hubs, not just indexes.

**When to update a {vocabulary.topic_map}:**

- New {vocabulary.note} belongs in Core Ideas
- New tension discovered
- Gap has been filled
- Synthesis insight emerged
- Navigation path worth documenting

**{vocabulary.topic_map} Size Check:**

After updating Core Ideas, count the links:

```bash
find {vocabulary.note_collection}/ -name "[moc-name].md" -type f -exec grep -c '^\- \[\[' {} +
```

If approaching the split threshold (configurable, default ~40): note in output "{vocabulary.topic_map} approaching split threshold (N links)"
If exceeding: warn "{vocabulary.topic_map} exceeds recommended size — consider splitting"

Splitting is a human decision (architectural judgment required), but /connect should surface the signal.

**{vocabulary.topic_map} Structure:**

```markdown
# [Topic Name]

[Brief orientation: what this topic covers, what questions it addresses, where to start reading. Keep to a paragraph or two. Do NOT write free-form synthesis here — {vocabulary.topic_map_plural} are navigation surfaces with cited observations, not places to assert model-derived insights]

## Core Ideas

- [[claim note]] — what it contributes to understanding
- [[another claim]] — how it fits or challenges existing ideas

## Tensions

- [[claim A]] and [[claim B]] conflict because... [genuine unresolved tension]

## Gaps

- nothing about X aspect yet
- need concrete examples of Y
- missing: comparison with Z approach
```

**Updating Core Ideas:**

Add new {vocabulary.note_plural} with context phrase explaining contribution:
```markdown
- [[new note]] — extends the quality argument by showing how friction teaches you what to check
```

Order matters. Place {vocabulary.note_plural} where they fit the logical flow, not alphabetically.

**Updating Tensions:**

If the new {vocabulary.note} creates or resolves tension:
```markdown
## Tensions

- [[composability]] demands small notes, but [[context limits]] means traversal has overhead. [[new note]] suggests the tradeoff depends on expected traversal depth.
```

Document genuine conflicts. Tensions are valuable, not bugs.

**Updating Gaps:**

Remove gaps that are now filled. Add new gaps discovered during this step.

### Step 7: Sibling cross-linking (cross-cutting)

For any pair of notes (A, B) in the batch where A's evaluated connections include B (or vice versa), apply the Bidirectional Consideration rule (see Step 8 reference material) and add the link(s) inline and in the Relevant Notes footer. Sibling-ness alone does not force a bidirectional link — relationship type controls direction. This step replaces the work the deleted pipeline Phase 2.4 (cross-connect) used to do; there is no separate cross-connect phase.

### Step 8: Apply inline connections + Relevant Notes footer (per-note)

For each note, apply its evaluated connections from Step 5. Sibling links from Step 7 are already in place; do not duplicate. Connections live in the prose, not just footers.

**Inline Links as Prose:**

The wiki link IS the argument. The title works as prose when linked. How it reads depends on granularity:

**Atomic notes (claims)** — the title IS a proposition, link it as one:
```markdown
Since [[throughput matters more than accumulation]], the question becomes who does the selecting.

This works because [[good systems learn from friction]] — each iteration improves the next.
```

**Structure notes (scope)** — the title describes territory, link it as a noun phrase:
```markdown
Building on [[how caching strategies affect API latency under load]], we chose a write-through approach.

Given [[trade-offs between consistency and availability in distributed systems]], eventual consistency was the pragmatic choice.
```

**Capture notes (content)** — the title describes an artifact, link it as a reference:
```markdown
As documented in [[quarterly planning meeting discussing Q3 priorities]], the hiring freeze extends through August.
```

Bad patterns (regardless of granularity):
```markdown
This relates to [[other note]].

See also [[throughput matters more than accumulation]].
```

**Where to add links:**

1. Inline in the body where the connection naturally fits the argument
2. In the body's `Relevant Notes:` footer with a context phrase
3. BOTH when the connection is strong enough

**Relevant Notes Footer Format:**

```markdown
---

Relevant Notes:
- [[note title]] — extends this by adding the temporal dimension
- [[another note]] — provides the mechanism this claim depends on

Topics:
- [[parent-moc]]
```

Context phrases use standard relationship vocabulary: extends, grounds, contradicts, exemplifies, synthesizes, enables.

**Bidirectional Consideration:**

When adding [[A]] to [[B]], ask: should [[B]] also link to [[A]]?

Not always. Relationships are not always symmetric:
- "extends" often is not bidirectional
- "exemplifies" usually goes one direction
- "contradicts" is often bidirectional
- "synthesizes" might reference both sources

Add the reverse link only if following that path would be useful for agent traversal.

### Step 9: Reconsider each note (per-note)

For each note, apply the guards. If guards fire, record `Reconsideration: skipped ({reason})` in the Output Block's per-note line. Otherwise run Sub-phases 6.1 and 6.2.

After forward connections and {vocabulary.topic_map} updates, reconsider the target {vocabulary.note} against the current state of the {vocabulary.note_collection}. Ask: **"What does the graph now say that this {vocabulary.note} does not yet cite?"** — not "what do I know now".

This is the backward pass that keeps the network alive. {vocabulary.note_plural} are living documents — they grow, get rewritten, sharpen their claims.

> "The {vocabulary.note} you wrote yesterday is a hypothesis. Today's knowledge is the test."

**Sub-phase 6 Guards.** Skip reconsideration entirely if ANY of these apply to the target {vocabulary.note}:

| Guard | Rationale |
|-------|-----------|
| `granularity: capture` | Raw capture does not produce new claims that change understanding. |
| Target has >5 incoming links | Already a hub — one more pass does not warrant full reconsideration. |
| Target has `type: tension` in YAML | Structural framework, not content that evolves. |
| Target is a {vocabulary.topic_map} | {vocabulary.topic_map_plural} are navigation, not claims to reconsider. |
| Target was already reconsidered in the current batch | Do not re-reconsider what was just reconsidered. |

**Check incoming links:**
```bash
find {vocabulary.note_collection}/ -name "*.md" -type f -exec grep -l '\[\[target note title\]\]' {} + | wc -l
```

If >= 5, skip reconsideration — record `Reconsideration: skipped (hub)` in the Output Block's per-note line.

If any guard fires, set the per-note line's `Reconsideration:` field to `skipped ({reason})` and proceed directly to the next note. Otherwise continue with Sub-phases 6.1 and 6.2.

#### Sub-phase 6.1: Evaluate the claim

**Does the original claim still hold?**

| Finding | Action |
|---------|--------|
| Claim holds, evidence strengthened | Note in Output Block; Step 8's connection additions already supply evidence |
| Claim holds but framing is weak | Rewrite for clarity (Sub-phase 6.2 action: Rewrite Content) |
| Claim is too vague | Sharpen to be more specific (Sub-phase 6.2 action: Sharpen Claim) |
| Claim is partially wrong | Revise with nuance (Sub-phase 6.2 action: Challenge Claim) |
| Claim is contradicted | Flag tension, propose revision (Sub-phase 6.2 action: Challenge Claim) |

**The Sharpening Test:**

Read the title. Ask: could someone disagree with this specific claim?
- If yes, the claim is sharp enough.
- If no, it is too vague and needs sharpening.

Example:
- Vague: "context matters" (who would disagree?)
- Sharp: "explicit context beats automatic memory" (arguable position)

#### Sub-phase 6.2: Apply changes

Apply changes directly. The pipeline needs to proceed without waiting for approval.

**When applying changes:**

1. Make changes atomically.
2. Preserve existing valid content.
3. Maintain prose flow — new wording reads naturally inline.
4. Verify all link targets exist.
5. Update description if the claim changed.

**The Reconsideration Actions.**

##### Rewrite Content

Prose may need improvement. The constraint: every sentence in the rewrite must cite source or a neighbor {vocabulary.note}. Do not substitute model knowledge for either.

**When to rewrite:**
- A cited neighbor now supplies the reasoning more clearly.
- Source evidence surfaced that sharpens a claim.
- Phrasing is awkward — prose polish that does not mutate claims.

**When NOT to rewrite:**
- "Reasoning is clearer now" — clearer by whose authority? Unless a cited neighbor or source passage carries that reasoning, the "clarity" is model-generated and fabricates authority.
- "Important nuance was missing" — missing from whose perspective? If the nuance is in the graph, cite the neighbor. If it is not, do not add it; flag the gap.

**How to rewrite:**
- Preserve the core claim (unless a cited contradiction warrants revision).
- Every sentence maps to source or a cited neighbor. No connective prose that floats free of both.
- Integrate new connections as cited inline wiki-links.
- Maintain the {vocabulary.note}'s voice, not its fabrications.

##### Sharpen the Claim

Vague claims cannot be built on. Sharpen means making the claim more specific and arguable.

**Sharpening patterns:**

| Vague | Sharp |
|-------|-------|
| "X is important" | "X matters because Y, which enables Z" |
| "consider doing X" | "X works when [condition] because [mechanism]" |
| "there are tradeoffs" | "[specific tradeoff]: gaining X costs Y" |

**When sharpening, also update:**
- Title (if claim changed) — use the rename script if available
- Description (must match new claim)
- Body (reasoning must support sharpened claim)

##### Challenge the Claim

New evidence contradicts the original. Do not silently "fix" — acknowledge the evolution.

**Challenge patterns:**

```markdown
# if partially wrong
The original insight was [X]. However, [[newer evidence]] suggests [Y]. The refined claim is [Z].

# if tension exists
This argues [X]. But [[contradicting note]] argues [Y]. The tension remains unresolved — possibly [X] applies in context A while [Y] applies in context B.

# if significantly wrong
This note originally claimed [X]. Based on [[evidence]], the claim is revised: [new claim].
```

**Always log challenges:** When a claim is challenged or revised, this is a significant event. Note it in the Output Block's `### Cascades` section with the original claim, the new evidence, and the revised position.

### Step 10: Update queue (shared)

After all per-note work for the batch is complete, advance every successfully processed entry's `current_phase` from `connect` to `verify` in `ops/queue/queue.json` via a single batched jq call. See the [Queue Self-Update](#queue-self-update) section below for the exact command.

### Step 11: Emit Output Block (shared)

Emit a single canonical Output Block as the final chat message — one block for the whole batch, regardless of N. See the [Output Block](#output-block) section below for the exact format.

## Handling Edge Cases

### No Connections Found

Sometimes a {vocabulary.note} genuinely does not connect yet. That is fine.

1. Ensure it is linked to at least one {vocabulary.topic_map} via Topics footer
2. Note in {vocabulary.topic_map} Gaps that this area needs development

### Conflicting Notes

When new content contradicts existing {vocabulary.note_plural}:

1. Document the tension in both {vocabulary.note_plural}
2. Add to {vocabulary.topic_map} Tensions section
3. Do not auto-resolve — flag for judgment

### Orphan Discovery

If you find {vocabulary.note_plural} with no connections:

1. Flag them in your output
2. Attempt to connect them
3. If genuinely orphaned, note in relevant {vocabulary.topic_map} Gaps

## Queue Self-Update

Before emitting the Output Block, advance every successfully processed entry in `ops/queue/queue.json` via a single `jq` call. Build `$COMPLETED_IDS_JSON` as a JSON array of the queue ids that completed (on a clean run, this equals the full work-list ids):

```bash
COMPLETED_IDS_JSON='["note-007","note-008","note-009","note-010"]'  # example — populate from successful completions
BATCH_ID="$ARGUMENTS"

jq --arg batch "$BATCH_ID" --argjson ids "$COMPLETED_IDS_JSON" \
   '(.tasks[] | select(.batch == $batch and (.id | IN($ids[])))) |=
    (.completed_phases += ["connect"] | .current_phase = "verify")' \
   ops/queue/queue.json > ops/queue/queue.json.tmp \
   && mv ops/queue/queue.json.tmp ops/queue/queue.json
```

If the Bash call fails (non-zero exit), resort to the Read and Write tools to read the original queue.json file and write the updated file back.

**Do not re-read after update.** A zero-exit on the `jq | mv` chain means the file was rewritten. Do NOT follow up with `jq '.tasks[] | select(.id == ...)'` or any other read of `queue.json` to "inspect" what you just wrote — it adds tokens but provides nothing the skill consumes before emitting the Output Block.

On a system-level error before the queue update, do not write the file — `queue.json` stays untouched and pipeline failure semantics handle the rest.

---

## Output Block

After finishing all steps for every note in the work list (or after a system-level error), emit the canonical block below as the final chat message. This is the ONLY chat output — no task file is written.

```
## Connect

**Batch:** {batch-id}
**Status:** ok | error: {short message}
**Queue:** advanced {N} entries: connect -> verify

### Discovery (shared)
- Topics scanned: [{list of topic ids}]
- Existing topic maps consulted: [{list of moc filenames}]
- Topic maps created: [{list of new moc filenames}] | NONE
- qmd queries issued: {Q}
- grep passes: {G}

### Per-note results
- [[note-1 title]] ({queue-id}) — {C1} connections, reconsidered ({status: unchanged|sharpened|challenged|revised}) | reconsideration skipped ({reason: granularity=capture | hub | tension | recent | moc})
- [[note-2 title]] ({queue-id}) — {C2} connections, reconsidered ({status}) | reconsideration skipped ({reason})
- ...

### Sibling cross-links
- [[note-A]] ↔ [[note-B]] — {relationship}: {one-line rationale}
- ...
| NONE

### Synthesis opportunities
- {one-line} | NONE

### Skipped reverse links
- [[target]] — {one-line reason} | NONE

### Cascades
- [[target]] — {reason} | NONE

### Flagged for attention
- {orphan | gap | tension — one line} | NONE

### Learnings
- [Friction]: {description} | NONE
- [Surprise]: {description} | NONE
- [Methodology]: {description} | NONE
- [Process gap]: {description} | NONE
```

The orchestrator parses only `Status:`, `Queue:`, and the Learnings section. Per-note details and discovery narration are human-readable.

On error, set `Status: error: <message>`, `Queue: no change (error)`, emit partial per-note results for audit, and leave `queue.json` unchanged.

---

## Critical Constraints

**Always:**
- Verify link targets exist
- Explain WHY connections exist
- Consider bidirectionality
- Update relevant {vocabulary.topic_map_plural}
