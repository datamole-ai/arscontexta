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

## Ownership

Use qmd directly for semantic discovery:

```bash
qmd query "<concept query>" --collection notes -n 15
qmd vsearch "<description or concept>" --collection notes -n 15
```

Use Obsidian CLI directly for vault-native facts:

```bash
obsidian links path="<root-relative note path>"
obsidian backlinks path="<root-relative note path>"
obsidian unresolved verbose format=json
obsidian properties
obsidian tags
```

Use Obsidian `move` or `rename` for graph-note path/name changes. After a move or rename, update every matching `artifacts[].path` to the new path; a stale path fails validation and aborts the pipeline.

## Rules

- Run every qmd and Obsidian command in its own Bash tool call. The command
  string must start with `qmd` or `obsidian` and contain exactly one invocation.
  Do not add leading commands, loops, pipes, semicolons, `&&`, or shell command
  substitutions. Inspect the command's complete output directly.
- Do not wrap qmd in Python.
- Edit note prose, footers, frontmatter, and topic maps directly in Markdown.
- For capture artifacts, never change text inside the verbatim fenced block.
- Every connection must have an explicit reason grounded in the artifact, source, existing note, or topic map.
- When changing topic maps or other graph notes not already listed in `artifacts`, add them to `artifacts` with `kind: "enrichment"`. Every edited file must appear in `artifacts`; it is the only channel into validation and the pipeline commit.
- Any navigation note this skill creates sets `content_type: moc` and `granularity: distilled`. This skill does not create regular content notes.
- Any tag added or changed during enrichment must match an entry in `ops/tags.yaml`. If none fits, append a new entry with `tag` and a one-sentence `meaning` there. Do not list `ops/tags.yaml` in `artifacts`.
- Capture notes arrive with only a `Source:` provenance line below the fenced block; never edit or remove it, validation byte-checks the payload against it. This skill owns adding their `Topics:` footer and any link edits, always below the fenced block. Link only to notes that exist, or create the topic map note first. Use the scoped unresolved check above.
- After your edits, no artifact in `artifacts` may contain an unresolved wiki link.

## Workflow

1. Read each artifact path in `artifacts`.
2. Use artifact text, title, description, and Topics footer to name search concepts.
3. Run qmd discovery for those concepts.
4. For every input artifact, inspect links and backlinks using its explicit
   `path=`. Inspect candidate notes and topic maps the same way when their graph
   context is needed. Run the vault-wide unresolved, property, and tag checks.
5. Read candidate notes and topic maps before editing.
6. Add only justified wiki links and topic-map entries.
7. Re-run links and backlinks with `path=` for every final artifact. Run
   `unresolved verbose format=json` and fail only when an unresolved entry names
   a final artifact in `sources`.
8. Return updated lean pipeline state.

## Output

Emit a single JSON object:

```json
{
  "batch": "<batch>",
  "source": "<source>",
  "artifacts": [
    {"kind": "note", "path": "notes/example.md"},
    {"kind": "enrichment", "path": "notes/topic-map.md"}
  ]
}
```

No prose, headings, or markdown fences. On failure, emit `status: "error"` with compact path/error details.
