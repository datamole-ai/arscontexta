# Three-Space Architecture Reference

Every generated system divides its workspace into three spaces: self, notes, and ops. This is not an organizational preference but an architectural decision driven by failure mode prevention. The three spaces have fundamentally different durability profiles, growth patterns, and query characteristics. Conflating any two produces predictable, documented failures.

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

### Optional Extensions (generated based on configuration)

| File/Directory | Included When | Purpose |
|---------------|---------------|---------|
| `relationships.md` | Domain involves multiple people | Key people, preferences, interaction patterns |
| `memory/` | Agent needs atomic self-knowledge beyond core files | Prose-titled atomic notes mirroring the notes/ pattern |

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
| Flat within entity type | No subfolders within entity directories. When multiple entity types are derived, note_collection contains typed subdirectories (e.g., projects/, contacts/). | Entity types are stable structural categories from derivation, not user-reorganizable hierarchy. Link stability holds because filenames remain globally unique across all entity directories. |
| Prose-sentence titles | Each note makes one claim, titled as a sentence | Enables wiki-link-as-prose pattern |
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

**Durable, composable, worth finding again.** If it won't be queried or linked, it doesn't belong here. Session-specific observations start in ops/ and get promoted when they earn permanence. Raw capture starts in inbox/ and gets processed into the note_collection through the processing pipeline. When the collection has entity-type subdirectories, the processing pipeline routes each note to the matching entity directory based on its schema entity_type.

### What Does NOT Belong in Notes

- Processing queue state -> ops/queue/
- Agent self-knowledge -> self/
- Health reports -> ops/health/
- Temporary scaffolding -> ops/

---

## Ops Space — Operational Coordination

**Durability:** Temporal. Content flows through, gets processed, and either graduates or gets archived.

**Growth pattern:** Fluctuating — grows during active work, shrinks during maintenance. Nothing in ops/ is permanent knowledge.

**Load pattern:** Targeted. Queue status, latest health report. Never loaded in bulk.

**Purpose:** Keep the knowledge graph clean by separating operational scaffolding from durable knowledge. Without ops/, queue state, health reports accumulate alongside genuine insights, polluting search results and inflating note counts.

### Contents

| Directory | Contents | Lifecycle |
|-----------|----------|-----------|
| `derivation.md` | The original derivation rationale — dimension positions, tradition mapping, vocabulary choices, rationale for each decision | Semi-permanent — rarely updated |
| `derivation-manifest.md` | Version tracking — arscontexta version, research snapshot date, feature blocks enabled, coherence validation results | Semi-permanent |
| `health/` | Schema validation results, orphan lists, link health metrics — point-in-time snapshots | Superseding — yesterday's report is superseded by today's |
| `queue/` | Processing queue state — what needs extraction, connection, verification | Flowing — items move through and complete |

### Content Promotion Rule

**Content moves from temporal to durable, never the reverse.** Promotion is one-directional:

```
inbox/ -> notes/ (when captured material earns a durable claim)
```

Content never moves FROM notes/ or self/ INTO ops/. Durable knowledge doesn't become temporal scaffolding.

### The Promotion Pattern

1. Content enters ops/ at low ceremony (session notes, queue entries, health reports)
2. When it demonstrates persistence — an insight proves useful across sessions, a pattern is confirmed — it gets promoted
3. Promotion means creating a proper note in notes/ or adding to self/, not moving the ops entry
4. The ops entry can then be archived, its value extracted

---

## Six Failure Modes of Conflation

Each conflation pattern produces specific, predictable failures:


### 1. Self into Notes

**What happens:** Agent identity, preferences, and operational methodology end up in the user's knowledge graph.

**What breaks:** Schema confusion — agent self-knowledge has different fields than domain knowledge. Search pollution — "how I process therapy reflections" is agent methodology, not a therapy insight. The user's graph contains content about the agent rather than about the domain. Progressive disclosure loads agent self-knowledge when searching for domain content.

**Example:** An agent note saying "I work best when processing in small batches" gets filed alongside user's therapy reflections.


### 2. Ops into Self

**What happens:** Agent identity gets polluted with temporal processing state — today's queue status, current health metrics, in-progress session context.

**What breaks:** Self/ becomes too large to load fully at session start. Temporal content creates noise in identity orientation. The agent's self-model includes "I have 12 items in queue" as if it were identity rather than current state.

**Example:** self/methodology.md includes "currently processing the Johnson 2026 paper" — which is ops state, not methodology.

### 3. Notes into Self

**What happens:** Domain knowledge gets stored in self/ because it felt personally relevant to the agent.

**What breaks:** Self/ bloats beyond what can be loaded at session start. The agent carries domain-specific knowledge as identity, which doesn't scale. Search in notes/ misses content that's hidden in self/. The distinction between "what the agent knows about itself" and "what the agent knows about the domain" collapses.

**Example:** A research agent stores "spaced repetition works better after exercise" in self/memory/ instead of notes/. It's domain knowledge, not agent self-knowledge — even though the agent found it interesting.

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
│   ├── relationships.md         # optional
│   └── memory/                  # optional
├── notes/                       # or domain-specific name (reflections/, concepts/, etc.)
│   ├── index.md                 # hub MOC
│   ├── [domain-mocs].md         # domain/topic MOCs
│   └── [prose-titled-notes].md  # atomic notes
├── inbox/                       # or domain-specific name
├── archive/                     # processed sources
├── templates/
└── ops/
    ├── derivation.md
    ├── derivation-manifest.md
    ├── health/
    └── queue/
```

### Multi-Entity Layout

When the derivation produces multiple entity types, note_collection becomes a parent directory with typed subdirectories:

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
│   └── ...
├── knowledge-base/              # note_collection (derived vocabulary term)
│   ├── index.md                 # hub MOC
│   ├── [topic-mocs].md          # topic MOCs span entity types
│   ├── projects/                # entity type directory
│   │   └── [prose-titled-notes].md
│   ├── contacts/                # entity type directory
│   │   └── [prose-titled-notes].md
│   └── blueprints/              # entity type directory
│       └── [prose-titled-notes].md
├── inbox/                       # unified capture zone
├── archive/                     # processed sources
├── templates/
└── ops/
    ├── derivation.md
    ├── derivation-manifest.md
    └── ...
```

Entity directories contain only atomic notes, not MOCs. If an entity type needs its own navigation (e.g., "all projects"), that is a topic MOC at the note_collection root, not an index inside the entity directory.

---

## Memory Type Routing Decision Tree

When the agent captures something, this decision tree determines where it belongs:

```
Is this about the agent itself?
├── YES: Is it durable self-knowledge?
│   ├── YES -> self/ (identity, methodology, goals, memory)
│   └── NO -> ops/ (observations, current processing state)
│
└── NO: Is this domain knowledge?
    ├── YES: Is it durable, composable, worth finding again?
    │   ├── YES -> notes/ (atomic note with proper schema)
    │   └── NO -> ops/ (observation, friction log, session note)
    │       └── May be promoted to notes/ later if it persists
    │
    └── NO: Is this operational coordination?
        └── YES -> ops/ (queue state, health report, session handoff)
```

**Quick routing rules:**

| Content Type | Destination | Why |
|-------------|-------------|-----|
| "I work best when..." | self/methodology.md | Agent operational learning |
| "The user prefers..." | self/relationships.md | Agent knowledge about user |
| "Spaced repetition helps memory" | notes/ | Domain knowledge |
| "Queue has 12 items" | ops/queue/ | Temporal coordination state |
| "Schema validation passed" | ops/health/ | Point-in-time diagnostic |
| "My goal this quarter is..." | self/goals.md | Agent orientation |

---

## Cross-Reference

- **Failure modes that afflict each space:** See `failure-modes.md` for the full failure mode taxonomy. Conflation failures (this document) are structural; failure-modes.md covers operational decay (collector's fallacy, orphan drift, schema erosion).
- **What goes in each space per domain:** See `use-case-presets.md` for domain-specific routing decisions (therapy reflections vs research claims vs PM decisions).
- **Kernel primitives that depend on three-space separation:** `self-space`, `session-rhythm`, and `discovery-first` all assume clean space boundaries. See `kernel.yaml`.
