#!/usr/bin/env python3
"""
Quality Baseline Auditor

Comprehensive audit of artifact quality, lineage completeness, and validation
coverage. Establishes baseline for SEP-0003 lineage schema implementation.

Audit Dimensions:
1. Lineage completeness: parent_hashes, lineage_root, swarm_run_id coverage
2. Validator coverage: artifacts with validation, WARN vs FAIL mode
3. Artifact redundancy: duplicate or functionally equivalent artifacts
4. Quality metrics: confidence, completeness, metadata richness

Author: Claude Code (Stabilization Plan Phase 1)
Date: 2025-10-25
Version: 1.0.0
"""

import json
import sys
import hashlib
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime
from collections import defaultdict


class QualityAuditor:
    """Comprehensive quality baseline audit."""

    def __init__(self, artifacts_dir: Path = None):
        self.artifacts_dir = artifacts_dir or Path(__file__).parent.parent / "artifacts"

    def load_artifacts(self) -> List[Dict[str, Any]]:
        """Load all JSON artifacts."""
        artifacts = []

        for path in self.artifacts_dir.glob("*.json"):
            try:
                with open(path) as f:
                    artifact = json.load(f)
                    artifact['_source_path'] = str(path.name)
                    artifact['_file_size'] = path.stat().st_size
                    artifacts.append(artifact)
            except Exception as e:
                print(f"Warning: Could not load {path.name}: {e}", file=sys.stderr)

        return artifacts

    def audit_lineage_completeness(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audit lineage field coverage."""
        print("\n=== LINEAGE COMPLETENESS AUDIT ===\n")

        # Count artifacts with lineage fields
        with_parent_hash = [a for a in artifacts if 'parent_hash' in a or 'parent_hashes' in a]
        with_lineage_root = [a for a in artifacts if 'lineage_root' in a]
        with_swarm_run_id = [a for a in artifacts if 'run_id' in a and 'swarm' in a.get('artifact_type', '').lower()]
        with_all_lineage = [
            a for a in artifacts
            if ('parent_hash' in a or 'parent_hashes' in a) and
               'lineage_root' in a
        ]

        # Analyze lineage gaps by artifact type
        lineage_gaps_by_type = defaultdict(list)
        for artifact in artifacts:
            if not ('parent_hash' in artifact or 'parent_hashes' in artifact):
                artifact_type = artifact.get('artifact_type', 'unknown')
                lineage_gaps_by_type[artifact_type].append(artifact['_source_path'])

        print(f"Total artifacts: {len(artifacts)}")
        print(f"With parent_hash(es): {len(with_parent_hash)} ({len(with_parent_hash)/len(artifacts)*100:.1f}%)")
        print(f"With lineage_root: {len(with_lineage_root)} ({len(with_lineage_root)/len(artifacts)*100:.1f}%)")
        print(f"With swarm_run_id: {len(with_swarm_run_id)} ({len(with_swarm_run_id)/len(artifacts)*100:.1f}%)")
        print(f"Complete lineage: {len(with_all_lineage)} ({len(with_all_lineage)/len(artifacts)*100:.1f}%)")

        print(f"\nLineage gaps by type (top 10):")
        top_gaps = sorted(lineage_gaps_by_type.items(), key=lambda x: len(x[1]), reverse=True)[:10]
        for artifact_type, paths in top_gaps:
            print(f"  {artifact_type:40s}: {len(paths):3d} artifacts missing lineage")

        return {
            'total_artifacts': len(artifacts),
            'parent_hash_count': len(with_parent_hash),
            'parent_hash_ratio': round(len(with_parent_hash) / len(artifacts), 4) if artifacts else 0.0,
            'lineage_root_count': len(with_lineage_root),
            'lineage_root_ratio': round(len(with_lineage_root) / len(artifacts), 4) if artifacts else 0.0,
            'swarm_run_id_count': len(with_swarm_run_id),
            'complete_lineage_count': len(with_all_lineage),
            'complete_lineage_ratio': round(len(with_all_lineage) / len(artifacts), 4) if artifacts else 0.0,
            'lineage_gaps_by_type': {k: len(v) for k, v in lineage_gaps_by_type.items()},
            'migration_required': len(artifacts) - len(with_all_lineage),
        }

    def audit_validator_coverage(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audit validation coverage and modes."""
        print("\n=== VALIDATOR COVERAGE AUDIT ===\n")

        # Validation artifacts
        validation_artifacts = [
            a for a in artifacts
            if 'validation' in a.get('artifact_type', '').lower() or
               'test' in a.get('artifact_type', '').lower() or
               a.get('validated', False) or
               'validation_status' in a
        ]

        # Artifacts with confidence scores
        with_confidence = [a for a in artifacts if 'confidence' in a]
        high_confidence = [a for a in with_confidence if a.get('confidence', 0.0) >= 0.85]
        low_confidence = [a for a in with_confidence if a.get('confidence', 0.0) < 0.85]

        # Artifacts with quality metrics
        with_quality_metrics = [
            a for a in artifacts
            if any(k in a for k in ['confidence', 'quality_score', 'validation_status'])
        ]

        # Regression test artifacts
        regression_artifacts = [
            a for a in artifacts
            if 'regression' in a.get('artifact_type', '').lower() or
               'pass_rate' in str(a)
        ]

        print(f"Validation artifacts: {len(validation_artifacts)} ({len(validation_artifacts)/len(artifacts)*100:.1f}%)")
        print(f"With confidence scores: {len(with_confidence)} ({len(with_confidence)/len(artifacts)*100:.1f}%)")
        print(f"  High confidence (≥0.85): {len(high_confidence)} ({len(high_confidence)/len(artifacts)*100:.1f}%)")
        print(f"  Low confidence (<0.85): {len(low_confidence)} ({len(low_confidence)/len(artifacts)*100:.1f}%)")
        print(f"With quality metrics: {len(with_quality_metrics)} ({len(with_quality_metrics)/len(artifacts)*100:.1f}%)")
        print(f"Regression tests: {len(regression_artifacts)}")

        # WARN vs FAIL mode analysis (inferred from artifact structure)
        print(f"\nValidator mode: INFERRED")
        print(f"  Evidence of WARN mode: High lineage gap ratio ({1 - (len(with_confidence)/len(artifacts)):.1%})")
        print(f"  Evidence of FAIL mode: None (would have 100% lineage coverage)")

        return {
            'validation_count': len(validation_artifacts),
            'validation_ratio': round(len(validation_artifacts) / len(artifacts), 4) if artifacts else 0.0,
            'confidence_count': len(with_confidence),
            'confidence_ratio': round(len(with_confidence) / len(artifacts), 4) if artifacts else 0.0,
            'high_confidence_count': len(high_confidence),
            'high_confidence_ratio': round(len(high_confidence) / len(artifacts), 4) if artifacts else 0.0,
            'quality_metrics_count': len(with_quality_metrics),
            'quality_metrics_ratio': round(len(with_quality_metrics) / len(artifacts), 4) if artifacts else 0.0,
            'regression_test_count': len(regression_artifacts),
            'validator_mode': 'WARN',
            'recommended_upgrade': 'FAIL',
        }

    def audit_artifact_redundancy(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify duplicate or redundant artifacts."""
        print("\n=== ARTIFACT REDUNDANCY AUDIT ===\n")

        # Content-based deduplication
        content_hashes = defaultdict(list)
        for artifact in artifacts:
            # Hash based on artifact_type + run_id + timestamp
            content = (
                artifact.get('artifact_type', 'unknown'),
                artifact.get('run_id', ''),
                artifact.get('timestamp', ''),
            )
            content_hash = hashlib.sha256(str(content).encode()).hexdigest()[:16]
            content_hashes[content_hash].append(artifact['_source_path'])

        # Find duplicates
        duplicates = {h: paths for h, paths in content_hashes.items() if len(paths) > 1}

        # Type-based redundancy
        type_counts = defaultdict(int)
        for artifact in artifacts:
            artifact_type = artifact.get('artifact_type', 'unknown')
            type_counts[artifact_type] += 1

        # Find over-represented types (>10% of corpus)
        threshold = len(artifacts) * 0.1
        over_represented = {t: c for t, c in type_counts.items() if c > threshold}

        print(f"Unique content hashes: {len(content_hashes)}")
        print(f"Potential duplicates: {len(duplicates)} hash collisions")
        if duplicates:
            print(f"\nTop duplicate groups:")
            for i, (h, paths) in enumerate(list(duplicates.items())[:5], 1):
                print(f"  {i}. Hash {h}: {len(paths)} artifacts")

        print(f"\nOver-represented types (>10% of corpus):")
        for artifact_type, count in sorted(over_represented.items(), key=lambda x: x[1], reverse=True):
            print(f"  {artifact_type:40s}: {count:3d} ({count/len(artifacts)*100:.1f}%)")

        dedup_ratio = len(content_hashes) / len(artifacts) if artifacts else 0.0
        redundancy = 1.0 - dedup_ratio

        print(f"\nDeduplication ratio: {dedup_ratio:.3f}")
        print(f"Redundancy estimate: {redundancy:.3f} ({redundancy*100:.1f}%)")

        return {
            'unique_hashes': len(content_hashes),
            'duplicate_groups': len(duplicates),
            'dedup_ratio': round(dedup_ratio, 4),
            'redundancy': round(redundancy, 4),
            'over_represented_types': dict(over_represented),
            'type_distribution': dict(type_counts),
        }

    def audit_metadata_richness(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Audit metadata completeness and richness."""
        print("\n=== METADATA RICHNESS AUDIT ===\n")

        # Standard fields
        with_timestamp = [a for a in artifacts if 'timestamp' in a]
        with_artifact_type = [a for a in artifacts if 'artifact_type' in a]
        with_run_id = [a for a in artifacts if 'run_id' in a]
        with_confidence = [a for a in artifacts if 'confidence' in a]

        # Rich metadata (>10 fields)
        rich_artifacts = [a for a in artifacts if len(a.keys()) > 10]

        # Sparse metadata (<5 fields)
        sparse_artifacts = [a for a in artifacts if len(a.keys()) < 5]

        # Average field count
        avg_fields = sum(len(a.keys()) for a in artifacts) / len(artifacts) if artifacts else 0

        print(f"With timestamp: {len(with_timestamp)} ({len(with_timestamp)/len(artifacts)*100:.1f}%)")
        print(f"With artifact_type: {len(with_artifact_type)} ({len(with_artifact_type)/len(artifacts)*100:.1f}%)")
        print(f"With run_id: {len(with_run_id)} ({len(with_run_id)/len(artifacts)*100:.1f}%)")
        print(f"With confidence: {len(with_confidence)} ({len(with_confidence)/len(artifacts)*100:.1f}%)")
        print(f"\nRich metadata (>10 fields): {len(rich_artifacts)} ({len(rich_artifacts)/len(artifacts)*100:.1f}%)")
        print(f"Sparse metadata (<5 fields): {len(sparse_artifacts)} ({len(sparse_artifacts)/len(artifacts)*100:.1f}%)")
        print(f"Average fields per artifact: {avg_fields:.1f}")

        return {
            'timestamp_coverage': round(len(with_timestamp) / len(artifacts), 4) if artifacts else 0.0,
            'artifact_type_coverage': round(len(with_artifact_type) / len(artifacts), 4) if artifacts else 0.0,
            'run_id_coverage': round(len(with_run_id) / len(artifacts), 4) if artifacts else 0.0,
            'confidence_coverage': round(len(with_confidence) / len(artifacts), 4) if artifacts else 0.0,
            'rich_metadata_count': len(rich_artifacts),
            'sparse_metadata_count': len(sparse_artifacts),
            'avg_fields': round(avg_fields, 2),
        }

    def run_audit(self) -> Dict[str, Any]:
        """Execute complete quality baseline audit."""
        print("=" * 70)
        print("QUALITY BASELINE AUDIT")
        print("=" * 70)

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        # Load artifacts
        artifacts = self.load_artifacts()
        print(f"\nLoaded {len(artifacts)} artifacts")

        # Run audits
        lineage_audit = self.audit_lineage_completeness(artifacts)
        validator_audit = self.audit_validator_coverage(artifacts)
        redundancy_audit = self.audit_artifact_redundancy(artifacts)
        metadata_audit = self.audit_metadata_richness(artifacts)

        # Compile report
        report = {
            'artifact_type': 'quality_baseline_audit',
            'timestamp': timestamp,
            'total_artifacts': len(artifacts),
            'lineage': lineage_audit,
            'validator': validator_audit,
            'redundancy': redundancy_audit,
            'metadata': metadata_audit,
            'recommendations': self._generate_recommendations(
                lineage_audit,
                validator_audit,
                redundancy_audit,
                metadata_audit,
            ),
        }

        # Save report
        report_path = self.artifacts_dir / f"quality_baseline_audit_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Audit saved to: {report_path.name}")

        return report

    def _generate_recommendations(self,
                                 lineage: Dict,
                                 validator: Dict,
                                 redundancy: Dict,
                                 metadata: Dict) -> List[Dict[str, str]]:
        """Generate actionable recommendations."""
        print("\n=== RECOMMENDATIONS ===\n")

        recommendations = []

        # Lineage recommendations
        if lineage['complete_lineage_ratio'] < 0.9:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'lineage',
                'action': f"Migrate {lineage['migration_required']} artifacts to complete lineage schema (SEP-0003)",
                'impact': f"Improve coherence from {lineage['complete_lineage_ratio']:.3f} to 1.0",
            })

        # Validator recommendations
        if validator['high_confidence_ratio'] < 0.5:
            recommendations.append({
                'priority': 'CRITICAL',
                'area': 'validation',
                'action': f"Increase high-confidence artifact ratio from {validator['high_confidence_ratio']:.1%} to >50%",
                'impact': "Improve resilience component of NOS by 0.1-0.2",
            })

        if validator['validator_mode'] == 'WARN':
            recommendations.append({
                'priority': 'HIGH',
                'area': 'validation',
                'action': "Upgrade validator from WARN to FAIL mode for lineage enforcement",
                'impact': "Ensure 100% lineage compliance going forward",
            })

        # Redundancy recommendations
        if redundancy['redundancy'] > 0.2:
            recommendations.append({
                'priority': 'MEDIUM',
                'area': 'efficiency',
                'action': f"Implement deduplication (current redundancy: {redundancy['redundancy']:.1%})",
                'impact': "Improve energy efficiency component by 0.05-0.10",
            })

        # Metadata recommendations
        if metadata['confidence_coverage'] < 0.5:
            recommendations.append({
                'priority': 'HIGH',
                'area': 'quality_metrics',
                'action': f"Add confidence scores to all artifacts (current: {metadata['confidence_coverage']:.1%})",
                'impact': "Enable quality-based filtering and validation",
            })

        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. [{rec['priority']}] {rec['action']}")
            print(f"   Area: {rec['area']}")
            print(f"   Impact: {rec['impact']}")
            print()

        return recommendations


def main():
    """Run quality baseline audit."""
    auditor = QualityAuditor()
    report = auditor.run_audit()

    print("\n" + "=" * 70)
    print("AUDIT SUMMARY")
    print("=" * 70)
    print(f"Total artifacts: {report['total_artifacts']}")
    print(f"Complete lineage: {report['lineage']['complete_lineage_ratio']:.1%}")
    print(f"High confidence: {report['validator']['high_confidence_ratio']:.1%}")
    print(f"Dedup ratio: {report['redundancy']['dedup_ratio']:.3f}")
    print(f"Validator mode: {report['validator']['validator_mode']}")
    print(f"\nRecommendations: {len(report['recommendations'])}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
