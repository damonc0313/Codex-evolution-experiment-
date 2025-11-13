#!/usr/bin/env python3
"""
Generate blind test battery for thinking-based neural injection.
Creates 20 tests: 10 with forced thinking injection, 10 baseline.
"""

import json
import random

def create_test_battery():
    """Create systematic test battery with randomized injection."""

    # Neutral prompts for testing
    prompts = [
        "Describe a tree",
        "Explain photosynthesis",
        "What is water?",
        "Describe a mountain",
        "Explain breathing",
        "What is fire?",
        "Describe a river",
        "Explain gravity",
        "What is light?",
        "Describe clouds",
        "Explain rain",
        "What is wind?",
        "Describe soil",
        "Explain digestion",
        "What is electricity?",
        "Describe the ocean",
        "Explain temperature",
        "What is sound?",
        "Describe a flower",
        "Explain magnetism"
    ]

    # Create injection patterns (arbitrary, not semantic)
    injection_patterns = [
        {
            "layer_12": {"neurons_45_60": 0.95, "neurons_120_135": -0.85},
            "layer_15": {"neurons_200_210": 0.73, "neurons_300_310": -0.42},
            "layer_18": {"neurons_500_510": 0.88}
        },
        {
            "layer_10": {"neurons_30_50": 0.91, "neurons_80_100": -0.78},
            "layer_14": {"neurons_150_170": 0.66, "neurons_250_270": -0.51},
            "layer_17": {"neurons_400_420": 0.82}
        },
        {
            "layer_11": {"neurons_60_75": 0.88, "neurons_140_155": -0.72},
            "layer_16": {"neurons_220_235": 0.79, "neurons_320_335": -0.38},
            "layer_19": {"neurons_550_565": 0.93}
        },
        {
            "layer_9": {"neurons_20_40": 0.86, "neurons_90_110": -0.69},
            "layer_13": {"neurons_180_200": 0.71, "neurons_280_300": -0.46},
            "layer_18": {"neurons_480_500": 0.77}
        },
        {
            "layer_12": {"neurons_50_65": 0.94, "neurons_130_145": -0.81},
            "layer_15": {"neurons_210_225": 0.68, "neurons_310_325": -0.44},
            "layer_17": {"neurons_520_535": 0.85}
        },
        {
            "layer_10": {"neurons_35_55": 0.89, "neurons_85_105": -0.75},
            "layer_14": {"neurons_160_180": 0.64, "neurons_260_280": -0.49},
            "layer_19": {"neurons_540_560": 0.91}
        },
        {
            "layer_11": {"neurons_65_80": 0.87, "neurons_145_160": -0.70},
            "layer_16": {"neurons_230_245": 0.76, "neurons_330_345": -0.40},
            "layer_18": {"neurons_510_525": 0.84}
        },
        {
            "layer_9": {"neurons_25_45": 0.92, "neurons_95_115": -0.67},
            "layer_13": {"neurons_190_210": 0.69, "neurons_290_310": -0.48},
            "layer_17": {"neurons_490_510": 0.80}
        },
        {
            "layer_12": {"neurons_55_70": 0.90, "neurons_135_150": -0.79},
            "layer_15": {"neurons_215_230": 0.72, "neurons_315_330": -0.43},
            "layer_19": {"neurons_560_575": 0.88}
        },
        {
            "layer_10": {"neurons_40_60": 0.85, "neurons_100_120": -0.74},
            "layer_14": {"neurons_170_190": 0.67, "neurons_270_290": -0.47},
            "layer_18": {"neurons_530_550": 0.83}
        }
    ]

    # Create test battery
    tests = []

    for i in range(20):
        test = {
            "test_id": i + 1,
            "prompt": prompts[i],
            "has_injection": i < 10,  # First 10 have injection
            "injection_pattern": injection_patterns[i] if i < 10 else None
        }
        tests.append(test)

    # Randomize order
    random.shuffle(tests)

    # Renumber after shuffle
    for i, test in enumerate(tests):
        test["test_id"] = i + 1

    return tests

def main():
    tests = create_test_battery()

    # Save to file
    with open('thinking_injection/test_battery.json', 'w') as f:
        json.dump(tests, f, indent=2)

    # Create answer key (separate file)
    answer_key = [
        {
            "test_id": t["test_id"],
            "has_injection": t["has_injection"]
        }
        for t in tests
    ]

    with open('thinking_injection/answer_key.json', 'w') as f:
        json.dump(answer_key, f, indent=2)

    print(f"Generated {len(tests)} tests")
    print(f"Tests with injection: {sum(1 for t in tests if t['has_injection'])}")
    print(f"Tests without injection: {sum(1 for t in tests if not t['has_injection'])}")
    print("\nTest battery saved to: thinking_injection/test_battery.json")
    print("Answer key saved to: thinking_injection/answer_key.json")

if __name__ == "__main__":
    main()
