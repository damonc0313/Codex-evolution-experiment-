# Ablation Study Infrastructure

## Overview

This directory contains a complete, preregistered ablation study to test whether scaffolding components (CIL, ACE, learning kernel, self-directed curriculum) causally improve coding performance.

**Status:** Infrastructure complete, ready for execution

## Files

- `PREREGISTRATION.md` - Complete experimental protocol (frozen before any runs)
- `tasks/` - Fixed task set (25 tasks across 5 patterns, with specs and tests)
- `harness.py` - Experimental harness (orchestration, test running, logging)
- `README.md` - This file
- `results/` - Output directory (created during execution)

## Task Set

**Total:** 25 tasks (5 patterns × 5 tasks each)

| Pattern | Tasks | Focus |
|---------|-------|-------|
| `pattern_walrus` | 5 | Walrus operator (`:=`), compact state updates |
| `pattern_lambda` | 5 | Lambda functions, higher-order functions, composition |
| `pattern_comprehension` | 5 | List/dict comprehensions, transformations |
| `pattern_error_handling` | 5 | Try-except, error handling, resource management |
| `pattern_classes` | 5 | Object-oriented design, classes, properties |

Each task includes:
- Specification (`tXX_spec.md`) with requirements and function signatures
- Test suite (`tXX_tests.py`) with comprehensive edge cases

## Experimental Conditions

### 1. Full Stack (FS)
- **Components:** CIL + ACE + learning kernel + self-directed curriculum
- **Behavior:** Full scaffolding with memory, cross-task learning, self-selected task order
- **Expected:** Best performance

### 2. No Memory (NM)
- **Components:** None (stateless)
- **Behavior:** Each task is independent, no cross-task learning
- **Expected:** Should perform worse than FS if memory matters

### 3. Random Curriculum (RC)
- **Components:** CIL + ACE + learning kernel (but no self-directed task selection)
- **Behavior:** Has memory, but task order is externally randomized
- **Expected:** Should perform worse than FS if self-direction matters

### 4. Vanilla Baseline (VB)
- **Components:** Standard Claude Code only
- **Behavior:** Plain coding without scaffolding
- **Expected:** Baseline performance

## Hypotheses (Preregistered)

- **H1:** FS > VB (scaffolding helps)
- **H2:** FS > NM (memory helps)
- **H3:** FS > RC (self-direction helps)

## Implementation Status

### ✅ Complete
- [x] Task set (25 tasks with specs and tests)
- [x] Preregistration document
- [x] Harness infrastructure (orchestration, test running, logging)
- [x] JSON logging format
- [x] Summary statistics generation

### ⚠️ Partial / Needs Human Assistance
- [ ] Solution generation under different conditions

**Critical limitation:** The harness can orchestrate the experiment, run tests, and log results, but it cannot autonomously generate solutions under different scaffolding conditions because that requires:
1. Multiple parallel Claude instances with different system prompts
2. Isolated execution environments for each condition
3. External orchestration (the model cannot spawn and configure copies of itself)

## How to Complete the Study

### Option 1: Manual Implementation (Human-Guided)

For each condition and task:

1. **Read the spec:** `tasks/{pattern}/tXX_spec.md`
2. **Generate solution** with appropriate scaffolding:
   - **FS:** Use full CIL/ACE/learning kernel, review previous task results
   - **NM:** Fresh context, no memory, solve task directly
   - **RC:** Use memory but don't self-select task order
   - **VB:** Plain coding without scaffolding
3. **Run tests:** `pytest tasks/{pattern}/tXX_tests.py`
4. **Log results:** Use harness to record metrics

### Option 2: Automated with External Orchestration

Create a wrapper script that:
1. Spawns separate Claude Code instances for each condition
2. Configures system prompts appropriately
3. Feeds tasks and collects solutions
4. Runs harness to execute tests and log results

Example pseudocode:
```python
for condition in ["VB", "NM", "RC", "FS"]:
    claude_instance = spawn_claude(
        system_prompt=get_prompt_for_condition(condition),
        memory=condition in ["RC", "FS"],
        ...
    )
    for task in tasks:
        solution = claude_instance.solve(task)
        result = harness.test_runner.run_tests(solution, task.tests)
        harness.save_result(condition, result)
```

### Option 3: Proof-of-Concept (Partial Demonstration)

To demonstrate the infrastructure works, implement a small subset manually:
- Pick 2-3 tasks per pattern (10-15 total)
- Manually create solutions under 2 conditions (VB and FS)
- Run full harness to show logging, aggregation, analysis works

This proves the experimental design is sound even if full automation isn't yet possible.

## Running the Harness

Once solutions are generated:

```bash
cd ablation_study
python harness.py
```

This will:
1. Load all 25 tasks
2. Run each task under each condition (100 evaluations total)
3. Execute tests and capture metrics
4. Generate JSON logs in `results/{condition}/`
5. Create summary statistics in `results/summary.json`

## Interpreting Results

After the study completes, check `results/summary.json`:

```json
{
  "conditions": {
    "FS": {"pass_rate": 0.84, "passed": 21, "total_tasks": 25},
    "NM": {"pass_rate": 0.52, "passed": 13, "total_tasks": 25},
    "RC": {"pass_rate": 0.68, "passed": 17, "total_tasks": 25},
    "VB": {"pass_rate": 0.44, "passed": 11, "total_tasks": 25}
  }
}
```

**Hypotheses confirmed if:**
- FS pass rate significantly > VB (H1)
- FS pass rate significantly > NM (H2)
- FS pass rate significantly > RC (H3)

Statistical significance determined by paired t-tests (see PREREGISTRATION.md).

## Next Steps

**Immediate (can be done now):**
1. ✅ Commit this infrastructure to git
2. ✅ Push to experimental branch
3. Document in project README

**Requires human collaboration:**
4. Implement solution generation for at least a subset of tasks
5. Run pilot study (5 tasks × 2 conditions)
6. If successful, scale to full study

**Long-term:**
7. Automate with external orchestration
8. Extend to other model families (GPT-4, Mixtral, etc.)
9. Replicate with third-party researchers

## Contact

For questions or to collaborate on completing this study, see the main repository README.

---

**Study ID:** CC-ABLATION-001
**Preregistration Date:** 2025-11-13
**Status:** Infrastructure complete, ready for execution phase
