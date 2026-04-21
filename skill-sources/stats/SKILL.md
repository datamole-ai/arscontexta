---
name: stats
description: Show vault statistics and knowledge graph metrics. Provides a snapshot of vault health, growth, and progress. Triggers on "/stats", "vault stats", "how big is my vault".
version: "1.0"
allowed-tools: Read, Grep, Glob, Bash
---

## Runtime Configuration

### Vocabulary

All output must use domain-native terms.
Derivation manifest for vocabulary mapping:
!`cat ops/derivation-manifest.md`

---

## Philosophy

**Make the invisible visible.**

The knowledge graph grows silently. Without metrics, the user cannot tell whether their system is healthy, growing, stagnating, or fragmenting. /stats provides a snapshot that makes growth tangible — numbers that show progress, health indicators that catch problems, and trends that reveal trajectory.

The output should make the user feel informed, not overwhelmed. Metrics are evidence, not judgment. "12 orphans" is a fact. What to DO about it belongs to /{vocabulary.cmd_reflect}.

---

## Step 1: Collect Metrics

Gather all metrics. Run these checks in parallel where possible to minimize latency.

### 1a. Knowledge Graph Metrics

```bash
NOTES_DIR="{vocabulary.note_collection}"

# Note count (excluding MOCs)
TOTAL_FILES=$(find "$NOTES_DIR"/ -name "*.md" -type f | wc -l | tr -d ' ')
MOC_COUNT=$(find "$NOTES_DIR"/ -name "*.md" -type f -exec grep -l '^content_type: moc' {} + 2>/dev/null | wc -l | tr -d ' ')
NOTE_COUNT=$((TOTAL_FILES - MOC_COUNT))

# Connection count (all wiki links across notes/)
LINK_COUNT=$(find "$NOTES_DIR"/ -name "*.md" -type f -exec grep -ohP '\[\[[^\]]+\]\]' {} + 2>/dev/null | wc -l | tr -d ' ')

# Average connections per note
if [[ "$NOTE_COUNT" -gt 0 ]]; then
  AVG_LINKS=$(echo "scale=1; $LINK_COUNT / $NOTE_COUNT" | bc)
else
  AVG_LINKS="0"
fi

# Link density
if [[ "$NOTE_COUNT" -gt 1 ]]; then
  POSSIBLE=$((NOTE_COUNT * (NOTE_COUNT - 1)))
  DENSITY=$(echo "scale=4; $LINK_COUNT / $POSSIBLE" | bc)
else
  DENSITY="N/A"
fi
```

### 1b. Health Metrics

```bash
# Orphan count (notes with zero incoming links)
ORPHAN_COUNT=0
for f in $(find "$NOTES_DIR"/ -name "*.md" -type f); do
  NAME=$(basename "$f" .md)
  grep -q '^content_type: moc' "$f" 2>/dev/null && continue
  INCOMING=$(grep -rl "\[\[$NAME\]\]" "$NOTES_DIR"/ 2>/dev/null | grep -v "$f" | wc -l | tr -d ' ')
  [[ "$INCOMING" -eq 0 ]] && ORPHAN_COUNT=$((ORPHAN_COUNT + 1))
done

# Dangling link count
DANGLING_COUNT=$(find "$NOTES_DIR"/ -name "*.md" -type f -exec grep -ohP '\[\[([^\]]+)\]\]' {} + 2>/dev/null | sort -u | while read -r link; do
  NAME=$(echo "$link" | sed 's/\[\[//;s/\]\]//')
  ! find "$NOTES_DIR"/ -name "$NAME.md" -type f | grep -q . && echo "$NAME"
done | wc -l | tr -d ' ')

# Schema compliance — % of notes with a description field (required by the schema).
# This is a rough signal; /health runs the full per-field schema check.
MISSING_DESC=$(find "$NOTES_DIR"/ -name "*.md" -type f -exec grep -L '^description:' {} + 2>/dev/null | wc -l | tr -d ' ')
if [[ "$TOTAL_FILES" -gt 0 ]]; then
  COMPLIANT=$((TOTAL_FILES - MISSING_DESC))
  COMPLIANCE=$(echo "scale=0; $COMPLIANT * 100 / $TOTAL_FILES" | bc)
else
  COMPLIANCE="N/A"
fi

# MOC coverage
COVERED=0
for f in $(find "$NOTES_DIR"/ -name "*.md" -type f); do
  NAME=$(basename "$f" .md)
  grep -q '^content_type: moc' "$f" 2>/dev/null && continue
  if find "$NOTES_DIR"/ -name "*.md" -type f -exec grep -l '^content_type: moc' {} + 2>/dev/null | xargs grep -l "\[\[$NAME\]\]" >/dev/null 2>&1; then
    COVERED=$((COVERED + 1))
  fi
done
if [[ "$NOTE_COUNT" -gt 0 ]]; then
  COVERAGE=$(echo "scale=0; $COVERED * 100 / $NOTE_COUNT" | bc)
else
  COVERAGE="N/A"
fi
```

### 1c. Pipeline Metrics

```bash
# Inbox items
INBOX_COUNT=$(find {vocabulary.inbox}/ -name "*.md" 2>/dev/null | wc -l | tr -d ' ')

# Queue pending
if [[ -f "ops/queue/queue.json" ]]; then
  QUEUE_PENDING=$(jq '[.tasks[] | select(.status=="pending")] | length' ops/queue/queue.json 2>/dev/null || echo 0)
  QUEUE_DONE=$(jq '[.tasks[] | select(.status=="done")] | length' ops/queue/queue.json 2>/dev/null || echo 0)
else
  QUEUE_PENDING=0
  QUEUE_DONE=0
fi

# Processed ratio (notes vs inbox)
TOTAL_CONTENT=$((NOTE_COUNT + INBOX_COUNT))
if [[ "$TOTAL_CONTENT" -gt 0 ]]; then
  PROCESSED_PCT=$(echo "scale=0; $NOTE_COUNT * 100 / $TOTAL_CONTENT" | bc)
else
  PROCESSED_PCT="N/A"
fi
```

### 1d. Growth Metrics

```bash
# This week's growth (notes with created_at: date within last 7 days).
WEEK_AGO=$(date -v-7d +%Y-%m-%d 2>/dev/null || date -d '7 days ago' +%Y-%m-%d 2>/dev/null)
if [[ -n "$WEEK_AGO" ]]; then
  THIS_WEEK_NOTES=$(find "$NOTES_DIR"/ -name "*.md" -type f -exec grep -l "^created_at: " {} + 2>/dev/null | while read -r f; do
    CREATED=$(grep '^created_at:' "$f" | head -1 | awk '{print $2}')
    [[ "$CREATED" > "$WEEK_AGO" || "$CREATED" == "$WEEK_AGO" ]] && echo "$f"
  done | wc -l | tr -d ' ')
else
  THIS_WEEK_NOTES="?"
fi

# This week's connections (approximate — count links in recently created notes)
if [[ "$THIS_WEEK_NOTES" -gt 0 && -n "$WEEK_AGO" ]]; then
  THIS_WEEK_LINKS=$(find "$NOTES_DIR"/ -name "*.md" -type f -exec grep -l "^created_at: " {} + 2>/dev/null | while read -r f; do
    CREATED=$(grep '^created_at:' "$f" | head -1 | awk '{print $2}')
    [[ "$CREATED" > "$WEEK_AGO" || "$CREATED" == "$WEEK_AGO" ]] && grep -oP '\[\[[^\]]+\]\]' "$f" 2>/dev/null
  done | wc -l | tr -d ' ')
else
  THIS_WEEK_LINKS="?"
fi
```

### 1e. System Metrics

```bash
# Self space (invariant — must exist)
if [[ -d "self/" ]]; then
  SELF_FILES=$(find self/ -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
  SELF_STATUS="$SELF_FILES files"
else
  SELF_STATUS="MISSING (invariant primitive)"
fi

# Observations pending
# Not all vaults declare `content_type: observation`; zero is a valid result.
OBS_PENDING=0
for f in $(find "$NOTES_DIR"/ -name "*.md" -type f -exec grep -l '^content_type: observation' {} + 2>/dev/null); do
  grep -q '^status: pending' "$f" 2>/dev/null && OBS_PENDING=$((OBS_PENDING + 1))
done

# Tensions pending
# Not all vaults declare `content_type: tension`; zero is a valid result.
TENSION_PENDING=0
for f in $(find "$NOTES_DIR"/ -name "*.md" -type f -exec grep -l '^content_type: tension' {} + 2>/dev/null); do
  grep -qE '^status: (open|pending)' "$f" 2>/dev/null && TENSION_PENDING=$((TENSION_PENDING + 1))
done
```

Adapt all directory names to domain vocabulary. Skip checks for directories that do not exist — report "N/A" instead of errors.

---

## Step 2: Format Output

### Full Output (default)

Generate a progress bar for the Processed metric:

```
Progress bar calculation:
  filled = PROCESSED_PCT / 5 (number of = characters out of 20)
  empty = 20 - filled
  bar = [===...   ] PCT%
```

```
--=={ stats }==--

  Knowledge Graph
  ===============
  {vocabulary.note_plural}:  [NOTE_COUNT]
  Connections:               [LINK_COUNT] (avg [AVG_LINKS] per {vocabulary.note})
  {vocabulary.topic_map_plural}:   [MOC_COUNT] (covering [COVERAGE]% of {vocabulary.note_plural})

  Health
  ======
  Orphans:      [ORPHAN_COUNT]
  Dangling:     [DANGLING_COUNT]
  Schema:       [COMPLIANCE]% compliant

  Pipeline
  ========
  Processed:    [==============      ] [PROCESSED_PCT]%
  Inbox:        [INBOX_COUNT] items
  Queue:        [QUEUE_PENDING] pending tasks

  Growth
  ======
  This week:    +[THIS_WEEK_NOTES] {vocabulary.note_plural}, +[THIS_WEEK_LINKS] connections
  Graph density: [DENSITY]

  System
  ======
  Self space:      [SELF_STATUS]
  Observations:    [OBS_PENDING] pending
  Tensions:        [TENSION_PENDING] open

  Generated by Ars Contexta
```

### Interpretation Notes

After the stats block, add brief interpretation for any notable findings:

| Condition | Note |
|-----------|------|
| COMPLIANCE < 90 | "Schema compliance below 90% — some {vocabulary.note_plural} missing required fields" |
| OBS_PENDING >= 10 | "[N] pending observations — run /health for details" |
| TENSION_PENDING >= 5 | "[N] open tensions — run /health for details" |
| PROCESSED_PCT < 50 | "More content in inbox than in {vocabulary.note_collection}/ — consider processing backlog" |
| THIS_WEEK_NOTES == 0 | "No new {vocabulary.note_plural} this week" |

Only show interpretation notes when conditions are notable. A healthy vault gets just the stats, no warnings.

---

## Step 3: Trend Analysis (when history exists)

If previous /stats runs are logged in `ops/stats-history.yaml` (or similar), compare current metrics against the last snapshot:

```
  Trend (vs last check):
    {vocabulary.note_plural}: [N] (+[delta] since [date])
    Connections:              [N] (+[delta])
    Density:                  [N] ([up/down/stable])
    Orphans:                  [N] ([improved/worsened/stable])
```

If no history exists, skip trend analysis. Do NOT create the history file — that is /health's responsibility.
