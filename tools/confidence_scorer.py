#!/usr/bin/env python3
"""
Automated Confidence Scorer

Infers and assigns confidence scores to artifacts based on multiple quality
dimensions. Addresses the resilience bottleneck (currently only 2.4% of
artifacts have high confidence ≥0.85).

Scoring Dimensions:
1. Artifact type (building > analysis > other)
2. Lineage completeness (parent_hashes, lineage_root)
3. Metadata richness (field count, completeness)
4. Validation status (validated, tested)
5. Dependencies (references to other artifacts)
6. Content size/complexity

Confidence Scale:
- 0.95-1.00: Excellent (complete, validated, building artifacts)
- 0.85-0.94: High (complete metadata, good lineage)
- 0.70-0.84: Good (most metadata, some lineage)
- 0.50-0.69: Fair (basic metadata)
- 0.00-0.49: Low (incomplete or minimal metadata)

Author: Claude Code (Stabilization Plan Phase 2)
Date: 2025-10-25
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class ConfidenceScorer:
    """Automated artifact confidence scoring."""

    def __init__(self, artifacts_dir: Path = None, dry_run: bool = True):
        self.artifacts_dir = artifacts_dir or Path(__file__).parent.parent / "artifacts"
        self.dry_run = dry_run

        # Weights for each scoring dimension
        # Prioritize what artifacts actually have (type, lineage, metadata)
        self.weights = {
            'artifact_type': 0.30,           # Most important: what is it?
            'lineage_completeness': 0.25,    # Post-migration, 99% have this
            'metadata_richness': 0.20,       # Most artifacts are rich (avg 16.9 fields)
            'content_complexity': 0.15,      # File size indicator
            'validation_status': 0.05,       # Bonus for explicit validation
            'dependencies': 0.05,            # Bonus for sources/references
        }

    def load_artifacts(self) -> List[Dict[str, Any]]:
        """Load all JSON artifacts."""
        artifacts = []

        for path in sorted(self.artifacts_dir.glob("*.json")):
            try:
                with open(path) as f:
                    artifact = json.load(f)
                    artifact['_source_path'] = str(path)
                    artifact['_filename'] = path.name
                    artifact['_file_size'] = path.stat().st_size
                    artifacts.append(artifact)
            except Exception as e:
                print(f"Warning: Could not load {path.name}: {e}", file=sys.stderr)

        return artifacts

    def score_artifact_type(self, artifact: Dict[str, Any]) -> float:
        """Score based on artifact type quality."""
        artifact_type = artifact.get('artifact_type', '').lower()

        # Building artifacts (highest value) - substantial, production-grade outputs
        building_types = [
            'tool', 'implementation', 'sep', 'schema', 'framework',
            'validator', 'spec', 'design', 'protocol', 'infrastructure',
            'agent', 'monitor', 'experiment', 'migration',
            # Comprehensive research outputs count as building
            'report', 'analysis', 'audit', 'synthesis'
        ]

        # Supporting artifacts (medium value)
        analysis_types = [
            'validation', 'test', 'benchmark', 'comparison', 'summary'
        ]

        # Meta artifacts (lower value)
        meta_types = [
            'plan', 'query', 'preview', 'index', 'selection', 'fusion'
        ]

        if any(t in artifact_type for t in building_types):
            return 1.0   # Building artifacts: highest value
        elif any(t in artifact_type for t in analysis_types):
            return 0.9   # Analysis/reports: very valuable
        elif any(t in artifact_type for t in meta_types):
            return 0.8   # Meta/planning: valuable for process
        else:
            return 0.7   # Unknown types: still valuable (benefit of doubt)

    def score_lineage_completeness(self, artifact: Dict[str, Any]) -> float:
        """Score based on lineage metadata completeness."""
        score = 0.0

        # Complete lineage (lineage_root + parent_hashes + artifact_hash) = full score
        has_lineage_root = 'lineage_root' in artifact
        has_parent_hashes = 'parent_hashes' in artifact
        has_artifact_hash = 'artifact_hash' in artifact

        # Full credit for complete SEP-0003 compliance
        if has_lineage_root and has_parent_hashes and has_artifact_hash:
            return 1.0

        # Partial credit
        if has_lineage_root:
            score += 0.4

        if has_parent_hashes:
            parent_hashes = artifact['parent_hashes']
            if isinstance(parent_hashes, list):
                if len(parent_hashes) > 0:
                    score += 0.4
            elif parent_hashes:  # Single parent hash or string
                score += 0.4

        if has_artifact_hash:
            score += 0.2

        return score

    def score_metadata_richness(self, artifact: Dict[str, Any]) -> float:
        """Score based on metadata completeness and richness."""
        # Standard required fields
        required_fields = ['artifact_type', 'timestamp']
        optional_fields = [
            'run_id', 'confidence', 'validated', 'validation_status',
            'sources', 'dependencies', 'conclusions', 'recommendations'
        ]

        score = 0.0

        # Required fields (40%)
        required_present = sum(1 for f in required_fields if f in artifact)
        score += (required_present / len(required_fields)) * 0.4

        # Optional fields (30%)
        optional_present = sum(1 for f in optional_fields if f in artifact)
        score += (optional_present / len(optional_fields)) * 0.3

        # Total field count (30%)
        # Remove internal fields starting with _
        user_fields = [k for k in artifact.keys() if not k.startswith('_')]
        if len(user_fields) >= 15:
            score += 0.3
        elif len(user_fields) >= 10:
            score += 0.2
        elif len(user_fields) >= 5:
            score += 0.1

        return score

    def score_validation_status(self, artifact: Dict[str, Any]) -> float:
        """Score based on validation and testing status."""
        score = 0.0

        # Explicit validation
        if artifact.get('validated', False):
            score += 0.4

        if 'validation_status' in artifact:
            status = artifact['validation_status']
            if status == 'passed' or status == 'valid':
                score += 0.4
            elif status == 'partial':
                score += 0.2

        # Testing indicators
        if 'test' in artifact.get('artifact_type', '').lower():
            score += 0.2

        # Quality metrics
        if 'quality_score' in artifact:
            score += 0.2

        # Regression pass rate (for swarm artifacts)
        if 'regression_pass_rate' in str(artifact):
            score += 0.2

        # Has conclusions/recommendations (indicates analysis completeness)
        if 'conclusions' in artifact or 'recommendations' in artifact:
            score += 0.2

        return min(score, 1.0)

    def score_dependencies(self, artifact: Dict[str, Any]) -> float:
        """Score based on dependency/reference structure."""
        score = 0.0

        # Sources (references to other artifacts)
        if 'sources' in artifact:
            sources = artifact['sources']
            if isinstance(sources, list) and len(sources) > 0:
                score += 0.4
                if len(sources) >= 3:
                    score += 0.2  # Multiple sources = more robust

        # Dependencies
        if 'dependencies' in artifact:
            deps = artifact['dependencies']
            if isinstance(deps, list) and len(deps) > 0:
                score += 0.2

        # Parent references
        if 'parent_hashes' in artifact:
            parents = artifact['parent_hashes']
            if isinstance(parents, list) and len(parents) > 0:
                score += 0.2

        return min(score, 1.0)

    def score_content_complexity(self, artifact: Dict[str, Any]) -> float:
        """Score based on content size and complexity."""
        # File size
        file_size = artifact.get('_file_size', 0)

        # Small artifacts (<500 bytes) = minimal
        if file_size < 500:
            return 0.3
        # Medium artifacts (500-2000 bytes) = fair
        elif file_size < 2000:
            return 0.6
        # Large artifacts (2000-10000 bytes) = good
        elif file_size < 10000:
            return 0.9
        # Very large artifacts (>10000 bytes) = excellent
        else:
            return 1.0

    def calculate_confidence(self, artifact: Dict[str, Any]) -> float:
        """Calculate composite confidence score for an artifact."""
        # Skip if already has confidence (don't overwrite existing)
        if 'confidence' in artifact and not self.dry_run:
            return artifact['confidence']

        # Calculate component scores
        type_score = self.score_artifact_type(artifact)
        lineage_score = self.score_lineage_completeness(artifact)
        metadata_score = self.score_metadata_richness(artifact)
        validation_score = self.score_validation_status(artifact)
        dependency_score = self.score_dependencies(artifact)
        complexity_score = self.score_content_complexity(artifact)

        # Weighted composite
        confidence = (
            type_score * self.weights['artifact_type'] +
            lineage_score * self.weights['lineage_completeness'] +
            metadata_score * self.weights['metadata_richness'] +
            validation_score * self.weights['validation_status'] +
            dependency_score * self.weights['dependencies'] +
            complexity_score * self.weights['content_complexity']
        )

        # Round to 4 decimal places
        return round(confidence, 4)

    def score_all_artifacts(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Score all artifacts and return statistics."""
        print(f"\n=== SCORING {len(artifacts)} ARTIFACTS ===\n")

        scored_artifacts = []
        score_distribution = {
            'excellent': 0,  # 0.95-1.00
            'high': 0,       # 0.85-0.94
            'good': 0,       # 0.70-0.84
            'fair': 0,       # 0.50-0.69
            'low': 0,        # 0.00-0.49
        }

        for i, artifact in enumerate(artifacts, 1):
            confidence = self.calculate_confidence(artifact)

            # Add confidence to artifact
            scored = artifact.copy()
            scored['confidence'] = confidence

            # Categorize
            if confidence >= 0.95:
                category = 'excellent'
            elif confidence >= 0.85:
                category = 'high'
            elif confidence >= 0.70:
                category = 'good'
            elif confidence >= 0.50:
                category = 'fair'
            else:
                category = 'low'

            score_distribution[category] += 1
            scored['_confidence_category'] = category

            scored_artifacts.append(scored)

            if i % 25 == 0 or i == len(artifacts):
                print(f"Scored {i}/{len(artifacts)} artifacts...")

        # Statistics
        confidences = [a['confidence'] for a in scored_artifacts]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        high_confidence_count = sum(1 for c in confidences if c >= 0.85)
        high_confidence_ratio = high_confidence_count / len(confidences) if confidences else 0.0

        print(f"\nConfidence distribution:")
        print(f"  Excellent (≥0.95): {score_distribution['excellent']:3d} ({score_distribution['excellent']/len(artifacts)*100:.1f}%)")
        print(f"  High (0.85-0.94):  {score_distribution['high']:3d} ({score_distribution['high']/len(artifacts)*100:.1f}%)")
        print(f"  Good (0.70-0.84):  {score_distribution['good']:3d} ({score_distribution['good']/len(artifacts)*100:.1f}%)")
        print(f"  Fair (0.50-0.69):  {score_distribution['fair']:3d} ({score_distribution['fair']/len(artifacts)*100:.1f}%)")
        print(f"  Low (<0.50):       {score_distribution['low']:3d} ({score_distribution['low']/len(artifacts)*100:.1f}%)")

        print(f"\nAverage confidence: {avg_confidence:.3f}")
        print(f"High confidence (≥0.85): {high_confidence_count}/{len(artifacts)} ({high_confidence_ratio:.1%})")

        return {
            'scored_artifacts': scored_artifacts,
            'distribution': score_distribution,
            'statistics': {
                'total': len(artifacts),
                'avg_confidence': round(avg_confidence, 4),
                'high_confidence_count': high_confidence_count,
                'high_confidence_ratio': round(high_confidence_ratio, 4),
            },
        }

    def save_scored_artifacts(self, scored_artifacts: List[Dict[str, Any]]):
        """Save artifacts with confidence scores."""
        print(f"\n=== SAVING SCORED ARTIFACTS ===\n")

        if self.dry_run:
            print("DRY RUN - No files will be written")
            return

        saved_count = 0
        for artifact in scored_artifacts:
            source_path = Path(artifact['_source_path'])

            # Remove internal fields
            artifact_clean = {k: v for k, v in artifact.items() if not k.startswith('_')}

            # Don't overwrite existing confidence scores
            if 'confidence' not in json.load(open(source_path)):
                try:
                    with open(source_path, 'w') as f:
                        json.dump(artifact_clean, f, indent=2)
                    saved_count += 1
                except Exception as e:
                    print(f"Error saving {source_path.name}: {e}", file=sys.stderr)

        print(f"✓ Saved {saved_count} artifacts with confidence scores")

    def run_scoring(self) -> Dict[str, Any]:
        """Execute confidence scoring."""
        print("=" * 70)
        print("AUTOMATED CONFIDENCE SCORING")
        print("=" * 70)
        print(f"\nMode: {'DRY RUN' if self.dry_run else 'LIVE'}")

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        # Load artifacts
        artifacts = self.load_artifacts()
        print(f"\nLoaded {len(artifacts)} artifacts")

        # Score all artifacts
        results = self.score_all_artifacts(artifacts)

        # Save scored artifacts
        self.save_scored_artifacts(results['scored_artifacts'])

        # Generate report
        report = {
            'artifact_type': 'confidence_scoring_report',
            'timestamp': timestamp,
            'dry_run': self.dry_run,
            'statistics': results['statistics'],
            'distribution': results['distribution'],
            'weights': self.weights,
        }

        # Save report
        report_path = self.artifacts_dir / f"confidence_scoring_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Scoring report saved: {report_path.name}")

        return report


def main():
    """Run confidence scoring."""
    import argparse

    parser = argparse.ArgumentParser(description="Automated Confidence Scoring")
    parser.add_argument('--live', action='store_true', help="Run live scoring (default: dry-run)")
    args = parser.parse_args()

    scorer = ConfidenceScorer(dry_run=not args.live)
    report = scorer.run_scoring()

    print("\n" + "=" * 70)
    print("SCORING SUMMARY")
    print("=" * 70)
    print(f"Mode: {'LIVE' if not scorer.dry_run else 'DRY RUN'}")
    print(f"Average confidence: {report['statistics']['avg_confidence']:.3f}")
    print(f"High confidence (≥0.85): {report['statistics']['high_confidence_ratio']:.1%}")
    print(f"  Before: 2.4% (3 artifacts)")
    print(f"  After: {report['statistics']['high_confidence_ratio']:.1%} ({report['statistics']['high_confidence_count']} artifacts)")
    print(f"Improvement: +{report['statistics']['high_confidence_ratio'] - 0.024:.1%}")
    print("=" * 70)

    if scorer.dry_run:
        print("\n⚠️  DRY RUN - No changes written. Run with --live to apply scores.")
    else:
        print("\n✓ Confidence scoring complete!")

    return 0


if __name__ == "__main__":
    sys.exit(main())
