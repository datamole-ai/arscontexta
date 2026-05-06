---
name: health
description: Run condition-based vault health diagnostics. 8 categories — schema compliance, orphan detection, link health, description quality, three-space boundaries, processing throughput, stale notes, MOC coherence. Returns actionable FAIL/WARN/PASS report with specific fixes ranked by impact. Triggers on "/health", "check vault health", "maintenance report", "what needs fixing".
version: "1.0"
context: fork
allowed-tools: Read, Grep, Glob, Bash
---

## Runtime Configuration (Step 0 — before any processing)

Read these files to configure domain-specific behavior:

1. **`ops/derivation-manifest.md`** — vocabulary mapping, folder names, platform hints
   - Use `vocabulary.note_collection` for the notes folder name
   - Use `vocabulary.entity_directories` for the list of entity type subdirectories
   - Use `vocabulary.inbox` for the inbox folder name
   - Use `vocabulary.note` for the note type name in output
   - Use `vocabulary.topic_map` for MOC/topic map references
   - Use `vocabulary.topic_maps` for plural form

2. **`ops/config.yaml`** — thresholds

3. **Three-space reference** — `${CLAUDE_PLUGIN_ROOT}/reference/three-spaces.md` for boundary rules

4. **Templates** — read template files to understand required schema fields for validation

If these files don't exist (pre-init invocation or standalone use), use universal defaults:
- note collection: `note_collection/`
- inbox folder: `inbox/`
- topic map: topic maps in note_collection/

---

## EXECUTE NOW

**Execute these steps:**

1. Run health-check.sh:
   ```bash
   bash "${CLAUDE_PLUGIN_ROOT}/skills/health/scripts/health-check.sh"
   ```
   The script covers Categories 1, 2, 3, 5, 6, 7, 8 plus Maintenance Signals and a leading scan summary.

2. Run **Category 4 (Description Quality)** yourself — it is semantic judgment the script cannot perform. See "## Category 4 — Description Quality" below for the heuristic.

3. Compose the report using the master template under "## Output Format". Replace the script's `[4] PENDING` line with your Cat 4 verdict.

4. Rank the **top 3 recommended actions** by impact (see "Prioritize by Impact" tier table) and append.

5. Write the full report to `ops/health/YYYY-MM-DD-report.md`. If a report already exists for today, append a counter: `YYYY-MM-DD-report-2.md`.

If `health-check.sh` exits nonzero, emit `ERROR: health-check.sh failed (exit <code>)` and stop. Do not attempt recovery.

---

## Category 4 — Description Quality

**What it checks:** Every {vocabulary.note}'s description adds genuine information beyond the title — not just a restatement.

**How to check:**

For each {vocabulary.note}:
1. Read the title (filename without extension)
2. Read the `description` field from YAML frontmatter
3. Evaluate: does the description add scope, mechanism, or implication that the title does not cover?

**Quality heuristics:**

| Check | Threshold |
|-------|-----------|
| Description length | 50-200 chars ideal. < 30 chars = too terse. > 250 chars = too verbose |
| Restatement detection | If description uses >70% of the same words as the title = restatement |
| Information added | Description should mention mechanism, scope, or implication not in title |

**Thresholds:**

| Condition | Level |
|-----------|-------|
| Description is a clear restatement of the title | WARN |
| Description is < 30 characters | WARN |
| Description is missing entirely | WARN (also caught by Category 1) |
| Description adds genuine new information | PASS |

**This check requires judgment.** Use semantic understanding, not just string matching. A description that uses different words but says the same thing as the title is still a restatement.

**Output format:**
```
[4] Description Quality .......... WARN
    2 descriptions are restatements:
      - notes/quality-matters.md
        Title: "quality matters more than quantity"
        Description: "quality is more important than quantity in knowledge work"
        Issue: restates title without adding mechanism or implication
      - notes/structure-helps.md
        Title: "structure without processing provides no value"
        Description: "having structure without processing it is not valuable"
        Issue: exact restatement
    Recommendation: rewrite descriptions to add scope, mechanism, or implication
```

---

## Condition-Based Maintenance Signals

After running all applicable diagnostic categories, check these condition-based triggers. These are NOT the 8 categories above — they are cross-cutting signals that suggest specific skill invocations.

| Condition | Threshold | Recommendation |
|-----------|-----------|---------------|
| Inbox items | >= 3 items | Consider /structure, /capture, or /pipeline |
| Orphan notes | Any persistent (> 7d) | Run /connect on orphaned notes |
| Dangling links | Any | Fix broken references immediately |
| Stale notes | Low links + old | Consider /connect |
| {vocabulary.topic_map} oversized | > 40 notes | Consider splitting |
| Queue stalled | Tasks pending > 2 sessions without progress | Surface as blocked |
| Trigger coverage gap | Known maintenance condition has no configured trigger | Flag gap itself |

**How to check condition counts:**

```bash
# Inbox items
INBOX_COUNT=$(find {vocabulary.inbox}/ -name '*.md' -not -path '*/archive/*' 2>/dev/null | wc -l | tr -d ' ')


# Queue stalled
PENDING_TASKS=$(jq '[.tasks[] | select(.status=="pending")] | length' ops/queue/queue.json 2>/dev/null || echo 0)
```

**The meta-trigger:** Include a "trigger coverage" check. Compare known maintenance conditions against what is actually being checked. If a maintenance condition has no corresponding check or trigger configured, that gap itself is a finding. This prevents the failure mode where maintenance debt accumulates undetected.

---

## Output Format

The complete health report follows this structure.

```
=== HEALTH REPORT ===
Date: YYYY-MM-DD
Notes scanned: N | Topic maps: N | Inbox items: N

Summary: N FAIL, N WARN, N PASS

FAIL:
- [Category N]: [brief description of failure]
  [specific files and details]

WARN:
- [Category N]: [brief description of warning]
  [specific files and details]

PASS:
- [Category N]: [confirmation]

---

[1] Schema Compliance ............ PASS | WARN | FAIL
    [details — specific files, specific issues]

[2] Orphan Detection ............. PASS | WARN | FAIL
    [details — specific files, age, link count]

[3] Link Health .................. PASS | WARN | FAIL
    [details — specific dangling links, where referenced]

[4] Description Quality .......... PASS | WARN | FAIL
    [details — specific files, title vs description comparison]

[5] Three-Space Boundaries ....... PASS | WARN | FAIL
    [details — specific boundary violations by type]

[6] Processing Throughput ........ PASS | WARN | FAIL
    inbox: N | notes: N | in-progress: N | ratio: N%

[7] Stale Notes .................. PASS | WARN | FAIL
    [N notes older than 30d with <2 incoming links, sorted by priority]

[8] MOC Coherence ................ PASS | WARN | FAIL
    [details — note count per topic map, coverage gaps, bare links]

---

Maintenance Signals:
    [condition-based triggers from table above, if any thresholds met]
    - observations: N pending (threshold: 10) [TRIGGERED | OK]
    - tensions: N pending (threshold: 5) [TRIGGERED | OK]
    - inbox: N items (threshold: 3) [TRIGGERED | OK]
    - sessions: N unprocessed (threshold: 5) [TRIGGERED | OK]

---

Recommended Actions (top 3, ranked by impact):
1. [Most impactful action — specific command + specific file]
2. [Second priority — specific command + specific file]
3. [Third priority — specific command + specific file]
=== END REPORT ===
```

### Report Storage

Write every health report to `ops/health/YYYY-MM-DD-report.md`. If multiple reports are run on the same day, append a counter: `YYYY-MM-DD-report-2.md`.

This creates a health history. Trends across reports reveal systemic patterns that individual reports miss.

---

## Quality Standards

### Be Specific

Every finding MUST name the specific file(s) involved.

Bad: "some notes lack descriptions"
Good: "notes/example-note.md and notes/another-note.md are missing the description field"

Bad: "there are dangling links"
Good: "[[nonexistent-claim]] is referenced in notes/old-note.md (line 14) and notes/related.md (line 22) but no file with that name exists"

### Prioritize by Impact

Not all issues are equal. The recommended actions section ranks by impact:

| Impact Tier | Examples | Why |
|------------|---------|-----|
| Highest | Dangling links, persistent orphans | Broken promises in the graph — readers hit dead ends |
| High | Schema violations, boundary violations | Structural integrity — compounds into larger problems |
| Medium | Description quality, stale notes | Retrieval quality — degraded but not broken |
| Low | {vocabulary.topic_map} size warnings, throughput ratio | Maintenance debt — matters at scale |

### Don't Overwhelm

- Focus on the top 5-10 issues in the recommended actions
- Group related issues (3 notes missing descriptions = 1 finding, not 3)
- For large vaults, cap per-category detail at 10 specific files, then summarize: "...and 15 more"

### Distinguish FAIL from WARN

| Level | Meaning | Action Required |
|-------|---------|----------------|
| FAIL | Structural issue — something is broken | Fix before it compounds |
| WARN | Improvement opportunity — something is suboptimal | Address when convenient |
| PASS | Category is healthy | No action needed |
| INFO | Noteworthy but not actionable | Context for understanding |

**FAIL is reserved for:** Dangling links (broken graph), persistent orphans (> 7 days), severe schema violations (missing frontmatter entirely), critical boundary violations.

**WARN is for everything else** that is suboptimal but not broken.

---

## Edge Cases

### Empty Vault

A vault with 0 notes is not unhealthy — it is new. Report:
```
Notes scanned: 0 | Topic maps: 0 | Inbox items: N
All categories PASS (no notes to check)
Maintenance Signal: inbox has N items — consider /structure or /capture to start building knowledge
```

### Large Vaults (500+ notes)

- Cap per-category file listings at 10, then summarize
- Consider running checks in batches if performance degrades
- Focus recommended actions on highest-impact items

---

## Integration with Other Skills

Health report findings feed into other skills:

| Finding | Feeds Into | How |
|---------|-----------|-----|
| Orphan notes | /connect | Run connect to find connections for orphaned notes |
| Stale notes | /connect | Run connect to revisit old notes against current graph state |
| Description quality issues | /verify or manual rewrite | Fix descriptions to improve retrieval |
| Schema violations | /verify | Run verification to fix specific schema issues |
| Boundary violations | Manual restructuring | Move files to correct space |
| Processing throughput | /structure, /capture, or /pipeline | Process inbox items to improve ratio |
| {vocabulary.topic_map} oversized | Manual split | Split oversized {vocabulary.topic_maps} into sub-{vocabulary.topic_maps} |

**The health-to-action loop:**
```
/health (diagnose) -> specific findings -> specific skill invocation -> /health (verify fix)
```

Health is diagnostic only — it measures state without prescribing changes. The user, or the agent acting with user approval, decides which fixes to apply based on the report's ranked recommendations.
