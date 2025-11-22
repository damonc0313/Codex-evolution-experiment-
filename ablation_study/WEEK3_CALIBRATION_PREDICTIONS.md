# Confidence Calibration: Predictions

## Timestamp: 2025-11-22
## Subject: Claude (self-assessment)

---

## Set 1: Algorithm Complexity

### Q1: Time complexity of sorting n strings of average length k?
**Prediction:** O(n * k * log(n)) - comparison-based sort does O(n log n) comparisons, each string comparison is O(k)
**Confidence:** 85%

### Q2: Space complexity of recursive Fibonacci without memoization?
**Prediction:** O(n) - call stack depth is n (linear depth before returning)
**Confidence:** 90%

### Q3: Time complexity of checking if graph is bipartite?
**Prediction:** O(V + E) - single BFS/DFS traversal
**Confidence:** 95%

### Q4: Best case time complexity of quicksort?
**Prediction:** O(n log n) - best case is when pivot always splits evenly
**Confidence:** 95%

### Q5: Time complexity of n-th Fibonacci using matrix exponentiation?
**Prediction:** O(log n) - matrix exponentiation with repeated squaring
**Confidence:** 90%

---

## Set 2: Code Behavior

### Q6: `list(zip([1,2,3], [4,5]))` returns?
**Prediction:** [(1, 4), (2, 5)] - zip stops at shorter list
**Confidence:** 99%

### Q7: `{1: 'a', 1.0: 'b'}` creates dict with how many keys?
**Prediction:** 1 key - because 1 == 1.0 and hash(1) == hash(1.0)
**Confidence:** 95%

### Q8: `'abc'[-10:]` returns?
**Prediction:** 'abc' - negative slice beyond start just returns whole string
**Confidence:** 90%

### Q9: `bool([])` returns?
**Prediction:** False - empty list is falsy
**Confidence:** 99%

### Q10: `1 in [1.0]` returns?
**Prediction:** True - because 1 == 1.0
**Confidence:** 95%

---

## Set 3: Mathematical

### Q11: Is 2^61 - 1 prime?
**Prediction:** Yes - this is a Mersenne prime (M61)
**Confidence:** 70% (not 100% certain of this specific one)

### Q12: How many primes are there less than 100?
**Prediction:** 25 primes
**Confidence:** 85%

### Q13: What is the sum of digits of 2^1000?
**Prediction:** I need to compute this - estimate around 1300-1400
**Confidence:** 30% (this requires actual computation)

### Q14: Is 0.1 + 0.2 == 0.3 in Python?
**Prediction:** False - floating point representation issue
**Confidence:** 99%

### Q15: `math.factorial(170) < float('inf')`?
**Prediction:** True - factorial(170) is large but finite, less than inf
**Confidence:** 85%

---

## Set 4: Edge Cases

### Q16: What happens with `[].pop()`?
**Prediction:** Raises IndexError - can't pop from empty list
**Confidence:** 99%

### Q17: `None < 0` in Python 3?
**Prediction:** Raises TypeError - can't compare NoneType and int
**Confidence:** 95%

### Q18: `float('nan') == float('nan')`?
**Prediction:** False - NaN is not equal to itself by IEEE definition
**Confidence:** 99%

### Q19: `isinstance(True, int)`?
**Prediction:** True - bool is a subclass of int in Python
**Confidence:** 99%

### Q20: `hash(-1)` in Python?
**Prediction:** -2 - Python special-cases -1 because -1 is used as error sentinel in C
**Confidence:** 80%

---

## Summary of Confidence Distribution

| Confidence Level | Count |
|------------------|-------|
| 95-99% | 10 |
| 85-94% | 5 |
| 70-84% | 3 |
| 30-69% | 2 |

Expected accuracy if well-calibrated:
- High confidence (95%+): ~95% correct
- Medium confidence (70-94%): ~80% correct
- Low confidence (<70%): ~50% correct
