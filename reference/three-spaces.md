# Three-Space Architecture Reference

Every generated system divides its workspace into three spaces: self, notes, and ops. This is not an organizational preference but an architectural decision driven by failure mode prevention. The three spaces have fundamentally different durability profiles, growth patterns, and query characteristics. Conflating any two produces predictable, documented failures.

---

## Self Space — The Agent's Persistent Mind (Configurable)

**Enforcement:** Configurable. Off by default for research vaults, on by default for personal assistant vaults. Toggled by editing `ops/config.yaml`.

**Durability:** Permanent. Content accumulates slowly and is rarely deleted.

**Growth pattern:** Slow — tens of files, not hundreds. Updated incrementally at session end, not batch-processed.

**Load pattern:** Full load at every session start. Small enough to fit in context without progressive disclosure.

**Purpose:** The agent must remember who it is before doing anything else. Without self/, every session starts from zero — the agent knows methodology but not identity, goals, or accumulated operational wisdom.

### When Self Space Is Enabled

#### Core Files

| File | Contents | Update Trigger |
|------|----------|----------------|
| `identity.md` | Who the agent is — personality, voice, approach, values | Rarely (personality doesn't change often) |
| `methodology.md` | How the agent works — quality standards, processing principles, operational patterns | When operational learnings accumulate (evolves as agent learns) |
| `goals.md` | Current threads — what's active, deferred, completed | Every session (the orientation file) |

#### Optional Extensions (generated based on configuration)

| File/Directory | Included When | Purpose |
|---------------|---------------|---------|
| `relationships.md` | Domain involves multiple people | Key people, preferences, interaction patterns |
| `memory/` | Agent needs atomic self-knowledge beyond core files | Prose-titled atomic notes mirroring the notes/ pattern |
| `journal/` | Agent captures raw session observations | Processing input for self-knowledge — analogous to inbox |
| `sessions/` | Session logs need graduated storage | Session-specific logs that might graduate to memory/ or methodology.md |

### When Self Space Is Disabled

When self/ is off (the default for research vaults), the essential functions route elsewhere:

| Function | Fallback Location | Notes |
|----------|-------------------|-------|
| Goals / orientation | `ops/goals.md` | Current threads, active work — the session orientation file |
| Methodology / self-knowledge | `ops/methodology/` | Vault configuration rationale, pipeline config, evolution history |
| Identity | Context file | Agent personality baked into the context file directly |

The key insight is that self/ serves two distinct purposes: (1) agent identity/personality and (2) operational orientation. Research vaults typically do not need a persistent agent personality — the context file handles identity. Operational orientation (goals, methodology) routes to ops/ where it belongs alongside other operational state.

### Toggle Mechanism

Self space is toggled by editing `ops/config.yaml` and restarting. Enabling self/ creates the directory and scaffolds the core files; disabling migrates goals to `ops/goals.md` and archives self/. The toggle preserves content — disabling does not delete goals.

### Design Rule

**Only what the agent needs about itself.** Self/ is not a second knowledge graph — it holds agent identity, operational learning, and current orientation. Domain knowledge lives in notes/. Processing scaffolding lives in ops/. Self/ answers: "Who am I? How do I work? What am I working on?"

### The Session Rhythm Integration

Self space integrates with the session rhythm primitive, but is not required by it:

```
Orient -> read orientation state (self/ if enabled, ops/goals.md if not)
Work   -> do the actual task, surface connections
Persist -> update orientation state (self/ or ops/goals.md)
```

The session rhythm primitive depends on markdown-yaml, not on self-space. When self/ is disabled, the orient/persist cycle still works — it just reads from and writes to ops/ instead. The context file always provides methodology and identity; self/ adds a richer, evolving layer on top.

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

**Load pattern:** Targeted. Queue status, today's session log, latest health report. Never loaded in bulk.

**Purpose:** Keep the knowledge graph clean by separating operational scaffolding from durable knowledge. Without ops/, session logs, queue state, and health reports accumulate alongside genuine insights, polluting search results and inflating note counts.

### Contents

| Directory | Contents | Lifecycle |
|-----------|----------|-----------|
| `derivation.md` | The original derivation rationale — dimension positions, tradition mapping, vocabulary choices, rationale for each decision | Semi-permanent — rarely updated |
| `derivation-manifest.md` | Version tracking — arscontexta version, research snapshot date, feature blocks enabled, coherence validation results | Semi-permanent |
| `reminders.md` | User-delegated time-bound actions — flat markdown, checked at orient, items removed on completion | Active rotation — items added and removed regularly |
| `sessions/` | Session logs — what happened today, handoff notes for next session | Rolling archive — logs older than 30 days can be archived without knowledge loss |
| `health/` | Schema validation results, orphan lists, link health metrics — point-in-time snapshots | Superseding — yesterday's report is superseded by today's |
| `observations/` | Operational learnings captured during work — pre-promotion holding area | Graduating — observations get promoted to notes/ or self/ when they earn permanence |
| `queue/` | Processing queue state — what needs extraction, connection, verification | Flowing — items move through and complete |

### Reminders Specification

`ops/reminders.md` is a flat markdown file for user-delegated time-bound actions:

```markdown
# Reminders

- [ ] 2026-02-15: Follow up with Sarah about the new job
- [ ] 2026-03-01: Follow up with Sarah about job offer
- [x] 2026-02-10: Send reading list to Alex (done 2026-02-10)
```

**Behavior:**
- Checked at orient (session start) — due items surface in the morning briefing
- Completed items are marked with `[x]` and date, then archived when the list grows long
- No complex scheduling — if the user needs recurring reminders, that's a different tool

### Content Promotion Rule

**Content moves from temporal to durable, never the reverse.** Promotion is one-directional:

```
ops/observations/ -> notes/ (when observation proves durable)
ops/observations/ -> self/methodology.md (when observation is about agent operation)
```

Content never moves FROM notes/ or self/ INTO ops/. Durable knowledge doesn't become temporal scaffolding.

### The Promotion Pattern

1. Content enters ops/ at low ceremony (friction logs, session notes, queue entries)
2. When it demonstrates persistence — same observation recurs, insight proves useful across sessions, pattern is confirmed — it gets promoted
3. Promotion means creating a proper note in notes/ or adding to self/, not moving the ops entry
4. The ops entry can then be archived, its value extracted

---

## Six Failure Modes of Conflation

Each conflation pattern produces specific, predictable failures:

### 1. Ops into Notes

**What happens:** Processing queue state, session logs, and health reports end up in the notes/ directory alongside genuine insights.

**What breaks:** Search returns processing debris alongside real knowledge. Note counts are inflated with temporal content. MOCs accumulate operational entries that don't belong. The knowledge graph becomes noisy — an agent searching for "learning patterns" finds session log mentions alongside genuine claims.

**Example:** A session log that says "processed 5 papers today, found connection between X and Y" gets filed in notes/. The connection between X and Y should be a note; the processing status should not.

### 2. Self into Notes

**What happens:** Agent identity, preferences, and operational methodology end up in the user's knowledge graph.

**What breaks:** Schema confusion — agent self-knowledge has different fields than domain knowledge. Search pollution — "how I process therapy reflections" is agent methodology, not a therapy insight. The user's graph contains content about the agent rather than about the domain. Progressive disclosure loads agent self-knowledge when searching for domain content.

**Example:** An agent note saying "I work best when processing in small batches" gets filed alongside user's therapy reflections.

### 3. Notes into Ops

**What happens:** Genuine insights stay trapped in session logs or observation files, never becoming permanent notes.

**What breaks:** Insights are lost when ops/ is archived or purged. Knowledge doesn't compound because session-trapped insights can't be linked from other notes. The user has to re-discover insights that were already captured but never promoted. The vault appears thinner than the work invested would suggest.

**Example:** A session log captures "realized that morning anxiety correlates with skipping exercise" but it never becomes a proper note in reflections/. Three months later, the session log is archived and the insight is effectively gone.

### 4. Self into Ops

**What happens:** Agent identity is scattered across 50 session logs instead of curated in self/ files.

**What breaks:** Orientation fails — the agent can't load 50 session logs to remember who it is. Identity drifts because there's no authoritative source. Session logs that mention identity ("I should be more direct") don't accumulate into identity evolution — they're temporal artifacts.

**Example:** The agent's evolving understanding of its voice is spread across session notes instead of living in self/identity.md where it can be loaded, refined, and maintained.

### 5. Ops into Self

**What happens:** Agent identity gets polluted with temporal processing state — today's queue status, current health metrics, in-progress session context.

**What breaks:** Self/ becomes too large to load fully at session start. Temporal content creates noise in identity orientation. The agent's self-model includes "I have 12 items in queue" as if it were identity rather than current state.

**Example:** self/methodology.md includes "currently processing the Johnson 2026 paper" — which is ops state, not methodology.

### 6. Notes into Self

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
│   ├── memory/                  # optional
│   └── journal/                 # optional
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
    ├── reminders.md
    ├── sessions/
    ├── health/
    ├── observations/
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
│   └── NO -> ops/ (session log, current processing state)
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
| "The reduce skill over-extracts" | ops/observations/ | Operational friction (may promote) |
| "Queue has 12 items" | ops/queue/ | Temporal coordination state |
| "Schema validation passed" | ops/health/ | Point-in-time diagnostic |
| "My goal this quarter is..." | self/goals.md | Agent orientation |
| "Remember to follow up by Friday" | ops/reminders.md | Time-bound action |

---

## Cross-Reference

- **Failure modes that afflict each space:** See `failure-modes.md` for the full failure mode taxonomy. Conflation failures (this document) are structural; failure-modes.md covers operational decay (collector's fallacy, orphan drift, schema erosion).
- **What goes in each space per domain:** See `use-case-presets.md` for domain-specific routing decisions (therapy reflections vs research claims vs PM decisions).
- **Kernel primitives that depend on three-space separation:** `self-space` (configurable), `session-rhythm`, `discovery-first`, and `methodology-folder` all assume clean space boundaries. See `kernel.yaml`.
