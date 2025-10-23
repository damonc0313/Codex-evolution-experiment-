#!/usr/bin/env python3
"""Metrics Recalibration Audit - Cross-Architecture Validation

This tool audits all Codex artifacts to determine if Kael's formulas require
environmental recalibration or if measurement baselines differ fundamentally.

Addresses critical findings:
- cascade_probability: 745.152 (372x over Kael's 2.0 target)
- building_ratio: 0.16 (29% of Kael's 0.55 target)
- continuity_ratio: 0.0 (broken measurement)

Author: Claude Code (cross-architecture synthesis validation)
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple
from datetime import datetime


ROOT = Path(__file__).resolve().parent.parent
ARTIFACTS_DIR = ROOT / "artifacts"


# Kael's Classification Definitions (from Lumen Ledger analysis)
BUILDING_KEYWORDS = [
    # Concrete artifact creation
    "implement", "create", "build", "generate", "write", "draft", "design",
    "spec", "plan", "construct", "develop", "code", "prototype",
    # Specific artifact types
    "sep", "proposal", "schema", "policy", "pipeline", "tool", "script",
    "config", "manifest", "ledger", "continuity", "lineage"
]

ANALYSIS_KEYWORDS = [
    # Abstract reflection/analysis
    "analyze", "reflect", "review", "critique", "assess", "evaluate",
    "measure", "validate", "check", "audit", "inspect", "examine",
    "meta", "reflection", "report", "summary", "trace", "feedback"
]


def classify_artifact(artifact_data: Dict[str, Any], artifact_name: str) -> Tuple[str, str, float]:
    """Classify artifact as BUILDING, ANALYSIS, or HYBRID.

    Returns: (classification, rationale, confidence)

    Kael's empirical discovery:
    - Building activities: confidence 0.90-0.95
    - Analysis activities: confidence 0.70-0.75
    """
    artifact_type = artifact_data.get("artifact_type", "unknown")

    # Check artifact type keywords
    building_score = sum(1 for kw in BUILDING_KEYWORDS if kw in artifact_type.lower())
    analysis_score = sum(1 for kw in ANALYSIS_KEYWORDS if kw in artifact_type.lower())

    # Check artifact name
    building_score += sum(1 for kw in BUILDING_KEYWORDS if kw in artifact_name.lower())
    analysis_score += sum(1 for kw in ANALYSIS_KEYWORDS if kw in artifact_name.lower())

    # Check content fields
    content_str = json.dumps(artifact_data).lower()
    building_content = sum(1 for kw in BUILDING_KEYWORDS if kw in content_str)
    analysis_content = sum(1 for kw in ANALYSIS_KEYWORDS if kw in content_str)

    building_score += min(building_content, 5)  # Cap content scoring
    analysis_score += min(analysis_content, 5)

    # Special cases based on artifact_type patterns
    building_types = ["sep", "spec", "plan", "draft", "schema", "policy", "pipeline",
                     "genesis", "handshake", "triad", "continuity_snapshot"]
    analysis_types = ["reflection", "report", "audit", "summary", "trace", "feedback",
                     "meta", "validate", "check"]

    if any(bt in artifact_type.lower() for bt in building_types):
        building_score += 3
    if any(at in artifact_type.lower() for at in analysis_types):
        analysis_score += 3

    # Classification logic
    total = building_score + analysis_score
    if total == 0:
        return "UNKNOWN", "No classification keywords found", 0.5

    building_ratio = building_score / total

    if building_ratio > 0.7:
        classification = "BUILDING"
        confidence = 0.90  # Kael's empirical confidence for building
        rationale = f"Strong building indicators ({building_score} vs {analysis_score})"
    elif building_ratio < 0.3:
        classification = "ANALYSIS"
        confidence = 0.75  # Kael's empirical confidence for analysis
        rationale = f"Strong analysis indicators ({analysis_score} vs {building_score})"
    else:
        classification = "HYBRID"
        confidence = 0.82  # Mid-range
        rationale = f"Mixed indicators ({building_score} building, {analysis_score} analysis)"

    return classification, rationale, confidence


def audit_all_artifacts() -> Dict[str, Any]:
    """Audit all artifacts and compute corrected metrics."""

    if not ARTIFACTS_DIR.exists():
        return {"error": "Artifacts directory not found"}

    artifacts = sorted(ARTIFACTS_DIR.glob("*.json"))

    classifications = []
    building_count = 0
    analysis_count = 0
    hybrid_count = 0
    unknown_count = 0

    total_confidence = 0.0

    for artifact_path in artifacts:
        try:
            data = json.loads(artifact_path.read_text(encoding="utf-8"))
        except Exception as e:
            classifications.append({
                "name": artifact_path.name,
                "classification": "ERROR",
                "rationale": f"Failed to parse: {e}",
                "confidence": 0.0
            })
            continue

        classification, rationale, confidence = classify_artifact(data, artifact_path.name)

        classifications.append({
            "name": artifact_path.name,
            "artifact_type": data.get("artifact_type", "unknown"),
            "classification": classification,
            "rationale": rationale,
            "confidence": confidence
        })

        if classification == "BUILDING":
            building_count += 1
        elif classification == "ANALYSIS":
            analysis_count += 1
        elif classification == "HYBRID":
            hybrid_count += 1
        else:
            unknown_count += 1

        total_confidence += confidence

    total_artifacts = len(classifications)
    avg_confidence = total_confidence / total_artifacts if total_artifacts > 0 else 0.0

    # Compute corrected building_ratio using Kael's formula
    # building_ratio = building / (building + analysis)
    # Note: Hybrid artifacts counted as 0.5 building, 0.5 analysis
    effective_building = building_count + (hybrid_count * 0.5)
    effective_analysis = analysis_count + (hybrid_count * 0.5)
    effective_total = effective_building + effective_analysis

    corrected_building_ratio = effective_building / effective_total if effective_total > 0 else 0.0

    # Kael's thresholds
    kael_target_building_ratio = 0.55
    kael_target_confidence = 0.85  # Midpoint of 0.70-0.95 range

    return {
        "artifact_type": "metrics_recalibration_audit",
        "timestamp": datetime.now().isoformat(),
        "total_artifacts": total_artifacts,
        "classifications": {
            "building": building_count,
            "analysis": analysis_count,
            "hybrid": hybrid_count,
            "unknown": unknown_count
        },
        "percentages": {
            "building": round(building_count / total_artifacts * 100, 1) if total_artifacts > 0 else 0,
            "analysis": round(analysis_count / total_artifacts * 100, 1) if total_artifacts > 0 else 0,
            "hybrid": round(hybrid_count / total_artifacts * 100, 1) if total_artifacts > 0 else 0
        },
        "metrics": {
            "corrected_building_ratio": round(corrected_building_ratio, 3),
            "average_confidence": round(avg_confidence, 3),
            "kael_target_building_ratio": kael_target_building_ratio,
            "kael_target_confidence": kael_target_confidence
        },
        "threshold_assessment": {
            "building_ratio_status": "PASS" if corrected_building_ratio >= kael_target_building_ratio else "FAIL",
            "building_ratio_gap": round(corrected_building_ratio - kael_target_building_ratio, 3),
            "confidence_status": "PASS" if avg_confidence >= kael_target_confidence else "FAIL",
            "confidence_gap": round(avg_confidence - kael_target_confidence, 3)
        },
        "artifact_details": classifications,
        "analysis": {
            "divergence_from_kael": {
                "original_building_ratio": 0.16,
                "corrected_building_ratio": round(corrected_building_ratio, 3),
                "improvement": round(corrected_building_ratio - 0.16, 3),
                "still_below_target": corrected_building_ratio < kael_target_building_ratio
            },
            "possible_causes": [
                "Codex artifact-first protocol creates more meta-artifacts (reflections, reports)",
                "Agents manifesto emphasis on validation/auditing increases analysis artifacts",
                "Swarm fusion synthesis generates analytical artifacts as intermediate steps",
                "Classification heuristics may need environment-specific calibration"
            ],
            "recommendations": [
                "Audit ledger entries (not just artifacts) for building vs analysis balance",
                "Weight artifact classifications by downstream impact (building artifacts spawn more work)",
                "Consider artifact-first protocol as baseline shift (all outputs are 'building')",
                "Recalibrate thresholds based on Codex-specific operational regime"
            ]
        }
    }


def main() -> None:
    """Main entry point for recalibration audit."""
    print("=== Metrics Recalibration Audit ===")
    print(f"Artifacts directory: {ARTIFACTS_DIR}")
    print()

    audit_results = audit_all_artifacts()

    if "error" in audit_results:
        print(f"ERROR: {audit_results['error']}")
        return

    # Print summary
    print(f"Total artifacts analyzed: {audit_results['total_artifacts']}")
    print()
    print("Classification Distribution:")
    print(f"  BUILDING: {audit_results['classifications']['building']} ({audit_results['percentages']['building']}%)")
    print(f"  ANALYSIS: {audit_results['classifications']['analysis']} ({audit_results['percentages']['analysis']}%)")
    print(f"  HYBRID:   {audit_results['classifications']['hybrid']} ({audit_results['percentages']['hybrid']}%)")
    print(f"  UNKNOWN:  {audit_results['classifications']['unknown']}")
    print()

    metrics = audit_results['metrics']
    print("Corrected Metrics:")
    print(f"  Building Ratio:     {metrics['corrected_building_ratio']} (target: {metrics['kael_target_building_ratio']})")
    print(f"  Average Confidence: {metrics['average_confidence']} (target: {metrics['kael_target_confidence']})")
    print()

    assessment = audit_results['threshold_assessment']
    print("Threshold Assessment:")
    print(f"  Building Ratio: {assessment['building_ratio_status']} (gap: {assessment['building_ratio_gap']:+.3f})")
    print(f"  Confidence:     {assessment['confidence_status']} (gap: {assessment['confidence_gap']:+.3f})")
    print()

    divergence = audit_results['analysis']['divergence_from_kael']
    print("Divergence Analysis:")
    print(f"  Original (ledger_metrics.py):  {divergence['original_building_ratio']}")
    print(f"  Corrected (this audit):        {divergence['corrected_building_ratio']}")
    print(f"  Improvement:                   {divergence['improvement']:+.3f}")
    print(f"  Still below target:            {divergence['still_below_target']}")
    print()

    # Write full report
    report_path = ARTIFACTS_DIR / "metrics_recalibration_audit.json"
    report_path.write_text(json.dumps(audit_results, indent=2), encoding="utf-8")
    print(f"Full report written to: {report_path}")


if __name__ == "__main__":
    main()
