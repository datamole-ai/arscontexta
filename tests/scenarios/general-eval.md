This file contains the evaluation criteria for general scenario runs.

It is a list of checks that need to be performed on the final vault individually.

For each criteria group, spawn an evaluator agent that evaluates the criteria group and returns important information you need to generate the report.

If the scenario contains `eval.md`, read it only during evaluation. It is the answer key
for prompts under that scenario's `questions/` directory and must not be exposed to the
candidate.

## Criteria groups

### Vault structure
Set of checks focusing on the structure of the vault.

- The vault manifest is complete: required directories, `.second-brain`, `CLAUDE.md`, `notes/index.md`, `.gitignore`, governed files, six generated skills, and vault-local tooling are present
- Immutable generated files match their repository sources: `CLAUDE.md`, `.gitignore`, `ops/schema.yaml`, generated skills, and tooling source; allow `ops/tags.yaml` and notes to evolve
- Source accounting is exact: inbox is empty, every scenario source appears exactly once in `archive/` with identical content, and no unrelated archived sources exist
- All knowledge notes are direct children of `notes/`; no nested note directories exist
- Every note has exactly the four governed frontmatter fields `content_type`, `granularity`, `description`, and `tags`
- Final operational state is complete: qmd has the single `notes` collection with mask `notes/**/*.md`, Git contains the initial commit and one pipeline commit per scenario source, and no tracked changes remain

### Verification
Set of checks focusing on the verification of the vault.

- Run the vault's health skill and check the output shows no errors

### Run logs

Use one evaluator for the setup logs and one evaluator for each processing run.

#### Setup trace

- Setup runs the prerequisite commands before asking questions or writing files
- Setup presents the proposed tags and receives approval before the first file write
- Generation follows the required order: copy template, lock tooling dependencies, write approved tags, initialize qmd, validate, then create the initial Git commit
- Setup changes only the approved tag registry; it does not generate or rewrite fixed template files manually
- Every command succeeds before setup advances to the next phase

#### Processing trace

- Each source runs in a fresh session and processes files in scenario filename order
- The process uses exactly one requested mode, `--structure` or `--capture`; it asks when the mode is absent instead of guessing
- Each batch follows the required order: seed, structure or capture, connect, verify, commit, then qmd refresh
- Skill boundaries are respected:
  - structure and capture read their governed files and complete source before writing
  - structure and capture do not call qmd
  - capture uses `vault capture` instead of copying source text manually
  - capture makes no more than two `vault capture` attempts; its second attempt follows only `"retryable": true`, and any second or non-retryable failure stops; process never adds another producer invocation
  - connect runs qmd and Obsidian commands separately, reads candidate notes before editing, and reruns graph checks after editing
  - verify runs after connect and before staging
- The process stages only the archived source, reported artifacts, and `ops/tags.yaml`
- The batch commit occurs only after successful verification

### Knowledge answers

If the scenario has a `questions/` directory, use one evaluator for each question turn.

- Every question prompt is run after all scenario sources have been processed, in question filename order
- Every question uses a fresh candidate session, and the exact prompt plus its stream log are preserved in the run
- There is exactly one recorded answer for every question listed in the scenario's `eval.md`, with no extra or missing question turns
- Check only the final answer returned to the user, not hidden reasoning or tool output
- Mark an answer as passing when it states every required fact listed for that question in `eval.md`
- Accept wording, capitalization, accents, and formatting variants when they express the same fact
- Do not require citations, source paths, reasoning, a specific retrieval command, or exact wording
- Ignore unrelated extra material unless it directly contradicts or negates a required fact
- Treat each question as one pass/fail check and report separate totals for single-source and multi-source questions

### Statistics
Use an evaluation agent to collect metrics.

Runtime
- total wall time
- setup time
- processing time per source
- question-answering time per prompt
- turns, tool calls, failed calls

Knowledge output
- source words
- notes created and modified
- knowledge/source word ratio
- internal links and cross-source links
- MOC coverage
- unresolved knowledge links

Costs
- input, reasoning, output tokens

Knowledge answers
- correct answers out of total
- single-source correct answers out of total
- multi-source correct answers out of total

## Output report

Aggregate the results of the criteria groups returned by the evaluator agents 
to standalone markdown file acting as a report.

Start the report with a summary of the criteria groups and the overall score followed by statistics. Include each knowledge question as one check in the overall score.

After the first section, the report should focus on bringing out the key issues 
and reasons why the candidate failed to meet the criteria so that the output is
actionable for the candidate.
