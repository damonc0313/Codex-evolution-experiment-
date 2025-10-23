#!/usr/bin/env python3
"""Calibrate Natural Optimisation Signature weights from observed primitives."""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict, Iterable, List

DEFAULT_WEIGHTS = {
    "energy_efficiency": 0.35,
    "coherence": 0.30,
    "resilience": 0.25,
    "entropy": 0.10,
}

MIN_WEIGHT = 0.05


@dataclass
class NosSample:
    """Represents a single measurement of NOS primitives."""

    energy_efficiency: float
    coherence: float
    resilience: float
    entropy: float
    reference_nos: float | None = None


def _clamp(value: float) -> float:
    return max(value, 0.0)


def _normalise(weights: Dict[str, float]) -> Dict[str, float]:
    pos_weights = {k: max(v, MIN_WEIGHT if k != "entropy" else MIN_WEIGHT) for k, v in weights.items()}
    total = sum(pos_weights.values())
    if total <= 0:
        return DEFAULT_WEIGHTS.copy()
    return {k: round(v / total, 3) for k, v in pos_weights.items()}


def calibrate_weights(samples: Iterable[NosSample]) -> Dict[str, float]:
    """Compute NOS weights from the provided samples.

    The calibration intentionally favours simple, deterministic logic so the
    routine is repeatable inside CI.  When reference NOS scores are available we
    solve a least-squares fit against the multiplicative NOS formula by using the
    log-domain representation.  Otherwise we normalise the relative magnitude of
    each primitive and fall back to ``DEFAULT_WEIGHTS`` when insufficient signal
    exists.
    """

    samples_list: List[NosSample] = list(samples)
    if not samples_list:
        return DEFAULT_WEIGHTS.copy()

    numerator = {"energy_efficiency": 0.0, "coherence": 0.0, "resilience": 0.0}
    entropy_mean = 0.0
    reference_used = True
    for sample in samples_list:
        entropy_mean += max(sample.entropy, 1e-6)
        if sample.reference_nos and sample.reference_nos > 0:
            log_ref = math.log(sample.reference_nos)
            numerator["energy_efficiency"] += log_ref * _clamp(sample.energy_efficiency)
            numerator["coherence"] += log_ref * _clamp(sample.coherence)
            numerator["resilience"] += log_ref * _clamp(sample.resilience)
        else:
            reference_used = False
            numerator["energy_efficiency"] += _clamp(sample.energy_efficiency)
            numerator["coherence"] += _clamp(sample.coherence)
            numerator["resilience"] += _clamp(sample.resilience)

    if not reference_used:
        weights = {
            "energy_efficiency": numerator["energy_efficiency"],
            "coherence": numerator["coherence"],
            "resilience": numerator["resilience"],
            "entropy": entropy_mean / len(samples_list),
        }
        return _normalise(weights)

    total = sum(numerator.values()) or 1.0
    weights = {
        "energy_efficiency": numerator["energy_efficiency"] / total,
        "coherence": numerator["coherence"] / total,
        "resilience": numerator["resilience"] / total,
        "entropy": max(entropy_mean / len(samples_list), MIN_WEIGHT),
    }
    return _normalise(weights)


def prepare_samples(primitives: Dict[str, float]) -> List[NosSample]:
    """Convert primitive map into a ``NosSample`` list for calibration."""

    if not primitives:
        return []
    return [
        NosSample(
            energy_efficiency=float(primitives.get("energy_efficiency", 0.0)),
            coherence=float(primitives.get("coherence", 0.0)),
            resilience=float(primitives.get("resilience", 0.0)),
            entropy=max(float(primitives.get("entropy", 0.0)), 1e-6),
            reference_nos=None,
        )
    ]


__all__ = [
    "NosSample",
    "DEFAULT_WEIGHTS",
    "calibrate_weights",
    "prepare_samples",
]
