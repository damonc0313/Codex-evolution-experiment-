---
artifact_type: sep_preview
id: SEP-0004
title: Continuous Operation Protocol
status: draft
digest: bac265842793d60f
created: 2025-10-23
---

# Summary
This preview outlines the work needed to promote Kael continuous-operation
metrics into enforceable guardrails. It captures validator updates, KPI targets,
and tests required to graduate from advisory warnings to hard failures.

# Motivation
- Sustain autonomous cycles without human prompts while preventing drift.
- Ensure lineage schema upgrades measurably increase building ratio and task
  queue depth.
- Instrument cascade probability as a first-class KPI for saturation risks.

# Proposed Changes
1. **Validator Hardening** — Add mandatory checks that docs/LEDGER_KAEL_2025-10-23.md
   exists, has a stamped digest, and continuous_operation thresholds are met.
2. **KPI Enforcement** — Compute cascade_probability, building_ratio, and
   task_multiplication during validation; fail if below policy minima.
3. **Self-Query Assertions** — Extend autonomous query harness to document how
   each new directive improves at least one KPI above baseline.

# Tests
- `python tools/validate_kernel.py` fails when manifesto or Kael ledger is
  missing or malformed.
- Regression harness loads `tests/kael_hypotheses.json` ensuring formulas match
  loop policy values.
- Smoke swarm verifies regression_pass_rate ≥ 0.85 and continuity_ratio ≥ 0.90
  after applying SEP-0004 patches.

# KPIs
| Metric | Target | Source |
| ------ | ------ | ------ |
| building_ratio | ≥ 0.55 | `tools/ledger_metrics.measure_building_ratio` |
| task_multiplication | ≥ 1.6 | `tools/ledger_metrics.estimate_task_multiplication` |
| cascade_probability | ≥ 1.0 | `tools/ledger_metrics.compute_cascade_probability` |
| novelty_rate | ≥ 0.35 | self-query encoder |

# Risks & Mitigations
- **Risk:** Validator hardening may block iteration if metrics temporarily dip.
  **Mitigation:** Stage rollout with feature flag and fallback WARN level.
- **Risk:** Building ratio heuristics may misclassify artifacts.
  **Mitigation:** Provide manual override threshold in loop policy for debugging.

# Rollback Plan
- Revert validator gating to WARN, restore previous loop_policy values, and
  remove SEP-0004 feature flag from runtime state.
