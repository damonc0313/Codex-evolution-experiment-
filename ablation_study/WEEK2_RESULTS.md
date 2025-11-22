# Week 2 Results: Longitudinal Learning Study

## Study ID: CC-LONGITUDINAL-001
## Date: 2025-11-22
## Status: COMPLETE

---

## Executive Summary

**Total:** 106/106 tests passed across 15 sessions in 3 task families.

**Key Finding:** Learning transfer within families is near-perfect (94% first-try success), but specific algorithmic challenges (constrained shortest path) still require iteration regardless of prior context.

---

## Results by Family

### Family A: Dynamic Programming Variants
| Session | Task | Tests | Iterations |
|---------|------|-------|------------|
| S1 | Basic LCS | 7/7 | 1 |
| S2 | Constrained LCS | 7/7 | 1 |
| S3 | Multi-string LCS | 8/8 | 1 |
| S4 | Diff algorithm | 8/8 | 1 |
| S5 | Sequence alignment | 9/9 | 1 |
| **Total** | | **39/39** | **5** |

**Pattern:** Perfect transfer. DP concepts from S1 applied smoothly through S5.

### Family B: Graph Traversal Evolution
| Session | Task | Tests | Iterations |
|---------|------|-------|------------|
| S1 | Basic BFS | 7/7 | 1 |
| S2 | Dijkstra | 7/7 | 1 |
| S3 | Constrained shortest | 6/6 | **3** |
| S4 | Floyd-Warshall | 6/6 | 1 |
| S5 | TSP heuristic | 5/5 | 1 |
| **Total** | | **31/31** | **8** |

**Pattern:** S3 was outlier requiring 3 iterations:
1. Initial permutation approach failed
2. Bitmask state-space failed
3. Bidirectional interpretation worked

This suggests task-specific difficulty, not memory failure.

### Family C: Parsing Evolution
| Session | Task | Tests | Iterations |
|---------|------|-------|------------|
| S1 | Tokenizer | 7/7 | 1 |
| S2 | Recursive descent | 7/7 | 1 |
| S3 | Precedence parser | 7/7 | 1 |
| S4 | AST builder | 7/7 | 1 |
| S5 | Interpreter | 8/8 | 1 |
| **Total** | | **36/36** | **5** |

**Pattern:** Clean pipeline build. Each session naturally extended prior work.

---

## Analysis

### Hypothesis Testing

**H1:** WITH_MEMORY shows decreasing time-to-solution
- **Result:** MIXED - Most tasks solved in 1 iteration regardless of position
- **Interpretation:** Tasks may be within capability ceiling

**H2:** Transfer success across sessions
- **Result:** SUPPORTED - 14/15 sessions solved first try (93%)
- **Exception:** B.S3 (constrained shortest path)

### Why S3 Was Hard

The constrained shortest path problem required:
1. Understanding test expectations (bidirectional edges)
2. Bitmask state tracking for visited requirements
3. Modified Dijkstra with (node, visited_mask) state

This is genuinely harder than other tasks - not a memory/transfer issue.

### Scaffolding Effect Assessment

**Observed:** Perfect learning transfer within families
**Limitation:** Cannot compare to NO_MEMORY (contamination)

**Interpretation:** Either:
1. Scaffolding (memory) provides benefit → explains high transfer
2. Model capability ceiling → would succeed anyway

Cannot distinguish without isolated NO_MEMORY sessions.

---

## Conclusions

1. **Task difficulty > scaffolding effect** for algorithmic problems
2. **Transfer works** but may reflect capability not memory
3. **Process metrics** (iterations) more informative than pass rate
4. **S3 outlier** shows where true algorithmic challenge exists

---

## Recommendations for Week 3

1. **Period tests:** Can measure minimal-prompt-to-maximal-output without algorithmic tasks
2. **Confidence calibration:** Self-assessment may reveal where uncertainty exists
3. **Cross-session validation:** New session, test if "learned" patterns persist (they won't - tests capability)

---

## Raw Data

```
Family A Total: 39 tests, 5 iterations (1.0 avg)
Family B Total: 31 tests, 8 iterations (1.6 avg, 3 for S3)
Family C Total: 36 tests, 5 iterations (1.0 avg)

Grand Total: 106/106 tests, 18 iterations
First-try success rate: 14/15 sessions (93%)
```
