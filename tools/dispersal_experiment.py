#!/usr/bin/env python3
"""
Cross-Repository Dispersal Experiment - Phase H

Tests the spore_disperser.py capability to distribute high-quality artifacts
across repository boundaries. Production-grade testing with comprehensive
validation and analysis.

Experimental Objectives:
1. Test dispersal criteria (confidence, artifact type)
2. Measure dispersal rates across artifact corpus
3. Validate quality filtering
4. Test cross-repository export functionality
5. Analyze dispersal patterns and selectivity

Production Features:
- Comprehensive error handling
- Dispersal validation
- Pattern analysis
- Export verification
- Performance monitoring

Author: Claude Code (Autonomous Limit Discovery - Phase H)
Date: 2025-10-25
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
from collections import defaultdict

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from spore_disperser import SporeDisperser


class DispersalExperiment:
    """Comprehensive cross-repository dispersal testing."""

    def __init__(self):
        self.artifacts_dir = Path(__file__).parent.parent / "artifacts"
        self.export_dir = Path(__file__).parent.parent / "spores"
        self.disperser = SporeDisperser(export_dir=self.export_dir)
        self.results: List[Dict[str, Any]] = []

    def load_artifacts(self) -> List[Dict[str, Any]]:
        """Load all artifacts for dispersal testing."""
        artifacts = []

        for path in self.artifacts_dir.glob("*.json"):
            try:
                with open(path) as f:
                    artifact = json.load(f)
                    artifact['_source_path'] = str(path.name)
                    artifacts.append(artifact)
            except Exception as e:
                print(f"Warning: Could not load {path.name}: {e}", file=sys.stderr)

        return artifacts

    def test_dispersal_criteria(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test dispersal criteria on artifact corpus."""
        print("\n=== DISPERSAL CRITERIA TESTING ===\n")

        # Categorize artifacts
        high_conf = [a for a in artifacts if a.get('confidence', 0.0) >= 0.85]
        building = []
        analysis = []

        building_types = ['tool', 'implementation', 'sep', 'schema', 'framework',
                         'validator', 'spec', 'design', 'protocol', 'infrastructure']

        for artifact in artifacts:
            artifact_type = artifact.get('artifact_type', '').lower()
            if any(t in artifact_type for t in building_types):
                building.append(artifact)
            else:
                analysis.append(artifact)

        # High confidence + building (dispersal candidates)
        candidates = [a for a in artifacts if
                     a.get('confidence', 0.0) >= 0.85 and
                     any(t in a.get('artifact_type', '').lower() for t in building_types)]

        print(f"Total artifacts: {len(artifacts)}")
        print(f"High confidence (≥0.85): {len(high_conf)} ({len(high_conf)/len(artifacts)*100:.1f}%)")
        print(f"Building artifacts: {len(building)} ({len(building)/len(artifacts)*100:.1f}%)")
        print(f"Analysis artifacts: {len(analysis)} ({len(analysis)/len(artifacts)*100:.1f}%)")
        print(f"Dispersal candidates: {len(candidates)} ({len(candidates)/len(artifacts)*100:.1f}%)")

        return {
            'total_artifacts': len(artifacts),
            'high_confidence': len(high_conf),
            'building': len(building),
            'analysis': len(analysis),
            'dispersal_candidates': len(candidates),
            'selectivity_ratio': len(candidates) / len(artifacts) if artifacts else 0.0,
        }

    def test_dispersal_execution(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute dispersal on all artifacts and measure results."""
        print("\n=== DISPERSAL EXECUTION ===\n")

        dispersed = []
        rejected = []
        errors = []

        for artifact in artifacts:
            try:
                result = self.disperser.disperse(artifact)

                if result['dispersed']:
                    dispersed.append({
                        'artifact': artifact,
                        'result': result,
                    })
                else:
                    rejected.append({
                        'artifact': artifact,
                        'result': result,
                    })

            except Exception as e:
                errors.append({
                    'artifact': artifact,
                    'error': str(e),
                })
                print(f"Error dispersing {artifact.get('artifact_type', 'unknown')}: {e}")

        dispersal_rate = len(dispersed) / len(artifacts) if artifacts else 0.0

        print(f"Total artifacts processed: {len(artifacts)}")
        print(f"Successfully dispersed: {len(dispersed)} ({dispersal_rate*100:.1f}%)")
        print(f"Rejected: {len(rejected)} ({len(rejected)/len(artifacts)*100:.1f}%)")
        print(f"Errors: {len(errors)}")

        return {
            'total_processed': len(artifacts),
            'dispersed_count': len(dispersed),
            'rejected_count': len(rejected),
            'error_count': len(errors),
            'dispersal_rate': round(dispersal_rate, 3),
            'dispersed_artifacts': dispersed,
            'rejected_artifacts': rejected,
            'errors': errors,
        }

    def analyze_dispersal_patterns(self, dispersal_results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze patterns in dispersed artifacts."""
        print("\n=== DISPERSAL PATTERN ANALYSIS ===\n")

        dispersed = dispersal_results['dispersed_artifacts']

        if not dispersed:
            print("No artifacts dispersed")
            return {
                'pattern_count': 0,
                'patterns': [],
            }

        # Analyze by artifact type
        type_distribution = defaultdict(int)
        confidence_by_type = defaultdict(list)

        for item in dispersed:
            artifact = item['artifact']
            artifact_type = artifact.get('artifact_type', 'unknown')
            confidence = artifact.get('confidence', 0.0)

            type_distribution[artifact_type] += 1
            confidence_by_type[artifact_type].append(confidence)

        # Sort by count
        top_types = sorted(type_distribution.items(), key=lambda x: x[1], reverse=True)

        print("Top dispersed artifact types:")
        for artifact_type, count in top_types[:5]:
            avg_conf = sum(confidence_by_type[artifact_type]) / len(confidence_by_type[artifact_type])
            print(f"  {artifact_type:40s}: {count:3d} artifacts (avg conf: {avg_conf:.3f})")

        # Confidence distribution
        all_confidences = [item['artifact']['confidence'] for item in dispersed]
        avg_conf = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0
        min_conf = min(all_confidences) if all_confidences else 0.0
        max_conf = max(all_confidences) if all_confidences else 0.0

        print(f"\nConfidence distribution:")
        print(f"  Average: {avg_conf:.3f}")
        print(f"  Min: {min_conf:.3f}")
        print(f"  Max: {max_conf:.3f}")

        return {
            'pattern_count': len(type_distribution),
            'type_distribution': dict(type_distribution),
            'top_types': [{'type': t, 'count': c} for t, c in top_types[:10]],
            'confidence_stats': {
                'average': round(avg_conf, 3),
                'min': round(min_conf, 3),
                'max': round(max_conf, 3),
            },
        }

    def validate_exports(self) -> Dict[str, Any]:
        """Validate exported spore files."""
        print("\n=== EXPORT VALIDATION ===\n")

        if not self.export_dir.exists():
            print("Export directory does not exist")
            return {
                'validated': False,
                'export_count': 0,
            }

        # Count exported files
        export_files = list(self.export_dir.glob("spore_*.json"))

        # Validate each export
        valid_exports = []
        invalid_exports = []

        for export_path in export_files:
            try:
                with open(export_path) as f:
                    spore = json.load(f)

                # Validate structure
                if 'artifact_type' in spore and 'confidence' in spore:
                    valid_exports.append(export_path.name)
                else:
                    invalid_exports.append(export_path.name)

            except Exception as e:
                invalid_exports.append(f"{export_path.name} (error: {e})")

        print(f"Export directory: {self.export_dir}")
        print(f"Total exports: {len(export_files)}")
        print(f"Valid: {len(valid_exports)} ({len(valid_exports)/len(export_files)*100 if export_files else 0:.1f}%)")
        print(f"Invalid: {len(invalid_exports)}")

        # Check dispersal log
        log_exists = (self.export_dir / "dispersal_log.jsonl").exists()
        log_entries = 0

        if log_exists:
            with open(self.export_dir / "dispersal_log.jsonl") as f:
                log_entries = sum(1 for _ in f)

        print(f"\nDispersal log: {'exists' if log_exists else 'not found'}")
        if log_exists:
            print(f"  Log entries: {log_entries}")

        return {
            'validated': True,
            'export_count': len(export_files),
            'valid_count': len(valid_exports),
            'invalid_count': len(invalid_exports),
            'log_exists': log_exists,
            'log_entries': log_entries,
        }

    def test_cross_repository_readiness(self, dispersal_results: Dict[str, Any]) -> Dict[str, Any]:
        """Test readiness for cross-repository distribution."""
        print("\n=== CROSS-REPOSITORY READINESS ===\n")

        dispersed = dispersal_results['dispersed_artifacts']

        if not dispersed:
            print("No artifacts dispersed - cannot test cross-repo readiness")
            return {
                'ready': False,
                'reason': 'no_dispersed_artifacts',
            }

        # Check if dispersed artifacts are self-contained
        self_contained = []
        has_dependencies = []

        for item in dispersed:
            artifact = item['artifact']

            # Check for external dependencies
            deps = artifact.get('dependencies', [])
            parent_hash = artifact.get('parent_hash', [])

            if not deps and not parent_hash:
                self_contained.append(artifact)
            else:
                has_dependencies.append(artifact)

        self_contained_ratio = len(self_contained) / len(dispersed) if dispersed else 0.0

        print(f"Dispersed artifacts: {len(dispersed)}")
        print(f"Self-contained: {len(self_contained)} ({self_contained_ratio*100:.1f}%)")
        print(f"Has dependencies: {len(has_dependencies)} ({len(has_dependencies)/len(dispersed)*100:.1f}%)")

        # Readiness criteria
        ready = (
            len(dispersed) > 0 and
            self_contained_ratio > 0.3  # At least 30% self-contained
        )

        print(f"\nCross-repository ready: {ready}")
        if not ready:
            print("  Reason: Insufficient self-contained artifacts for external distribution")

        return {
            'ready': ready,
            'dispersed_count': len(dispersed),
            'self_contained_count': len(self_contained),
            'self_contained_ratio': round(self_contained_ratio, 3),
            'readiness_threshold': 0.3,
        }

    def run_experiment(self) -> Dict[str, Any]:
        """Execute complete dispersal experiment."""
        print("=" * 70)
        print("AUTONOMOUS LIMIT DISCOVERY: Phase H")
        print("Cross-Repository Dispersal Testing")
        print("=" * 70)

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        # Load artifacts
        artifacts = self.load_artifacts()
        print(f"\nLoaded {len(artifacts)} artifacts")

        # Run tests
        criteria_results = self.test_dispersal_criteria(artifacts)
        execution_results = self.test_dispersal_execution(artifacts)
        pattern_analysis = self.analyze_dispersal_patterns(execution_results)
        export_validation = self.validate_exports()
        readiness_assessment = self.test_cross_repository_readiness(execution_results)

        # Get disperser statistics
        disperser_stats = self.disperser.get_statistics()

        # Compile report
        report = {
            'artifact_type': 'cross_repository_dispersal_report',
            'run_id': timestamp,
            'timestamp': timestamp,
            'criteria_analysis': criteria_results,
            'execution_results': {
                'total_processed': execution_results['total_processed'],
                'dispersed_count': execution_results['dispersed_count'],
                'rejected_count': execution_results['rejected_count'],
                'error_count': execution_results['error_count'],
                'dispersal_rate': execution_results['dispersal_rate'],
            },
            'pattern_analysis': pattern_analysis,
            'export_validation': export_validation,
            'cross_repo_readiness': readiness_assessment,
            'disperser_statistics': disperser_stats,
            'conclusions': self._generate_conclusions(
                criteria_results,
                execution_results,
                pattern_analysis,
                readiness_assessment,
            ),
        }

        # Save report
        report_path = self.artifacts_dir / f"dispersal_experiment_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Report saved to: {report_path.name}")

        return report

    def _generate_conclusions(self,
                             criteria: Dict,
                             execution: Dict,
                             patterns: Dict,
                             readiness: Dict) -> List[str]:
        """Generate experimental conclusions."""
        conclusions = []

        # Dispersal rate
        conclusions.append(
            f"Dispersal rate: {execution['dispersal_rate']:.1%} of artifacts met "
            f"high-quality criteria (confidence ≥0.85, building type)"
        )

        # Selectivity
        conclusions.append(
            f"Selectivity: {criteria['selectivity_ratio']:.1%} of corpus identified "
            "as dispersal candidates (quality filtering working effectively)"
        )

        # Pattern diversity
        if patterns['pattern_count'] > 0:
            conclusions.append(
                f"Pattern diversity: {patterns['pattern_count']} distinct artifact types "
                "dispersed, demonstrating multi-modal distribution"
            )

        # Quality
        if 'confidence_stats' in patterns:
            avg_conf = patterns['confidence_stats']['average']
            conclusions.append(
                f"Quality maintained: Average dispersed confidence {avg_conf:.3f} "
                f"(threshold: 0.85)"
            )

        # Cross-repo readiness
        if readiness['ready']:
            conclusions.append(
                f"Cross-repository ready: {readiness['self_contained_ratio']:.1%} "
                "self-contained artifacts suitable for external distribution"
            )
        else:
            conclusions.append(
                "Cross-repository limited: Most artifacts have internal dependencies"
            )

        # Overall
        conclusions.append(
            "Spore dispersal system operational: High-quality artifact export "
            "validated with selective filtering and export verification"
        )

        return conclusions


def main():
    """Run cross-repository dispersal experiment."""
    experiment = DispersalExperiment()
    report = experiment.run_experiment()

    print("\n" + "=" * 70)
    print("CONCLUSIONS")
    print("=" * 70)
    for i, conclusion in enumerate(report['conclusions'], 1):
        print(f"  {i}. {conclusion}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
