# /ask Skill Generator Template

When generating the `/ask` skill for a vault, produce `.claude/skills/ask/SKILL.md` with this structure. Apply vocabulary transformation from `reference/vocabulary-transforms.md` throughout — same pass that runs on CLAUDE.md and `ops/features/*.md`.

---

## Frontmatter (always include)

```yaml
---
name: ask
description: User-invoked reference lookup for questions about this vault's structure, schema, pipeline, {DOMAIN:topic maps}, templates, or derivation. Invoke explicitly with /ask <question>.
allowed-tools: Read, Grep, Glob
---
```

Frontmatter is emitted verbatim except for the `description:` line, which undergoes vocabulary transformation.

---

## Body

Three parts. Target total length: ~70 lines after vocabulary transform.

### Part A — Overview (~10 lines)

A fixed-shape paragraph describing the three-space architecture and pointing to `ops/derivation.md` for the full justification chain. Use this shape:

```markdown
## Overview

This vault separates three concerns:

- `self/` — agent identity and session continuity.
- `{DOMAIN:note_collection}/` — the knowledge graph.
- `ops/` — coordination and system references.

The {DOMAIN:processing} pipeline routes raw material through `{DOMAIN:inbox}/` into `{DOMAIN:note_collection}/` via named skills. For the derivation record, read `ops/derivation.md`.
```

### Part B — Topic sections (one per generated feature)

Emit one section per feature that ended up in `ops/features/`. Do NOT emit a section for a feature whose reference file does not exist.

Section template:

```markdown
### [Topic heading — domain-native]
[2-line orientation: what the feature covers + when to care about it.]
Read `ops/features/<name>.md`. Rationale: `ops/derivation.md` §<slug>.
```

Canonical mapping (source file → `/ask` section heading). Sections appear in this order:

| `ops/features/` file | Section heading |
|---|---|
| `note-granularity.md` | `### {DOMAIN:Note} granularity` |
| `wiki-links.md` | `### Wiki-links / graph edges` |
| `mocs.md` | `### {DOMAIN:Topic maps}` |
| `processing-pipeline.md` | `### {DOMAIN:Processing} pipeline` |
| `semantic-search.md` | `### Semantic search` |
| `schema.md` | `### Schema / frontmatter` |
| `maintenance.md` | `### Maintenance checks` |
| `session-rhythm.md` | `### Session rhythm` |
| `templates.md` | `### Templates` |
| `ethical-guardrails.md` | `### Ethical guardrails` |
| `self-space.md` | `### Self space` |
| `helper-functions.md` | `### Helper functions` |

For the 2-line orientation, summarize the feature file's opening paragraph. Do not invent detail that is not in the file. If unsure, reread the feature file and copy its mission sentence with light compression.

### Part C — Cross-cutting routes (~5 lines)

A fixed-shape "When the question spans files" section. Use this content:

```markdown
## When the question spans files

- "Why is my system configured this way?" → read `ops/derivation.md`.
- "What do I know about <topic>?" — not a system question; grep `{DOMAIN:note_collection}/` with Grep, or use semantic search.
```

---

## Skill-body composition steps for the generation agent

1. List `ops/features/*.md` that were actually written in the previous step.
2. Emit frontmatter (domain-adapted `description`).
3. Emit Part A overview.
4. For each generated feature, emit a Part B section in the canonical order above. Skip features whose file was not written.
5. Emit Part C cross-cutting routes.
6. Apply a final vocabulary-transform pass on the assembled file.
7. Write to `.claude/skills/ask/SKILL.md` inside the vault.

---

## What this skill is NOT

- Not a feature-summary inliner. Content stays in `ops/features/*.md`.
- Not auto-triggered. Description states explicit invocation.
- Not a behavioral guide. Behavioral rules stay in CLAUDE.md.
