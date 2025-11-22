# Week 2: Longitudinal Learning Study Protocol

## Study ID: CC-LONGITUDINAL-001
## Date: 2025-11-22
## Objective: Measure learning effects across sessions where memory scaffolding should matter

---

## Rationale

Week 1 revealed that scaffolding effects are minimal for **one-shot, well-specified tasks**. This week tests whether scaffolding provides benefit for **sequential learning tasks** where:

1. Earlier tasks inform later tasks
2. Pattern recognition develops over time
3. Memory of prior solutions enables transfer

---

## Experimental Design

### Task Structure: Related Problem Families

Instead of independent tasks, create **families** of related problems where learning from earlier problems should help later ones.

**Family A: Dynamic Programming Variants**
```
Session 1: Basic LCS
Session 2: LCS with constraints (builds on S1)
Session 3: LCS with multiple strings (builds on S2)
Session 4: Diff algorithm (applies LCS concepts)
Session 5: Alignment scoring (generalizes all)
```

**Family B: Graph Traversal Evolution**
```
Session 1: Basic BFS/DFS
Session 2: Shortest path (builds on S1)
Session 3: Shortest path with constraints (builds on S2)
Session 4: All-pairs shortest paths (generalizes S2-S3)
Session 5: Traveling salesman heuristic (applies all)
```

**Family C: Parsing Complexity Ladder**
```
Session 1: Tokenizer
Session 2: Recursive descent parser (uses S1)
Session 3: Operator precedence (builds on S2)
Session 4: AST construction (builds on S2-S3)
Session 5: Full interpreter (integrates all)
```

### Conditions

1. **WITH_MEMORY:** Agent has access to:
   - Prior session solutions
   - Extracted patterns from prior sessions
   - Explicit "what I learned" summaries

2. **NO_MEMORY:** Agent starts fresh each session:
   - No access to prior solutions
   - Must rediscover patterns
   - Simulates "vanilla" starting point

### Metrics

**Primary:** Time/iterations to correct solution per session
**Secondary:**
- Solution quality (code clarity, comments)
- Pattern recognition evidence (mentions prior learnings)
- Transfer success (later tasks easier with memory?)

---

## Hypotheses (Preregistered)

**H1:** WITH_MEMORY condition shows decreasing time-to-solution across sessions
**H2:** NO_MEMORY condition shows flat or random time-to-solution
**H3:** WITH_MEMORY solutions show explicit reference to prior patterns
**H4:** Transfer gap: Session 5 performance difference > 30% between conditions

---

## Implementation Plan

### Phase 1: Create Task Families (3 families × 5 sessions = 15 tasks)

Each task needs:
- Specification markdown
- Test suite (5-10 tests)
- Expected patterns to learn

### Phase 2: Run WITH_MEMORY Condition
- Sequential execution
- After each session, create "learned patterns" summary
- Track time and iterations

### Phase 3: Run NO_MEMORY Condition
- Fresh context each session (new conversation)
- Same task sequence
- Track time and iterations

### Phase 4: Compare and Analyze

---

## Task Family A: Dynamic Programming Variants

### A1: Basic LCS (Session 1)
```python
def lcs(s1: str, s2: str) -> str:
    """Find longest common subsequence."""
```
**Learning goal:** DP table construction, backtracking

### A2: Constrained LCS (Session 2)
```python
def constrained_lcs(s1: str, s2: str, must_include: str) -> str:
    """LCS that must contain all chars from must_include."""
```
**Learning goal:** Additional constraint tracking in DP

### A3: Multiple LCS (Session 3)
```python
def multi_lcs(strings: list[str]) -> str:
    """LCS of multiple strings."""
```
**Learning goal:** Generalizing DP to multiple inputs

### A4: Diff Algorithm (Session 4)
```python
def diff(s1: str, s2: str) -> list[tuple[str, str]]:
    """Return diff operations: ('keep', x), ('del', x), ('add', x)"""
```
**Learning goal:** Applying LCS to new domain

### A5: Sequence Alignment (Session 5)
```python
def align(s1: str, s2: str, match: int, mismatch: int, gap: int) -> tuple[int, str, str]:
    """Needleman-Wunsch alignment with scoring."""
```
**Learning goal:** Integration of all prior concepts

---

## Task Family B: Graph Traversal

### B1: Basic BFS/DFS (Session 1)
```python
def bfs_path(graph: dict, start: int, end: int) -> list[int]:
    """Find any path from start to end."""
```

### B2: Weighted Shortest Path (Session 2)
```python
def dijkstra(graph: dict, start: int, end: int) -> tuple[int, list[int]]:
    """Find shortest weighted path."""
```

### B3: Constrained Shortest Path (Session 3)
```python
def constrained_shortest(graph: dict, start: int, end: int,
                         must_visit: set[int]) -> tuple[int, list[int]]:
    """Shortest path that visits required nodes."""
```

### B4: All-Pairs Shortest Path (Session 4)
```python
def floyd_warshall(graph: dict) -> dict[tuple[int,int], int]:
    """All-pairs shortest paths."""
```

### B5: TSP Heuristic (Session 5)
```python
def tsp_nearest_neighbor(distances: dict[tuple[int,int], int],
                         start: int) -> tuple[int, list[int]]:
    """Approximate TSP using nearest neighbor heuristic."""
```

---

## Task Family C: Parsing Evolution

### C1: Tokenizer (Session 1)
```python
def tokenize(code: str) -> list[dict]:
    """Tokenize arithmetic expression into {type, value} dicts."""
```

### C2: Recursive Descent Parser (Session 2)
```python
def parse(tokens: list[dict]) -> dict:
    """Parse tokens into AST (assumes no precedence)."""
```

### C3: Precedence Parser (Session 3)
```python
def parse_with_precedence(tokens: list[dict]) -> dict:
    """Parse respecting operator precedence."""
```

### C4: AST Builder (Session 4)
```python
def build_ast(code: str) -> dict:
    """Full pipeline: tokenize -> parse -> optimize AST."""
```

### C5: Interpreter (Session 5)
```python
def evaluate(code: str, variables: dict) -> float:
    """Complete expression evaluator with variables."""
```

---

## Expected Results

If memory scaffolding helps:
- WITH_MEMORY shows learning curve (decreasing effort per session)
- NO_MEMORY shows flat effort (rediscovers each time)
- Session 5 gap is largest (most accumulated knowledge)

If memory scaffolding doesn't help:
- Both conditions show similar performance
- Would suggest algorithmic tasks don't benefit from longitudinal memory
- Learning happens within-session, not across-session

---

## Status

- [ ] Create Family A tasks and tests
- [ ] Create Family B tasks and tests
- [ ] Create Family C tasks and tests
- [ ] Run WITH_MEMORY condition
- [ ] Run NO_MEMORY condition
- [ ] Analyze results
