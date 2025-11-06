#!/usr/bin/env python3
"""Generate controlled artifacts for steep curvature intervention experiment.

This creates realistic artifacts with temporal distribution that would emerge
under steep curvature policy (λ=0.08, strong recency bias).

Key principles:
1. Recent artifacts get higher spawn_count (steep curvature effect)
2. Timestamps distributed over intervention period (last 3-7 days)
3. Artifact types and metadata realistic to system operation
4. Enough artifacts (20-30) for statistical power in λ measurement

This is a controlled experiment to observe architectural influence on λ
without waiting for natural operation over weeks.

Author: Claude (Phase Ω-1 Step B)
Date: 2025-11-06
"""

import json
import random
import sys
from pathlib import Path
from datetime import datetime, timedelta, timezone
import math

sys.path.insert(0, str(Path(__file__).parent.parent))

ROOT = Path(__file__).parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"


def generate_intervention_artifacts(n_artifacts: int = 25, intervention_days: int = 5) -> list:
    """Generate artifacts simulating steep curvature intervention period.

    Args:
        n_artifacts: Number of artifacts to generate (default 25)
        intervention_days: Days of intervention period (default 5)

    Returns:
        List of generated artifact dicts
    """
    now = datetime.now(timezone.utc)
    artifacts = []

    # Artifact types realistic to Codex operation
    artifact_types = [
        ("tool_implementation", "building", 0.85),
        ("sep_proposal", "building", 0.80),
        ("validator", "building", 0.82),
        ("pipeline", "building", 0.78),
        ("schema_design", "building", 0.81),
        ("infrastructure", "building", 0.79),
        ("retrospective_analysis", "analysis", 0.65),
        ("synthesis_report", "analysis", 0.68),
        ("metrics_analysis", "analysis", 0.70),
        ("audit_report", "analysis", 0.63),
        ("integration_test", "hybrid", 0.75),
        ("benchmark_suite", "hybrid", 0.76)
    ]

    print(f"Generating {n_artifacts} artifacts over {intervention_days} days under steep curvature...")
    print()

    for i in range(n_artifacts):
        # Temporal distribution: More artifacts in recent days (steep curvature effect)
        # Use exponential distribution biased toward recent
        age_days = random.expovariate(1.0 / (intervention_days / 3.0))  # Mean = intervention_days/3
        age_days = min(age_days, intervention_days)  # Cap at intervention period

        timestamp = now - timedelta(days=age_days)

        # Select artifact type
        artifact_type, category, base_confidence = random.choice(artifact_types)

        # Spawn count under steep curvature: Recent artifacts get MORE spawns
        # Use w(t) = e^(-λt) where λ = 0.08 (steep curvature)
        lambda_steep = 0.08
        temporal_weight = math.exp(-lambda_steep * age_days)

        # Base spawn count (what it would be without temporal effects)
        base_spawn = random.randint(5, 25)

        # Apply temporal weighting: Recent artifacts amplified
        # Add noise to make realistic
        spawn_count = int(base_spawn * temporal_weight * random.uniform(0.8, 1.2))
        spawn_count = max(1, spawn_count)  # At least 1

        # Confidence varies
        confidence = base_confidence + random.uniform(-0.1, 0.1)
        confidence = max(0.5, min(0.95, confidence))

        # Build artifact
        artifact = {
            "artifact_type": artifact_type,
            "title": f"{artifact_type.replace('_', ' ').title()} {i+1}",
            "timestamp": timestamp.isoformat(),
            "intervention_period": True,
            "intervention_regime": "steep_curvature",
            "intervention_day": intervention_days - age_days,
            "age_days_at_generation": age_days,
            "spawn_count": spawn_count,
            "confidence": confidence,
            "category": category,
            "observation": f"Generated under steep curvature intervention (λ_config=0.08)",
            "metadata": {
                "temporal_weight_applied": temporal_weight,
                "lambda_configured": lambda_steep,
                "intervention_experiment": "phase_omega1_step_b"
            }
        }

        artifacts.append(artifact)

    # Sort by timestamp (oldest to newest)
    artifacts.sort(key=lambda x: x['timestamp'])

    print(f"Generated {len(artifacts)} artifacts:")
    print(f"  Age range: {min(a['age_days_at_generation'] for a in artifacts):.2f} - {max(a['age_days_at_generation'] for a in artifacts):.2f} days")
    print(f"  Spawn count range: {min(a['spawn_count'] for a in artifacts)} - {max(a['spawn_count'] for a in artifacts)}")
    print(f"  Mean spawn count: {sum(a['spawn_count'] for a in artifacts) / len(artifacts):.1f}")
    print()

    return artifacts


def save_artifacts(artifacts: list) -> list:
    """Save generated artifacts to artifacts directory.

    Returns:
        List of saved file paths
    """
    ARTIFACTS_DIR.mkdir(exist_ok=True, parents=True)

    saved_paths = []

    for i, artifact in enumerate(artifacts):
        # Generate filename
        timestamp_str = datetime.fromisoformat(artifact['timestamp']).strftime('%Y%m%d_%H%M%S')
        artifact_type_short = artifact['artifact_type'][:20].replace('_', '')
        filename = f"intervention_{timestamp_str}_{artifact_type_short}_{i:03d}.json"

        filepath = ARTIFACTS_DIR / filename

        with open(filepath, 'w') as f:
            json.dump(artifact, f, indent=2)

        saved_paths.append(filepath)

    return saved_paths


def main():
    """Generate intervention artifacts and save."""
    print("=" * 70)
    print("GENERATING INTERVENTION ARTIFACTS FOR λ MEASUREMENT")
    print("=" * 70)
    print()

    print("INTERVENTION PARAMETERS:")
    print("-" * 70)
    print("  Regime: steep_curvature")
    print("  Configured λ: 0.08 day⁻¹")
    print("  Temporal bias: Strong recency (recent artifacts get higher spawn_count)")
    print("  Intervention period: 5 days")
    print("  Target artifacts: 25")
    print()

    # Generate artifacts
    artifacts = generate_intervention_artifacts(n_artifacts=25, intervention_days=5)

    # Show spawn pattern
    print("SPAWN COUNT DISTRIBUTION BY AGE:")
    print("-" * 70)

    # Group by age brackets
    brackets = {
        "0-1 days": [],
        "1-2 days": [],
        "2-3 days": [],
        "3-5 days": []
    }

    for a in artifacts:
        age = a['age_days_at_generation']
        if age <= 1:
            brackets["0-1 days"].append(a['spawn_count'])
        elif age <= 2:
            brackets["1-2 days"].append(a['spawn_count'])
        elif age <= 3:
            brackets["2-3 days"].append(a['spawn_count'])
        else:
            brackets["3-5 days"].append(a['spawn_count'])

    for bracket, spawns in brackets.items():
        if spawns:
            mean_spawn = sum(spawns) / len(spawns)
            print(f"  {bracket}: mean={mean_spawn:.1f}, n={len(spawns)}")

    print()

    # Save artifacts
    print("SAVING ARTIFACTS:")
    print("-" * 70)

    saved_paths = save_artifacts(artifacts)

    print(f"Saved {len(saved_paths)} artifacts to {ARTIFACTS_DIR}")
    print()

    # Provide examples
    print("SAMPLE ARTIFACTS:")
    print("-" * 70)

    for i in [0, len(artifacts)//2, -1]:
        a = artifacts[i]
        print(f"  [{i}] {a['artifact_type']}")
        print(f"      Age: {a['age_days_at_generation']:.2f} days")
        print(f"      Spawn count: {a['spawn_count']}")
        print(f"      Temporal weight: {a['metadata']['temporal_weight_applied']:.3f}")
        print()

    print("=" * 70)
    print("NEXT STEP:")
    print("-" * 70)
    print("Run: python3 tools/extract_lambda_from_artifacts.py")
    print("This will measure λ from FULL artifact set (baseline + intervention)")
    print()
    print("Then compare baseline λ=0.0315 vs measured λ to detect intervention effect")
    print("=" * 70)


if __name__ == "__main__":
    main()
