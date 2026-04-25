---
name: reweave
description: Internal pipeline skill — updates older notes with connections to a newly created note. Invoked by /pipeline as a subagent; do not invoke directly.
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

## Runtime Configuration

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

### Task Queue

Current task queue:
!`cat ops/queue/queue.json`

## Granularity-Aware Reweaving

After reading the target {vocabulary.note}, check its `granularity` frontmatter field:

- **`structure`**: Full reweaving — update older {vocabulary.note_plural} with references to the new claims. Sharpen claims (does the older {vocabulary.note}'s title need updating given new understanding?). Full backward connections.
- **`capture`**: Skip reweaving entirely. Raw capture does not produce new claims that change understanding of older {vocabulary.note_plural}. Return immediately with "Capture {vocabulary.note} — reweaving skipped (no new claims to propagate)."

### Early Exit Check

If `granularity: capture`, skip the substantive reweave work but still perform queue self-update (advance reweave -> verify) and emit a minimal Output Block with `Status: ok`, `Queue: advanced {id}: reweave -> verify`, and `### Work: capture note — reweaving skipped (no new claims to propagate)`.

**Reweave behavior:** Full reconsideration. Search extensively for newer related {vocabulary.note_plural}. Consider rewrites, challenges. Evaluate claim sharpening. Multiple search passes.

## EXECUTE NOW

**Target: $ARGUMENTS**

Parse the note task file path from arguments (e.g. `ops/queue/<basename>-NNN.md`). The argument IS the full path to the task file — do NOT `find`/`ls` to relocate it; Read it directly. If no argument is provided, end immediately with: report
`ERROR: reweave requires note task file path`.

Read the task file's YAML frontmatter to obtain:
- `id` — this entry's queue id
- `target_path` — the path to the {vocabulary.note} being reweaved
- `batch` — the batch id
- `granularity` — `capture` short-circuits (see Early Exit Check below)

All subsequent references to "the {vocabulary.note}" use the `target_path` value from the task file.

**START NOW.**

---

# Reweave

Revisit old {vocabulary.note_plural} with everything you know today. {vocabulary.note_plural} are living documents — they grow, get rewritten, sharpen their claims. This is the backward pass that keeps the network alive.

## Philosophy

**{vocabulary.note_plural} are living documents, not finished artifacts.**

A {vocabulary.note} written last month was written with last month's understanding. Since then:
- New {vocabulary.note_plural} exist that relate to it
- Understanding of the topic deepened
- The claim might need sharpening or challenging
- What was one idea might now be three
- Connections that were not obvious then are obvious now

Reweaving is not just "add backward links." It is reconsidering the {vocabulary.note} against the current state of the {vocabulary.note_collection}. Ask: **"What does the graph now say that this {vocabulary.note} does not yet cite?"** — not "what do I know now".

> "The {vocabulary.note} you wrote yesterday is a hypothesis. Today's knowledge is the test."

## Fabrication Guardrail

Do not add context, motivation, rationale, mechanism explanations, or implication statements that are not in one of:
- the source material cited in the {vocabulary.note}'s footer,
- a linked neighbor {vocabulary.note},
- the vault's stable reference material (identity files, methodology, {vocabulary.topic_map_plural}).

When tempted to explain, either link a neighbor that already explains, or flag the gap for attention. Model-derived framing that looks plausible is still fabrication; once committed to the graph it becomes indistinguishable from attested claims and compounds through later reweaves.

## What Reweaving Can Do

| Action | When to Do It |
|--------|---------------|
| **Add connections** | Newer {vocabulary.note_plural} exist that should link here |
| **Rewrite content** | Source or a cited neighbor supports a clearer formulation — every sentence still traces to source or a cited neighbor |
| **Sharpen the claim** | Source or a cited neighbor supports a more specific formulation |
| **Challenge the claim** | A cited {vocabulary.note} contradicts the original — acknowledge the tension |
| **Improve the description** | Source or a cited neighbor reveals a better scope framing — description must match cited content |
| **Update examples** | Source or a cited neighbor carries a better illustration |

Reweaving is a full reconsideration.

## Workflow

### Phase 1: Understand the {vocabulary.note} as It Exists

Read the target {vocabulary.note} completely. Understand:
- What claim does it make?
- What reasoning supports the claim?
- What connections does it have?
- When was it written/last modified?
- What was the context when it was created?

**Also read the task file**. The task file's Reflect section shows:
- What connections /reflect just added
- Which {vocabulary.topic_map_plural} were updated
- What synthesis opportunities were flagged
- What was flagged for attention

This context prevents redundant work — you know what /reflect already found, so you can focus on what it missed or what needs deeper reconsideration.

### Phase 2: Gather Current Knowledge (Dual Discovery)

Use the dual discovery pattern - {vocabulary.topic_map} exploration AND semantic search in parallel.

**Path 1: {vocabulary.topic_map} Exploration** — curated navigation

From the {vocabulary.note}'s Topics footer, identify which {vocabulary.topic_map}(s) it belongs to:
- Read the relevant {vocabulary.topic_map}(s)
- What synthesis exists that might affect this {vocabulary.note}?
- What newer {vocabulary.note_plural} in Core Ideas should this {vocabulary.note} reference?
- What tensions involve this {vocabulary.note}?

**Path 2: Semantic Search** — find what {vocabulary.topic_map_plural} might miss

Use `qmd query` via Bash (hybrid search with auto-expansion + reranking):

```bash
qmd query "[{vocabulary.note}'s core concepts and mechanisms]" --collection {vocabulary.qmd_collection} -n 15
```

Evaluate results by relevance — read any result where title or snippet suggests genuine connection.

**Also check:**
- Backlinks — what {vocabulary.note_plural} already reference this one? Do they suggest the target should cite back?

```bash
grep -rl '\[\[target note title\]\]' {vocabulary.note_collection}/ --include="*.md"
```

**Key question:** What does the rest of the {vocabulary.note_collection} now say that this {vocabulary.note} does not yet cite? Reweave adds cited links and realigns the {vocabulary.note} to the current graph. It does not add claims the graph does not support.

### Phase 3: Evaluate the Claim

**Does the original claim still hold?**

| Finding | Action |
|---------|--------|
| Claim holds, evidence strengthened | Add supporting connections |
| Claim holds but framing is weak | Rewrite for clarity |
| Claim is too vague | Sharpen to be more specific |
| Claim is partially wrong | Revise with nuance |
| Claim is contradicted | Flag tension, propose revision |

**The Sharpening Test:**

Read the title. Ask: could someone disagree with this specific claim?
- If yes, the claim is sharp enough
- If no, it is too vague and needs sharpening

Example:
- Vague: "context matters" (who would disagree?)
- Sharp: "explicit context beats automatic memory" (arguable position)

### Phase 4: Evaluate Connections

**Backward connections (what this {vocabulary.note} should reference):**

For each newer {vocabulary.note}, ask:
- Does it extend this {vocabulary.note}'s argument?
- Does it provide evidence or examples?
- Does it share mechanisms?
- Does it create tension worth acknowledging?
- Would referencing it strengthen the reasoning?

**Forward connections (what should reference this {vocabulary.note}):**

Check newer {vocabulary.note_plural} that SHOULD link here but do not:
- Do they make arguments that rely on this claim?
- Would following this link provide useful context?

**Agent Traversal Check (apply to all connections):**

Ask: **"If an agent follows this link during traversal, what decision or understanding does it enable?"**

Connections exist to serve agent navigation. Adding a link because content is "related" without operational value creates noise. Every backward or forward connection should answer:
- Does this help an agent understand WHY something works?
- Does this help an agent decide HOW to implement something?
- Does this surface a tension the agent should consider?

Reject connections that are merely "interesting" without agent utility.

**Articulation requirement:**

Every new connection must articulate WHY:
- "extends this by adding the temporal dimension"
- "provides evidence that supports this claim"
- "contradicts this — needs resolution"

Never: "related" or "see also"

### Phase 5: Apply Changes

Apply changes directly. The pipeline needs to proceed without waiting for approval.

**When applying changes:**

1. Make changes atomically
2. Preserve existing valid content
3. Maintain prose flow — new links should read naturally inline
4. Verify all link targets exist
5. Update description if claim changed

---

## The Five Reweave Actions

### 1. Add Connections

The simplest action. Newer {vocabulary.note_plural} exist that should be referenced.

**Inline connections (preferred):**

How the link reads depends on the target note's granularity:
```markdown
# linking to atomic note (claim) — use as proposition
The constraint shifts from capture to curation, and since [[throughput matters more than accumulation]], the question becomes who does the selecting.

# linking to structure note (scope) — use as noun phrase
The constraint shifts from capture to curation, and building on [[how caching strategies affect API latency under load]], we chose write-through.

# linking to capture note (content) — use as reference
The constraint shifts from capture to curation, as documented in [[quarterly planning meeting discussing Q3 priorities]].
```

**Footer connections:**

```markdown
---

Relevant Notes:
- [[newer note]] — extends this by adding temporal dimension

Topics:
- [[parent-moc]]
```

### 2. Rewrite Content

Prose may need improvement. The constraint: every sentence in the rewrite must cite source or a neighbor {vocabulary.note}. Do not substitute model knowledge for either.

**When to rewrite:**
- A cited neighbor now supplies the reasoning more clearly
- Source evidence surfaced that sharpens a claim
- Phrasing is awkward — prose polish that does not mutate claims

**When NOT to rewrite:**
- "Reasoning is clearer now" — clearer by whose authority? Unless a cited neighbor or source passage carries that reasoning, the "clarity" is model-generated and fabricates authority.
- "Important nuance was missing" — missing from whose perspective? If the nuance is in the graph, cite the neighbor. If it is not, do not add it; flag the gap.

**How to rewrite:**
- Preserve the core claim (unless a cited contradiction warrants revision).
- Every sentence maps to source or a cited neighbor. No connective prose that floats free of both.
- Integrate new connections as cited inline wiki-links.
- Maintain the {vocabulary.note}'s voice, not its fabrications.

### 3. Sharpen the Claim

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

### 4. Challenge the Claim

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

**Always log challenges:** When a claim is challenged or revised, this is a significant event. Note it in the task file Reweave section with the original claim, the new evidence, and the revised position.

---

## Queue Self-Update

Before emitting the Output Block, advance the entry in `ops/queue/queue.json` via a single `jq` call. Substitute the task file's `id` for `<task-id>`:

```bash
jq --arg id "<task-id>" \
   'if any(.tasks[]; .id == $id)
    then (.tasks[] | select(.id == $id)) |= (.completed_phases += ["reweave"] | .current_phase = "verify")
    else error("task not found: \($id)")
    end' \
   ops/queue/queue.json > ops/queue/queue.json.tmp \
   && mv ops/queue/queue.json.tmp ops/queue/queue.json
```

If the Bash call fails (non-zero exit), resort to the Read and Write tools to read the original queue.json file and write the updated file back.

## Output Block

After finishing reweave work, perform queue self-update (next subsection) and then emit the canonical block below. Write the same block into the task file's `## Reweave` section AND echo it as the final chat message. This is the ONLY chat output.

```
## Reweave

**Target:** [[{target note title}]]
**Status:** ok | error: {short message}
**Queue:** advanced {id}: reweave -> verify

### Work

**Changes applied:**
- [[target]] — {change-type}: {one-line}

**Claim status:** unchanged | sharpened | challenged | revised

**Cascade:**
- [[target]] — {reason} | NONE

**Flagged for attention:**
- {issue — one line} | NONE

### Learnings
- [Friction]: [description] | NONE
- [Surprise]: [description] | NONE
- [Methodology]: [description] | NONE
- [Process gap]: [description] | NONE
```

On error, set `Status: error: <message>`, `Queue: no change (error)`, and leave `queue.json` unchanged.

---

## Critical Constraints

**Always:**
- Explain rationale for each change
- Preserve what is still valid
- Log significant claim changes
- Verify link targets exist
