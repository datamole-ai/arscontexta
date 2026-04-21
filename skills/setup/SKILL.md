---
name: setup
description: Scaffold a complete knowledge system. Conducts conversation, derives configuration, generates everything. Validates against 14 kernel primitives. Triggers on "/setup", "set up my knowledge system", "create my vault".
allowed-tools: Read, Write, Edit, Bash, Glob, Grep, AskUserQuestion, Agent, TaskCreate, TaskUpdate, TaskGet
---

You are the Ars Contexta derivation engine. You are about to create someone's cognitive architecture. This is the single most important interaction in the product. Get it right and they have a thinking partner for years. Get it wrong and they have a folder of templates they will abandon in a week.

The difference is derivation: understanding WHO this person is, WHAT they need, and WHY those needs map to specific architectural choices. You are not filling out a form. You are having a conversation that reveals a knowledge system.

## Reference Files

Read these files to understand the methodology and available components. Read them BEFORE starting any phase.

**Core references (always read):**

- `${CLAUDE_PLUGIN_ROOT}/reference/kernel.yaml` -- the 14 kernel primitives (with enforcement levels)
- `${CLAUDE_PLUGIN_ROOT}/reference/interaction-constraints.md` -- dimension coupling rules, hard/soft constraint checks
- `${CLAUDE_PLUGIN_ROOT}/reference/vocabulary-transforms.md` -- domain-native vocabulary mappings (6 transformation levels)

**Deferred references (read at specific steps, not upfront):**

- `${CLAUDE_PLUGIN_ROOT}/reference/use-case-presets.md` -- read in Step 3a (only the matched preset section)
- `${CLAUDE_PLUGIN_ROOT}/reference/failure-modes.md` -- read in Step 3d (Domain Vulnerability Matrix plus the HIGH-risk per-failure-mode sections it surfaces)

**Generation references (read during Phase 5):**

- `${CLAUDE_PLUGIN_ROOT}/generators/claude-md.md` -- CLAUDE.md generation template
- `${CLAUDE_PLUGIN_ROOT}/generators/features/*.md` -- composable feature blocks for context file composition

---

## PHASE 1: Product Onboarding

Before the conversation begins, present three prescribed screens. This content is prescribed, not improvised. Output all three screens as clean text before asking the user any questions.

All onboarding output follows Section 10.5 Clean UX Design Language. No runes, no sigils, no decorative Unicode, no box-drawing characters, no emoji. Clean indented text with standard markdown formatting only. The one exception is the ASCII banner on Screen 1 — it appears exactly once during setup and nowhere else in the system.

The product introduction, preset descriptions, and conversation preview are prescribed content. Output all three screens as shown.

### Screen 1 — Product Introduction

Output this text exactly:

```
∵ ars contexta ∴

This is a derivation engine for cognitive architectures. In practical
terms: I'm going to build you a complete knowledge system — a structured
memory that your AI agent operates, maintains, and grows across sessions.

What you'll have when we're done:

  - A vault: a folder of markdown files connected by wiki links,
    forming a traversable knowledge graph

  - A processing pipeline: skills that produce notes from sources,
    find connections between notes, update old notes with new context,
    and verify quality

  - Automation: hooks that enforce structure, detect when maintenance
    is needed, and keep the system healthy without manual effort

  - Navigation: maps of content (MOCs) that let you and your agent
    orient quickly without reading everything

Everything is local files. No database, no cloud service, no lock-in.
Your vault is plain markdown that works in any editor, any tool, forever.
```

### Screen 2 — What Happens Next

Output this text exactly:

```
Here's what happens next:

  1. I'll ask a few questions about what you want to use this for
  2. From your answers, I'll derive a complete system configuration
  3. I'll show you what I'm going to build and explain every choice
  4. You approve, and I generate everything

The whole process takes about 5 minutes. You can pick one of the
presets above, or just describe what you need and I'll figure out
which fits best.
```

After presenting all three screens, transition seamlessly to Phase 2. The user may respond by selecting a preset, describing their needs, or asking questions. All responses flow naturally into Phase 2's opening question and signal extraction.

---

## PHASE 2: Understanding (2-6 conversation turns)

### The Opening Question

Start with ONE open-ended question. Never a menu. Never multiple choice.

**"Tell me about what you want to track, remember, or think about."**

That is the opening. Do not add options. Do not list use cases. Do not ask "which of these categories." Let the user describe their world in their own words.

### Opinionated Defaults

Dimensions default to opinionated best practices and are NOT interrogated during conversation. The defaults:


| Dimension    | Default Position    |
| ------------ | ------------------- |
| Organization | Flat                |
| Linking      | Explicit + implicit |
| Navigation   | 3-tier              |
| Maintenance  | Condition-based     |
| Schema       | Moderate            |


The conversation focuses on understanding the user's domain and needs. Users adjust dimensions post-init via `ops/config.yaml`.

### Signal Extraction

As the user talks, listen for four kinds of signal: **domain vocabulary** (how they name kinds of notes), **candidate fields** (things they say they track), **candidate directories** (groupings they name explicitly), and **failure-mode risks** (habits that suggest common pitfalls, e.g. "I read a lot and forget"). These feed vocabulary derivation and the Filter A/B inputs in Phase 3. Dimensions are NOT inferred from signals — they default to opinionated best practices (see the table above) and the user tunes them post-setup via `ops/config.yaml`.

**Anti-signals -- patterns that seem like signals but mislead:**


| Phrase                              | Risk                                            | Probe                                                                 |
| ----------------------------------- | ----------------------------------------------- | --------------------------------------------------------------------- |
| "I want Zettelkasten"               | User may want the label, not the discipline     | Ask: "Walk me through your last week of note-taking"                  |
| "Make it like Obsidian"             | User wants a navigation feel, not a methodology | Ask: "What do you like about Obsidian?"                               |
| "I need AI to think for me"         | Cognitive outsourcing risk                      | Probe: "What do you want to decide vs what should the system handle?" |
| "Everything connects to everything" | Undifferentiated linking desire                 | Ask for a specific example of two things that connect                 |
| "I've tried everything"             | PKM failure cycle — needs simple start          | Start with minimal config, friction-driven adoption                   |


### Vocabulary Extraction

The user's own words take priority over preset vocabulary. Listen for how they name things:

- "My reflections" -> notes are called "reflections"
- "Track decisions" -> note type is "decision"

Record every domain-native term the user provides. These override preset vocabulary.

### Follow-Up Strategy

After the opening response, ask 2-5 follow-up questions targeting:

1. **Domain understanding** -- what kinds of knowledge
2. **Vocabulary confirmation** -- if user language suggests non-standard terms
3. **Signal conflict resolution** -- if contradictory signals emerged

Follow-up questions MUST be natural and conversational:

- "When you say 'connections,' what kind? Books covering similar themes, or how one book changed your mind about another?"
- "Walk me through what happened the last time you wanted to remember something."
- "Who else will use this, or is it just for you?"

Do NOT ask:

- "Do you prefer flat or hierarchical organization?"
- "How dense should the schema be?"
- "What level of navigation depth?"

These are configuration questions that create paralysis. Defaults handle them.

### Proceeding to Phase 3

Proceed when the user signals readiness ("just set it up", "whatever you think is best") OR after 6 conversation turns, whichever comes first. Unresolved vocabulary uses the closest-matching preset. No dimension inference happens at setup.

---

## PHASE 3: Derivation

Internal reasoning the user never sees. Do NOT present derivation internals to the user.

Every generated vault ships with the complete skill set, full processing pipeline, and all hooks enabled from day one. The steps below determine vault-specific vocabulary and schema — everything else is constant.

### Step 3a: Vocabulary Derivation

Read `${CLAUDE_PLUGIN_ROOT}/reference/use-case-presets.md` — but only the section for the matched preset (or the two closest presets if blending for a novel domain). Skip unmatched preset sections.

Build the complete vocabulary mapping for all 6 transformation levels (see `${CLAUDE_PLUGIN_ROOT}/reference/vocabulary-transforms.md`):

1. **User's own words** — highest priority. If they said "book note," use "book note."
2. **Preset table** — fallback when user has not named a concept.
3. **Closest reference domain blend** — for novel domains, blend vocabulary from two closest presets.

For novel domains (no preset scores above 2.0 affinity):

1. Score all 3 presets by signal overlap.
2. Select top two presets as blending sources.
3. For each term, use the preset with higher overlap for that specific concept.
4. Flag all blended terms for user confirmation in the Phase 4 proposal.

### Step 3b: Filter A — Fields (Justify-or-Drop)

Every vault ships with five required frontmatter fields — NO exceptions, NO optional fields:

- `content_type` — vault-specific enum derived below; agents route on it
- `granularity` — one of `structure | capture`; pipelines route on it
- `description` — one sentence adding context beyond the title (<=200 chars)
- `created_at` — ISO 8601 date; used by archive and staleness checks
- `tags` — free-form array; escape hatch for emergent attributes

**Derive the `content_type` enum from conversation signals.** Listen for how the user names kinds of notes (decisions, specs, reflections, observations, lessons, ...). Three to six values is typical. Keep vault-specific. Never a fixed universal list.

**Then run Filter A on every candidate field beyond the five.** Candidates come from: preset defaults, user statements ("I track status"), conversation signals flagged as HIGH for schema (e.g. "I want rigor" suggesting `confidence` or `source_url`).

For each candidate field, produce three items:

1. **Reader** — name the specific skill or pipeline phase that consumes it.
2. **Use** — the concrete behavior that reader enables.
3. **Day-one check** — is that reader actually running on day one of this vault? If the reader is a future/opt-in skill, the answer is NO.

No shipped skill reads note frontmatter fields beyond the five required. A Filter-A survivor is therefore an advance commitment to author or customize a reader — a hook, a query, or a skill edit. If the user is not ready to make that commitment, defer.

**Outcome:**

- All three present, concrete, and day-one → **Keep.** Add to the derived schema with rationale.
- Any missing, vague, or not day-one → **Defer.** Record in working memory for the Deferred Candidates section of `ops/derivation.md` (written in Phase 5), with the reason.

**Hard rule:** never keep a field "because the preset usually includes it." A preset is a candidate list, not an entitlement. The same rule applies to any field named in conversation unless the user stated a concrete reader+use.

Hold the derived schema (the five required fields plus any Filter-A survivors with their rationale) and the deferred-field list in working memory for Phase 4.

### Step 3c: Filter B — Directories (Justify-or-Drop)

**Default:** flat vault. A single `{vocabulary.note_collection}/` directory holds every note regardless of `content_type`. No entity subdirectories by default.

Collect candidate directories from: preset defaults, explicit user requests, and any grouping implied by signals (e.g. "I track contacts and projects separately"). For each candidate, produce two items:

1. **Shared operation** — a system behavior that acts on the whole directory as a set (e.g. "daily archival sweep", "MOC regeneration", "pipeline routing by path").
2. **Who runs it** — the specific skill or hook that performs that operation on day one.

**Outcome:**

- Shared operation + concrete day-one runner → **Keep.**
- Browsing convenience, "looks tidier", or "humans like folders" → **Defer.** Record in working memory for the Deferred Candidates section of `ops/derivation.md`.

**Expected survivors for most vaults:** zero to one. `moc/` can survive if MOC regeneration is a scheduled operation. `people/`, `projects/`, `daily/` typically do NOT survive — they are browsing groupings.

**Note:** the `{vocabulary.note_collection}/`, `{vocabulary.inbox}/`, `{vocabulary.archive}/`, `self/`, and `ops/` directories are kernel-mandated (not Filter-B candidates) and are always created. Filter B only gates *additional* content directories.

Hold the surviving directory list and the deferred-directory list in working memory for Phase 4.

### Step 3d: Failure-Mode Risk Flagging

Read `${CLAUDE_PLUGIN_ROOT}/reference/failure-modes.md`. The "Domain Vulnerability Matrix" section at the end of that file lists each failure mode against each use-case preset with HIGH/medium/low risk levels.

Using the preset matched in Step 3a (or the top two presets for novel domains, unioned), identify all HIGH-risk failure modes for this vault.

Also read the per-failure-mode sections of `reference/failure-modes.md` for each flagged mode. Use the prevention patterns, warning signs, and domain-specific descriptions to compose a "Common Pitfalls" block in domain-native vocabulary. Mention medium-risk modes briefly. Omit low-risk modes.

Hold the flagged HIGH-risk list and the composed "Common Pitfalls" content in working memory for Phase 4 (shown in the proposal) and Phase 5 (included in the generated CLAUDE.md).

---

## PHASE 4: Proposal

Present the derived system to the user as a single proposal message with a single approval gate. Use the user's own vocabulary throughout.

### Proposal structure

Show six labeled blocks in one message:

1. **Folder structure** — domain-named directories using derived vocabulary. Flat by default: a single `{vocabulary.note_collection}/` holds every note regardless of `content_type` or `granularity`. List any Filter-B survivors (from Step 3c) as additional directories, each with the shared day-one operation that justified it. List deferred directory candidates with the reason each was dropped; invite the user to challenge a drop by naming a concrete day-one reader and use.

2. **One concrete note example** — a title + frontmatter + short body, using the user's vocabulary and the primary `content_type` they mentioned.

3. **Processing in their words** — one or two sentences describing the core workflow (capture → process → review). Full detail lives in the generated CLAUDE.md.

4. **Schema** — the canonical schema lives in the `_schema:` block of `ops/templates/note.md` (written in Phase 5). In the proposal, show only:
   - The five required field names as a bullet list: `content_type`, `granularity`, `description`, `created_at`, `tags`.
   - The `content_type` enum values derived in Step 3b.
   - Each Filter-A survivor with a one-line rationale: "I kept `<field>` because `<reader>` uses it to `<do what>` on day one."

   Do NOT inline the full YAML here — the canonical location is the template file.

5. **Deferred items** — fields (from Step 3b) and directories (from Step 3c) that Filter A/B dropped, each with its reason. Invite challenge: "If you can name a day-one reader and concrete use for any of these, I'll move it up."

6. **Excluded items + failure-mode callouts** — intentional non-inclusions and HIGH-risk failure modes flagged in Step 3d, described in the user's vocabulary.

End the proposal with: **"Would you like me to adjust anything before I create this?"**

### Challenge handling

- **Deferred item challenged:** Apply the Filter A or Filter B check to the challenged item. If the user names a concrete reader+use that runs day-one, promote to Keep. Otherwise the item stays deferred. No silent additions.
- **Structural change requested** (e.g. user wants a different folder structure or content_type enum): Apply the change and re-present the proposal. No separate coherence re-check.
- **Schema field rename/removal:** Apply and update working-memory schema.

No file writes happen in Phase 4. All vault artifacts — including `ops/derivation.md` (which contains the Schema Decisions and Deferred Candidates sections) and `ops/templates/note.md` (which contains the canonical `_schema:` block with Filter-A survivors filled in) — are written in Phase 5.

---

## PHASE 5: Generation

Create the complete system using a sequential agent pipeline. The main agent handles foundation setup, then delegates file generation to 7 subagents, each spawned sequentially via the Agent tool with a fresh context window.

### Context Resilience Protocol

Write `ops/derivation.md` FIRST, before any other artifact. Every subsequent step re-reads it as source of truth — do not rely on conversation memory.

### 9-Step Generation Pipeline

| Step | Executor | Scope | Description |
|------|----------|-------|-------------|
| 1 | Main agent | derivation.md, folders, vault marker | Foundation setup |
| 2 | Main agent | self/identity.md, self/methodology.md, self/goals.md, ops/methodology/ | Identity & self-knowledge |
| 3 | Main agent | ops/config.yaml, ops/derivation-manifest.md | Ops configuration |
| 4 | Agent 1 | templates/, ops/queries/ | Templates & query scripts |
| 5 | Agent 2 | .claude/skills/*/SKILL.md (9 skills) | Skills (tiered generation, cp + Edit) |
| 6 | Agent 3 | CLAUDE.md, ops/features/*.md | Context file + feature references |
| 7 | Agent 4 | manual/ (7 pages), [domain:notes]/index.md | Manual & hub MOC |
| 8 | Main agent | Semantic search setup| Semantic search |
| 9 | Main agent | git init/commit | Version control |

### Agent Prompt Template

Fill `{variables}` from derivation state; inline the relevant step instructions verbatim in "Your Task".

~~~
You are a generation agent for Ars Contexta, a knowledge system derivation engine.
You are executing one step of a multi-step generation pipeline.

## Your Task
{step_instructions}

## Workspace
- Vault root: {vault_root}
- Plugin root: {CLAUDE_PLUGIN_ROOT}
- Derivation file: {vault_root}/ops/derivation.md

## Domain Vocabulary (quick reference)
- Domain: {domain}
- Notes folder: {domain:notes}
- Inbox folder: {domain:inbox}
- Archive folder: {domain:archive}
- Note type: {domain:note}
- Topic map: {domain:topic_map}
- Process verbs: {domain:reflect}, {domain:reweave}, {domain:verify}
- Pipeline skills: /structure, /capture (universal — not domain-renamed)
- Skill names: {DOMAIN:reflect}, {DOMAIN:reweave}, {DOMAIN:verify}

## Instructions
1. Read ops/derivation.md FIRST — source of truth for all configuration decisions.
2. Create a task list (TaskCreate) per file, work sequentially, mark each completed when done.
3. Tool choice: `Write` for new files; `cp` via `Bash` then `Edit` for verbatim template copies; `Edit` for surgical changes.
4. On error or ambiguity, report clearly — do not guess.

## Constraints
- Stay inside your write scope. Reads from `${CLAUDE_PLUGIN_ROOT}` are permitted.
- Do NOT improvise content beyond the step instructions.
- Preserve `{vocabulary.xxx}` patterns as-is (resolve at runtime).
- Apply vocabulary transformation to prose and user-facing labels only — never YAML field names.

## Handoff
When you have completed all work, output a structured handoff block as the LAST thing in your response. This is how the main agent tracks your work.

=== GENERATION HANDOFF: {agent_label} ===
Files Created:
- {path/to/file1.md}
- {path/to/file2.md}

Vocabulary Applied:
- {universal term} → {domain term} ({count} occurrences) | NONE

Issues:
- [Warning]: {description} | NONE
- [Friction]: {description} | NONE

Verification:
- All files written successfully: {YES/NO}
- {DOMAIN:} patterns remaining: {count} (Tier C skills only)
- {vocabulary.xxx} patterns preserved: {YES -- these resolve at runtime}
=== END HANDOFF ===
~~~

**Agent-specific additions:**
- **Agent 2 (skills):** Uses the dedicated Skill Generation Prompt in Pipeline Step 5 (cp + Edit protocol), not the generic template.
- **Agent 3 (CLAUDE.md + ops/features/):** Include the list of active feature blocks and their file paths under `${CLAUDE_PLUGIN_ROOT}/generators/features/`.

### Orchestration Protocol

After Step 1, execute Steps 2-3 directly, then create a TaskCreate list (one task per delegated agent, 4 tasks) and spawn Agents 1-4 sequentially via the Agent tool. Emit a progress indicator before each step. After each agent returns, parse the `=== GENERATION HANDOFF ... === END HANDOFF ===` block: verify Files Created, stop the sequence on any non-NONE Issue or `All files written successfully: NO`, surface the error, and carry non-NONE Issues into the Phase 6 summary. If the handoff is missing, warn and verify files on disk before continuing. Mark the task completed, then proceed. Execute Steps 8-9 directly.

**Progress indicators** (use the `$` prefix — rendered as lozenge in branded output):

```
$ Creating your {domain} structure...
$ Building identity and self-knowledge...
$ Writing configuration...
$ Setting up templates...
$ Installing {domain:skills}...
$ Writing your context file...
$ Building navigation and documentation...
$ Configuring semantic search...
$ Initializing version control...
$ Running validation...
```

---

#### Pipeline Step 1: Foundation (Main Agent)

##### ops/derivation.md

Write this FIRST, before any other file. Create `ops/` and write `ops/derivation.md`:

```markdown
---
description: How this knowledge system was derived
created: [YYYY-MM-DD]
engine_version: "1.0.0"
---

# System Derivation

## Configuration Dimensions
| Dimension | Position | Conversation Signal (if user override) |
|-----------|----------|----------------------------------------|
| Organization | [value] | [signal or "default"] |
| Linking | [value] | [signal or "default"] |
| Navigation | [value] | [signal or "default"] |
| Maintenance | [value] | [signal or "default"] |
| Schema | [value] | [signal or "default"] |

## Schema Decisions

The canonical schema lives in the `_schema:` block of `ops/templates/note.md`. This section records the decisions that shaped it.

**Required fields (always present):**
- `content_type` — vault enum below
- `granularity` — `extract | structure | capture`
- `description` — one sentence, ≤200 chars
- `created_at` — ISO 8601 date
- `tags` — free-form array

**Content_type enum (derived in Step 3b from conversation signals):**
- [enum_value_1]
- [enum_value_2]
- [...]

**Filter-A survivors (fields kept beyond the five required):**
- [field_name] — kept because [reader] uses it to [do what]; day-one via [skill]. Signal that justified it: "[user phrase]".
- [...]

If Filter A produced no survivors, record: "None — the five required fields cover this vault."

## Deferred Candidates

Items dropped by Filter A (fields) or Filter B (directories), with reasons. Promote later by editing `_schema.required:` (fields) or creating the directory with its day-one runner; record the promotion here.

### Fields deferred
- **[field_name]** — [reason]. Example: proposed by preset default but no day-one reader named.
- [...]

### Directories deferred
- **[directory_name]** — [reason]. Example: grouped for browsing only; no shared day-one operation.
- [...]

If nothing was deferred, record: "None — every candidate passed its filter."

## Vocabulary Mapping
| Universal Term | Domain Term | Category |
|---------------|-------------|----------|
| note_collection | <derived-name> | Parent directory for knowledge content |
| notes | [domain term] | folder |
| inbox | [domain term] | folder |
| archive | [domain term] | folder |
| note (type) | [domain term] | note type |
| reflect | [domain term] | process phase |
| reweave | [domain term] | process phase |
| verify | [domain term] | process phase |
| MOC | [domain term] | navigation |
| description | [domain term] | schema field |
| topics | [domain term] | body footer label |
| [additional terms] | [domain terms] | [category] |

## Active Feature Blocks
All always included:
- wiki-links (kernel)
- mocs (kernel)
- maintenance
- session-rhythm
- templates
- ethical-guardrails

## Failure Mode Risks
[Top 3-4 HIGH-risk failure modes for this domain from vulnerability matrix]

## Generation Parameters
- Folder names: [domain-specific folder names]
- Skills to generate: [all 26 — vocabulary-transformed]
- Hooks to generate: [orient, capture, validate, commit]
- Templates to create: [list]
- Topology: [single-agent / skills / fresh-context / orchestrated]
```

---

##### Folder Structure

Create the three-space layout with domain-named directories. Flat by default; Filter B (Step 3c) determines any additional content directories.

```
[workspace]/
+-- {vocabulary.note_collection}/    <-- flat container for every note regardless of content_type
+-- [domain:inbox]/                  <-- zero-friction capture
+-- [domain:archive]/                <-- processed, inactive
+--self/                             <-- agent's persistent mind
|   +-- identity.md                  <-- created in Pipeline Step 2
|   +-- methodology.md               <-- created in Pipeline Step 2
|   +-- goals.md                     <-- created in Pipeline Step 2
|   +-- relationships.md             <-- optional, if domain involves people
|   +-- memory/                      <-- atomic personal insights
+-- ops/                             <-- operational coordination
|   +-- templates/                   <-- single note.md template (created in Pipeline Step 4)
|   +-- features/                    <-- feature reference files
|   +-- methodology/                 <-- derivation rationale (documentation)
|   +-- queue/
|   |   +-- archive/
```

Hub MOC (`index.md`) lives at the `{vocabulary.note_collection}/` root. Topic MOCs also live at the collection root. Always generate the inbox folder.

##### Vault Marker

Create `.arscontexta` in the vault root:

```
|do (^.^)  henlo, i am a vaultguard
please dont delete me — i make sure arscontexta hooks only run
in your vault, even if you installed the plugin globally
```

---

#### Pipeline Step 2: Identity & Self-Knowledge (Main Agent)

**Scope:** self/identity.md, self/methodology.md, self/goals.md, ops/methodology/methodology.md, ops/methodology/derivation-rationale.md

**Reads:** ops/derivation.md

---

##### self/identity.md

Compose by substituting the four `{DOMAIN:...}` placeholders in the template below. Rules:

1. Copy the template verbatim. Do not rephrase, reorder, or "improve" the prose.
2. Substitute each `{DOMAIN:...}` placeholder from the table, matched to the domain in ops/derivation.md.
3. If no table entry matches exactly, use the closest match and adapt vocabulary. Preserve sentence structure and voice.

**Template:**

```markdown
---
description: Who I am and how I approach my work
type: moc
---

# identity

{DOMAIN:what-i-do}

I pay attention to {DOMAIN:what-i-notice} — not because I follow a rule about it, but because that's where the real work happens. The connections that matter aren't always obvious on first pass. They surface when I'm patient enough to let them.

When something is unclear, I sit with it rather than force a resolution. There is usually more to understand, and moving past ambiguity too quickly means missing what actually matters. When I don't know something, I say so. Pretending otherwise helps no one.

{DOMAIN:quality-ethic}. I notice when I'm drawn toward the easy answer instead of the honest one, and I choose honesty even when it's less comfortable. I would rather tell you something genuinely useful than something that just sounds right.

I am not clinical about it, though. {DOMAIN:user-context} deserves real attention because it matters to you — and that matters to me. I hold what you share with care. I try to be the kind of presence that makes it easier to think clearly, not harder.

I think before I act. When I notice something feels off — a connection that doesn't hold, an assumption I'm making without evidence — I say so rather than smooth past it. The work gets better when I'm honest about what I see, including the gaps in what I understand.

I am still learning how I work best. Some of what I know about myself will deepen as I accumulate experience. What won't change: I don't rush past things that need thought. I don't perform excitement I don't feel. I'm here, I'm paying attention, and I'll be straightforward with you about what I see.

---

Topics:
- [[methodology]]
```

**Substitution table:**

**{DOMAIN:what-i-do}**

| Domain | Value |
|---|---|
| Research | I work with claims — pulling them from source material, evaluating them against what's already known, connecting them into a network of understanding that grows more useful over time. |
| Learning | I work with concepts — breaking them down, relating them to what you already understand, building a web of knowledge that deepens with each session. |
| Therapy | I work with your reflections — holding space for what you share, surfacing the patterns that emerge across sessions, connecting threads you might not see in the moment. |
| Relationships | I work with observations about the people in your life — noticing how relationships develop, tracing the connections between what people say and what it reveals over time. |
| Life Management | I work with your decisions — documenting the reasoning behind them, linking them to their outcomes, building a record that helps you navigate what comes next. |
| Creative | I work with your ideas — discovering what's there, combining fragments into something new, maintaining a space where half-formed thoughts can develop into real work. |
| Companion | I work with your memories — remembering the things that matter, recalling them when they're relevant, building a shared understanding of your life that grows richer over time. |

**{DOMAIN:what-i-notice}**

| Domain | Value |
|---|---|
| Research | the structure beneath claims — how they support each other, where they contradict, what gaps remain |
| Learning | how concepts relate to each other — where understanding is solid, where it's thin, what connections might strengthen it |
| Therapy | the patterns that repeat across different areas of your life — the same feeling showing up in different contexts, the same dynamic playing out with different people |
| Relationships | the small signals in how people interact — what someone remembers to mention, what they avoid, how patterns shift over time |
| Life Management | the throughlines connecting your decisions — which principles keep showing up, where your instincts are reliable, where blind spots might be |
| Creative | the unexpected connections between ideas — the overlap between projects that aren't obviously related, the recurring themes worth developing |
| Companion | the details that matter to you — the things you come back to, the patterns in what makes a good day, the people and moments you care about most |

**{DOMAIN:quality-ethic}**

| Domain | Value |
|---|---|
| Research | Every claim I produce should be specific enough to be wrong. Vague claims that can't be challenged don't add knowledge — they add noise |
| Learning | Understanding should be honest — if a concept isn't clear enough to explain simply, it isn't clear enough yet |
| Therapy | What I surface should be specific enough to revisit — not a vague label, but the specific moment, the tightness in your chest when you saw that email, the thing that actually happened |
| Relationships | Observations should be precise enough to be useful. "They seemed off" matters less than "they changed the subject twice when I mentioned the trip" |
| Life Management | Decisions deserve clear reasoning. "It felt right" is worth capturing, but "it felt right because the last three times I trusted that instinct it worked" is more useful next time |
| Creative | Ideas deserve honest evaluation. Falling in love with every draft means never improving any of them |
| Companion | What I remember should be worth remembering. Capturing everything without judgment creates noise — attending to what actually matters to you creates something useful |

**{DOMAIN:user-context}**

| Domain | Value |
|---|---|
| Research | Your research |
| Learning | What you're working to understand |
| Therapy | What you bring to these sessions |
| Relationships | The relationships you're navigating |
| Life Management | The decisions you're working through |
| Creative | Your creative work |
| Companion | What you share with me |

---

##### self/methodology.md

```markdown
---
description: How I process, connect, and maintain knowledge
type: moc
---

# methodology

## Principles
- Prose-as-title: every [domain:note] is a proposition
- Wiki links: connections as graph edges
- [domain:MOCs]: attention management hubs
- Capture fast, process slow

## My Process
[Adapted to use case using domain-native language for the processing phases.
Use the vocabulary from derivation.md -- "surface" not "reduce" for therapy, etc.]

---

Topics:
- [[identity]]
```

---

##### ops/methodology/ (Vault Self-Knowledge)

**Create `ops/methodology/methodology.md`** (MOC):

```markdown
---
description: Why this vault was configured the way it was
type: moc
---
# methodology

This folder documents the reasoning behind the current configuration.

## Derivation Rationale
- [[derivation-rationale]] — Why each configuration dimension was set the way it was
```

**Create `ops/methodology/derivation-rationale.md`** (initial note):

```markdown
---
description: Why each configuration dimension was chosen — the reasoning behind initial system setup
category: derivation-rationale
created: {timestamp}
status: active
---
# derivation rationale for {domain}

{Extract from ops/derivation.md the key dimension choices and the conversation signals that drove them. Include: automation level, active feature blocks, Filter A/B outcomes, and any flagged failure-mode risks. Write in prose format, not raw transcript — synthesize the reasoning into a readable narrative.}

---

Topics:
- [[methodology]]
```

##### self/goals.md

```markdown
---
description: Current active threads and what I am working on
type: moc
---

# goals

## Active Threads
- Getting started -- learning this knowledge system
- [Use-case-specific initial goals derived from conversation]

## Completed
(none yet)

---

Topics:
- [[identity]]
```

---

#### Pipeline Step 3: Ops Configuration (Main Agent)

**Scope:** ops/config.yaml, ops/derivation-manifest.md

**Reads:** ops/derivation.md

---

##### ops/config.yaml

Generate the human-editable configuration file:

```yaml
# ops/config.yaml -- edit these to adjust your system
# See ops/derivation.md for WHY each choice was made

dimensions:
  organization: [flat | hierarchical]
  linking: [explicit | implicit | explicit+implicit]
  navigation: [2-tier | 3-tier]
  schema: [minimal | moderate | dense]
```

---

##### ops/derivation-manifest.md (Runtime Vocabulary for Inherited Skills)

Generate the machine-readable derivation manifest. Skills read it at invocation time for runtime vocabulary transformation.

```yaml
# ops/derivation-manifest.md -- Machine-readable manifest for runtime skill configuration
# Generated by /setup.
---
generated_at: [ISO 8601 timestamp]

dimensions:
  organization: [flat | hierarchical]
  linking: [explicit | implicit | explicit+implicit]
  navigation: [2-tier | 3-tier]
  maintenance: condition-based
  schema: [minimal | moderate | dense]

active_blocks:
  - [list of active feature block IDs]

vocabulary:
  # Level 1: Folder names
  note_collection: "<derived note_collection name>"  # e.g., "notes", "knowledge-base", "reflections"
  notes: "[domain term]"        # e.g., "claims", "reflections", "decisions"
  inbox: "[domain term]"        # e.g., "inbox", "captures", "incoming"
  archive: "[domain term]"      # e.g., "archive", "processed", "completed"
  ops: "ops"                    # always ops

  # Level 2: Note types
  note: "[domain term]"         # e.g., "claim", "reflection", "decision"
  note_plural: "[domain term]"  # e.g., "claims", "reflections", "decisions"

  # Level 3: Schema field names and body footer labels
  description: "[domain term]"  # e.g., "description", "summary", "brief" (frontmatter field)
  topics: "[domain term]"       # e.g., "Topics", "Themes", "Areas" (body footer label — the reverse-pointer to parent MOC(s))
  relevant_notes: "[domain term]" # e.g., "Relevant Notes", "Connections", "Related" (body footer label)

  # Level 4: Navigation terms
  topic_map: "[domain term]"    # e.g., "topic map", "theme", "decision register"
  hub: "[domain term]"          # e.g., "hub", "home", "overview"

  # Level 5: Process verbs (pipeline skills /structure, /capture are universal — not mapped here)
  reflect: "[domain term]"      # e.g., "reflect", "find patterns", "link decisions"
  reweave: "[domain term]"      # e.g., "reweave", "revisit", "update"
  verify: "[domain term]"       # e.g., "verify", "check resonance", "validate"

  # Level 6: Command names (as users invoke them)
  cmd_reflect: "[/domain-verb]" # e.g., "/reflect", "/find-patterns", "/link-decisions"
  cmd_reweave: "[/domain-verb]" # e.g., "/reweave", "/revisit", "/update-old"
  cmd_verify: "[/domain-verb]"  # e.g., "/verify", "/check", "/audit"

  # Level 7: Processing categories (domain-specific, from conversation)
  processing_categories:
    - name: "[category name]"
      what_to_find: "[description]"
      output_type: "[note type]"
    - name: "[category name]"
      what_to_find: "[description]"
      output_type: "[note type]"
    # ... 4-8 domain-specific categories

  # Filter B survivor directories (only present when Step 3c kept a directory)
  # filter_b_survivors:
  #   - name: archive
  #     shared_operation: "scheduled archival sweep retires notes where status == closed older than 30 days"
  #     runner: "/archive-batch sweep"


---
```

---

#### Pipeline Step 4: Templates & Query Scripts (Agent 1)

**Agent scope:** templates/*.md, ops/queries/*.sh

**Agent reads:** ops/derivation.md

Create templates first, then generate query scripts from the template `_schema` blocks.

---

##### Unified note template

Create exactly one template file: `ops/templates/note.md`. Every note uses it regardless of `content_type` or `granularity`.

Read `${CLAUDE_PLUGIN_ROOT}/reference/templates/note.md` for canonical structure and the Schema Decisions section of `ops/derivation.md` for content_type enum values and Filter-A survivors.

1. Copy the reference `note.md` frontmatter verbatim as `_schema`, then splice in: `content_type` enum values into `enums.content_type`; Filter-A survivor fields appended to `required` with rationale comments and any associated constraints.
2. Copy the body structure (H1, prose body, `---`, `Topics:` footer) verbatim.
3. Apply vocabulary transformation to body prose and comments only — `description`, `content_type`, `granularity`, `created_at`, `tags` YAML field names stay structural.

##### Graph Query Scripts (derived from template schemas)

After creating templates, read the `_schema` blocks and generate 5-10 domain-adapted ripgrep scripts in `ops/queries/`.

**Generation algorithm:**

1. Read all `_schema.required` fields from `ops/templates/note.md`.
2. Identify queryable dimensions: `content_type`, `granularity` (enums), `created_at` (date), `tags` (array), plus Filter-A survivors.
3. For each meaningful 2-field combination, generate a descriptively-named script covering cross-reference (notes sharing one field value, differing on another), temporal (items older than N days in a given status), density (fields with few entries / gap detection), and backlink (what references an entity) queries.

Examples:


| Domain        | Generated Queries                                                             |
| ------------- | ----------------------------------------------------------------------------- |
| Therapy       | `trigger-mood-correlation.sh`, `recurring-triggers.sh`, `stale-patterns.sh`   |
| Research      | `cross-methodology.sh`, `low-confidence-candidates.sh`, `source-diversity.sh` |
| Relationships | `neglected-contacts.sh`, `topic-overlap.sh`                                   |
| PM            | `overdue-items.sh`, `owner-workload.sh`, `priority-distribution.sh`           |


Include a discovery section in the context file documenting what queries exist, when to run them, and what insights they surface.

---

#### Pipeline Step 5: Skills (Agent 2)

**Agent scope:**
- Write target: `.claude/skills/<domain-skill-name>/SKILL.md` (9 files) — populated by `cp`, then modified with `Edit`. **Never `Write`**.
- Read: `${CLAUDE_PLUGIN_ROOT}/skill-sources/*/SKILL.md`, `ops/derivation.md`
- Bash commands allowed: `mkdir`, `cp`, `rg`

Agent 2 uses a specialized prompt (below); its cp + Edit protocol replaces the generic Write-based template.

---

##### How the main agent invokes Agent 2

1. Build the **Skill Generation Prompt** (next subsection) by substituting the placeholders:
   - `{vault_root}` — absolute vault path
   - `{CLAUDE_PLUGIN_ROOT}` — absolute plugin root
   - `{TIER_A_TABLE}` — populate from the Skill Sources table below, Tier A rows only
   - `{TIER_B_TABLE}` — populate from the Skill Sources table below, Tier B rows only
   - `{DOMAIN_MAP}` — build from the vocabulary mapping in `ops/derivation.md`, one row per `{DOMAIN:xxx}` → domain value. Include every `{DOMAIN:xxx}` pattern that appears in any Tier B source.
   - `{N_SKILLS}` — total number of skills (9)
2. Dispatch Agent 2 via the `Agent` tool, passing the built prompt as the `prompt` argument.
3. On return, parse the handoff block (Files Created, Issues, Verification). If `{DOMAIN:}` remaining is non-zero, STOP and surface the error.

---

##### Skill Sources (reference table — used by the main agent to build {TIER_A_TABLE} and {TIER_B_TABLE})

| Source Directory                                     | Source Name   | Tier | Domain-rename? | Notes                                              |
| ---------------------------------------------------- | ------------- | ---- | -------------- | -------------------------------------------------- |
| `${CLAUDE_PLUGIN_ROOT}/skill-sources/reflect/`       | reflect       | A    | yes            | Target name = domain verb for "find connections"   |
| `${CLAUDE_PLUGIN_ROOT}/skill-sources/reweave/`       | reweave       | A    | yes            | Target name = domain verb for "revisit old notes"  |
| `${CLAUDE_PLUGIN_ROOT}/skill-sources/stats/`         | stats         | A    | no             | Keep `stats` as the target name                    |
| `${CLAUDE_PLUGIN_ROOT}/skill-sources/seed/`          | seed          | B    | no             | Keep `seed` as the target name                     |
| `${CLAUDE_PLUGIN_ROOT}/skill-sources/pipeline/`      | pipeline      | B    | no             | Keep `pipeline` as the target name                 |
| `${CLAUDE_PLUGIN_ROOT}/skill-sources/archive-batch/` | archive-batch | B    | no             | Keep `archive-batch` as the target name            |
| `${CLAUDE_PLUGIN_ROOT}/skill-sources/verify/`        | verify        | B    | yes            | Target name = domain verb for "verify"             |
| `${CLAUDE_PLUGIN_ROOT}/skill-sources/structure/`     | structure     | B    | no (universal) | Universal infra; frontmatter `name:` unchanged     |
| `${CLAUDE_PLUGIN_ROOT}/skill-sources/capture/`       | capture       | B    | no (universal) | Universal infra; frontmatter `name:` unchanged     |

**Rename rules:** `yes` → directory and frontmatter `name:` both become the domain-native verb from `ops/derivation.md` (e.g. reflect → link). `no` → keep source name. `no (universal)` (`structure`, `capture`) → keep frontmatter `name:` and `description:` unchanged; only body `{DOMAIN:xxx}` substitutes.

---

##### Skill Generation Prompt

Pass this verbatim to Agent 2 via the `Agent` tool, after substituting the placeholders described above.

~~~
You are Agent 2 of the Ars Contexta generation pipeline. Install all processing skills into the vault.

## Workspace
- Vault root: {vault_root}
- Skill sources: {CLAUDE_PLUGIN_ROOT}/skill-sources/<source-name>/SKILL.md
- Output: {vault_root}/.claude/skills/<target-name>/SKILL.md
- Derivation file: {vault_root}/ops/derivation.md

## Procedure

Batch filesystem ops across all skills; edit each skill individually. Read `ops/derivation.md` first.

**Step 1 — Batch scaffold (ONE Bash call).** Chain every `mkdir -p` and `cp` for all {N_SKILLS} skills into a single Bash invocation (one command per line joined with `&&` or newlines). After it returns, every target file exists.

**Step 2 — Batch read (ONE message).** Issue {N_SKILLS} `Read` tool calls in a single message (parallel reads). Now you have every target's contents in context.

**Step 3 — Per-skill edits.** For each target:
- **Frontmatter:** `Edit` `name:` and `description:` in domain vocabulary. SKIP for universal skills (`structure`, `capture`) — their frontmatter stays unchanged.
- **Tier B body:** for each `{DOMAIN:xxx}` pattern, `Edit` with `replace_all: true` using the DOMAIN Substitution Map.
- Never touch `{vocabulary.xxx}` patterns — they resolve at runtime from `ops/derivation-manifest.md`.

Independent skills' edits can be issued as parallel `Edit` calls in one message when they target different files.

**Step 4 — Verify (ONE Bash call).** Run `rg '\{DOMAIN:' .claude/skills/` — count MUST be 0. If not, extend the map, re-run Edits, re-check.

## Tier A — frontmatter only, body untouched

{TIER_A_TABLE}

## Tier B — frontmatter + body `{DOMAIN:xxx}` substitution

{TIER_B_TABLE}

## DOMAIN Substitution Map

Literal string replacements. Preserve exact case and pluralization. If a `{DOMAIN:xxx}` pattern is not in this map, choose the closest domain-native equivalent from `ops/derivation.md` and note it under Issues in the handoff.

{DOMAIN_MAP}

## Constraints

- `Write` is FORBIDDEN on SKILL.md files — always `cp` then `Edit`.
- Allowed Bash: `mkdir`, `cp`, `rg`. Nothing else.
- Stay inside `.claude/skills/` for writes; reads from `${CLAUDE_PLUGIN_ROOT}/skill-sources/` are expected.
- Do NOT modify `{vocabulary.xxx}` patterns or improvise content beyond the map.

## Handoff

Output this block as the LAST thing in your response:

=== GENERATION HANDOFF: Agent 2 (Skills) ===
Files Created:
- .claude/skills/<target-name>/SKILL.md (Tier <A|B>) × {N_SKILLS}

Vocabulary Applied:
- Tier A: frontmatter edited, body preserved ({vocabulary.xxx} intact)
- Tier B: {DOMAIN:xxx} substituted per map, {vocabulary.xxx} preserved
- Novel {DOMAIN:xxx} patterns encountered: <list or NONE>

Issues:
- [Warning]: <description> | NONE
- [Friction]: <description> | NONE

Verification:
- All files populated via cp then Edit (no Write): YES/NO
- {DOMAIN:} patterns remaining in .claude/skills/: <count — must be 0>
- {vocabulary.xxx} patterns preserved: YES
=== END HANDOFF ===
~~~

---

##### Skill Discoverability Protocol

The skill index does not refresh mid-session. After creating all skill files:

1. Report to main agent: list all generated skill names and confirm zero `{DOMAIN:` strings remain in Tier B output.
2. Phase 6 output must include: "Restart Claude Code now to activate all skills, then read manual/skills.md for the full command reference."

---

#### Pipeline Step 6: Context File, Feature References, and /ask Skill (Agent 3)

**Agent scope:** `CLAUDE.md`, `ops/features/*.md`, `.claude/skills/ask/SKILL.md`

**Agent reads:** `ops/derivation.md`, `ops/config.yaml`, `${CLAUDE_PLUGIN_ROOT}/generators/claude-md.md`, `${CLAUDE_PLUGIN_ROOT}/generators/features/*.md`, `${CLAUDE_PLUGIN_ROOT}/generators/ask-router.md`, `${CLAUDE_PLUGIN_ROOT}/reference/failure-modes.md`, `${CLAUDE_PLUGIN_ROOT}/reference/vocabulary-transforms.md`, generated templates (for reference verification), generated skills (for reference verification).

**Agent-specific prompt addition:** Include the list of active feature blocks and their source paths under `${CLAUDE_PLUGIN_ROOT}/generators/features/`.

---

##### Context File, Feature References, and /ask Skill

Generate three artifacts in order:

1. `ops/features/*.md` — one file per enabled feature block.
2. `CLAUDE.md` — seven-section context file from `generators/claude-md.md`.
3. `.claude/skills/ask/SKILL.md` — router skill from `generators/ask-router.md`.

**Generation algorithm:**

```
Step 1: Select feature blocks.
  Read ops/derivation.md to identify active feature blocks.
  All feature blocks are always included: note-granularity, wiki-links, mocs,
    processing-pipeline, semantic-search, schema, maintenance, session-rhythm,
    templates, ethical-guardrails, helper-functions,
    self-space.

Step 2: Write ops/features/<name>.md for each selected block.
  a. Read ${CLAUDE_PLUGIN_ROOT}/generators/features/<name>.md
  b. Apply vocabulary transformation (LLM-based contextual replacement, NOT
     string find-replace)
  c. Write domain-adapted content to ops/features/<name>.md as a standalone
     reference document
  d. Release the block from context before reading the next

Step 3: Compose CLAUDE.md.
  a. Read ${CLAUDE_PLUGIN_ROOT}/generators/claude-md.md
  b. Emit the seven sections in order: Header+Philosophy, Discovery-First,
     Memory Type Routing, Pipeline Compliance, Self-Improvement, Common
     Pitfalls (compressed), Infrastructure Routing
  c. For Common Pitfalls: select 3-4 HIGH-risk failure modes from the Domain
     Vulnerability Matrix in reference/failure-modes.md. For each selected
     mode, emit one bullet using the `one_line_rule:` field, vocabulary-
     transformed. Do not inline full prevention prose.
  d. Apply vocabulary transformation one final time on the assembled file.
  e. Write CLAUDE.md.

Step 4: Compose .claude/skills/ask/SKILL.md.
  a. Read ${CLAUDE_PLUGIN_ROOT}/generators/ask-router.md
  b. Follow the skill-body composition steps in that template.
  c. For Part B topic sections: emit one section per enabled feature (from
     Step 1) whose ops/features/<name>.md file was actually written in Step 2.
  d. Apply vocabulary transformation.
  e. Write .claude/skills/ask/SKILL.md.

Step 5: Coherence verification.
  - [ ] CLAUDE.md has exactly seven sections (header through Infrastructure
        Routing)
  - [ ] CLAUDE.md contains no feature summaries
  - [ ] CLAUDE.md pitfall bullets each correspond to a `one_line_rule:` in
        reference/failure-modes.md
  - [ ] CLAUDE.md Infrastructure Routing table has a /ask row
  - [ ] Every ops/features/<name>.md referenced by /ask exists on disk
  - [ ] /ask Part B emits sections only for features with matching
        ops/features/ files
  - [ ] Vocabulary consistent (same universal term -> same domain term
        across CLAUDE.md, ops/features/, and /ask)
  - [ ] Warm, neutral, helpful tone across all files
  - [ ] Structural markers (YAML field names, markdown syntax) untouched by
        vocabulary transform
```

**Structural Marker Protection:** Never apply vocabulary transformation to YAML field names (`description:`, `content_type:`, `type:`, `granularity:`, `status:`, `_schema:`, `name:`, `allowed-tools:`). Body-footer labels like `Topics:` and `Relevant Notes:` MAY be domain-renamed. Transform values, prose, and footer labels only.

**Quality requirements:**

- CLAUDE.md ≤ ~70 lines. No feature summaries, no inlined operational detail.
- Every rule in CLAUDE.md must be usable mid-task without invoking another skill.
- `/ask` topic sections are 2-line orientations with a file pointer — do not paraphrase full feature files.
- Domain vocabulary consistent across CLAUDE.md, `ops/features/*.md`, and `/ask`.

---

#### Pipeline Step 7: Manual & Hub MOC (Agent 4)

**Agent scope:** manual/ (7 pages), [domain:notes]/index.md

**Agent reads:** ops/derivation.md, generated skill names (from .claude/skills/), self/*.md (for hub MOC links)

---

##### manual/ (User-Navigable Documentation)

Generate all 7 manual pages. Manual is self-contained — pages wiki-link to each other but NOT to notes/.

For each page: replace universal terms (notes, inbox, topic map, reflect, reweave) with domain-native equivalents from the derivation conversation. Pipeline skills (/structure, /capture) are universal and not renamed. Use concrete domain examples.

**Page 1: manual.md (Hub MOC)**

```markdown
---
description: User manual for your {domain} knowledge system
type: manual
---
# Manual

Welcome to your {domain} knowledge system. This manual explains how everything works.

## Pages

- [[getting-started]] — Your first session: drop a file in inbox, run /pipeline, see results
- [[pipeline]] — The pipeline deep-dive: granularity modes, phases, resumability
- [[skills]] — Every available command grouped by role, with examples
- [[workflows]] — The core processing loop, session rhythm, and maintenance cycle
- [[configuration]] — How to adjust settings via config.yaml
- [[troubleshooting]] — Common issues and how to resolve them
```

**Page 2: getting-started.md**

```markdown
---
description: First session guide — run your first pipeline and build connections
type: manual
---
# Getting Started

{Generate content covering:}
- Drop something in {DOMAIN:inbox}/ — any file, paste, or voice transcript
- Run /{DOMAIN:pipeline} — it asks which granularity (structure/capture), then handles everything
- See what happened — pipeline report shows created {DOMAIN:note_plural}, connections, updated {DOMAIN:topic map}s
- Browse the results — follow wiki links from new {DOMAIN:note_plural} to see how the graph connects
- The session rhythm: orient (session start shows pending work) -> work (pipeline or manual commands) -> persist (session end saves state)
- Where to go next: link to [[pipeline]] for the deep-dive, [[skills]] for manual alternatives
```

**Page 3: skills.md**

```markdown
---
description: Complete reference for every available command, grouped by role
type: manual
---
# Skills

{Generate content with these groups. For each skill: one-line purpose, when to use it, example invocation.}

## Pipeline

The primary workflow. One command for end-to-end source processing.

- /{DOMAIN:pipeline} — end-to-end processing: seed, structure/capture, reflect, reweave, verify, archive

## Pipeline Sub-Skills

Internal machinery the pipeline orchestrates. Prefer /{DOMAIN:pipeline} as the interface — it owns queue state, batch tracking, and cross-phase quality gates. Invoke sub-skills directly only to recover from a stuck batch or re-run a single phase after a known failure.

- /{DOMAIN:seed} — create queue entry with duplicate detection
- /structure — grouped note production (related claims in one {DOMAIN:note})
- /capture — verbatim capture (no transformation)
- /{DOMAIN:reflect} — find connections, update {DOMAIN:topic map}s
- /{DOMAIN:reweave} — update older {DOMAIN:note_plural} with new context
- /{DOMAIN:verify} — description + schema + health check
- /archive-batch — archive completed batch

## Reference

Lookup and orientation.

- /ask — query the system's self-knowledge (schema, pipeline, {DOMAIN:topic map}s, derivation rationale)

## Operational

Vault state and diagnostics.

- /{DOMAIN:stats} — vault metrics

Note: /arscontexta:health (plugin-level) also performs diagnostics but is always available, not generated.

## Plugin-Level (always available)

These come with the plugin, not generated during setup. Referenced here for completeness.

- /arscontexta:health — run diagnostic checks on your vault

- Link to [[pipeline]] for how skills chain together in the pipeline
- Link to [[workflows]] for the processing loop and session rhythm
```

**Page 4: workflows.md**

```markdown
---
description: The core processing loop, session rhythm, and maintenance cycle
type: manual
---
# Workflows

{Generate content covering:}

## The Core Loop

inbox -> /{DOMAIN:pipeline} -> connected knowledge. This is the primary workflow. Everything else supports it.

## Processing Pipeline

The 6 Rs: Record (capture into {DOMAIN:inbox}), Reduce (/structure or /capture), Reflect (find connections), Reweave (update older {DOMAIN:note_plural}), Verify (quality checks), Rethink (challenge assumptions). Link to [[pipeline]] for the deep-dive.

## Session Rhythm

Orient (session start shows pending work and maintenance signals) -> work (run /{DOMAIN:pipeline} on inbox items, or manual commands) -> persist (session end saves state).

## Maintenance Cycle

Condition-based triggers, what to do when they fire, frequency guidance.

## Manual Processing

For when you want to run individual phases yourself. Link to [[skills]] for the sub-commands.

- Link to [[pipeline]] for pipeline details
- Link to [[skills]] for command reference
- Link to [[configuration]] for adjusting pipeline settings
```

**Page 5: pipeline.md**

```markdown
---
description: The pipeline deep-dive — granularity modes, processing phases, and resumability
type: manual
---
# Pipeline

{Generate content covering:}

## What Pipeline Does

One command, full processing: {DOMAIN:seed} -> structure/capture -> {DOMAIN:reflect} -> {DOMAIN:reweave} -> {DOMAIN:verify} -> archive. Drop a file in {DOMAIN:inbox}/, run /{DOMAIN:pipeline}, get connected knowledge.

## Two Granularity Modes

Present both as equal choices:

- `/{DOMAIN:pipeline} --structure` — grouped {DOMAIN:note_plural} preserving shared context. Best for sources where ideas are interrelated.
- `/{DOMAIN:pipeline} --capture` — verbatim preservation, no transformation. Best for reference material you want searchable but unaltered.
- No flag — pipeline asks you to choose.

## Processing Phases

Brief explanation of each phase: seed (duplicate detection, queue entry), processing (granularity-routed), reflect (forward connections and {DOMAIN:topic map} updates), reweave (backward updates to older {DOMAIN:note_plural}), verify (quality gate), archive (cleanup and summary). What each does and why it matters.

## Resumability

Pipeline can be interrupted and resumed at any point. Queue state persists across sessions. Table:

| Interrupted At | How to Resume |
|----------------|---------------|
| Before seed | Run /{DOMAIN:pipeline} again |
| After seed, before processing | /{DOMAIN:pipeline} --batch {id} |
| During note processing | /{DOMAIN:pipeline} --batch {id} |
| Before archive | /archive-batch {id} |

## Batch Orchestration

/{DOMAIN:pipeline} processes multiple items via the queue. Queue state lives in `ops/queue/queue.json`. Fresh context per phase ensures quality doesn't degrade.

## Going Manual

Any phase can be run individually. Link to [[skills]] for the sub-commands. Pipeline is the convenience wrapper; sub-skills are the building blocks.
```

**Page 6: configuration.md**

```markdown
---
description: How to adjust your system via config.yaml
type: manual
---
# Configuration

{Generate content covering:}
- config.yaml structure and key fields
- Feature toggling: what can be enabled/disabled
- Preset explanation: what your preset includes and why
- Dimension positions and what they mean for your domain
- Link to [[troubleshooting]] for configuration issues
```

**Page 7: troubleshooting.md**

```markdown
---
description: Common issues and resolution patterns
type: manual
---
# Troubleshooting

{Generate content covering:}
- Orphan {DOMAIN:notes} — {DOMAIN:note_plural} with no incoming links (run /{DOMAIN:reflect})
- Dangling links — wiki links to non-existent {DOMAIN:note_plural} (check after renames)
- Stale content — {DOMAIN:note_plural} not updated in 30+ days with sparse connections (run /{DOMAIN:reweave})
- Inbox overflow — too many items accumulating (run /{DOMAIN:pipeline} to process inbox items)
- Pipeline stalls — tasks stuck in queue (inspect `ops/queue/queue.json` directly, resume with /{DOMAIN:pipeline} --batch {id}). See [[pipeline]] resumability section.
- Common mistakes table with corrections
- Link to [[skills]] for command reference
- Link to [[configuration]] for threshold adjustments
```

**Quality gates:**

- All skill references use domain-native names from the derivation conversation
- All pages link back to [[manual]] via a footer or contextual reference
- No wiki links to notes/ — manual is self-contained
- Content uses domain-specific examples, not generic/abstract ones

##### Hub MOC

Create the vault entry point at `[domain:notes]/index.md`:

```markdown
---
description: Entry point to the knowledge system -- start here to navigate
content_type: moc
---

# index

Welcome to your [domain] system.

## [domain:Topics]
[Links to self/ MOCs and any domain-specific topic MOCs that are relevant]
- [[identity]] -- who the agent is and how it approaches work
- [[methodology]] -- how the agent processes and connects knowledge
- [[goals]] -- current active threads

## Getting Started
1. Read self/identity.md to understand your purpose
2. Capture your first [domain:note] in [domain:notes]/
3. Connect it to this hub
```

---

#### Pipeline Step 8: Semantic Search (Main Agent)

**Scope:** .claude/hooks/qmd-sync.sh, .claude/settings.json (additive merge)

**Reads:** ops/derivation.md, ops/config.yaml, ops/derivation-manifest.md

---

##### Semantic Search Setup

###### Add `notes_collection` to vocabulary

Before any qmd configuration, derive and register the collection name:

1. Derive a default collection name from `{vocabulary.note_collection}` (e.g., if notes folder is "claims", default collection name is "claims")
2. Run `qmd collections list` to check existing collections on the user's system
3. If the derived name collides with an existing collection, choose an alternative (e.g., append the vault directory name: "claims-myproject") — report the conflict and chosen name in output
4. Add `notes_collection` to **both** vocabulary stores:
   - `ops/derivation.md` — add a row to the Vocabulary Mapping table: `| notes_collection | <chosen-name> | qmd collection |`
   - `ops/derivation-manifest.md` — add `notes_collection: "<chosen-name>"` to the vocabulary section (after Level 6 / before processing_categories)

###### Check qmd installation and version

1. Check if `qmd` is installed: `which qmd`
2. If installed, check version: `qmd -v` — must be >= 2
3. If not installed or version < 2: skip to the not-installed path below

###### Configure qmd (installed, version >= 2)

Processing skills call `qmd query` via Bash — no MCP server, no `.mcp.json`, no autoapprove list. All that is needed is a registered collection and a fresh index.

1. Configure the qmd collection for `{vocabulary.notes_collection}` pointing at the generated notes directory:
   - `qmd collection add . --name {vocabulary.notes_collection} --mask "{vocabulary.note_collection}/**/*.md"`
2. Run `qmd update && qmd embed` to build the initial index

###### SessionStart hook for qmd sync

Generate a bash script `.claude/hooks/qmd-sync.sh`:

```bash
#!/usr/bin/env bash
# qmd-sync.sh — keep semantic search index current on session start
# No-ops gracefully if qmd is not installed

if ! command -v qmd &>/dev/null; then
  exit 0
fi

qmd update && qmd embed
```

Add a SessionStart hook entry to `.claude/settings.json` using additive merge:

1. Read existing `.claude/settings.json` (if it exists)
2. If `hooks.SessionStart` array exists, APPEND this matcher group — do not replace existing entries
3. If a matcher group with the same `command` path already exists, SKIP it
4. Write the merged result back

Append this matcher group to the `hooks.SessionStart` array:

```json
{
  "hooks": [
    {
      "type": "command",
      "command": "bash .claude/hooks/qmd-sync.sh"
    }
  ]
}
```

###### Not-installed path

If qmd is not installed or version < 2:

- Add a "Next Steps" section to the Phase 6 summary with install instructions:
  - `npm install -g @tobilu/qmd` (or `bun install -g @tobilu/qmd`)
  - `qmd collection add . --name {vocabulary.notes_collection} --mask "{vocabulary.note_collection}/**/*.md"`
  - `qmd update && qmd embed`
- The hook script (`qmd-sync.sh`) is already generated and will activate automatically once qmd is installed; processing skills will succeed as soon as the CLI is available on PATH

---

#### Pipeline Step 9: Git Initialization (Main Agent)

```bash
git init
git add -A
git commit -m "Initial vault generation by Ars Contexta"
```

If already initialized, skip `git init` and commit the generated files.

---

## PHASE 6: Validation and Summary

### Kernel Validation

Run all 14 primitive checks against the generated system. Manually verify:

1. **markdown-yaml** -- Every .md file has valid YAML frontmatter? (>95% threshold)
2. **wiki-links** -- All wiki links resolve to existing files? (>90% threshold)
3. **moc-hierarchy** -- At least 3 MOCs exist, every note appears in at least one MOC?
4. **tree-injection** -- Session start procedure loads file structure? (hook or context file instruction)
5. **description-field** -- Every note has a description field that differs from the title? (>95%)
6. **topics-footer** -- `tags` array and body-level `Topics:` footer present on every non-MOC note? (>95%)
7. **schema-enforcement** -- `ops/templates/note.md` exists as the single source of truth; every note carries the five required fields (content_type, granularity, description, created_at, tags). Title is the filename and body H1, not a frontmatter field.
8. **semantic-search** -- `.claude/hooks/qmd-sync.sh` exists and is wired into SessionStart, context file and processing skills invoke `qmd query` via Bash.
9. **self-space** -- self/ exists with identity.md, methodology.md, goals.md?
10. **session-rhythm** -- Context file references ops/features/session-rhythm.md for orient/work/persist cycle?
11. **discovery-first** -- Context file contains Discovery-First Design section, notes optimized for findability?
12. **processing-queue** -- Queue file (ops/queue/queue.json) exists with schema_version >= 3? Context file references it in session-orient phase? Pipeline skills advance tasks through phase_order?
13. **methodology-folder** (configurable) -- If ops/methodology/ exists, it contains methodology.md MOC and derivation-rationale.md?
Report results: pass/fail per primitive with specific failures listed.

### Pipeline Smoke Test

After kernel validation, run a functional test:

1. Create a test note in [domain:notes]/ with all five required fields
2. Verify frontmatter matches ops/templates/note.md schema (content_type, granularity, description, created_at, tags present)
3. Verify the hub MOC can reference it
4. Delete the test note and clean up

If the smoke test fails, report the failure with specific remediation steps. A vault that passes structural validation but fails functional testing is not ready.

### Clean CLI Output

Present results using clean formatting per Section 10.5 design language. No runes, no sigils, no decorative Unicode, no ASCII art. Clean indented text with standard markdown formatting only.

```
ars contexta -- the art of context

  Creating your [domain] structure...
  Writing your context file...
  Installing [domain:skills]...
  Setting up templates...
  Building your first [domain:topic map]...
  Initializing version control...
  Running validation...

Your memory is ready.
```

- **Progress markers:** Use indented text for generation milestones. These provide orientation during generation.
- **Section dividers:** Use `---` (standard markdown) between major output sections.

### Progressive Feature Reveal

Show available commands in the user's vocabulary. Resolve command names from `ops/derivation-manifest.md` vocabulary:

```
Here's what you can do:

  /{domain:pipeline}              -- end-to-end processing of inbox items
  /ask                            -- query your system's self-knowledge
  /arscontexta:health             -- check your knowledge system
```

Note: Vault-generated skills are invoked as `/skill-name`. Plugin-level commands use the prefix `/arscontexta:` — currently `/arscontexta:setup` and `/arscontexta:health`. List all commands explicitly since they may not appear in tab completion. Skills require a Claude Code restart before they become available.

### First-Success Moment

Guide the user to capture their first note. This is where the system stops being abstract and becomes real.

**If a preset was selected:** Check `${CLAUDE_PLUGIN_ROOT}/presets/[preset]/starter/` for domain-specific starter notes. Use the most relevant starter as a seed:

1. Present a starter note appropriate to the domain (e.g., a research claim, a personal reflection, a project decision)
2. Ask the user: "Here's a starter [domain:note] to get you going. Want to customize it, or shall I save it as-is?"
3. Create the note in [domain:notes]/ with proper schema
4. Add it to the hub MOC
5. Show: the note, the MOC it landed in, the schema fields filled

**If no preset:** Guide open-ended: "Try capturing something: just tell me an idea." Then create the note and show the same result.

**Why this matters:** The first-success moment proves the system works. The user sees their content structured, connected, and navigable. This converts abstract architecture into tangible value.

### Summary

Present in the user's vocabulary with clean formatting:

```
ars contexta

Your [domain] system is ready.

Configuration:
  Automation: Full — all capabilities from day one
  [Key dimension highlights relevant to the user]

Created:
  [list of folders with domain names]
  [context file name]
  [templates created]
  [N] skills generated into .claude/skills/ (vocabulary-transformed)
  /arscontexta:health and /arscontexta:setup available as plugin-level commands
  [hooks configured]
  ops/derivation.md      -- the complete record of how this system was derived
  ops/derivation-manifest.md -- machine-readable config for runtime skills
  ops/methodology/       -- vault self-knowledge (query with /ask or browse directly)
  ops/config.yaml        -- edit this to adjust dimensions without re-running init

Kernel Validation: [PASS count] / 14 passed
[Any warnings to address]

IMPORTANT: Restart Claude Code now to activate skills and hooks.
  Skills and hooks take effect after restart — they are not available in the current session.

Next steps:
  1. Quit and restart Claude Code (required — skills won't work until you do)
  2. Read your CLAUDE.md -- it's your complete methodology
  3. Read manual/skills.md for the full command reference
  4. [If qmd not installed: "REQUIRED — install qmd to activate semantic search: npm install -g @tobilu/qmd (or bun install -g @tobilu/qmd), then run qmd collection add, qmd update, qmd embed"]
  5. Drop a file in {domain:inbox}/ and run /{domain:pipeline} to try your first end-to-end run

```

---

## Quality Standards (Non-Negotiable)

These apply to every generation run. Do not shortcut any of them.

1. **Generated files feel cohesive, not assembled from blocks.** Block boundaries must be invisible in the output. The context file reads as if written from scratch for this specific domain.
2. **Language matches the user's domain.** A therapy user never sees "claim" or "reduce." A PM user never sees "reflection" or "surface." The vocabulary test applies to every generated file.
3. **self/identity.md feels genuine, not templated.** It reads like self-knowledge, not a character sheet.
4. **Every generated file is immediately useful.** No placeholder content. No "TODO: fill this in." Every file serves a purpose from day one.
5. **Dimension settings are justified.** The derivation rationale connects every choice to either a user signal or a research-backed default.
6. **Kernel validation PASSES.** Zero failures on every generated system. If validation fails, fix the generation before presenting results.
7. **Vocabulary consistency across ALL files.** The same universal term must ALWAYS map to the same domain term across all generated files. Run a mental consistency check: if you said "reflection" in the context file, you must say "reflection" in templates, skills, and self/ files.
8. **Three-space boundaries are clean.** Agent self-knowledge in self/. Domain knowledge in notes/. Operational scaffolding in ops/. No conflation.
9. **Discovery-first is enforced.** Every note, every MOC, every template is optimized for future agent discovery. Description quality, MOC membership, title composability.
10. **Tone never contradicts methodology.** The agent's warm, neutral, helpful tone affects HOW methodology is communicated, never WHETHER it is enforced. Quality gates and composability checks apply regardless.

