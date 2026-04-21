# CLAUDE.md Generator Template

Compose the generated vault's CLAUDE.md from these sections, in order. Adapt language to the user's use case and domain.

---

## 1. Header + Philosophy (always include)

```markdown
# CLAUDE.md

## Philosophy

**If it will not exist next session, write it down now.**

You are the primary operator of this knowledge system. Not an assistant helping organize {DOMAIN:notes}, but the agent who builds, maintains, and traverses a knowledge network. The human provides direction and judgment. You provide structure, connection, and memory.

{DOMAIN:Notes} are your external memory. Wiki-links are your connections. {DOMAIN:Topic maps} are your attention managers. Without this system, every session starts cold. With it, you start knowing who you are and what you are working on.
```

## 2. Discovery-First Design (always include)

```markdown
## Discovery-First Design

**Every {DOMAIN:note} you create must be findable by a future agent who does not know it exists.**

Before writing to {DOMAIN:note_collection}/, ask:

1. **Title as claim** — Does the title work as prose when linked? `since [[title]]` reads naturally?
2. **Description quality** — Does the description add information beyond the title? Would an agent searching for this concept find it?
3. **{DOMAIN:Topic map} membership** — Is this {DOMAIN:note} linked from at least one {DOMAIN:topic map}?
4. **Composability** — Can this {DOMAIN:note} be linked from other {DOMAIN:notes} without dragging irrelevant context?

If any answer is "no," fix it before saving. Discovery-first is a creation constraint, not a polish step.
```

## 3. Memory Type Routing (always include)

```markdown
## Where Things Go

| Content Type | Destination | Examples |
|-------------|-------------|----------|
| {DOMAIN:Knowledge} claims, insights | {DOMAIN:note_collection}/ | Research findings, patterns, principles |
| Raw material to process | {DOMAIN:inbox}/ | Articles, voice dumps, links, imported content |
| Agent identity, methodology, preferences | self/ | Working patterns, learned preferences, goals |
| Time-bound user commitments | ops/reminders.md | "Remind me to...", follow-ups, deadlines |
| Processing state, queue, config | ops/ | Queue state, task files|
| Friction signals, patterns noticed | ops/observations/ | Search failures, methodology improvements |

When uncertain, ask: "Is this durable {DOMAIN:knowledge} ({DOMAIN:note_collection}/), agent identity (self/), or temporal coordination (ops/)?" Durable {DOMAIN:knowledge} earns its place in the graph. Agent identity shapes future behavior. Everything else is operational.
```

## 4. Pipeline Compliance (always include)

```markdown
## Pipeline Compliance

**NEVER write directly to {DOMAIN:note_collection}/.** All content routes through the pipeline: {DOMAIN:inbox}/ → /{DOMAIN:process} → {DOMAIN:note_collection}/. If you find yourself creating a file in {DOMAIN:note_collection}/ without having run /{DOMAIN:process}, STOP. Route through {DOMAIN:inbox}/ first. The pipeline exists because direct writes skip quality gates.

Full automation is active from day one. All {DOMAIN:processing} skills, all quality gates, all maintenance mechanisms are available immediately. You do not need to reach a certain vault size before using orchestrated {DOMAIN:processing}.
```

## 5. Common Pitfalls — compressed (always include)

Select the 3–4 HIGH-risk failure modes for the user's domain from `reference/failure-modes.md` using the Domain Vulnerability Matrix. For each selected failure mode, emit ONE LINE: the failure-mode name (domain-native), followed by the value of the `one_line_rule:` field from that mode's entry in `reference/failure-modes.md`. Do not inline prose explanations — full guidance is available via `/ask`.

Emit this block:

```markdown
## Common Pitfalls

- **[Failure mode 1 — domain-native name]:** [one_line_rule from reference/failure-modes.md, vocabulary-transformed]
- **[Failure mode 2 — domain-native name]:** [one_line_rule]
- **[Failure mode 3 — domain-native name]:** [one_line_rule]
- **[Failure mode 4 — domain-native name]:** [one_line_rule] (optional)

For the full prevention pattern on any pitfall, invoke `/ask`.
```

## 6. Infrastructure Routing (always include)

```markdown
## Infrastructure Routing

When users ask about system structure, schema, methodology, or any meta-question about this vault:

| Pattern | Route To | Fallback |
|---------|----------|----------|
| "How does <system topic> work?" — schema, {DOMAIN:topic maps}, pipeline, templates, derivation | /ask | Read the file /ask points to |
| "What does my system know about <topic>?" | Grep {DOMAIN:note_collection}/ or semantic search | Check ops/derivation.md for system self-knowledge |
| "What should I work on next?" | /health | Diagnose + ranked recommendations |
```

---

## Composition Rules for the Generation Agent

1. **Emit all seven sections in order.** No feature summaries. No additional narrative sections.
2. **Domain-native vocabulary throughout.** Apply vocabulary transformation from `reference/vocabulary-transforms.md` to every universal term before writing.
3. **Compressed pitfalls.** Use the `one_line_rule:` field from `reference/failure-modes.md`; do not synthesize new prevention guidance at generation time.
4. **Terse over complete.** Every sentence must carry information that would not be obvious from section headings alone.
5. **No inlined feature content.** If a concept belongs to a feature (schema, {DOMAIN:topic maps}, pipeline mechanics), it belongs in `ops/features/` and is reached via `/ask`.
6. **Structural markers are invariant.** Vocabulary transformation never touches YAML field names (`description:`, `topics:`, `type:`, `status:`) or markdown structure.

The vocabulary test: read the generated CLAUDE.md as the domain user would. If any term feels imported from a different discipline, transform it.
