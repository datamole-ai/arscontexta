---
name: connect
description: Internal pipeline skill -- owns qmd discovery, Obsidian graph fact gathering, topic-map updates, and final graph edits for pipeline artifacts.
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob, Bash
---

## Execute

Target: `$ARGUMENTS`

Parse the target as pipeline state JSON. It must contain `batch`, `source`, and `artifacts`.

If state is missing or invalid, emit:

```json
{"status":"error","error":"connect requires pipeline state JSON"}
```

Read:

```bash
cat ops/derivation-manifest.yaml
```

## Ownership

`/connect` owns all semantic and graph discovery after producer validation.

Use qmd directly for semantic discovery:

```bash
qmd query "<concept query>" --collection "<qmd_collection>" -n 15
qmd vsearch "<description or concept>" --collection "<qmd_collection>" -n 15
```

Use Obsidian CLI directly for vault-native facts:

```bash
obsidian links
obsidian backlinks
obsidian unresolved
obsidian properties
obsidian tags
```

Use Obsidian `move` or `rename` for graph-note path/name changes.

## Rules

- Do not rely on queue state.
- Do not expect semantic neighbors from `/structure` or `/capture`.
- Do not call Python graph helpers; they do not exist in the runtime.
- Do not wrap qmd in Python.
- Edit note prose, footers, frontmatter, and topic maps directly in Markdown.
- For capture artifacts, never change text inside the verbatim fenced block.
- Every connection must have an explicit reason grounded in the artifact, source, existing note, or topic map.
- When changing topic maps or other graph notes not already listed in `artifacts`, add their paths to `commit_paths`.

## Workflow

1. Read each artifact path in `artifacts`.
2. Use artifact text, title, description, and Topics footer to name search concepts.
3. Run qmd discovery for those concepts.
4. Use Obsidian CLI to inspect existing links, backlinks, unresolved links, properties, and tags.
5. Read candidate notes and topic maps before editing.
6. Add only justified wiki links and topic-map entries.
7. Re-run targeted Obsidian checks for changed paths.
8. Return updated lean pipeline state.

## Output

Emit a single JSON object:

```json
{
  "batch": "<batch>",
  "source": "<source>",
  "artifacts": [{"kind": "note", "path": "notes/example.md"}],
  "commit_paths": ["notes/topic-map.md"]
}
```

No prose, headings, or markdown fences. On failure, emit `status: "error"` with compact path/error details.
