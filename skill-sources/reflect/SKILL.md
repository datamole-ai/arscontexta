---
name: reflect
description: Internal pipeline skill — finds connections for a newly created note and updates topic maps. Invoked by /pipeline as a subagent; do not invoke directly.
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

Parse the note task file path from arguments (e.g. `ops/queue/my-source-010.md`). The argument IS the full path to the task file — do NOT `find`/`ls` to relocate it; Read it directly. If no argument is provided, end immediately with: report `ERROR: reflect requires note task file path`.

Read the task file's YAML frontmatter to obtain:
- `id` — this entry's queue id (e.g. `note-010`)
- `target_path` — the path to the {vocabulary.note} being connected
- `batch` — the batch id this note belongs to
- `granularity` — routes connection-finding depth

All subsequent references to "the {vocabulary.note}" use the `target_path` value from the task file.

**START NOW.** Reference below explains methodology — use to guide, not as output.

---

# Reflect

Find connections, weave the knowledge graph, update {vocabulary.topic_map_plural}. This is the forward-connection phase of the processing pipeline.

## Philosophy

**The network IS the knowledge.**

Individual {vocabulary.note_plural} are less valuable than their relationships. A {vocabulary.note} with fifteen incoming links is an intersection of fifteen lines of thought. Connections create compound value as the vault grows.

This is not keyword matching. This is semantic judgment — understanding what {vocabulary.note_plural} MEAN to determine how they relate. A {vocabulary.note} about "friction in systems" might deeply connect to "verification approaches" even though they share no words. You are building a traversable knowledge graph, not tagging documents.

**Quality over speed. Explicit over vague.**

Every connection must pass the articulation test: can you say WHY these {vocabulary.note_plural} connect? "Related" is not a relationship. "Extends X by adding Y" or "contradicts X because Z" is a relationship.

Bad connections pollute the graph. They create noise that makes real connections harder to find. When uncertain, do not connect.

## Workflow

### Phase 1: Understand What You Are Connecting

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

Read the task file to see what the processing phase discovered. The reduce notes, semantic neighbor field, and classification provide critical context about why this {vocabulary.note} was produced and what it relates to.

### Phase 2: Discovery (Find Candidates)

Use dual discovery: {vocabulary.topic_map} exploration AND semantic search in parallel. These are complementary, not sequential.

**Capture discovery trace as you go.** Note which {vocabulary.topic_map_plural} you read, which queries you ran (with scores), which searches you tried. This becomes the Discovery Trace section in output — proving methodology was followed, not reconstructed after the fact.

**Primary discovery (run in parallel):**

**Path 1: {vocabulary.topic_map} Exploration** — curated navigation

If you know the topic (check the {vocabulary.note}'s Topics footer), start with the {vocabulary.topic_map}:

- Read the relevant {vocabulary.topic_map}(s)
- Follow curated links in Core Ideas — these are human/agent-curated connections
- Note what is already connected to similar concepts
- Check Tensions and Gaps for context
- What do agent notes reveal about navigation?

{vocabulary.topic_map_plural} tell you what thinking exists and how it is organized. Someone already decided what matters for this topic.

**Path 2: Semantic Search** — find what {vocabulary.topic_map_plural} might miss

Use `qmd query` via Bash (hybrid search with auto-expansion + reranking):

```bash
qmd query "[{vocabulary.note}'s core concepts and mechanisms]" --collection {vocabulary.qmd_collection} -n 15
```

Evaluate results by relevance — read any result where title or snippet suggests genuine connection. Semantic search finds {vocabulary.note_plural} that share MEANING even when vocabulary differs. A {vocabulary.note} about "iteration cycles" might connect to "learning from friction" despite sharing no words.

**Secondary discovery (after primary):**

**Step 3: Keyword Search**

For specific terms and exact matches:
```bash
grep -r "term" {vocabulary.note_collection}/ --include="*.md"
```

Use grep when:
- You know the exact words that should appear
- Searching for specific terminology or phrases
- Finding all uses of a named concept
- The vocabulary is stable and predictable

**Step 4: Description Scan**

Use ripgrep to scan {vocabulary.note} frontmatter descriptions for edge cases:
- Does this extend the source {vocabulary.note}?
- Does this contradict or create tension?
- Does this provide evidence or examples?

Flag candidates with a reason (not just "related").

**Step 5: Link Following**

From promising candidates, follow their existing links:
- What do THEY connect to?
- Are there clusters of related {vocabulary.note_plural}?
- Do chains emerge that your source {vocabulary.note} should join?

This is graph traversal. You are exploring the neighborhood.

### Phase 3: Evaluate Connections

For each candidate connection, apply the articulation test.

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

### Phase 4: Add Inline Connections

Connections live in the prose, not just footers.

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
2. In the relevant_notes YAML field with context phrase
3. BOTH when the connection is strong enough

**Relevant Notes Format:**

```yaml
relevant_notes:
  - "[[note title]] — extends this by adding the temporal dimension"
  - "[[another note]] — provides the mechanism this claim depends on"
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

**Reweave Task Filtering (when adding bidirectional links):**

When you edit an older {vocabulary.note} to add a reverse link, you MAY flag it for full reconsideration via reweave. But SKIP reweave flagging if ANY of these apply:

| Skip Condition | Rationale |
|----------------|-----------|
| Note has >5 incoming links | Already a hub — one more link does not warrant full reconsideration |
| Note has `type: tension` in YAML | Structural framework, not content that evolves |
| Note was reweaved in current batch | Do not re-reweave what was just reweaved |
| Note is a {vocabulary.topic_map} | {vocabulary.topic_map_plural} are navigation, not claims to reconsider |

**Check incoming links:**
```bash
find {vocabulary.note_collection}/ -name "*.md" -type f -exec grep -l '\[\[note name\]\]' {} + | wc -l
```

If >= 5, skip reweave flagging.

### Phase 5: Update {vocabulary.topic_map_plural}

{vocabulary.topic_map_plural} are synthesis hubs, not just indexes.

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

Splitting is a human decision (architectural judgment required), but /reflect should surface the signal.

**{vocabulary.topic_map} Structure:**

```markdown
# [Topic Name]

[Opening synthesis: Claims about the topic. Not "this {vocabulary.topic_map} collects {vocabulary.note_plural}" but "the core insight is Y because Z." This IS thinking, not meta-description.]

## Core Ideas

- [[claim note]] — what it contributes to understanding
- [[another claim]] — how it fits or challenges existing ideas

## Tensions

- [[claim A]] and [[claim B]] conflict because... [genuine unresolved tension]

## Gaps

- nothing about X aspect yet
- need concrete examples of Y
- missing: comparison with Z approach

---

Agent Notes:
- YYYY-MM-DD: [what was explored]. [the insight or dead end].
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

Remove gaps that are now filled. Add new gaps discovered during reflection.

### Phase 6: Add Agent Notes

Agent notes are breadcrumbs for future navigation.

**Add agent notes when:**
- Non-obvious navigation path discovered
- Dead end worth documenting
- Productive {vocabulary.note} combination found
- Insight about topic cluster emerged

**Format:**
```markdown
Agent Notes:
- YYYY-MM-DD: [what was explored]. [the insight or finding].
```

**Good agent notes:**
```markdown
- 2026-02-15: tried connecting via "learning" — too generic. better path: friction -> verification -> quality. the mechanism chain is tighter.
- 2026-02-15: [[claim A]] and [[claim B]] form a tight pair. A sets the standard, B teaches the method.
```

**Bad agent notes:**
```markdown
- 2026-02-15: read the {vocabulary.topic_map} and added some links.
- 2026-02-15: connected [[note A]] to [[note B]].
```

The test: would this help a future agent navigate more effectively?


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

Before emitting the Output Block, update `ops/queue/queue.json`:

1. Read the file.
2. Locate the entry with `id` matching the task file's `id`.
3. Append `"reflect"` to `completed_phases`.
4. Set `current_phase: "reweave"` (the next phase per `phase_order.note` / `phase_order.enrichment`).
5. Write the file back.

If reading or writing fails, do NOT emit a successful Output Block. Emit `Status: error: queue write failed` with `Queue: no change (error)` and stop.

---

## Output Block

After finishing connection work, emit the canonical block below. Write the same block into the task file's `## Reflect` section (replacing any placeholder) AND echo it as the final chat message. This is the ONLY chat output.

```
## Reflect

**Target:** [[{target note title}]]
**Status:** ok | error: {short message}
**Queue:** advanced {id}: reflect -> reweave

### Work

**Discovery trace:**
- {vocabulary.topic_map} exploration: [[moc-name]] — candidates: [[note A]], [[note B]]
- Semantic search: "[query]" — top hits: [[note E]] (0.74, mechanism overlap), [[note F]] (0.61, surface only)
- Keyword search: grep "specific term" — [[note H]]

**Connections added:**
- [[source note]] -> [[target]] — [relationship]: [why]
- inline: added link to [[note]] in paragraph about X

**{vocabulary.topic_map} updates:**
- [[moc-name]]: added [[note]] to Core Ideas — [contribution]; updated Tensions: [[A]] vs [[B]]

**Synthesis opportunities:** [list or NONE]

**Flagged for attention:** [orphans, broad notes, unresolved tensions — or NONE]

### Files Modified
- {vocabulary.note_collection}/[note name].md (inline links added)
- {vocabulary.note_collection}/[moc-name].md (Core Ideas updated)
- {task file path} (## Reflect section)
- ops/queue/queue.json (advanced {id})

### Learnings
- [Friction]: [description] | NONE
- [Surprise]: [description] | NONE
- [Methodology]: [description] | NONE
- [Process gap]: [description] | NONE
```

On error, set `Status: error: <message>`, `Queue: no change (error)`, write the partial `### Work` content for audit, and leave `queue.json` unchanged.

---

## Critical Constraints

**Always:**
- Verify link targets exist
- Explain WHY connections exist
- Consider bidirectionality
- Update relevant {vocabulary.topic_map_plural}
- Add agent notes when navigation insights emerge
- Capture discovery trace as you work
