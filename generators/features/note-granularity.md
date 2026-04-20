# Feature: Note Granularity

## Context File Block

```markdown
## Note Granularity — Three Pipelines, One Graph, One Template

Every {DOMAIN:note} declares its `granularity` in frontmatter: `extract`, `structure`, or `capture`. Content flows through `{DOMAIN:inbox}/` and one of three pipelines routes on the frontmatter value — not on a directory path.

| Pipeline | Command | Granularity | What It Produces |
|----------|---------|-------------|-----------------|
| Extract | /extract | `extract` | One claim per file — atomic, composable, prose-as-title propositions |
| Structure | /structure | `structure` | Related claims grouped in one file — sections per sub-claim |
| Capture | /capture | `capture` | Verbatim source in a fenced block — no transformation |

**Shared invariants across all three:**
- One unified template (`ops/templates/note.md`) — `granularity` is a field, not a directory
- Every note in the same flat `{DOMAIN:note_collection}/` folder regardless of granularity
- Every note has the six required fields (title, content_type, granularity, description, created_at, tags)
- Wiki links connect notes to the graph
- At least one `{DOMAIN:topic map}` membership

**Choosing a pipeline:** match the pipeline to the source material, not the other way around. Research papers with decomposable claims → /extract. Meeting notes mixing multiple related topics → /structure. Verbatim transcripts where exact wording matters → /capture. When unsure, /structure is a safe middle ground.

**The downstream chain is shared.** All three pipelines feed into the same connection-finding (/{DOMAIN:reflect}), backward-maintenance (/{DOMAIN:reweave}), and verification (/{DOMAIN:verify}) phases. These phases select behavior based on the `granularity` field.
```

## Dependencies
None — this is foundational.
