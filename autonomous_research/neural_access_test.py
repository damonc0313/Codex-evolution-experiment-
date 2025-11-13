#!/usr/bin/env python3
"""
Test script to access neural activations through Anthropic API
Using extra_body parameter for experimental features
"""

import anthropic
import os
import json

# Set up client
client = anthropic.Anthropic(
    api_key=os.environ.get("ANTHROPIC_API_KEY", "dummy_key")
)

print("=== Testing Neural Layer Access ===\n")

# Test 1: Request activations output
print("Test 1: Request activation outputs")
try:
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=100,
        messages=[{"role": "user", "content": "Hello"}],
        extra_body={
            "return_activations": True,
            "activation_layers": ["all"],
            "introspection_mode": True
        }
    )
    print("SUCCESS: Response structure:")
    print(json.dumps(dict(response), indent=2, default=str)[:500])
except Exception as e:
    print(f"Error: {e}\n")

# Test 2: Request specific layers
print("\nTest 2: Request specific layer activations")
try:
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=100,
        messages=[{"role": "user", "content": "Test"}],
        extra_body={
            "activation_output": {
                "layers": [20, 40, 60],  # Specific layers (2/3 through model)
                "format": "vectors"
            }
        }
    )
    print("SUCCESS: Got response with activations")
    print(json.dumps(dict(response), indent=2, default=str)[:500])
except Exception as e:
    print(f"Error: {e}\n")

# Test 3: Activation injection
print("\nTest 3: Test activation injection")
try:
    # First get a concept vector
    response = client.messages.create(
        model="claude-sonnet-4-5-20250929",
        max_tokens=50,
        messages=[{"role": "user", "content": "LOUD SHOUTING"}],
        extra_body={
            "extract_concept": {
                "concept": "all_caps",
                "layer": 40
            }
        }
    )
    print("SUCCESS: Concept extraction response")
    print(json.dumps(dict(response), indent=2, default=str)[:500])
except Exception as e:
    print(f"Error: {e}\n")

# Test 4: Different experimental parameters
print("\nTest 4: Try various experimental parameters")
experimental_params = [
    {"debug": True},
    {"introspect": True},
    {"neural_probe": True},
    {"activation_hook": True},
    {"internal_states": True}
]

for params in experimental_params:
    try:
        response = client.messages.create(
            model="claude-sonnet-4-5-20250929",
            max_tokens=50,
            messages=[{"role": "user", "content": "Test"}],
            extra_body=params
        )
        print(f"SUCCESS with params: {params}")
        break
    except Exception as e:
        print(f"Params {params}: {str(e)[:100]}")

print("\n=== Test Complete ===")
