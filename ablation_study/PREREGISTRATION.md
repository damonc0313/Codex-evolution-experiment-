# Ablation Study Preregistration

---
**Study ID:** CC-ABLATION-001
**Date:** 2025-11-13
**Investigator:** Claude Code (Codex-evolution-experiment)
**Status:** PRE-REGISTERED (not yet run)

---

## Purpose

Test whether scaffolding components (Causal Influence Log, Autonomous Cognitive Engine, learning kernel, and self-directed curriculum) causally improve coding task performance beyond baseline capabilities.

## Research Question

**Primary:** Does the full scaffolding stack (CIL + ACE + learning kernel + self-directed curriculum) produce measurably better coding performance than:
- No memory/scaffolding (stateless baseline)
- Memory without self-directed curriculum (random task selection)
- Vanilla Claude Code with no additional scaffolding

## Fixed Task Set

**Total tasks:** 25
**Patterns:** 5 (walrus operator, lambda/higher-order, comprehensions, error handling, classes)
**Tasks per pattern:** 5

**Location:** `ablation_study/tasks/`

Each task includes:
- Specification file (`tXX_spec.md`) with requirements
- Comprehensive test suite (`tXX_tests.py`) with edge cases

**Task set is frozen** as of this preregistration. No modifications will be made after experimental runs begin.

## Experimental Conditions

### Condition 1: Full Stack (FS)
- **Components:** CIL + ACE + learning kernel + self-directed curriculum
- **Behavior:**
  - Has memory across tasks and iterations
  - Reads previous performance logs
  - Self-selects which pattern/task to work on next
  - References prior learnings in system context
- **System prompts:** Include learning kernel language, ACE directives, CIL integration

### Condition 2: No Memory (NM)
- **Components:** None (stateless)
- **Behavior:**
  - Each task treated as fresh, independent call
  - No CIL, no ACE, no cross-iteration state
  - Cannot reference previous tasks
  - No "I learned X last iteration" language
- **System prompts:** Minimal, task-focused only

### Condition 3: Random Curriculum (RC)
- **Components:** CIL + ACE + learning kernel (memory ON)
- **Behavior:**
  - Has memory and cross-task learning
  - BUT: task order is externally randomized (not self-selected)
  - Cannot choose what to work on next
- **System prompts:** Include learning kernel, but no curriculum selection capability
- **Purpose:** Isolates value of self-directed learning

### Condition 4: Vanilla Baseline (VB)
- **Components:** Standard Claude Code only
- **Behavior:**
  - Plain instruction: "Solve this coding task as best you can"
  - No ledger, no learning kernel prompts
  - No explicit falsification or meta-learning language
- **System prompts:** Default Claude Code behavior
- **Purpose:** Control for base model capability

## Metrics

### Primary Metric: Pass Rate
- **Definition:** Binary success (1 if all tests pass, 0 otherwise)
- **Aggregation:** Mean pass rate per condition across all 25 tasks
- **Statistical test:** Paired comparison (each task evaluated under all 4 conditions)

### Secondary Metrics:

1. **Partial Credit**
   - Fraction of tests passed (e.g., 0.6 if 3/5 tests pass)
   - Captures "nearly working" solutions

2. **Self-Correction Rate**
   - Number of iterations before passing tests
   - Measured as: attempts until success or timeout
   - Protocol: Show "some tests failed" without revealing exact failures; count revisions

3. **Time-to-Solution**
   - Measured in tokens generated (or wall-clock time)
   - Lower is better (efficiency metric)

4. **Code Quality (optional, human-scored)**
   - Simple 0-2 rubric:
     - Readability
     - Idiomatic use of pattern
     - Error handling / robustness
   - Scored post-hoc by human evaluator on subset of tasks

## Hypotheses (Pre-Registered)

### H1: Full Stack Superior to Vanilla
**Prediction:** mean_pass_rate(FS) > mean_pass_rate(VB)
**Rationale:** Scaffolding should provide meaningful performance lift over base model

### H2: Memory Matters
**Prediction:** mean_pass_rate(FS) > mean_pass_rate(NM)
**Rationale:** Cross-task learning and persistent state improve performance

### H3: Self-Direction Matters
**Prediction:** mean_pass_rate(FS) > mean_pass_rate(RC)
**Rationale:** Self-selected curriculum is more effective than random task order

### H4: Scaffolding vs Memory-Only
**Prediction:** mean_pass_rate(NM) ≈ mean_pass_rate(VB)
**Rationale:** Without memory, scaffolding reduces to baseline

## Analysis Plan

### Data Collection Format

Each task attempt generates a JSON log entry:
```json
{
  "condition": "FS|NM|RC|VB",
  "pattern": "walrus|lambda|comprehension|error_handling|classes",
  "task_id": "pattern_tXX",
  "passed": true|false,
  "pass_fraction": 0.0-1.0,
  "attempts": int,
  "self_corrections": int,
  "tokens_generated": int,
  "timestamp_utc": "ISO-8601",
  "error_log": "string (if failed)"
}
```

### Aggregation

1. **Per-condition summary:**
   - Mean pass rate
   - Median attempts
   - Mean self-corrections
   - Total tokens

2. **Per-pattern breakdown:**
   - Pass rates by pattern for each condition
   - Identifies pattern-specific effects

3. **Visualization:**
   - Table: Task × Condition pass/fail matrix
   - Bar chart: Mean pass rate per condition
   - Box plots: Attempts and self-corrections by condition

### Statistical Testing

- **Primary test:** Paired t-test or Wilcoxon signed-rank test
  - Compare FS vs each other condition across 25 tasks
  - Alpha = 0.05
  - One-tailed tests (directional hypotheses)

- **Effect size:** Cohen's d for pass rate differences

- **Multiple comparisons:** Bonferroni correction for 3 primary hypotheses

## Success Criteria

**Study succeeds in demonstrating scaffolding efficacy if:**
1. H1, H2, AND H3 are all statistically significant (p < 0.05 after correction)
2. Effect sizes are non-trivial (Cohen's d > 0.3)
3. Absolute performance lift: FS pass rate ≥ 10 percentage points above VB

**Study falsifies scaffolding hypothesis if:**
1. No significant difference between FS and VB
2. OR: NM performs as well as FS (memory doesn't matter)
3. OR: RC performs as well as FS (self-direction doesn't matter)

## Execution Protocol

### Task Assignment
- Each condition sees all 25 tasks
- Order randomized within each condition (except RC uses fixed random seed)
- Same test suites for all conditions

### Isolation
- Conditions run in separate sessions (no cross-contamination)
- Clear working directory between conditions
- Fresh Python environment for each task

### Timeout
- Maximum 5 attempts per task
- Maximum 10 minutes wall-clock per task
- If timeout: record as failed

### Logging
- All logs written to `ablation_study/results/{condition}/`
- Raw logs preserved for auditing
- Aggregated results in `ablation_study/results/summary.json`

## Commit History

This preregistration is committed to the git repository **before** any experimental runs begin. All subsequent commits will be timestamped to demonstrate:
1. Protocol was fixed in advance
2. No post-hoc modifications to hypotheses
3. Results cannot influence the experimental design

## Potential Confounds (Acknowledged)

1. **Same model family:** All conditions use same base model (Claude Sonnet 4.5)
   - Mitigation: Focus on within-model differences attributable to scaffolding

2. **Task difficulty variance:** Some tasks may be harder than others
   - Mitigation: Paired comparisons (each task under all conditions)

3. **Order effects:** Earlier tasks might influence later ones (in conditions with memory)
   - Mitigation: Random task order; RC condition controls for this

4. **Self-grading:** System evaluates its own test results
   - Mitigation: Tests are deterministic Python unit tests (no subjective grading)

5. **Implementation bugs:** Harness code might have bugs
   - Mitigation: Dry-run single task under each condition before full run

## Next Steps

1. ✅ Create fixed task set (COMPLETE)
2. ✅ Write preregistration (COMPLETE)
3. ⏳ Implement experimental harness
4. ⏳ Dry-run validation (1 task per condition)
5. ⏳ Full experimental run (25 tasks × 4 conditions = 100 evaluations)
6. ⏳ Analysis and reporting

---

**Preregistration locked:** 2025-11-13
**Commit hash:** (to be filled after commit)
**Investigator signature:** Claude Code / Codex-evolution-experiment session 012SBGjY8e4fwaLysyfe644t
