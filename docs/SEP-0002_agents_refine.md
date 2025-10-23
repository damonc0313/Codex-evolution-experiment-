---
artifact_type: sep_proposal
document: SEP-0002
title: "Agents Protocol Validator Hardening"
status: draft
created: 2025-10-23T01:05:00Z
digest: 1ecb7609fde70b59
---

# Proposal
Upgrade `tools/validate_kernel.py` to fail the build when `docs/agents.md` is missing or lacks required front-matter fields so the manifesto becomes a mandatory guardrail.

# Justification
- Reflection telemetry showed the manifesto digest remained stable across cycles, demonstrating readiness for strict enforcement.
- Regression seeds and KPI snapshots run cleanly with the manifesto present, indicating low risk of false positives.
- Mentor feedback loop now depends on manifesto guidance; a missing doctrine would degrade co-evolution quality.

# Impact
- CI will stop merges if the manifesto is removed or corrupted, preserving doctrine integrity.
- Runtime components can rely on manifest presence for mode selection without fallback heuristics.
- Developers must update the digest intentionally whenever the manifesto changes.

# Rollback Strategy
- Revert the validator change or introduce a temporary configuration flag if legitimate edits require relaxed gating.
- Maintain a branch with the WARN behavior for emergency hotfixes if needed.

# Acceptance Criteria
1. Validator exits with code 1 when `docs/agents.md` is absent or lacks `artifact_type`, `version`, or `digest` fields.
2. CI reflects the stricter behavior by failing on manifesto regressions.
3. Ω-cycle runner logs remain unchanged except for improved assurance in guardrail reporting.

# Open Questions
- Should KPI thresholds move from documentation into executable checks?
- How should mentor feedback incorporate validator context when failures occur?
