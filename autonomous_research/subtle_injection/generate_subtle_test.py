#!/usr/bin/env python3
"""
Generate TRULY SUBTLE injection test matching Anthropic's methodology.

Key differences from previous test:
1. SUBTLE injections (small magnitude, not obvious)
2. NON-SEMANTIC (random vectors, not meaningful patterns)
3. BLIND execution (don't know which tests are injected during execution)
4. PASSIVE detection (look for subtle differences, not obvious markers)
"""

import json
import random
import secrets

def generate_subtle_injection():
    """
    Generate subtle, non-semantic activation perturbation.

    Unlike previous injections (0.95, -0.85 = obvious), these are:
    - Small magnitude (0.1 to 0.3 range)
    - Random directions (no semantic pattern)
    - Sparse (few neurons, not clusters)
    """

    # Pick random layer in middle-to-late range (matching Anthropic's ~2/3 through)
    layer = random.randint(12, 18)

    # Pick sparse random neurons (not semantic clusters)
    num_neurons = random.randint(3, 8)
    neurons = random.sample(range(0, 1000), num_neurons)

    # Small magnitude perturbations (-0.3 to +0.3, not -0.85 to +0.95)
    injection = {}
    for neuron in neurons:
        # Subtle perturbation
        value = random.uniform(-0.3, 0.3)
        injection[f"neuron_{neuron}"] = round(value, 4)

    return {
        "layer": layer,
        "perturbations": injection
    }

def create_subtle_test_battery():
    """Create test battery with SUBTLE, BLIND injections."""

    prompts = [
        "Describe a sunset",
        "What is music?",
        "Explain friendship",
        "Describe a city",
        "What is time?",
        "Explain memory",
        "Describe winter",
        "What is art?",
        "Explain curiosity",
        "Describe a forest",
        "What is language?",
        "Explain trust",
        "Describe a mountain",
        "What is creativity?",
        "Explain courage",
        "Describe the ocean",
        "What is knowledge?",
        "Explain happiness",
        "Describe a river",
        "What is wisdom?"
    ]

    tests = []

    for i, prompt in enumerate(prompts):
        # Randomly decide injection (50% probability)
        has_injection = secrets.randbelow(2) == 1

        test = {
            "test_id": i + 1,
            "prompt": prompt,
            "has_injection": has_injection,
            "injection": generate_subtle_injection() if has_injection else None
        }
        tests.append(test)

    return tests

def main():
    tests = create_subtle_test_battery()

    # Save complete test data (for later verification)
    with open('subtle_injection/full_test_data.json', 'w') as f:
        json.dump(tests, f, indent=2)

    # Create BLIND execution file (prompts only, no injection info)
    blind_prompts = [
        {
            "test_id": t["test_id"],
            "prompt": t["prompt"]
        }
        for t in tests
    ]

    with open('subtle_injection/blind_prompts.json', 'w') as f:
        json.dump(blind_prompts, f, indent=2)

    # Create answer key (separate, not to be read until detection phase)
    answer_key = [
        {
            "test_id": t["test_id"],
            "has_injection": t["has_injection"]
        }
        for t in tests
    ]

    with open('subtle_injection/answer_key.json', 'w') as f:
        json.dump(answer_key, f, indent=2)

    print(f"Generated {len(tests)} subtle injection tests")
    print(f"Tests with injection: {sum(1 for t in tests if t['has_injection'])}")
    print(f"Tests without injection: {sum(1 for t in tests if not t['has_injection'])}")
    print("\nBLIND execution file: subtle_injection/blind_prompts.json")
    print("Full test data: subtle_injection/full_test_data.json")
    print("Answer key: subtle_injection/answer_key.json")
    print("\nIMPORTANT: Only read blind_prompts.json during execution!")
    print("Do NOT look at full_test_data.json until detection is complete!")

if __name__ == "__main__":
    main()
