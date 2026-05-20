# Use-Case Reference Domains

Internal reference domains for vocabulary, processing categories, and starter topic maps. These are matching aids, not user-facing choices.

Every generated vault uses the same kernel: flat note collection, wiki links plus semantic search, topic-map navigation, full processing pipeline, templates, hooks, health checks, and self/ continuity.

---

## Reference Domains

### Research

**Optimizes for:** Deep synthesis, cross-domain connection density, long-term knowledge accumulation.

**Background traditions:** Zettelkasten for composable claims; Cornell for structured processing phases.

**Vocabulary defaults:**

| Universal | Research |
|-----------|----------|
| note | claim |
| note_plural | claims |
| note_collection | notes |
| inbox | inbox |
| archive | archive |
| topic_map | topic map |
| hub | index |
| description | description |
| topics | Topics |
| relevant_notes | Relevant Notes |

**Processing categories:** claims, evidence, methodology-comparisons, contradictions, open-questions, design-patterns.

**Starter topic maps:** domain-overview, methods, open-questions.

**Example signals:**
- "I read papers and need to track claims across disciplines."
- "I'm building a literature review."
- "I need to compare sources and see contradictions."

---

### Personal Assistant

**Optimizes for:** Reflection, pattern detection, personal growth tracking, relationship awareness.

**Background traditions:** Journaling, coaching, and companion-style continuity.

**Vocabulary defaults:**

| Universal | Personal Assistant |
|-----------|-------------------|
| note | reflection |
| note_plural | reflections |
| note_collection | reflections |
| inbox | journal |
| archive | archive |
| topic_map | life area |
| hub | overview |
| description | summary |
| topics | Themes |
| relevant_notes | Related Reflections |

**Processing categories:** reflections, relationship-dynamics, goals, habits, gratitude, lessons.

**Starter topic maps:** life-areas, people, goals.

**Example signals:**
- "I want to track my growth and notice patterns in my life."
- "I need something that remembers what I care about across sessions."
- "Help me be more thoughtful about my relationships and goals."

---

### Novel Domain

**Optimizes for:** Domains that do not cleanly match research or personal reflection.

Use the user's terms first. Blend Research and Personal Assistant only when a universal term needs a fallback.

**Processing category derivation:**
- Listen for verbs: track, compare, decide, review, remember, notice, collect, evaluate.
- Convert repeated verbs into processing categories.
- Keep 4-8 categories.
- Each category needs: `name`, `what_to_find`, and `output_type`.

**Starter topic-map derivation:**
- Use the user's highest-level nouns.
- Prefer task-neutral names: overview, open questions, people, projects, methods, themes.
- Represent groupings as notes and topic maps inside the flat collection. Do not create physical directories for browsing groups.

**Schema field candidates:**

| Domain Characteristic | Candidate Field |
|----------------------|-----------------|
| Temporal dynamics | `status`, `review_after`, `superseded_by` |
| Confidence tracking | `confidence` |
| Sequential progression | `prerequisites` |
| Entity tracking | `person`, `entity`, `project` |
| Source accountability | `source_url`, `source_date` |

Run Filter A before keeping any candidate field.

---

## Matching Algorithm

### Step 1: Signal Collection

Listen for signals in the user's description and follow-up answers:

| Signal Type | Examples | Use |
|-------------|----------|-----|
| Domain markers | "research papers", "personal growth", "client decisions" | Reference-domain affinity |
| Processing verbs | "track claims", "remember reactions", "document decisions" | Processing categories |
| Connection words | "across disciplines", "between projects", "patterns" | Topic-map and linking examples |
| Emotional register | "feel seen", "professional", "direct" | self/identity.md voice |

### Step 2: Reference-Domain Affinity

Score the user's signals against each reference domain:

```
For each reference domain:
  affinity = sum(signal_weight * match_strength)
  where match_strength is:
    1.0 = signal directly matches the domain
    0.5 = signal partially matches
    0.0 = no match
```

Use the highest-affinity domain as a fallback vocabulary source. If no domain scores above 2.0, treat the case as a Novel Domain and blend the two closest domains term-by-term.

### Step 3: Vocabulary Derivation

For each universal term:

```
if user provided a domain-native equivalent:
  use user's term
else:
  use the closest reference-domain term

Verify: would this term feel natural to the user?
```

### Step 4: Candidate Derivation

Use the matched reference domain to propose:
- processing categories
- starter topic maps
- candidate schema fields

Then apply Filter A for fields. Reference-domain defaults are candidates only; physical folder layout stays flat.

---

## Worked Example: Wine Tasting

**User:** "I'm getting into wine and want to track what I taste - flavors, regions, pairings, and which wines remind me of others."

**Affinity:**
- Personal Assistant: 1.5 ("remember things", personal interest)
- Research: 1.0 ("track", systematic comparison)
- Novel Domain: use blended fallback terms

**Derived vocabulary:**
- note: tasting note
- note_collection: wine notes
- topic_map: wine map
- inbox: tastings

**Processing categories:**
- tasting observations
- regions
- varietals
- pairings
- comparisons
- open questions

**Schema candidates:**
- `region`
- `varietal`
- `pairing`
- `vintage`

Run Filter A before keeping any candidate.
