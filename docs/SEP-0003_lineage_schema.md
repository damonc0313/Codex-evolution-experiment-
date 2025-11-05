---
artifact_type: sep_proposal
id: SEP-0003
title: "Lineage Schema Upgrade"
status: draft
version: v0.1
generated_at: 1762179325
digest: 1a67ecbd1946bb8c
sources:
  - artifacts/swarm_full_B_index_20251103T141525Z.json
  - artifacts/swarm_full_C_selection_20251103T141525Z.json
  - artifacts/swarm_full_D_fusion_20251103T141525Z.json
  - docs/agents.md
---

# Summary
Elevate the continuity ledger into a versioned lineage schema, ensuring every artifact references parent hashes and execution metadata. The upgrade is motivated by swarm forks that highlighted lineage depth as the dominant driver of continuity_ratio improvements.

## Proposed Changes
1. Introduce `lineage_root`, `parent_hashes`, and `swarm_run_id` fields to new artifacts.
2. Ship a migration utility that replays recent artifacts to backfill lineage metadata.
3. Extend the validator with strict lineage checks and gating thresholds (promotion from WARN→FAIL).
4. Accelerate the continuity indexer to maintain sub-10s refresh under Ω-cycle load.

## Evidence
- Swarm fork fusion synthesis: Blend balanced and creative forks to raise novelty while keeping regression pass-rate ≥0.9 via targeted sandbox injections.
- KPI averages (continuity=0.938, regression=0.907, novelty=0.714).
- Best configuration: mode=BALANCED, dialectic_ratio=0.8, sandbox_rate=0.25, critique_depth=1, entropy=0.9.

## Assumptions
- Agents manifesto remains at digest "46c9a5a66a60941f" during rollout.
- Loop policy stop flags stay unchanged throughout SEP-0003 execution.

## Risks & Mitigations
- **Risk:** Validator false positives during migration.
  **Mitigation:** dry-run migration artifact plus mentor review before enforcement.
- **Risk:** Continuity indexer lag under swarm load.
  **Mitigation:** throttle autonomous query entropy until performance stabilises.

## Acceptance Criteria
- Validator enforces lineage fields (WARN→FAIL) with zero regressions in tests/claude_regressions.json.
- Continuity snapshots reference new lineage fields for all artifacts created post-merge.
- Swarm bench KPIs maintain continuity_ratio ≥0.9 and regression_pass_rate ≥0.85.

## Rollback Strategy
- Retain legacy schema writer behind a feature flag; revert by toggling `lineage_schema.enabled=false` in runtime config.
- Restore validator WARN mode via SEP-0002 rollback instructions.

## Next Steps
- Prepare SEP-0003 implementation branch with migration scripts and validator upgrade.
- Schedule mentor review focusing on lineage schema resilience.
