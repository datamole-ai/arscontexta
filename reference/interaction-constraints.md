# Dimension Interaction Constraints

How choices in one dimension create pressure on others. The derivation engine uses this to detect incoherent configurations and warn the user before generating.

The valid configuration space is much smaller than the combinatorial product. Five dimensions with two-to-three positions each produces a much smaller theoretical combination space. Most are incoherent.

---

### Granularity (Per-Invocation)

Granularity is not a system dimension. It is chosen per invocation via `/structure` (grouped claims) or `/capture` (raw). Processing intensity and automation level are operational settings (`ops/config.yaml`), not design dimensions. Interaction constraints below apply to the 5 remaining dimensions: organization, linking, navigation, maintenance, schema.

---

## Cross-Dimension Interaction Matrix

Each cell describes the pressure that the row dimension's pole creates on the column dimension.

| Row → Col | Organization | Linking | Nav Depth | Maintenance | Schema |
|-----------|-------------|---------|-----------|-------------|--------|
| **Flat organization** | — | requires explicit links | requires MOC overlay | neutral | neutral |
| **Hierarchical org** | — | folder membership as linking | folder browsing sufficient | neutral | neutral |
| **Explicit+implicit linking** | neutral | — | neutral | neutral | neutral (semantic search is always enabled — a kernel invariant, not a linking-dependent option) |

---

## Coherence Rules for Init

When the user selects dimension values, check these rules. WARN on soft violations, BLOCK on hard violations.

### Soft Constraints (WARN)

These produce friction but can work with compensating mechanisms:

_No soft constraints currently apply to the linking dimension — semantic search is invariant, so implicit linking no longer depends on an optional tool._


### Kernel Primitive Constraints

These constraints apply to the 13 kernel primitives and their INVARIANT/CONFIGURABLE status:

**INVARIANT primitives (always present, cannot be disabled):**

3. `schema_enforcement == false` (Primitive 7)
   → BLOCK: "Schema enforcement is INVARIANT. Without validation, metadata drift corrupts retrieval within weeks."

4. `wiki_links == false` (Primitive 3)
   → BLOCK: "Wiki links are INVARIANT. They are the universal reference form and the foundation of the graph database."

5. `self_space == false` (Primitive 8)
   → BLOCK: "Self space is INVARIANT. self/ with identity.md, methodology.md, and goals.md is required in every vault; the agent's persistent memory cannot be disabled at the config level."

6. `semantic_search == false` (Primitive 10)
   → BLOCK: "Semantic search is INVARIANT. Processing skills (/reflect, /verify, /structure, /seed) call `qmd query` via Bash directly. It cannot be disabled at the config level; if qmd is not installed, the wiring is still generated and the install is surfaced as a required next step."

**Condition-based maintenance constraints:**

7. `condition_thresholds_all_zero`
   → WARN: "All condition-based maintenance thresholds are set to zero (disabled). The vault will not surface maintenance tasks. Consider enabling at least orphan detection and dangling link checks."

8. `processing_queue == false` (Primitive 13)
   → BLOCK: "The processing queue is INVARIANT. Without queue tracking, the pipeline has no lifecycle visibility and cannot resume after interruption."

---

## Compensating Mechanisms

Some dimension mismatches can be compensated rather than blocked:

| Mismatch | Compensating Mechanism | Effectiveness |
|----------|----------------------|---------------|
| Dense schema + no validation hooks | Good templates reduce manual validation burden | Moderate — helps at capture, not at maintenance |

Interaction constraints split into hard (violating them produces failure) and soft (violating them produces friction that compensating mechanisms can overcome). Hard constraints are enforced at derivation time; soft constraints are surfaced as warnings and either auto-resolved via cascade or recorded in the derivation rationale.

---

## Derivation Application

When generating a system:

1. **Start from use-case preset** (or tradition preset) — these are pre-validated coherence points
2. **Allow user customization** — but check each change against interaction constraints
3. **Cascade recommendations** — granularity is per-invocation and does not require cascade recommendations; apply cascade logic only to the 5 remaining dimensions (organization, linking, navigation, maintenance, schema)
4. **Document justification** — include interaction constraint reasoning in the derivation rationale section of the generated context file
5. **Flag unresolved tensions** — if user overrides a warning, note it in the generated system

The derivation rationale should include which constraints were active and how they were resolved.
