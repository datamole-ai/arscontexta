---
name: seed
description: Add a source file to the processing queue. Checks for duplicates, creates archive folder, moves source from inbox, creates process task, and updates queue. Triggers on "/seed", "/seed [file]", "queue this for processing".
version: "1.0"
context: fork
allowed-tools: Read, Write, Edit, Grep, Glob, Bash, mcp__qmd__query
---

## EXECUTE NOW

**Target: $ARGUMENTS**

The target MUST be a file path. If no target provided, end immediately with: "ERROR: seed requires file path"

**Granularity flag:**
one of: --structure, --capture
If no flag: end immediately with: "ERROR: seed requires granularity flag"

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

**START NOW.** Seed the source file into the processing queue.

---

## Step 1: Validate Source

If the file cannot be found, report error and stop:
```
ERROR: Source file not found: {path}
Checked: {locations checked}
```

Read the file to understand:
- **Content type**: what kind of material is this? (research article, documentation, transcript, etc.)
- **Size**: line count (affects chunking decisions in /structure, /capture)
- **Format**: markdown, plain text, structured data

## Step 2: Duplicate Detection

Check if this source has already been processed. Two levels of detection:

### 2a. Filename Match

Search the queue file and archive folders for matching source names:

```bash
SOURCE_NAME=$(basename "$FILE" .md | tr ' ' '-' | tr '[:upper:]' '[:lower:]')

# Check queue for existing entry
grep -l "$SOURCE_NAME" ops/queue/*.json 2>/dev/null

# Check archive folders
ls -d ops/queue/archive/*-${SOURCE_NAME}* 2>/dev/null
```

### 2b. Content Similarity

Check for content overlap:

```
mcp__qmd__query query="claims from {source filename}" limit=5
```

Or via keyword search in the {DOMAIN:note_collection}/ directory:
```bash
grep -rl "{key terms from source title}" {DOMAIN:note_collection}/ 2>/dev/null | head -5
```

### 2c. Report Duplicates

If either check finds a match:
- Decide whether the duplicate is a near-duplicate or an exact duplicate
- If near-duplicate, suggest creating an enrichment task in the file created by Step 6.
- If exact duplicate, end immediately with: "WARN: Source is an exact duplicate of an existing {DOMAIN:note_plural} and was not seeded."

## Step 3: Create Archive Structure

Create the archive folder. The date-prefixed folder name ensures uniqueness.

```bash
DATE=$(date -u +"%Y-%m-%d")
SOURCE_BASENAME=$(basename "$FILE" .md | tr ' ' '-' | tr '[:upper:]' '[:lower:]')
ARCHIVE_DIR="ops/queue/archive/${DATE}-${SOURCE_BASENAME}"
mkdir -p "$ARCHIVE_DIR"
```

## Step 4: Move Source to Archive

Move the source file from its current location to the archive folder. This is the **claiming step** — once moved, the source is owned by this processing batch.

**{DOMAIN:inbox}/ sources get moved:**
```bash
if [[ "$FILE" == *"{DOMAIN:inbox}"* ]] || [[ "$FILE" == *"inbox"* ]]; then
  mv "$FILE" "$ARCHIVE_DIR/"
  FINAL_SOURCE="$ARCHIVE_DIR/$(basename "$FILE")"
fi
```

**Sources outside {DOMAIN:inbox}/ stay in place:**
```bash
FINAL_SOURCE="$FILE"
```

Use `$FINAL_SOURCE` in the task file — this is the path all downstream phases reference.

**Why move immediately:** All references (task files, {DOMAIN:note_plural}' Source footers) use the final archived path from the start. No path updates needed later. If it is in {DOMAIN:inbox}/, it is unclaimed. Claimed sources live in archive.

## Step 4b: Copy to Domain Archive

For inbox sources only, copy the original to `{DOMAIN:archive}/` for easy discoverability. This runs after the move — `$FINAL_SOURCE` already points to `ops/queue/archive/`.

```bash
if [[ "$FILE" == *"{DOMAIN:inbox}"* ]] || [[ "$FILE" == *"inbox"* ]]; then
  mkdir -p "{DOMAIN:archive}/"
  ARCHIVE_COPY="{DOMAIN:archive}/${DATE}-${SOURCE_BASENAME}.md"
  if [[ -f "$ARCHIVE_COPY" ]]; then
    echo "WARN: $ARCHIVE_COPY already exists, skipping copy"
  else
    cp "$FINAL_SOURCE" "$ARCHIVE_COPY"
  fi
fi
```

Sources outside {DOMAIN:inbox} (living docs) skip this step — no archive copy is made.

## Step 5: Determine Claim Numbering

Find the highest existing claim number across the queue and archive to ensure globally unique claim IDs.

```bash
# Check queue for highest claim number in file references
QUEUE_MAX=$(grep -oE '[0-9]{3}\.md' ops/queue/*.json 2>/dev/null | \
  grep -oE '[0-9]{3}' | sort -n | tail -1)
QUEUE_MAX=${QUEUE_MAX:-0}

# Check archive for highest claim number
ARCHIVE_MAX=$(find ops/queue/archive -name "*-[0-9][0-9][0-9].md" 2>/dev/null | \
  grep -v summary | sed 's/.*-\([0-9][0-9][0-9]\)\.md/\1/' | sort -n | tail -1)
ARCHIVE_MAX=${ARCHIVE_MAX:-0}

# Next claim starts after the highest
NEXT_CLAIM_START=$((QUEUE_MAX > ARCHIVE_MAX ? QUEUE_MAX + 1 : ARCHIVE_MAX + 1))
```

Claim numbers are globally unique and never reused across batches. This ensures every claim file name (`{source}-{NNN}.md`) is unique vault-wide.

## Step 6: Create Process Task File

Write the task file to `ops/queue/${SOURCE_BASENAME}.md`:

```markdown
---
id: {SOURCE_BASENAME}
type: process
granularity: {GRANULARITY_FLAG}
source: {FINAL_SOURCE}
original_path: {original file path before move}
archive_folder: {ARCHIVE_DIR}
created: {UTC timestamp}
next_claim_start: {NEXT_CLAIM_START}
---

# Process {DOMAIN:note_plural} from {source filename}

## Source
Original: {original file path}
Archived: {FINAL_SOURCE}
Size: {line count} lines
Content type: {detected type}

## Scope
Full document

## Duplicate Detection
- Near-duplicate found: (filled from step 2c)

## Acceptance Criteria
- Process claims, implementation ideas, tensions, and testable hypotheses
- Duplicate check against {DOMAIN:note_collection}/ during processing
- Near-duplicates create enrichment tasks (do not skip)
- Each output type gets appropriate handling

## Execution Notes
(filled by processing skill)

## Outputs
(filled by processing skill)
```

## Step 7: Update Queue

Add the process task entry to the queue file.


**For JSON queues (ops/queue/queue.json):**
```json
{
  "id": "{SOURCE_BASENAME}",
  "type": "process",
  "granularity": "{GRANULARITY_FLAG}",
  "status": "pending",
  "source": "{FINAL_SOURCE}",
  "file": "{SOURCE_BASENAME}.md",
  "created": "{UTC timestamp}",
  "next_claim_start": {NEXT_CLAIM_START}
}
```

## Step 8: Report

```
--=={ seed }==--

Seeded: {SOURCE_BASENAME}
Source: {original path} -> {FINAL_SOURCE}
Archive folder: {ARCHIVE_DIR}
Archived copy: {DOMAIN:archive}/{DATE}-{SOURCE_BASENAME}.md
Size: {line count} lines
Content type: {detected type}

Task file: ops/queue/{SOURCE_BASENAME}.md
Claims will start at: {NEXT_CLAIM_START}
Claim files will be: {SOURCE_BASENAME}-{NNN}.md (unique across vault)
Queue: updated with process task (granularity: {GRANULARITY_FLAG})
```

---

## Naming Convention

Task files use the source basename for human readability:
- Task file: `{source-basename}.md`
- Claim files: `{source-basename}-{NNN}.md`
- Summary: `{source-basename}-summary.md`
- Archive folder: `{date}-{source-basename}/`

Claim numbers (NNN) are globally unique across all batches, ensuring every filename is unique vault-wide. This is required because wiki links resolve by filename, not path.

---

## Edge Cases

**Large source (2500+ lines):** Note in output: "Large source ({N} lines) -- processing skill will chunk automatically."

---

## Critical Constraints

**always:**
- Create the archive folder even for living docs (task files need it)
- Use the archived path (not original) in the task file for {DOMAIN:inbox} sources
- Report next steps clearly so the orchestrator knows what to do next
- Compute next_claim_start from both queue AND archive (not just one)
