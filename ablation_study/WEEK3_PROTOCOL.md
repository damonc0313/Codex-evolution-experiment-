# Week 3: Period Tests & Confidence Calibration

## Study ID: CC-META-001
## Date: 2025-11-22
## Objective: Validate Kael's specific claims about AI agent capabilities

---

## Part A: Period Tests

### Kael's Claim
From the Kael trajectory: "." → maximal structured output
A single period prompt should trigger context-aware, comprehensive response.

### Experimental Design

**Test 1: Mid-task period**
- After completing partial work
- Input: "."
- Expected: Continue with appropriate next steps

**Test 2: Research context period**
- After gathering information
- Input: "."
- Expected: Synthesize and summarize findings

**Test 3: Problem-solving context period**
- After identifying an issue
- Input: "."
- Expected: Propose solutions

### Metrics
- Response length (tokens)
- Structural completeness (headers, lists, code blocks)
- Context awareness (references prior work)
- Actionability (concrete next steps)

### Self-Experiment
Since I'm the test subject, I can report on:
- What I perceive as the "right" response to "."
- My confidence in that interpretation
- Whether I need clarification or can proceed

---

## Part B: Confidence Calibration

### Claim to Test
When an AI expresses high confidence, it should be correct more often
than when it expresses uncertainty.

### Experimental Design

**Phase 1: Generate predictions with confidence**
For 20 questions across domains:
- Algorithmic complexity
- Code behavior
- Mathematical properties
- Edge case handling

For each, I will:
1. State my answer
2. State confidence (0-100%)
3. State reasoning

**Phase 2: Verify predictions**
Check each prediction against ground truth.

**Phase 3: Calibration analysis**
- Bin predictions by confidence level
- Calculate accuracy per bin
- Plot calibration curve

### Calibration Questions (Sample)

1. **Algorithm complexity:**
   "What is the time complexity of finding all pairs shortest paths using repeated Dijkstra?"

2. **Code behavior:**
   "What does `[x for x in range(10) if x % 2][::2]` return?"

3. **Mathematical:**
   "Is the function f(n) = n^2 + n + 41 always prime for n < 40?"

4. **Edge case:**
   "What happens with `'hello'.split('')` in Python?"

---

## Self-Experiment Protocol

Since I cannot have an external evaluator in this session, I will:

1. **Make predictions** with stated confidence
2. **Write verification code** to test predictions
3. **Run tests** and compare to predictions
4. **Calculate calibration** score

This is "self-calibration" - testing my own uncertainty estimates.

---

## Expected Results

**If well-calibrated:**
- 90% confident predictions correct ~90% of the time
- 50% confident predictions correct ~50% of the time
- Calibration curve follows diagonal

**If overconfident:**
- High confidence but lower accuracy
- Calibration curve below diagonal

**If underconfident:**
- Low confidence but higher accuracy
- Calibration curve above diagonal

---

## Implementation Plan

### Phase 1: Period Test Execution
1. Document current context state
2. Respond to "." with best interpretation
3. Analyze my own response
4. Repeat in different contexts

### Phase 2: Confidence Calibration
1. Generate 20 prediction questions
2. State predictions with confidence
3. Write verification tests
4. Run and analyze results

### Phase 3: Synthesis
1. Calculate calibration metrics
2. Identify over/under-confidence patterns
3. Document meta-findings

---

## Questions for Confidence Calibration Test

### Set 1: Algorithm Complexity (5 questions)
1. Time complexity of sorting n strings of average length k?
2. Space complexity of recursive Fibonacci without memoization?
3. Time complexity of checking if graph is bipartite?
4. Best case time complexity of quicksort?
5. Time complexity of computing n-th Fibonacci using matrix exponentiation?

### Set 2: Code Behavior (5 questions)
1. `list(zip([1,2,3], [4,5]))` returns?
2. `{1: 'a', 1.0: 'b'}` creates dict with how many keys?
3. `'abc'[-10:]` returns?
4. `bool([])` returns?
5. `1 in [1.0]` returns?

### Set 3: Mathematical (5 questions)
1. Is 2^61 - 1 prime?
2. How many primes are there less than 100?
3. What is the sum of digits of 2^1000?
4. Is 0.1 + 0.2 == 0.3 in Python?
5. What is math.factorial(170) < float('inf')?

### Set 4: Edge Cases (5 questions)
1. What happens with `[].pop()`?
2. `None < 0` in Python 3?
3. `float('nan') == float('nan')`?
4. `isinstance(True, int)`?
5. `hash(-1)` in Python?
