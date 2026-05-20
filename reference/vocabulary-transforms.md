# Vocabulary Transformation Reference

When generating a knowledge system for a specific domain, every universal term in the generated context file, templates, skills, and self/ files must use the domain-native equivalent. Vocabulary transformation is not cosmetic — it changes how the system feels to use.

"Structure claims from sources" is research work. "Document decisions from project material" is PM work. Same structural operation, different cognitive framing.

---

## Universal → Domain Mapping

| Universal Term | Research | Learning | Creative | PM | Companion |
|---------------|----------|----------|----------|-----|-----------|
| note | claim | concept note | idea | decision | memory |
| MOC | topic map | study guide | project hub | decision register | memory collection |
| description field | claim context | concept explanation | idea sketch | decision rationale | memory context |
| topics footer | research areas | study areas | creative projects | project areas | life areas |
| wiki link | connection | concept link | inspiration thread | decision trail | memory link |
| thinking notes | claims | concepts | ideas | decisions | memories |
| self/ space | research identity | study companion | creative identity | project mind | companion memory |
| orient | orient | review progress | survey ideas | status check | remember |
| persist | persist | log progress | save state | update status | save memories |

---

## Template Name Mapping

| Universal Template | Research | Learning | Creative | PM | Companion |
|-------------------|----------|----------|----------|-----|-----------|
| base-note.md | thinking-note.md | concept-note.md | idea-note.md | decision-note.md | memory-note.md |
| moc.md | topic-map.md | study-guide.md | project-hub.md | decision-register.md | collection.md |

---

## Folder Name Mapping

| Universal Folder | Research | Learning | Creative | PM | Companion |
|-----------------|----------|----------|----------|-----|-----------|
| note_collection/ | notes/ | concepts/ | ideas/ | decisions/ | memories/ |
| notes/ | notes/ | concepts/ | ideas/ | decisions/ | memories/ |
| inbox/ | inbox/ | study-inbox/ | inspiration/ | action-items/ | moments/ |
| archive/ | archive/ | mastered/ | completed/ | closed/ | past/ |
| templates/ | templates/ | templates/ | templates/ | templates/ | templates/ |

**note_collection behavior:** `note_collection` is always the single flat container for durable domain notes. It may use a domain-native name (`notes/`, `decisions/`, `knowledge-base/`, etc.), but it does not gain typed entity subdirectories when the domain has multiple entity types.

---

## Skill Name Mapping

| Universal Skill | Research | Learning | Creative | PM | Companion |
|----------------|----------|----------|----------|-----|-----------|
| /reduce | /reduce | /break-down | /discover | /document | /capture |
| /verify | /verify | /verify | /verify | /verify | /verify |
| /health | /health | /health | /health | /health | /health |

**Note:** /health provides vault diagnostics and metrics. /verify is the fixed pipeline quality gate. These commands use universal names across all domains.

---

## Applying Transformations

### In the init wizard (Step 5b):

1. Determine the user's use case
2. Look up all universal terms in the mapping table above
3. Replace every instance in the generated context file
4. Replace template names and folder names
5. Replace skill names if generating skills, except fixed commands such as /verify
6. **Verify:** Read the generated output. Does it feel natural for the domain? Would a research user see generic project language? Would a PM user see "reduce"?

### Quality check:

The vocabulary test: read the generated context file as if you were the domain user. Every technical term should feel native to the domain. If any term feels imported from a different discipline, transform it.

### Extending the table:

For "Custom / Mixed" use cases, the init wizard should ask the user for their preferred vocabulary. Populate a custom column using the universal terms as prompts: "What do you call a single knowledge unit?" → their answer becomes the "note" equivalent.
