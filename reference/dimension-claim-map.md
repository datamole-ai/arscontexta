# Dimension-Claim Map

Which research claims inform which configuration dimensions. The derivation engine uses this to trace every dimension choice back to specific evidence.

---

## Dimension 1: Organization (flat ↔ hierarchical)

| Claim | What It Says | Informs |
|-------|-------------|---------|
| associative ontologies beat hierarchical taxonomies | Heterarchy adapts while hierarchy brittles | Default recommendation |
| topological organization beats temporal for knowledge work | Concept-based beats date-based | Organization axis |
| navigational vertigo emerges in pure association systems | Without MOCs, unlinked neighbors become unreachable | When hierarchy is needed |
| faceted classification treats notes as multi-dimensional objects | Ranganathan's PMEST: facets compose multiplicatively | Alternative to folder hierarchy |

**Default position:** Flat with MOC overlay. Add folders only when file counts exceed tool limits.

---

## Dimension 2: Linking Philosophy (explicit-only ↔ explicit+implicit)

| Claim | What It Says | Informs |
|-------|-------------|---------|
| propositional link semantics transform wiki links from associative to reasoned | Moving from "related" to "this causes/enables/contradicts that" | Link quality standard |
| inline links carry richer relationship data than metadata fields | Prose context encodes WHY notes connect | Link format |
| concept-orientation beats source-orientation | Organizing by concept enables cross-domain edges | Link target design |
| controlled disorder engineers serendipity through semantic linking | Luhmann: perfect order yields zero surprise | When to add implicit |
| spreading activation models how agents should traverse | Graph traversal as primary discovery mechanism | Traversal pattern |

**Default position:** Explicit+implicit (wiki links primary, semantic search supplemental).

---

## Dimension 3: Navigation Depth (2-tier ↔ 4-tier)

| Claim | What It Says | Informs |
|-------|-------------|---------|
| MOCs are attention management devices not just organizational tools | Reduce context-switching cost by 23 minutes | Why depth matters |
| progressive disclosure means reading right not reading less | Each layer reveals more but costs more tokens | Layer design |
| basic level categorization determines optimal MOC granularity | Cognitive sweet spot for categorization depth | Tier count |
| community detection algorithms can inform when MOCs should split or merge | Algorithmic signals for structural maintenance | Maintenance trigger |

**Default position:** 3-tier (hub → domain → topic). Add 4th tier at >100 notes per topic.

---

## Dimension 4: Maintenance Sensitivity (tight thresholds ↔ lax thresholds)

| Claim | What It Says | Informs |
|-------|-------------|---------|
| backward maintenance asks what would be different if written today | Living documents, not finished artifacts | Maintenance philosophy |
| incremental formalization happens through repeated touching | Many small touches over time | Threshold pattern |
| gardening cycle implements tend prune fertilize operations | Separated maintenance phases | Phase structure |
| random note resurfacing prevents write-only memory | Counteracts structural attention bias | Anti-stagnation |
| spaced repetition scheduling could optimize vault maintenance | Front-loaded review intervals | Scheduling pattern |
| derived systems follow a seed-evolve-reseed lifecycle | Minimum viable → friction-driven → principled restructuring | Evolution pattern |

**Default position:** Condition-based for all domains with tight thresholds (low orphan/inbox tolerance). Agent processing speed makes tight thresholds the appropriate default regardless of domain rate of change.

---

## Dimension 5: Schema Density (minimal ↔ dense)

| Claim | What It Says | Informs |
|-------|-------------|---------|
| metadata reduces entropy enabling precision over recall | Pre-computed representations shrink search space | Why density helps |
| schema evolution follows observe-then-formalize not design-then-enforce | Start minimal, grow based on evidence | Evolution pattern |
| schema fields should use domain-native vocabulary not abstract terminology | Every abstractly-named field forces translation at capture | Naming constraint |
| type field enables structured queries without folder hierarchies | Content-kind metadata provides filtering axis | Minimum useful field |
| descriptions are retrieval filters not summaries | Lossy compression optimized for decision-making | Description design |

**Default position:** Minimal (description + topics). Add fields when querying patterns emerge.

---

## Cross-Dimension Interactions

| Interaction | Claim | Effect |
|-------------|-------|--------|

---

## Methodology Tradition Presets

See `tradition-presets.md` for the full tradition configurations, use-case presets, and mixing rules. That file is the single source of truth for preset definitions.
