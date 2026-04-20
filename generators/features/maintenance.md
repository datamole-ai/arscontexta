# Feature: Maintenance

## Context File Block

```markdown
## Maintenance — Keeping the Graph Healthy

A knowledge graph degrades without maintenance. Notes written last month don't know about notes written today. Links break when titles change. {DOMAIN:topic maps} grow stale as topics evolve. Maintenance is not optional — it's what keeps the system useful.

### Health Check Categories

Run these checks when conditions warrant — orphans detected, links broken, schema violations accumulated:

**1. Orphan Detection**
{DOMAIN:Notes} with no incoming links are invisible to traversal. Find them:
```bash
# Find notes not linked from anywhere
find {DOMAIN:note_collection}/ -name "*.md" -type f | while read f; do
  title=$(basename "$f" .md)
  rg -q "\[\[$title\]\]" {DOMAIN:note_collection}/ || echo "Orphan: $f"
done
```
Every orphan is either a gap (needs connections) or stale (needs archiving).

**2. Dangling Links**
Wiki links pointing to non-existent {DOMAIN:notes} create confusion:
```bash
# Find [[links]] to files that don't exist
rg -o '\[\[([^\]]+)\]\]' {DOMAIN:note_collection}/ -r '$1' --no-filename | sort -u | while read title; do
  find . -name "$title.md" -not -path "./.git/*" | grep -q . || echo "Dangling: [[$title]]"
done
```
Either create the missing {DOMAIN:note} or fix the link.

**3. Schema Validation**
Check that {DOMAIN:notes} have required YAML fields:
```bash
find {DOMAIN:note_collection}/ -name "*.md" -type f -exec rg -L '^description:' {} +    # missing descriptions
```
Missing descriptions mean the {DOMAIN:note} can't be filtered during search.

**4. {DOMAIN:Topic Map} Coherence**
{DOMAIN:Topic maps} should accurately reflect the notes they organize:
- Do all listed {DOMAIN:notes} still exist?
- Are there {DOMAIN:notes} on this topic NOT listed in the {DOMAIN:topic map}?
- Has the topic grown large enough to warrant splitting?

**5. Stale Content**
{DOMAIN:Notes} that haven't been touched in a long time may contain outdated claims. Check modification dates and review oldest notes first.

### Reweaving — The Backward Pass

New {DOMAIN:notes} create connections going forward. But older {DOMAIN:notes} don't automatically know about newer ones. Reweaving is the practice of revisiting old {DOMAIN:notes} and asking: "If I wrote this today, what would be different?"

**Reweaving can:**
- Add connections to newer {DOMAIN:notes} that didn't exist when the original was written
- Sharpen a claim that's become clearer with more context
- Split a {DOMAIN:note} that actually contains multiple ideas
- Challenge a claim that new evidence contradicts
- Rewrite prose to incorporate new links inline

**When to reweave:**
- After creating a batch of new {DOMAIN:notes} — check what older {DOMAIN:notes} should link to them
- When a health check flags sparse {DOMAIN:notes} with few connections
- When {DOMAIN:notes} have not been touched since N new notes were added to the graph
- When a {DOMAIN:note} feels disconnected from the rest of the graph

### Condition-Based Maintenance

Maintenance triggers are condition-based, not time-based. Time-based triggers (weekly, monthly, quarterly) assume uniform activity — a vault that scales fast would overwhelm a monthly check, while a vault used rarely would run empty checks on schedule. Condition-based triggers respond to actual state, firing exactly when the system needs attention.

| Condition | Threshold | Action When True |
|-----------|-----------|-----------------|
| Orphan {DOMAIN:notes} | Any detected | Surface for connection-finding |
| Dangling links | Any detected | Surface for resolution |
| {DOMAIN:Topic map} size | >40 {DOMAIN:notes} | Suggest sub-{DOMAIN:topic map} split |
| Pending observations | >=10 | Suggest /{DOMAIN:rethink} |
| Pending tensions | >=5 | Suggest /{DOMAIN:rethink} |
| Inbox pressure | Items older than 3 days | Suggest processing |
| Stale pipeline batch | >2 sessions without progress | Surface as blocked |
| Schema violations | Any detected | Surface for correction |

These conditions are evaluated by /health on demand. When a condition fires, /health reports it with specific files and ranked recommended actions — not a calendar reminder.

### Session Maintenance Checklist

Before ending a work session:
- [ ] New {DOMAIN:notes} are linked from at least one {DOMAIN:topic map}
- [ ] Wiki links in new {DOMAIN:notes} point to real files
- [ ] Descriptions add information beyond the title
- [ ] Changes are committed (automatic inside `/pipeline`; manual otherwise)

### The Maintenance Mindset

Maintenance is not cleanup — it's cultivation. Each pass through old {DOMAIN:notes} is an opportunity to deepen the graph. Reweaving discovers connections that weren't visible when the {DOMAIN:notes} were first written. Health checks reveal structural gaps that point toward missing insights.

The graph doesn't just get maintained. It gets better.

### Diagnostic Reconciliation via /health

Maintenance is diagnostic, not a separate queue of work. /health evaluates all conditions on demand and reports fired conditions with specific files and ranked actions.

The reconciliation pattern:
1. **Declare conditions** — the system defines what "healthy" looks like (desired state) via thresholds in `ops/config.yaml`
2. **Measure actual state** — /health compares reality against each condition across its 8 diagnostic categories plus cross-cutting maintenance signals
3. **Report findings** — /health produces a PASS/WARN/FAIL report with specific files, persisted to `ops/health/YYYY-MM-DD-report.md`
4. **Self-healing** — the user fixes the underlying issue; the next /health run confirms resolution

This is idempotent: running /health any number of times produces the same diagnostic report for unchanged state. There is no maintenance queue to keep clean — the state of the vault IS the state.

The key insight: you don't manage maintenance task status manually. Fix the underlying problem and the next /health run shows it resolved.

### Invariant-Based Diagnostics

/health checks invariants that together define a healthy system:

| Invariant | What It Checks |
|-----------|---------------|
| Inbox pressure | Is {DOMAIN:inbox/} accumulating unprocessed material? |
| Orphan {DOMAIN:notes} | Are there {DOMAIN:notes} with no incoming links? |
| Dangling links | Do wiki links point to non-existent {DOMAIN:notes}? |
| Observation accumulation | Have pending observations exceeded the threshold (10+)? |
| Tension accumulation | Have pending tensions exceeded the threshold (5+)? |
| {DOMAIN:Topic map} size | Has any {DOMAIN:topic map} grown beyond its healthy range? |
| Stale batches | Are there processing batches that have been sitting unfinished? |
| Schema compliance | Do all {DOMAIN:notes} pass schema validation? |
| Three-space boundaries | Is content leaking across self/, {DOMAIN:note_collection}/, and ops/? |

Each invariant is self-healing: fix the underlying issue (process the inbox, connect the orphan, resolve the tension) and the next /health run reports PASS.

### Impact-Ranked Recommendations

/health closes with "Recommended Actions (top 3, ranked by impact)" — concrete commands for specific files. Ranking follows impact tiers:

| Impact Tier | Examples | Why |
|------------|---------|-----|
| Highest | Dangling links, persistent orphans | Broken promises in the graph — readers hit dead ends |
| High | Schema violations, boundary violations | Structural integrity — compounds into larger problems |
| Medium | Description quality, stale notes | Retrieval quality — degraded but not broken |
| Low | {DOMAIN:Topic map} size warnings, throughput ratio | Maintenance debt — matters at scale |

### Integration with /{DOMAIN:rethink}

When /health detects signal accumulation (10+ pending observations OR 5+ pending tensions), it recommends /{DOMAIN:rethink}. This closes the loop: maintenance detects that the system has accumulated enough operational evidence to warrant a meta-cognitive pass. You review the evidence, promote insights, implement changes, and the system evolves. Maintenance feeds evolution, evolution improves maintenance.
```

## Dependencies
Requires: wiki-links (link health checks depend on wiki link infrastructure), mocs (MOC coherence checks require MOC awareness)
