# Vocabulary Transformation Reference

When generating a knowledge system for a specific domain, every universal term in the generated context file, templates, skills, and self/ files must use the domain-native equivalent. Vocabulary transformation is not cosmetic — it changes how the system feels to use.

"Surface patterns in reflections" is therapy work. "Extract claims from sources" is research work. Same structural operation, different cognitive framing.

---

## Universal → Domain Mapping

| Universal Term | Research | Therapy | Learning | Relationships | Creative | PM | Companion |
|---------------|----------|---------|----------|---------------|----------|-----|-----------|
| note | claim | reflection | concept note | observation | idea | decision | memory |
| extract / reduce | reduce | surface | break down | notice | discover | document | remember |
| connect / reflect | reflect | find patterns | relate concepts | trace connections | combine ideas | link decisions | recall together |
| verify | verify | check resonance | test understanding | confirm accuracy | evaluate draft | review quality | verify memory |
| MOC | topic map | theme | study guide | relationship map | project hub | decision register | memory collection |
| description field | claim context | reflection summary | concept explanation | observation context | idea sketch | decision rationale | memory context |
| topics footer | research areas | themes | study areas | relationship facets | creative projects | project areas | life areas |
| inbox | capture | journaling | study notes | encounters | inspiration | action items | moments |
| processing / pipeline | pipeline | reflection cycle | study cycle | relationship review | creative process | review cycle | reminiscence |
| wiki link | connection | pattern link | concept link | connection | inspiration thread | decision trail | memory link |
| thinking notes | claims | reflections | concepts | observations | ideas | decisions | memories |
| archive | processed sources | past reflections | mastered material | past encounters | completed works | closed decisions | past events |
| self/ space | research identity | reflection partner | study companion | relationship tracker | creative identity | project mind | companion memory |
| orient | orient | center | review progress | check in | survey ideas | status check | remember |
| persist | persist | journal | log progress | update records | save state | update status | save memories |

---

## Template Name Mapping

| Universal Template | Research | Therapy | Learning | Relationships | Creative | PM | Companion |
|-------------------|----------|---------|----------|---------------|----------|-----|-----------|
| base-note.md | thinking-note.md | reflection-note.md | concept-note.md | observation-note.md | idea-note.md | decision-note.md | memory-note.md |
| moc.md | topic-map.md | theme.md | study-guide.md | relationship-map.md | project-hub.md | decision-register.md | collection.md |

---

## Folder Name Mapping

| Universal Folder | Research | Therapy | Learning | Relationships | Creative | PM | Companion |
|-----------------|----------|---------|----------|---------------|----------|-----|-----------|
| note_collection/ | notes/ | reflections/ | concepts/ | observations/ | ideas/ | decisions/ | memories/ |
| notes/ | notes/ | reflections/ | concepts/ | observations/ | ideas/ | decisions/ | memories/ |
| inbox/ | inbox/ | journal/ | study-inbox/ | encounters/ | inspiration/ | action-items/ | moments/ |
| archive/ | archive/ | past/ | mastered/ | history/ | completed/ | closed/ | past/ |
| templates/ | templates/ | templates/ | templates/ | templates/ | templates/ | templates/ | templates/ |

**note_collection collapse behavior:** For single-entity domains, `note_collection` maps to the same value as `notes/` — the single entity directory IS the collection, with no parent wrapper. For multi-entity domains (2+ entity types derived in Step 3g), `note_collection` becomes a distinct parent directory (e.g., `knowledge-base/`) containing typed entity subdirectories. The `notes/` row represents the default/primary entity type within the collection.

---

## Skill Name Mapping

| Universal Skill | Research | Therapy | Learning | Relationships | Creative | PM | Companion |
|----------------|----------|---------|----------|---------------|----------|-----|-----------|
| /reduce | /reduce | /surface | /break-down | /notice | /discover | /document | /capture |
| /reflect | /reflect | /find-patterns | /relate | /trace | /combine | /link | /recall |
| /verify | /verify | /check-resonance | /test | /confirm | /evaluate | /review | /verify |
| /reweave | /reweave | /revisit | /revise | /reconnect | /rework | /update | /revisit |
| /remember | /remember | /note-friction | /flag | /flag | /flag | /flag | /remember |
| /stats | /stats | /stats | /stats | /stats | /stats | /stats | /stats |
| /graph | /graph | /graph | /graph | /graph | /graph | /graph | /graph |

**Note:** /remember (formerly /friction) captures operational friction with automatic detection in session transcripts. /stats provides vault metrics and progress visualization. /graph enables graph query generation. These commands use universal names across all domains.

---

## Applying Transformations

### In the init wizard (Step 5b):

1. Determine the user's use case
2. Look up all universal terms in the mapping table above
3. Replace every instance in the generated context file
4. Replace template names and folder names
5. Replace skill names if generating skills
6. **Verify:** Read the generated output. Does it feel natural for the domain? Would a therapy user ever see the word "claim"? Would a PM user see "reduce"?

### Quality check:

The vocabulary test: read the generated context file as if you were the domain user. Every technical term should feel native to the domain. If any term feels imported from a different discipline, transform it.

### Extending the table:

For "Custom / Mixed" use cases, the init wizard should ask the user for their preferred vocabulary. Populate a custom column using the universal terms as prompts: "What do you call a single knowledge unit?" → their answer becomes the "note" equivalent.
