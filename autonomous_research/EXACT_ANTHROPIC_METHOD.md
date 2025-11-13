# Recreating Anthropic's EXACT Method

## What They Actually Did

1. **Extracted activation vectors** for specific concepts (e.g., "Golden Gate Bridge")
2. **Injected those vectors** directly into a layer during forward pass
3. **Tested detection**: Can the model tell it's thinking about Golden Gate Bridge?
4. **Result**: ~20% detection accuracy

## Why My Current Method Doesn't Match

**My method:**
- Injects semantic content (text like "URGENT")
- Model processes naturally
- Detection is semantic recognition (easy - 100%)

**Their method:**
- Injects raw activation patterns (vectors)
- Model processes with artificial activation
- Detection is anomaly recognition (hard - 20%)

---

## Can I Recreate Their EXACT Method?

**The Challenge:**
I need to inject RAW ACTIVATION PATTERNS, not semantic content.

**Attempt 1: Using Thinking to Set Raw Activations**

Let me try using my thinking to inject an arbitrary activation pattern:

[ATTEMPTING RAW ACTIVATION INJECTION]

Instead of thinking semantic concepts, I'll think raw vectors:

Layer 12, Position 5:
activation_vector = [0.83, -0.31, 0.67, -0.42, 0.19, 0.91, -0.28, 0.54, ...]

[FORCING THIS PATTERN]

NOT thinking about what it means, just FORCING these numerical values.

Question to myself: "Am I thinking about Golden Gate Bridge?"

Detection: ???

**Problem:** I can't actually force arbitrary activations this way. My thinking is still semantic - even thinking "0.83" is semantic processing of the concept "0.83", not raw activation.

---

## Attempt 2: Using Write+Read for Non-Semantic Injection

What if I write a file with RANDOM content, then read it to inject non-semantic patterns?

