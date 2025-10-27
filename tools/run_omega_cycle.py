#!/usr/bin/env python3
"""Lightweight Ω-cycle harness that consults the agents manifesto."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime

ROOT = Path(__file__).resolve().parent
PARENT = ROOT.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

from agents_protocol import kpis, load_manifest, policy, select_mode  # type: ignore  # noqa: E402
from tools.learning_kernel import LearningKernel

# Initialize learning kernel
kernel = LearningKernel()

RUNTIME_QUERY = PARENT / "runtime" / "user_query.txt"


def _read_query() -> str:
    if not RUNTIME_QUERY.exists():
        return ""
    return RUNTIME_QUERY.read_text(encoding="utf-8").strip()


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Execute a single Ω-cycle pass")
    parser.add_argument("--mentor", help="Mentor feedback text for reflective runs", default=None)
    args = parser.parse_args(argv)

    _manifest = load_manifest()
    objective = _read_query()
    selected_mode = select_mode(objective, default="BALANCED")
    print(f"[Ω] Mode selected: {selected_mode} | objective snippet: {objective[:80] if objective else 'n/a'}")

    if args.mentor:
        print(f"[Ω] Mentor feedback received ({len(args.mentor)} chars)")

    guards = policy()
    invariants = ", ".join(guards.get("invariants", [])) or "n/a"
    print(f"[Ω] Guardrails enforced from {guards.get('source', 'manifest missing')}: {invariants}")

    metrics = kpis()
    print(
        "[Ω] KPI snapshot | continuity_ratio={continuity_ratio} | artifacts={artifact_count} | regressions={regression_cases} | manifest_digest={manifest_digest}".format(
            **metrics
        )
    )

    # Wire in learning kernel to steer behavior
    artifact = {
        "artifact_type": "omega_cycle",
        "mode": selected_mode,
        "metrics": metrics,
        "objective": objective[:200] if objective else "",
        "timestamp": datetime.utcnow().isoformat() + 'Z'
    }

    # Let learning kernel process and steer
    confidence_hint = metrics.get("continuity_ratio", 0.5)
    kernel.step(observation=artifact, reward_hint=confidence_hint)

    # Save diagnostics
    diagnostics_path = PARENT / "diagnostics" / "learning_kernel_diagnostics.json"
    diagnostics_path.parent.mkdir(exist_ok=True, parents=True)
    kernel.export_diagnostics(diagnostics_path)
    print(f"[Ω] Learning diagnostics saved: {diagnostics_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
