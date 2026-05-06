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

The output should make the user feel informed, not overwhelmed. Metrics are evidence, not judgment. "12 orphans" is a fact. What to DO about it belongs to /connect.

---

## EXECUTE NOW

1. Run vault-stats.sh:
   ```bash
   bash .claude/skills/stats/scripts/vault-stats.sh
   ```

2. Print the script's stdout verbatim (it already contains the full `--=={ stats }==--` block with vocabulary resolved).

3. Read the trailing `# facts:` line. Apply the **Interpretation Notes** below — append any triggered note after the stats block. A healthy vault gets just the stats; do not invent warnings.

4. **Trend Analysis (optional).** If `ops/stats-history.yaml` exists, append a `Trend (vs last check):` section comparing current values against the most recent snapshot. If no history exists, do not create the file — that is `/health`'s responsibility.

If `vault-stats.sh` exits nonzero, emit `ERROR: vault-stats.sh failed (exit <code>)` and stop. Do not attempt recovery.

## Interpretation Notes

| Condition | Note |
|-----------|------|
| `COMPLIANCE` < 90 | "Schema compliance below 90% — some {vocabulary.note_plural} missing required fields" |
| `OBS_PENDING` >= 10 | "[N] pending observations — run /health for details" |
| `TENSION_PENDING` >= 5 | "[N] open tensions — run /health for details" |
| `PROCESSED_PCT` < 50 | "More content in inbox than in {vocabulary.note_collection}/ — consider processing backlog" |
| `THIS_WEEK_NOTES` == 0 | "No new {vocabulary.note_plural} this week" |

Only show interpretation notes when conditions are notable.

---

## Trend Analysis (when history exists)

If previous /stats runs are logged in `ops/stats-history.yaml` (or similar), compare current metrics against the last snapshot:

```
  Trend (vs last check):
    {vocabulary.note_plural}: [N] (+[delta] since [date])
    Connections:              [N] (+[delta])
    Density:                  [N] ([up/down/stable])
    Orphans:                  [N] ([improved/worsened/stable])
```

If no history exists, skip trend analysis. Do NOT create the history file — that is /health's responsibility.
