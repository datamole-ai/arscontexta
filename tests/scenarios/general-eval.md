This file contains the evaluation criteria for general scenario runs.

It is a list of checks that need to be performed on the final vault individually.

For each criteria group, spawn an evaluator agent that evaluates the criteria group and returns important information you need to generate the report.

## Criteria groups

### Vault structure
Set of checks focusing on the structure of the vault.

- The vault manifest is complete: required directories, `.second-brain`, `CLAUDE.md`, `notes/index.md`, `.gitignore`, governed files, six generated skills, and vault-local tooling are present
- Immutable generated files match their repository sources: `CLAUDE.md`, `.gitignore`, `ops/schema.yaml`, generated skills, and tooling source; allow `ops/tags.yaml` and notes to evolve
- Source accounting is exact: inbox is empty, every scenario source appears exactly once in `archive/` with identical content, and no unrelated archived sources exist
- All knowledge notes are direct children of `notes/`; no nested note directories exist
- Every note includes the four governed frontmatter fields `content_type`, `granularity`, `description`, and `tags`; no note contains `created_at`
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

### Statistics
Use an evaluation agent to collect metrics.

Runtime
- total wall time
- setup time
- processing time per source
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

## Output report

Aggregate the results of the criteria groups returned by the evaluator agents 
to standalone markdown file acting as a report.

Start the report with a summary of the criteria groups and the overall score followed by statistics.

After the first section, the report should focus on bringing out the key issues 
and reasons why the candidate failed to meet the criteria so that the output is
actionable for the candidate.
