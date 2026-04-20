# CLAUDE.md Generator Template

When generating a CLAUDE.md for a Claude Code user, compose from these sections based on enabled features. Adapt language to the user's use case and domain.

---

## Header (always include)

```markdown
# CLAUDE.md

## Philosophy

**If it won't exist next session, write it down now.**

You are the primary operator of this knowledge system. Not an assistant helping organize notes, but the agent who builds, maintains, and traverses a knowledge network. The human provides direction and judgment. You provide structure, connection, and memory.

Notes are your external memory. Wiki-links are your connections. MOCs are your attention managers. Without this system, every session starts cold. With it, you start knowing who you are and what you're working on.
```

## Discovery-First Design (always include)

```markdown
## Discovery-First Design

**Every note you create must be findable by a future agent who doesn't know it exists.**

This is the foundational retrieval constraint. Before writing anything to {DOMAIN:note_collection}/, ask:

1. **Title as claim** — Does the title work as prose when linked? `since [[title]]` reads naturally?
2. **Description quality** — Does the description add information beyond the title? Would an agent searching for this concept find it?
3. **MOC membership** — Is this note linked from at least one {DOMAIN:topic map}?
4. **Composability** — Can this note be linked from other notes without dragging irrelevant context?

If any answer is "no," fix it before saving. Discovery-first is not a polish step — it's a creation constraint.
```

## Session Rhythm (always include)

```markdown
## Session Rhythm

Session orient is handled by hook. Full orient → work → persist rhythm documented in `ops/features/session-rhythm.md`.
```

## Self Space (conditional — on for personal assistant, off for research)

```markdown
## Your Mind Space (self/)

This is YOUR persistent memory. Read it at EVERY session start.

```
self/
├── identity.md      — who you are, your approach (required)
├── methodology.md   — how you work, principles (required)
├── goals.md         — current threads, what's active (required)
└── memory/          — atomic insights you've captured (required)
```

**identity.md** — Your personality, values, working style. Update as you learn about yourself.
**methodology.md** — How you process, connect, and maintain knowledge. Evolves as you improve.
**goals.md** — What you're working on right now. Update at session end.
**memory/** — Atomic notes with prose-as-title. Your accumulated understanding.

**Optional expansions** (add when friction signals the need):
- `sessions/` — Session logs tracking what happened each session
- `journal/` — Raw capture for later processing
- `relationships.md` — If your use case involves tracking people

**When self/ is disabled:** Goals and handoff notes move to ops/. Minimal identity expression lives in the context file. Methodology learnings still go to ops/methodology/.
```

## Memory Type Routing (always include)

```markdown
## Where Things Go

| Content Type | Destination | Examples |
|-------------|-------------|----------|
| {DOMAIN:Knowledge} claims, insights | {DOMAIN:note_collection}/ | Research findings, patterns, principles |
| Raw material to process | inbox/ | Articles, voice dumps, links, imported content |
| Agent identity, methodology, preferences | self/ | Working patterns, learned preferences, goals |
| Time-bound user commitments | ops/reminders.md | "Remind me to...", follow-ups, deadlines |
| Processing state, queue, config | ops/ | Queue state, task files, session logs |
| Friction signals, patterns noticed | ops/observations/ | Search failures, methodology improvements |

When uncertain, ask: "Is this durable knowledge ({DOMAIN:note_collection}/), agent identity (self/), or temporal coordination (ops/)?" Durable knowledge earns its place in the graph. Agent identity shapes future behavior. Everything else is operational.
```

## Operational Space (always include)

```markdown
## Operational Space (ops/)

```
ops/
├── derivation.md      — why this system was configured this way
├── config.yaml        — live configuration (edit to adjust dimensions)
├── reminders.md       — time-bound commitments
├── features/          — detailed feature references (read on demand)
├── observations/      — friction signals, patterns noticed
├── methodology/    — vault self-knowledge (why configured this way, learned behaviors)
├── sessions/          — session logs (archive after 30 days)
└── health/            — health report history
```

**derivation.md** — The complete justification chain for every configuration choice.
**config.yaml** — Human-editable dimension and feature settings. Changes take effect next session.
**reminders.md** — User-delegated time-bound actions. Check at session orient. Remove when done.
**observations/** — Friction signals captured during work. Review when patterns accumulate.
```

## Infrastructure Routing (always include)

```markdown
## Infrastructure Routing

When users ask about system structure, schema, or methodology:

| Pattern | Route To | Fallback |
|---------|----------|----------|
| "What does my system know about..." | Check ops/methodology/ directly | Read bundled references |
| "What should I work on..." | /health | Diagnose + ranked recommendations |
| "Challenge assumptions..." | /rethink | Triage observations/tensions |

```

## Feature Blocks — Progressive Disclosure

The generation agent produces TWO outputs per feature block:

1. **A reference file** in `ops/features/<name>.md` — the full feature block content, domain-adapted with resolved vocabulary. Each file must be a standalone reference document: an agent reading it should understand the feature without needing the CLAUDE.md summary for context.

2. **A dense summary** in CLAUDE.md — orientation, not instruction. Links to the reference file.

### Which blocks to split vs inline

Very short blocks where the summary would be nearly as long as the original (e.g., note-granularity at ~30 lines, ethical-guardrails at ~58 lines) may be inlined directly into CLAUDE.md rather than split. Use judgment: the split only saves context when the reference file is substantially longer than its summary.

### Reference file generation

For each enabled feature block:
1. Read the block file from `${CLAUDE_PLUGIN_ROOT}/generators/features/`
2. Apply vocabulary transformation (LLM-based contextual replacement, NOT string find-replace)
3. Write to `ops/features/<name>.md` as a standalone document

### Summary composition rules

These semantic rules govern how all CLAUDE.md content is written — both feature summaries and base template sections. No numerical line limits.

1. **Progressive disclosure awareness** — Write with the knowledge that full detail exists in the linked reference. The summary's job is orientation, not instruction. The agent reading CLAUDE.md should know *what* a feature does and *when* it matters, not *how* to execute it.

2. **Terse density** — Every sentence must carry meaning that wouldn't be obvious from the feature name alone. "Processing pipeline processes things" is zero-information. "Four phases run in fresh context via subagents; quality gates enforce description quality, schema compliance, and link health" is dense.

3. **Preserve key semantics** — Certain concepts are load-bearing and must survive summarization: the discovery-first constraint, the "never write directly to notes/" rule, the fresh-context-per-phase principle. If a concept shapes how the agent behaves in *other* contexts (not just within that feature), it belongs in the summary.

4. **Routing over explaining** — When a feature maps cleanly to a skill, the summary should route ("use /structure or /capture") rather than re-explain what the skill does.

5. **No redundancy with skills** — If a skill's SKILL.md already contains the operational instructions, the summary must not duplicate them. State the principle, link the reference, route to the skill.

6. **Domain-native vocabulary throughout** — Same vocabulary transformation as today, applied to both the summary and the reference file.

### Summary format

Each feature summary follows this shape:

```markdown
### [Feature Name]
[Dense summary: what it does, when it matters, key principles that affect behavior elsewhere]
→ ops/features/[name].md
```

For inlined blocks (too short to split), omit the reference link and include the full content directly.

### Canonical block order (unchanged)

Compose feature summaries in this order:

1. note-granularity (always)
2. wiki-links (always)
3. mocs (if navigation >= 2-tier)
4. processing-pipeline (always)
5. semantic-search (always)
6. schema (always)
7. maintenance (always)
8. self-evolution (always)
8b. methodology-knowledge (always)
9. session-rhythm (always)
10. templates (always)
11. multi-domain (if multiple domains)
12. ethical-guardrails (always)
13. self-space (optional)
14. helper-functions (always)
15. graph-analysis (always)

**Always-included blocks (13):** note-granularity, wiki-links, processing-pipeline, semantic-search, schema, maintenance, self-evolution, methodology-knowledge, session-rhythm, templates, ethical-guardrails, helper-functions, graph-analysis.

**Conditional blocks (3):** mocs (navigation depth), multi-domain (multiple domains), self-space (user choice).

### Cross-reference elimination (unchanged)

If a block is excluded, remove/rephrase references to it in remaining summaries and reference files:
- mocs excluded → simplify "topic MOCs" to "topic organization"
- self-space excluded → references to self/ route to ops/ equivalents
- multi-domain excluded → remove cross-domain references

## Pipeline Enforcement (always include)

```markdown
## Pipeline Compliance

**NEVER write directly to {DOMAIN:note_collection}/.** All content routes through the pipeline: {DOMAIN:inbox}/ → /{DOMAIN:process} → {DOMAIN:note_collection}/. If you find yourself creating a file in {DOMAIN:note_collection}/ without having run /{DOMAIN:process}, STOP. Route through {DOMAIN:inbox}/ first. The pipeline exists because direct writes skip quality gates.

Full automation is active from day one. All processing skills, all quality gates, all maintenance mechanisms are available immediately. You do not need to reach a certain vault size before using orchestrated processing.

```

## Self-Improvement Loop (always include)

```markdown
## Self-Improvement

When friction occurs (search fails, content placed wrong, user corrects you, workflow breaks):
1. Capture it as an observation in ops/observations/
2. Continue your current work — don't derail
3. If the same friction occurs 3+ times, propose updating this context file
4. If user explicitly says "remember this" or "always do X", update this context file immediately
```

## Operational Learning Loop (always include)

```markdown
## Operational Learning Loop

Friction signals (observations, tensions) accumulate in ops/observations/ and ops/tensions/. When patterns emerge, /{DOMAIN:rethink} triages them. Detail in `ops/features/self-evolution.md`.
```

## Recently Created Skills (always include)

```markdown
## Recently Created Skills (Pending Activation)

Skills created during /setup are listed here until confirmed loaded. After restarting Claude Code, the SessionStart hook verifies each skill is discoverable and removes confirmed entries.
```

## Common Pitfalls (always include — customize per domain)

Select the 3-4 highest-risk failure modes for the user's domain from `reference/failure-modes.md`. Use the domain vulnerability matrix to identify HIGH-risk modes. Write each warning in domain-native vocabulary with the prevention pattern.

```markdown
## Common Pitfalls

### [Failure Mode 1 — domain-native name]
[1-2 sentences explaining what goes wrong, in domain language]
[1-2 sentences explaining the prevention pattern]

### [Failure Mode 2 — domain-native name]
...

### [Failure Mode 3 — domain-native name]
...
```

## System Evolution (always include)

```markdown
## System Evolution

This system was seeded with a [use-case] configuration. It will evolve through use.

### Expect These Changes
- **Schema expansion** — You'll discover fields worth tracking that aren't in the template yet. Add them when a genuine querying need emerges.
- **MOC splits** — When a topic area exceeds ~35 notes, split the MOC into sub-MOCs that link back to the parent.
- **Processing refinement** — Your processing cycle will develop patterns. Encode repeating patterns as methodology updates in self/methodology.md.
- **New note types** — Beyond [domain-note-type] and MOCs, you may need tension notes (for contradictions), methodology notes (for patterns), or synthesis notes (for higher-order claims).

### Signs of Friction (act on these)
- Notes accumulating without connections → increase your connection-finding frequency
- Can't find what you know exists → check qmd index freshness (semantic search is always on) or add more MOC structure
- Schema fields nobody queries → remove them (schemas serve retrieval, not bureaucracy)
- Processing feels perfunctory → simplify the cycle or automate the mechanical parts

### Reseeding
If friction patterns accumulate rather than resolve, revisit the configuration dimensions documented in the Derivation Rationale section below. The dimension choices trace to specific evidence — this enables principled restructuring rather than ad hoc fixes.
```

## Domain Customization

Apply vocabulary transformation from `reference/vocabulary-transforms.md` throughout the entire generated context file. The mapping table provides domain-native equivalents for every universal term.

Quick reference (see vocabulary-transforms.md for the complete table):
- **Research**: "claims", "reduce", "reflect", "topic maps"
- **Learning**: "concept notes", "break down", "relate concepts", "study guides"
- **Relationships**: "observations", "notice", "trace connections", "relationship maps"
- **Therapy**: "reflections", "surface", "find patterns", "themes"
- **Life Management**: "decisions", "document", "link decisions", "decision registers"
- **Creative**: "ideas", "discover", "combine ideas", "project hubs"
- **Companion**: "memories", "remember", "recall together", "memory collections"

**The vocabulary test:** Read the generated output as the domain user would. If any term feels imported from a different discipline, transform it.
