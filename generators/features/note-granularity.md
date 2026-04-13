# Feature: Note Granularity

## Context File Block

```markdown
## Note Granularity — Three Pipelines, One Graph

Every piece of content enters through {DOMAIN:inbox/} and gets processed through one of three pipelines, chosen per invocation:

| Pipeline | Command | What It Produces | When To Use |
|----------|---------|-----------------|-------------|
| Extract | /extract | One claim per file — atomic, composable, prose-as-title propositions | Decomposable claims, research findings, patterns |
| Structure | /structure | Related claims grouped in one file — sections per sub-claim | Multi-faceted topics, sequential arguments, shared-context claims |
| Capture | /capture | Verbatim source in a fenced block — no transformation | Meeting transcripts, reference documents, exact-wording material |

**Shared invariants across all three:**
- Prose-as-title filenames (specific enough for search and linking)
- YAML frontmatter with `granularity: extract | structure | capture`
- `description` field required (adds info beyond the title)
- Wiki-links connecting to the knowledge graph
- At least one {DOMAIN:topic map} membership
- All notes coexist in the same {DOMAIN:notes/} folder

**Choosing a pipeline:** Match the pipeline to the material, not the other way around. Research papers with decomposable claims → /extract. Meeting notes mixing multiple related topics → /structure. Verbatim transcripts where exact wording matters → /capture. When unsure, /structure is a safe middle ground.

**The downstream chain is shared:** All three pipelines feed into the same connection-finding (/{DOMAIN:reflect}), backward-maintenance (/{DOMAIN:reweave}), and verification (/{DOMAIN:verify}) phases. These phases adjust their quality gates based on the `granularity` frontmatter field.
```

## Dependencies
None — this is a foundational feature that replaces atomic-notes.
