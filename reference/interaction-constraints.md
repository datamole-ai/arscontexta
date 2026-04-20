# Dimension Interaction Constraints

How choices in one dimension create pressure on others. The derivation engine uses this to detect incoherent configurations and warn the user before generating.

The valid configuration space is much smaller than the combinatorial product. Five dimensions with two-to-three positions each produces a much smaller theoretical combination space. Most are incoherent.

---

### Granularity (Per-Invocation)

Granularity is not a system dimension. It is chosen per invocation via `/extract` (atomic), `/structure` (moderate), or `/capture` (raw). Processing intensity and automation level are operational settings (`ops/config.yaml`), not design dimensions. Interaction constraints below apply to the 5 remaining dimensions: organization, linking, navigation, maintenance, schema.

---

## Cross-Dimension Interaction Matrix

Each cell describes the pressure that the row dimension's pole creates on the column dimension.

| Row → Col | Organization | Linking | Nav Depth | Maintenance | Schema |
|-----------|-------------|---------|-----------|-------------|--------|
| **Flat organization** | — | requires explicit links | requires MOC overlay | neutral | neutral |
| **Hierarchical org** | — | folder membership as linking | folder browsing sufficient | neutral | neutral |
| **Explicit+implicit linking** | neutral | — | neutral | neutral | requires semantic search tool |

---

## Coherence Rules for Init

When the user selects dimension values, check these rules. WARN on soft violations, BLOCK on hard violations.

### Soft Constraints (WARN)

These produce friction but can work with compensating mechanisms:

1. `linking == "explicit+implicit" + no_semantic_search`
   → "Implicit linking (semantic search) is enabled but no search tool is configured. The system will work with explicit links only."


### Kernel Primitive Constraints

These constraints apply to the 14 kernel primitives and their INVARIANT/CONFIGURABLE status:

**INVARIANT primitives (always present, cannot be disabled):**

1. `methodology_folder == false` (Primitive 14)
   → BLOCK: "The methodology folder is INVARIANT. Meta-skills (/rethink, /remember) require ops/methodology/ to reason about system state."

3. `schema_enforcement == false` (Primitive 7)
   → BLOCK: "Schema enforcement is INVARIANT. Without validation, metadata drift corrupts retrieval within weeks."

4. `wiki_links == false` (Primitive 3)
   → BLOCK: "Wiki links are INVARIANT. They are the universal reference form and the foundation of the graph database."

**CONFIGURABLE primitives (can be toggled):**

5. `self_space == true + preset == "research"`
   → WARN: "Self space is OFF by default for Research presets. The knowledge graph is the focus, not agent identity. Enable only if persistent agent memory across sessions is needed."

6. `self_space == false + preset == "personal_assistant"`
   → WARN: "Self space is ON by default for Personal Assistant presets. Agent identity and persistent memory are central to the experience. Disable only if the agent's sense of self is not needed."

7. `semantic_search == false + linking == "explicit+implicit"`
   → WARN: "Implicit linking works best with semantic search. Without qmd, it falls back to keyword overlap and MOC traversal."

**Condition-based maintenance constraints:**

8. `condition_thresholds_all_zero`
   → WARN: "All condition-based maintenance thresholds are set to zero (disabled). The vault will not surface maintenance tasks. Consider enabling at least orphan detection and dangling link checks."

9. `processing_queue == false` (Primitive 13)
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
