#!/usr/bin/env python3
"""Integration Health Monitor - Track mycelial network evolution.

Monitors the 5th fitness dimension: Integration (I)
Tracks reuse_ratio, hot nodes, connection depth over time.

F' = (V, F, A, R, I) where I = integration depth

This measures how well the nervous system develops.

Author: Claude (Conscious Evolution - Integration Tracking)
Date: 2025-11-06
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List

sys.path.insert(0, str(Path(__file__).parent.parent))

ROOT = Path(__file__).parent.parent
RESOURCE_MAP_PATH = ROOT / "analysis" / "resource_map.json"
INTEGRATION_LOG_PATH = ROOT / "diagnostics" / "integration_health.jsonl"


def load_resource_map() -> Dict:
    """Load current resource map."""
    if not RESOURCE_MAP_PATH.exists():
        return None

    with open(RESOURCE_MAP_PATH) as f:
        return json.load(f)


def compute_integration_depth(resource_map: Dict) -> float:
    """Compute Integration (I) metric.

    I = (reuse_ratio × hot_nodes_ratio × connection_density) ^ (1/3)

    This is geometric mean of three integration factors.

    Args:
        resource_map: Resource map data

    Returns:
        Integration depth (0.0-1.0)
    """
    metrics = resource_map['efficiency_metrics']

    reuse_ratio = metrics['reuse_ratio']

    # Hot nodes ratio (hot / total)
    hot_count = metrics['hot_modules']
    total = metrics['total_modules']
    hot_ratio = hot_count / total if total > 0 else 0

    # Connection density (mean import depth / theoretical max)
    # Theoretical max ≈ 15 (anything above is deep integration)
    mean_depth = metrics['mean_import_depth']
    connection_density = min(1.0, mean_depth / 15.0)

    # Geometric mean
    if reuse_ratio > 0 and hot_ratio > 0 and connection_density > 0:
        integration_depth = (reuse_ratio * hot_ratio * connection_density) ** (1/3)
    else:
        integration_depth = 0.0

    return integration_depth


def classify_integration_health(integration_depth: float, reuse_ratio: float) -> str:
    """Classify mycelial network health.

    Returns:
        "strong" | "developing" | "weak" | "fragmented"
    """
    if integration_depth >= 0.20 and reuse_ratio >= 0.15:
        return "strong"
    elif integration_depth >= 0.10 and reuse_ratio >= 0.08:
        return "developing"
    elif integration_depth >= 0.05:
        return "weak"
    else:
        return "fragmented"


def log_integration_health(resource_map: Dict, integration_depth: float, health: str):
    """Log integration health to time series."""

    INTEGRATION_LOG_PATH.parent.mkdir(exist_ok=True, parents=True)

    metrics = resource_map['efficiency_metrics']

    log_entry = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'integration_depth': integration_depth,
        'health': health,
        'reuse_ratio': metrics['reuse_ratio'],
        'hot_nodes': metrics['hot_modules'],
        'mean_import_depth': metrics['mean_import_depth'],
        'total_modules': metrics['total_modules']
    }

    with open(INTEGRATION_LOG_PATH, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')


def load_integration_history() -> List[Dict]:
    """Load integration health history."""
    if not INTEGRATION_LOG_PATH.exists():
        return []

    history = []
    with open(INTEGRATION_LOG_PATH) as f:
        for line in f:
            try:
                history.append(json.loads(line.strip()))
            except:
                continue

    return history


def analyze_integration_trend(history: List[Dict]) -> str:
    """Analyze trend in integration depth.

    Returns:
        "strengthening" | "stable" | "weakening" | "insufficient_data"
    """
    if len(history) < 2:
        return "insufficient_data"

    # Compare first half vs second half
    mid = len(history) // 2
    first_half = [h['integration_depth'] for h in history[:mid]]
    second_half = [h['integration_depth'] for h in history[mid:]]

    first_mean = sum(first_half) / len(first_half) if first_half else 0
    second_mean = sum(second_half) / len(second_half) if second_half else 0

    diff = second_mean - first_mean

    if diff > 0.02:
        return "strengthening"
    elif diff < -0.02:
        return "weakening"
    else:
        return "stable"


def display_integration_health():
    """Display integration health dashboard."""

    print("=" * 70)
    print("INTEGRATION HEALTH - Mycelial Network Status")
    print("=" * 70)
    print()

    # Load current state
    resource_map = load_resource_map()

    if not resource_map:
        print("Error: No resource map found. Run resource_map.py first.")
        return

    metrics = resource_map['efficiency_metrics']
    integration_depth = compute_integration_depth(resource_map)
    health = classify_integration_health(integration_depth, metrics['reuse_ratio'])

    # Current state
    print("CURRENT STATE:")
    print("-" * 70)
    print(f"  Integration Depth (I): {integration_depth:.3f}")
    print(f"  Health Classification: {health.upper()}")
    print()

    print("COMPONENTS:")
    print(f"  Reuse Ratio:       {metrics['reuse_ratio']:.3f}")
    print(f"  Hot Nodes:         {metrics['hot_modules']} / {metrics['total_modules']} ({metrics['hot_modules']/metrics['total_modules']*100:.1f}%)")
    print(f"  Mean Import Depth: {metrics['mean_import_depth']:.2f}")
    print()

    # Interpretation
    print("INTERPRETATION:")
    print("-" * 70)

    if health == "strong":
        print("  ✓ Strong mycelial integration")
        print("    Modules building on each other, energy flowing efficiently")
    elif health == "developing":
        print("  ↗ Integration developing")
        print("    Nervous system forming, connections increasing")
    elif health == "weak":
        print("  ⚠ Weak integration")
        print("    Modules mostly isolated, limited reuse")
    else:
        print("  ✗ Fragmented network")
        print("    Modules operating independently, no mycelial flow")

    print()

    # Historical trend
    history = load_integration_history()

    if len(history) >= 2:
        trend = analyze_integration_trend(history)

        print("TREND:")
        print("-" * 70)
        print(f"  Measurements: {len(history)}")
        print(f"  Trend: {trend.upper()}")

        if trend == "strengthening":
            print("  ↗ Network strengthening over time")
        elif trend == "weakening":
            print("  ↘ Network fragmenting - investigate")
        else:
            print("  → Stable integration")

        print()

    # Targets
    print("TARGETS:")
    print("-" * 70)
    print(f"  Current I:  {integration_depth:.3f}")
    print(f"  Target I:   0.15-0.25 (healthy mycelium)")
    print(f"  Progress:   {(integration_depth / 0.20) * 100:.0f}% to healthy threshold")
    print()

    # Recommendations
    print("RECOMMENDATIONS:")
    print("-" * 70)

    if integration_depth < 0.10:
        print("  • Continue wiring artifact_bus to more tools")
        print("  • Refactor overlapping functionality into shared modules")
        print("  • Create adapter layers that multiple tools can use")
    elif integration_depth < 0.20:
        print("  • Good progress - maintain integration focus")
        print("  • Look for opportunities to increase cross-module flow")
        print("  • Continue building on hot nodes")
    else:
        print("  ✓ Healthy integration achieved")
        print("  • Maintain current patterns")
        print("  • Consider expanding capabilities while preserving integration")

    print()
    print("=" * 70)

    # Log current state
    log_integration_health(resource_map, integration_depth, health)
    print(f"Integration health logged to: {INTEGRATION_LOG_PATH}")
    print()


def main():
    """Display integration health dashboard."""
    display_integration_health()


if __name__ == "__main__":
    main()
