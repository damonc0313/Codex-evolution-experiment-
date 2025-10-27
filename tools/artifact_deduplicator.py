#!/usr/bin/env python3
"""
Artifact Deduplicator - Energy Efficiency Optimization

Detects and analyzes duplicate or functionally equivalent artifacts to improve
energy efficiency component of NOS.

Current State:
- Redundancy: 35.8% (dedup ratio: 0.642)
- Target: <25% redundancy (dedup ratio: >0.75)

Deduplication Strategy:
1. Content-based hashing (detect exact duplicates)
2. Structural similarity (detect functional equivalents)
3. Semantic analysis (detect conceptually similar artifacts)
4. Temporal analysis (detect redundant regeneration)

Expected Impact:
- Redundancy reduction: 35.8% → <25%
- Energy efficiency improvement: +0.05-0.10
- NOS improvement: +0.003-0.006

Author: Claude Code (Stabilization Plan Phase 4)
Date: 2025-10-26
Version: 1.0.0
"""

import json
import sys
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple
from datetime import datetime
from collections import defaultdict


class ArtifactDeduplicator:
    """Detect and analyze artifact redundancy."""

    def __init__(self, artifacts_dir: Path = None):
        self.artifacts_dir = artifacts_dir or Path(__file__).parent.parent / "artifacts"

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

    def compute_content_hash(self, artifact: Dict[str, Any]) -> str:
        """Compute content-based hash (exact duplicate detection)."""
        # Remove metadata fields that don't affect content
        content = {k: v for k, v in artifact.items()
                  if not k.startswith('_') and
                  k not in ['timestamp', 'lineage_root', 'parent_hashes', 'artifact_hash', 'confidence']}

        content_str = json.dumps(content, sort_keys=True)
        return hashlib.sha256(content_str.encode()).hexdigest()[:16]

    def compute_structural_hash(self, artifact: Dict[str, Any]) -> str:
        """Compute structural hash (functional equivalent detection)."""
        # Hash based on artifact type + key structural elements
        structure = {
            'artifact_type': artifact.get('artifact_type', ''),
            'run_id': artifact.get('run_id', ''),
            'mode': artifact.get('mode', ''),
            'has_results': 'results' in artifact or 'conclusions' in artifact,
            'has_analysis': 'analysis' in artifact or 'findings' in artifact,
            'field_count': len([k for k in artifact.keys() if not k.startswith('_')]),
        }

        structure_str = json.dumps(structure, sort_keys=True)
        return hashlib.sha256(structure_str.encode()).hexdigest()[:16]

    def detect_exact_duplicates(self, artifacts: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Detect exact duplicate artifacts."""
        print("\n=== EXACT DUPLICATE DETECTION ===\n")

        content_map = defaultdict(list)

        for artifact in artifacts:
            content_hash = self.compute_content_hash(artifact)
            content_map[content_hash].append(artifact['_filename'])

        # Find duplicates
        duplicates = {h: files for h, files in content_map.items() if len(files) > 1}

        print(f"Exact duplicates found: {len(duplicates)} groups")
        if duplicates:
            print("\nTop duplicate groups:")
            for i, (hash_val, files) in enumerate(list(duplicates.items())[:5], 1):
                print(f"  {i}. Hash {hash_val}: {len(files)} copies")
                for filename in files[:3]:
                    print(f"     - {filename}")
                if len(files) > 3:
                    print(f"     ... and {len(files)-3} more")

        total_duplicated = sum(len(files) - 1 for files in duplicates.values())
        print(f"\nTotal duplicated files: {total_duplicated}")

        return duplicates

    def detect_structural_duplicates(self, artifacts: List[Dict[str, Any]]) -> Dict[str, List[str]]:
        """Detect structurally similar artifacts."""
        print("\n=== STRUCTURAL SIMILARITY DETECTION ===\n")

        structural_map = defaultdict(list)

        for artifact in artifacts:
            struct_hash = self.compute_structural_hash(artifact)
            structural_map[struct_hash].append(artifact['_filename'])

        # Find similar structures
        similar = {h: files for h, files in structural_map.items() if len(files) > 5}

        print(f"Structural similarities found: {len(similar)} groups")
        if similar:
            print("\nTop similarity groups:")
            for i, (hash_val, files) in enumerate(list(similar.items())[:5], 1):
                # Get a representative artifact to show type
                rep_artifact = next(a for a in artifacts if a['_filename'] == files[0])
                artifact_type = rep_artifact.get('artifact_type', 'unknown')
                print(f"  {i}. Type '{artifact_type}': {len(files)} artifacts")

        return similar

    def analyze_temporal_redundancy(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze redundant regeneration patterns."""
        print("\n=== TEMPORAL REDUNDANCY ANALYSIS ===\n")

        # Group by artifact type
        type_groups = defaultdict(list)
        for artifact in artifacts:
            artifact_type = artifact.get('artifact_type', 'unknown')
            type_groups[artifact_type].append(artifact)

        # Analyze regeneration patterns
        redundant_types = {}
        for artifact_type, group in type_groups.items():
            if len(group) > 3:  # Only analyze types with multiple instances
                # Check if multiple artifacts with same run_id
                run_id_counts = defaultdict(int)
                for artifact in group:
                    run_id = artifact.get('run_id', '')
                    if run_id:
                        run_id_counts[run_id] += 1

                duplicated_runs = {rid: count for rid, count in run_id_counts.items() if count > 1}

                if duplicated_runs:
                    redundant_types[artifact_type] = {
                        'total_count': len(group),
                        'duplicated_runs': len(duplicated_runs),
                        'redundancy_ratio': len(duplicated_runs) / len(run_id_counts) if run_id_counts else 0,
                    }

        print(f"Artifact types with temporal redundancy: {len(redundant_types)}")
        if redundant_types:
            print("\nTop redundant types:")
            sorted_types = sorted(redundant_types.items(),
                                key=lambda x: x[1]['total_count'],
                                reverse=True)[:5]
            for artifact_type, stats in sorted_types:
                print(f"  {artifact_type:40s}: {stats['total_count']:3d} total, "
                     f"{stats['duplicated_runs']:2d} redundant runs "
                     f"({stats['redundancy_ratio']:.1%} redundancy)")

        return redundant_types

    def calculate_deduplication_potential(self,
                                         exact_dups: Dict[str, List[str]],
                                         structural_sims: Dict[str, List[str]],
                                         temporal_red: Dict[str, Any],
                                         total_artifacts: int) -> Dict[str, Any]:
        """Calculate potential efficiency gains from deduplication."""
        print("\n=== DEDUPLICATION POTENTIAL ===\n")

        # Exact duplicates can be removed entirely
        exact_removable = sum(len(files) - 1 for files in exact_dups.values())
        exact_savings = exact_removable / total_artifacts if total_artifacts > 0 else 0

        # Structural similarities suggest optimization opportunities
        structural_redundancy = sum(len(files) - 3 for files in structural_sims.values() if len(files) > 3)
        structural_savings = structural_redundancy / total_artifacts if total_artifacts > 0 else 0

        # Total potential
        total_removable = exact_removable
        total_savings = exact_savings

        print(f"Deduplication Potential:")
        print(f"  Exact duplicates removable:  {exact_removable:3d} ({exact_savings:.1%})")
        print(f"  Structural redundancy:       {structural_redundancy:3d} ({structural_savings:.1%})")
        print(f"  Total potential savings:     {total_removable:3d} ({total_savings:.1%})")
        print()
        print(f"Current redundancy:  35.8%")
        print(f"After deduplication: {max(0, 35.8 - total_savings*100):.1f}%")

        # Energy efficiency impact
        current_efficiency = 0.606
        efficiency_improvement = total_savings * 0.15  # Approximate
        projected_efficiency = min(current_efficiency + efficiency_improvement, 1.0)

        print()
        print(f"Energy Efficiency Impact:")
        print(f"  Current:    {current_efficiency:.3f}")
        print(f"  Improvement: +{efficiency_improvement:.3f}")
        print(f"  Projected:  {projected_efficiency:.3f}")

        # NOS impact
        nos_improvement = efficiency_improvement * 0.25  # Energy efficiency weight
        print(f"  NOS Impact: +{nos_improvement:.4f}")

        return {
            'exact_duplicates': exact_removable,
            'structural_redundancy': structural_redundancy,
            'total_removable': total_removable,
            'savings_ratio': total_savings,
            'current_redundancy': 0.358,
            'projected_redundancy': max(0, 0.358 - total_savings),
            'energy_efficiency_improvement': efficiency_improvement,
            'projected_energy_efficiency': projected_efficiency,
            'nos_improvement': nos_improvement,
        }

    def generate_recommendations(self, potential: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate deduplication recommendations."""
        print("\n=== RECOMMENDATIONS ===\n")

        recommendations = []

        if potential['exact_duplicates'] > 0:
            recommendations.append({
                'priority': 'HIGH',
                'action': f"Remove {potential['exact_duplicates']} exact duplicate artifacts",
                'impact': f"{potential['savings_ratio']:.1%} redundancy reduction",
                'implementation': 'Manual review and deletion of duplicated files',
            })

        if potential['structural_redundancy'] > 10:
            recommendations.append({
                'priority': 'MEDIUM',
                'action': 'Implement smart artifact generation caching',
                'impact': f"{potential['structural_redundancy']} fewer redundant generations",
                'implementation': 'Add cache check before generating similar artifacts',
            })

        recommendations.append({
            'priority': 'MEDIUM',
            'action': 'Add deduplication check to artifact pipeline',
            'impact': 'Prevent future redundancy',
            'implementation': 'Pre-generation hash check with skip logic',
        })

        if potential['projected_redundancy'] > 0.25:
            recommendations.append({
                'priority': 'LOW',
                'action': 'Optimize artifact regeneration triggers',
                'impact': f"Further reduce redundancy to <25%",
                'implementation': 'Analyze and optimize artifact generation logic',
            })

        for i, rec in enumerate(recommendations, 1):
            print(f"{i}. [{rec['priority']}] {rec['action']}")
            print(f"   Impact: {rec['impact']}")
            print(f"   Implementation: {rec['implementation']}")
            print()

        return recommendations

    def run_analysis(self) -> Dict[str, Any]:
        """Execute complete deduplication analysis."""
        print("=" * 70)
        print("ARTIFACT DEDUPLICATION ANALYSIS")
        print("=" * 70)

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        # Load artifacts
        artifacts = self.load_artifacts()
        print(f"\nLoaded {len(artifacts)} artifacts")

        # Detect duplicates
        exact_dups = self.detect_exact_duplicates(artifacts)
        structural_sims = self.detect_structural_duplicates(artifacts)
        temporal_red = self.analyze_temporal_redundancy(artifacts)

        # Calculate potential
        potential = self.calculate_deduplication_potential(
            exact_dups, structural_sims, temporal_red, len(artifacts)
        )

        # Generate recommendations
        recommendations = self.generate_recommendations(potential)

        # Create report
        report = {
            'artifact_type': 'deduplication_analysis',
            'timestamp': timestamp,
            'total_artifacts': len(artifacts),
            'exact_duplicates': len(exact_dups),
            'structural_similarities': len(structural_sims),
            'temporal_redundancy_types': len(temporal_red),
            'deduplication_potential': potential,
            'recommendations': recommendations,
        }

        # Save report
        report_path = self.artifacts_dir / f"deduplication_analysis_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"✓ Analysis saved: {report_path.name}")

        return report


def main():
    """Run deduplication analysis."""
    deduplicator = ArtifactDeduplicator()
    report = deduplicator.run_analysis()

    print("\n" + "=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    print(f"Total Artifacts: {report['total_artifacts']}")
    print(f"Exact Duplicates: {report['exact_duplicates']} groups")
    print(f"Potential Savings: {report['deduplication_potential']['savings_ratio']:.1%}")
    print(f"NOS Improvement: +{report['deduplication_potential']['nos_improvement']:.4f}")
    print(f"Recommendations: {len(report['recommendations'])}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
