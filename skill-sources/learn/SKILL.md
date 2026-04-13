---
name: learn
description: Research a topic and grow your knowledge graph. Uses web search to investigate topics, files results with full provenance, and chains to processing pipeline. Triggers on "/learn", "/learn [topic]", "research this", "find out about".
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, WebSearch
---

## EXECUTE NOW

**Topic: $ARGUMENTS**

Parse immediately:
- If topic provided: research that topic
- If topic empty: read `self/goals.md` for highest-priority unexplored direction and propose it
- If no topic and no goals.md: ask "What would you like to research?"

**Steps:**

1. **Read config** — pipeline chaining mode, domain vocabulary
2. **Research** — WebSearch
3. **File to inbox** — with provenance metadata
4. **Chain to processing** — next step based on pipeline chaining mode
5. **Update goals.md** — append new research directions discovered

**START NOW.** Reference below explains methodology.

---

## Step 1: Read Configuration

```
ops/config.yaml             — pipeline chaining mode
ops/derivation-manifest.md  — domain vocabulary (inbox folder, reduce skill name)
```

**From config.yaml** (defaults if missing):
```yaml
pipeline:
  chaining: suggested             # manual | suggested | automatic
```

**From derivation-manifest.md** (universal defaults if missing):
- Inbox folder: `inbox/` (could be `journal/`, `encounters/`, etc.)
- Processing skill names: `/extract`, `/structure`, `/capture`
- Domain name and hub MOC name

---

## Step 2: Research

Output header:
```
Researching: [topic]
```

Call WebSearch:
```
WebSearch  query: "[topic]"
```

If WebSearch fails or returns empty:
```
FAIL: Research failed

  WebSearch returned no results for "[topic]"

  Try refining the topic or manually add research to [inbox-folder]/
```

On success: `Research complete`

---

## Step 3: File Results to Inbox

**Filename:** `YYYY-MM-DD-[slugified-topic].md` — lowercase, spaces to hyphens, no special chars.

**Write to** the domain inbox folder (from derivation-manifest, default `inbox/`). Create folder if missing.

### Provenance Frontmatter

```yaml
---
description: [1-2 sentence summary of key findings]
source_type: web-search
research_prompt: "[query sent to WebSearch]"
generated: [ISO 8601 timestamp — run: date -u +"%Y-%m-%dT%H:%M:%SZ"]
domain: "[domain name from derivation-manifest]"
topics: ["[[domain-hub-moc]]"]
---
```

### Body Structure

Format for downstream reduce extraction — findings as clear propositions, not raw dumps:

```markdown
# [Topic Title]

## Key Findings

[Synthesized findings organized by theme, not by source. Each finding
should be a clear proposition the reduce phase can extract as an atomic insight.]

## Sources

[List of sources with titles and URLs]

## Research Directions

[New questions, unexplored angles, follow-up topics. These feed goals.md.]
```

---

## Step 4: Chain to Processing

Read chaining mode from config (default: `suggested`).

```
Research complete

  Filed to: [inbox-folder]/[filename]

  Next: /[reduce-skill-name] [inbox-folder]/[filename]
```

Append based on mode:
- **manual:** (nothing extra)
- **suggested:** `Ready for processing when you are.`
- **automatic:** Replace "Next" line with `Queued for /[reduce-skill-name] -- processing will begin automatically.`

---

## Step 5: Update goals.md

If `self/goals.md` exists AND the research uncovered meaningful new directions:

1. Read goals.md, match existing format
2. Append under the appropriate section:
   ```
   - [New direction] (discovered via /learn: [original topic])
   ```

Skip silently if goals.md missing or no meaningful directions found. Do not add filler.

---

## Output Summary

Clean output wrapping the full flow:
```
ars contexta

Researching: [topic]

  Research complete -- [N] sources analyzed

  Filed to: [inbox-folder]/[filename]

  Next: /[reduce-skill-name] [inbox-folder]/[filename]
    [chaining context]

  [goals.md updated with N new research directions]
```

---

## Error Handling

| Error | Behavior |
|-------|----------|
| No topic, no goals.md | Ask: "What would you like to research?" |
| WebSearch fails | Report failure, suggest manual inbox filing |
| Empty results | Report "No results found", suggest refining topic |
| Config files missing | Use defaults silently |
| Inbox folder missing | Create it before writing |

---

## Skill Selection Routing

After /learn, the self-building loop continues:

| Phase | Skill | Purpose |
|-------|-------|---------|
| Extract insights | /[reduce-name] | Mine research for atomic propositions |
| Find connections | /[reflect-name] | Link new insights to existing graph |
| Update old notes | /[reweave-name] | Backward pass on touched notes |
| Quality check | /[verify-name] | Description quality, schema, links |

/learn is the entry point. Each run feeds the graph, and the graph feeds the next direction through goals.md.
