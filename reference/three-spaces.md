# Three-Space Architecture Reference

Every generated system divides its workspace into three spaces: self, notes, and ops. This is not an organizational preference. The three spaces have fundamentally different durability profiles, growth patterns, and query characteristics.

---

## Self Space — The Agent's Persistent Mind

**Enforcement:** Invariant. Every generated vault includes self/.

**Durability:** Permanent. Content accumulates slowly and is rarely deleted.

**Growth pattern:** Slow — tens of files, not hundreds. Updated incrementally at session end, not batch-processed.

**Load pattern:** Full load at every session start. Small enough to fit in context without progressive disclosure.

**Purpose:** The agent must remember who it is before doing anything else. Without self/, every session starts from zero — the agent knows methodology but not identity, goals, or accumulated operational wisdom.

### Core Files

| File | Contents | Update Trigger |
|------|----------|----------------|
| `identity.md` | Who the agent is — personality, voice, approach, values | Rarely (personality doesn't change often) |
| `methodology.md` | How the agent works — quality standards, processing principles, operational patterns | When operational learnings accumulate (evolves as agent learns) |
| `goals.md` | Current threads — what's active, deferred, completed | Every session (the orientation file) |

### Optional Extensions

| File/Directory | Included When | Purpose |
|---------------|---------------|---------|
| `relationships.md` | Domain involves multiple people | Key people, preferences, interaction patterns |

### Design Rule

**Only what the agent needs about itself.** Self/ is not a second knowledge graph — it holds agent identity, operational learning, and current orientation. Domain knowledge lives in notes/. Processing scaffolding lives in ops/. Self/ answers: "Who am I? How do I work? What am I working on?"

### The Session Rhythm Integration

Self space is the anchor of the session rhythm primitive:

```
Orient -> read self/identity.md, self/methodology.md, self/goals.md
Work   -> do the actual task, surface connections
Persist -> update self/goals.md (and methodology.md when learnings accumulate)
```

The context file documents the agent's purpose; self/ carries the evolving identity, methodology, and orientation layered on top.

---

## Notes Space — The User's Knowledge Graph

**Durability:** Permanent. Everything here should be worth finding again.

**Growth pattern:** Steady — varies by domain and processing intensity. Research vaults grow at 10-50 claims/week. Companion vaults grow at 2-5 memories/week.

**Load pattern:** Progressive disclosure. Too large to load fully. Use MOC navigation, description queries, semantic search, and link traversal to find relevant content.

**Purpose:** The reason the system exists. The user's intellectual workspace where knowledge compounds through connections.

### Structural Constants (from the kernel)

These hold across all generated systems:

| Constant | Implementation | Why It's Universal |
|----------|---------------|-------------------|
| Flat note collection | A single note_collection directory holds notes regardless of content type. | Link stability holds because filenames remain globally unique. Topic maps provide navigation without folder hierarchy. |
| Prose-sentence titles | Atomic notes make one claim; structure notes use one source-bounded proposition covering grouped subclaims | Enables wiki-link-as-prose pattern |
| MOC navigation | Hub -> domain -> topic -> notes | Manages attention at scale |
| Wiki links | `[[note title]]` creates graph edges | Spreading activation without infrastructure |
| Topics footer | Every note declares MOC membership | Bidirectional navigation |

### What Varies by Domain

| Aspect | Universal Pattern | Domain Adaptation |
|--------|-------------------|-------------------|
| Folder name | `notes/` | Vocabulary transform: `reflections/`, `concepts/`, `decisions/`, `memories/` |
| Note title style | Prose sentence | Domain phrasing: "client showed progress on..." vs "the evidence suggests..." |
| Schema fields | `description`, `topics` | Domain fields: `person`, `session_date`, `confidence`, `alternatives` |
| MOC vocabulary | Hub, domain, topic | Domain groupings: "themes", "project areas", "study guides" |

### Design Rule

**Durable, composable, worth finding again.** If it won't be queried or linked, it doesn't belong here. Session-specific observations start in ops/ and get promoted when they earn permanence. Raw capture starts in inbox/ and gets processed into the note_collection through the processing pipeline.

### What Does NOT Belong in Notes

- Runtime templates and derivation records -> ops/
- Agent self-knowledge -> self/
- Health workflow output -> transient JSON from `/health`
- Temporary scaffolding -> ops/

---

## Ops Space — Operational Coordination

**Durability:** Temporal. Content flows through, gets processed, and either graduates or gets archived.

**Growth pattern:** Fluctuating — grows during active work, shrinks during maintenance. Nothing in ops/ is permanent knowledge.

**Load pattern:** Targeted. Templates, derivation records, and session handoffs. Never loaded in bulk.

**Purpose:** Keep the knowledge graph clean by separating operational scaffolding from durable knowledge. Without ops/, templates, derivation records, and transient coordination artifacts accumulate alongside genuine insights, polluting search results and inflating note counts.

### Contents

| Directory | Contents | Lifecycle |
|-----------|----------|-----------|
| `derivation.md` | The original derivation record — domain summary, vocabulary choices, schema decisions, deferred candidates | Semi-permanent — rarely updated |
| `derivation-manifest.yaml` | Runtime vocabulary and folder-name manifest for generated skills | Semi-permanent |
| `templates/` | Canonical note templates and `_schema` blocks | Semi-permanent |

### Content Promotion Rule

**Content moves from temporal to durable, never the reverse.** Promotion is one-directional:

```
inbox/ -> notes/ (when captured material earns a durable claim)
```

Content never moves FROM notes/ or self/ INTO ops/. Durable knowledge doesn't become temporal scaffolding.

### The Promotion Pattern

1. Content enters ops/ at low ceremony (session notes, observations, derivation records)
2. When it demonstrates persistence — an insight proves useful across sessions, a pattern is confirmed — it gets promoted
3. Promotion means creating a proper note in notes/ or adding to self/, not moving the ops entry
4. The ops entry can then be archived, its value extracted

---

## Filesystem Layout

### Single-Entity Layout (default)

When the derivation produces one entity type, note_collection collapses to a flat directory:

```
project-root/
├── CLAUDE.md
├── .claude/
│   ├── hooks/
│   ├── skills/
│   └── settings.json
├── self/
│   ├── identity.md
│   ├── methodology.md
│   ├── goals.md
│   └── relationships.md         # optional
├── notes/                       # or domain-specific name (reflections/, concepts/, etc.)
│   ├── index.md                 # hub MOC
│   ├── [domain-mocs].md         # domain/topic MOCs
│   └── [prose-titled-notes].md  # atomic notes
├── inbox/                       # or domain-specific name
├── archive/                     # processed sources
└── ops/
    ├── derivation.md
    ├── derivation-manifest.yaml
    └── templates/
```

## Content Routing Decision Tree

When the agent captures something, this decision tree determines where it belongs:

```
Is this about the agent itself?
├── YES: Is it durable self-knowledge?
│   ├── YES -> self/ (identity, methodology, goals, relationships)
│   └── NO -> ops/ (observations, current processing state)
│
└── NO: Is this domain knowledge?
    ├── YES: Is it durable, composable, worth finding again?
    │   ├── YES -> notes/ (atomic note with proper schema)
    │   └── NO -> ops/ (observation, friction log, session note)
    │       └── May be promoted to notes/ later if it persists
    │
    └── NO: Is this operational coordination?
        └── YES -> ops/ (template, derivation record, session handoff)
```

**Quick routing rules:**

| Content Type | Destination | Why |
|-------------|-------------|-----|
| "I work best when..." | self/methodology.md | Agent operational learning |
| "The user prefers..." | self/relationships.md | Agent knowledge about user |
| "Spaced repetition helps memory" | notes/ | Domain knowledge |
| "Inbox has 12 unprocessed items" | transient `/health` JSON | Temporal coordination state |
| "Schema validation passed" | transient `/health` JSON | Point-in-time diagnostic |
| "My goal this quarter is..." | self/goals.md | Agent orientation |

---

## Cross-Reference

- **What goes in each space per domain:** See `use-case-presets.md` for domain-specific routing decisions (therapy reflections vs research claims vs PM decisions).
- **Kernel primitives that depend on three-space separation:** `self-space`, `session-rhythm`, and `discovery-first` all assume clean space boundaries. See `kernel.yaml`.
