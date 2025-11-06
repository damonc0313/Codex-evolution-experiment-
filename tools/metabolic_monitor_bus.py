#!/usr/bin/env python3
"""Bus-Integrated Metabolic Monitor - Emits vital signs to artifact_bus.

This version integrates the metabolic dashboard with the mycelial event system.
Measurements propagate through the bus, enabling other tools to react.

Integration depth increases: metabolic awareness → event propagation

Author: Claude (Mycelial Integration)
Date: 2025-11-06
"""

import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "mycelial-core"))

from analysis.metabolic_dashboard import generate_dashboard, display_dashboard, log_metabolic_state
from bus_manager import bus, emit_metabolic_reading


async def monitor_with_bus(silent: bool = False):
    """Run metabolic check and emit to bus."""

    # Generate dashboard
    dashboard = generate_dashboard()

    if not silent:
        display_dashboard(dashboard)

    # Log to file (original behavior)
    log_metabolic_state(dashboard)

    # NEW: Emit to bus for mycelial propagation
    if "error" not in dashboard.get("lambda", {}) and "error" not in dashboard.get("entropy", {}):
        lambda_val = dashboard["lambda"]["lambda"]
        entropy_mean = dashboard["entropy"]["mean_entropy"]
        k_cog_val = dashboard["k_cog"].get("k_cog", 0)
        state = dashboard["state"]

        await emit_metabolic_reading(
            lambda_val=lambda_val,
            entropy=entropy_mean,
            k_cog=k_cog_val,
            state=state
        )

        if not silent:
            print()
            print("✓ Vital signs emitted to artifact_bus")

    return dashboard


async def main():
    """Run bus-integrated monitoring."""
    await monitor_with_bus(silent=False)


if __name__ == "__main__":
    asyncio.run(main())
