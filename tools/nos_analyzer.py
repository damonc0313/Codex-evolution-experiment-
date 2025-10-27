#!/usr/bin/env python3
"""
NOS (Novelty-Optimised Score) Component Analyzer

Analyzes the four components of NOS to identify bottlenecks and optimization
opportunities. NOS gates autonomous expansion when below threshold (0.05).

NOS Components (equal weights: 0.25 each):
1. Energy Efficiency: Ratio of useful work to total work
2. Coherence: Quality of artifact interconnection and lineage
3. Resilience: System stability and error recovery capability
4. Entropy: Exploration diversity and novelty generation

This tool:
- Measures each NOS component from artifact corpus
- Calculates composite NOS score
- Identifies bottleneck components
- Suggests targeted improvements
- Validates against swarm-reported NOS

Author: Claude Code (Stabilization Plan Phase 1)
Date: 2025-10-25
Version: 1.0.0
"""

import json
import sys
import math
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
from collections import defaultdict
import statistics


class NOSAnalyzer:
    """Comprehensive NOS component analysis."""

    def __init__(self, artifacts_dir: Path = None):
        self.artifacts_dir = artifacts_dir or Path(__file__).parent.parent / "artifacts"
        self.weights = {
            'energy_efficiency': 0.25,
            'coherence': 0.25,
            'resilience': 0.25,
            'entropy': 0.25,
        }

    def load_artifacts(self) -> List[Dict[str, Any]]:
        """Load all JSON artifacts."""
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

    def measure_energy_efficiency(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Measure energy efficiency: ratio of productive work to total work.

        Metrics:
        - Building ratio: building artifacts / total artifacts
        - Deduplication ratio: unique artifacts / total artifacts
        - Time efficiency: artifacts / time_spent

        Score: Average of normalized metrics
        """
        print("\n=== ENERGY EFFICIENCY ANALYSIS ===\n")

        # Building artifacts (productive work)
        building_types = ['tool', 'implementation', 'sep', 'schema', 'framework',
                         'validator', 'spec', 'design', 'protocol', 'infrastructure',
                         'agent', 'monitor', 'experiment']

        building_artifacts = [
            a for a in artifacts
            if any(t in a.get('artifact_type', '').lower() for t in building_types)
        ]

        building_ratio = len(building_artifacts) / len(artifacts) if artifacts else 0.0

        # Content-based deduplication (hash artifact structure)
        unique_hashes = set()
        for artifact in artifacts:
            # Hash based on artifact_type + key fields
            artifact_type = artifact.get('artifact_type', 'unknown')
            content_hash = hash(frozenset([
                ('type', artifact_type),
                ('timestamp', artifact.get('timestamp', '')),
                ('run_id', artifact.get('run_id', '')),
            ]))
            unique_hashes.add(content_hash)

        dedup_ratio = len(unique_hashes) / len(artifacts) if artifacts else 0.0

        # Artifact generation rate (from swarm data if available)
        swarm_summaries = [a for a in artifacts if a.get('artifact_type') == 'swarm_summary']
        if swarm_summaries:
            latest_swarm = max(swarm_summaries, key=lambda x: x.get('timestamp', ''))
            time_to_artifact = latest_swarm.get('kpi_averages', {}).get('time_to_artifact_s', 0)
            if time_to_artifact > 0:
                artifact_rate = 1.0 / time_to_artifact  # artifacts per second
                # Normalize: 0.04 artifacts/s = 1.0 (target rate)
                rate_score = min(artifact_rate / 0.04, 1.0)
            else:
                rate_score = 0.5  # Default if no data
        else:
            rate_score = 0.5

        # Composite energy efficiency
        energy_efficiency = (building_ratio + dedup_ratio + rate_score) / 3.0

        print(f"Building ratio: {building_ratio:.3f} ({len(building_artifacts)}/{len(artifacts)})")
        print(f"Deduplication ratio: {dedup_ratio:.3f} ({len(unique_hashes)} unique)")
        print(f"Artifact rate score: {rate_score:.3f}")
        print(f"→ Energy Efficiency: {energy_efficiency:.3f}")

        return {
            'score': round(energy_efficiency, 4),
            'building_ratio': round(building_ratio, 4),
            'dedup_ratio': round(dedup_ratio, 4),
            'rate_score': round(rate_score, 4),
            'building_count': len(building_artifacts),
            'total_count': len(artifacts),
            'unique_count': len(unique_hashes),
        }

    def measure_coherence(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Measure coherence: quality of artifact interconnection and lineage.

        Metrics:
        - Lineage completeness: artifacts with parent_hashes / total
        - Continuity ratio: from swarm KPIs
        - DAG depth: average lineage depth

        Score: Average of normalized metrics
        """
        print("\n=== COHERENCE ANALYSIS ===\n")

        # Lineage completeness
        artifacts_with_lineage = [
            a for a in artifacts
            if a.get('parent_hash') or a.get('parent_hashes') or a.get('lineage_root')
        ]

        lineage_ratio = len(artifacts_with_lineage) / len(artifacts) if artifacts else 0.0

        # Continuity ratio from swarm KPIs
        swarm_summaries = [a for a in artifacts if a.get('artifact_type') == 'swarm_summary']
        if swarm_summaries:
            latest_swarm = max(swarm_summaries, key=lambda x: x.get('timestamp', ''))
            continuity_ratio = latest_swarm.get('kpi_averages', {}).get('continuity_ratio', 0.0)
        else:
            continuity_ratio = 0.0

        # DAG depth analysis (artifacts with run_id indicating lineage)
        artifacts_with_run_id = [a for a in artifacts if 'run_id' in a]
        run_id_ratio = len(artifacts_with_run_id) / len(artifacts) if artifacts else 0.0

        # Composite coherence
        coherence = (lineage_ratio + continuity_ratio + run_id_ratio) / 3.0

        print(f"Lineage completeness: {lineage_ratio:.3f} ({len(artifacts_with_lineage)}/{len(artifacts)})")
        print(f"Continuity ratio (swarm KPI): {continuity_ratio:.3f}")
        print(f"Run ID tracking: {run_id_ratio:.3f} ({len(artifacts_with_run_id)}/{len(artifacts)})")
        print(f"→ Coherence: {coherence:.3f}")

        return {
            'score': round(coherence, 4),
            'lineage_ratio': round(lineage_ratio, 4),
            'continuity_ratio': round(continuity_ratio, 4),
            'run_id_ratio': round(run_id_ratio, 4),
            'lineage_count': len(artifacts_with_lineage),
            'run_id_count': len(artifacts_with_run_id),
        }

    def measure_resilience(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Measure resilience: system stability and error recovery.

        Metrics:
        - Regression pass rate: from swarm KPIs
        - Validation pass rate: artifacts with validation / total
        - Error recovery rate: successful retries / total errors

        Score: Average of normalized metrics
        """
        print("\n=== RESILIENCE ANALYSIS ===\n")

        # Regression pass rate from swarm KPIs
        swarm_summaries = [a for a in artifacts if a.get('artifact_type') == 'swarm_summary']
        if swarm_summaries:
            latest_swarm = max(swarm_summaries, key=lambda x: x.get('timestamp', ''))
            regression_pass_rate = latest_swarm.get('kpi_averages', {}).get('regression_pass_rate', 0.0)
        else:
            regression_pass_rate = 0.0

        # Validation artifacts
        validation_artifacts = [
            a for a in artifacts
            if 'validation' in a.get('artifact_type', '').lower() or
               'test' in a.get('artifact_type', '').lower() or
               a.get('validated', False)
        ]

        validation_ratio = len(validation_artifacts) / len(artifacts) if artifacts else 0.0

        # High confidence artifacts (confidence >= 0.85)
        confidence_artifacts = [
            a for a in artifacts
            if a.get('confidence', 0.0) >= 0.85
        ]

        confidence_ratio = len(confidence_artifacts) / len(artifacts) if artifacts else 0.0

        # Composite resilience
        resilience = (regression_pass_rate + validation_ratio + confidence_ratio) / 3.0

        print(f"Regression pass rate (swarm KPI): {regression_pass_rate:.3f}")
        print(f"Validation coverage: {validation_ratio:.3f} ({len(validation_artifacts)}/{len(artifacts)})")
        print(f"High confidence artifacts: {confidence_ratio:.3f} ({len(confidence_artifacts)}/{len(artifacts)})")
        print(f"→ Resilience: {resilience:.3f}")

        return {
            'score': round(resilience, 4),
            'regression_pass_rate': round(regression_pass_rate, 4),
            'validation_ratio': round(validation_ratio, 4),
            'confidence_ratio': round(confidence_ratio, 4),
            'validation_count': len(validation_artifacts),
            'high_confidence_count': len(confidence_artifacts),
        }

    def measure_entropy(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Measure entropy: exploration diversity and novelty.

        Metrics:
        - Artifact type diversity: unique types / total artifacts
        - Novelty vs baseline: from swarm KPIs
        - Parameter space coverage: config diversity

        Score: Average of normalized metrics
        """
        print("\n=== ENTROPY ANALYSIS ===\n")

        # Artifact type diversity
        artifact_types = [a.get('artifact_type', 'unknown') for a in artifacts]
        unique_types = set(artifact_types)

        # Shannon entropy of type distribution
        type_counts = defaultdict(int)
        for atype in artifact_types:
            type_counts[atype] += 1

        total = len(artifact_types)
        shannon_entropy = 0.0
        for count in type_counts.values():
            p = count / total
            if p > 0:
                shannon_entropy -= p * math.log2(p)  # -p*log2(p)

        # Normalize Shannon entropy: max is log2(unique_types)
        max_entropy = math.log2(len(unique_types)) if len(unique_types) > 1 else 1.0
        normalized_shannon = shannon_entropy / max_entropy if max_entropy > 0 else 0.0

        # Novelty from swarm KPIs
        swarm_summaries = [a for a in artifacts if a.get('artifact_type') == 'swarm_summary']
        if swarm_summaries:
            latest_swarm = max(swarm_summaries, key=lambda x: x.get('timestamp', ''))
            novelty_score = latest_swarm.get('kpi_averages', {}).get('novelty_vs_baseline', 0.0)
        else:
            novelty_score = 0.0

        # Parameter diversity (from swarm forks)
        swarm_forks = [a for a in artifacts if 'fork' in a.get('artifact_type', '').lower()]
        if swarm_forks:
            # Measure config diversity
            configs = set()
            for fork in swarm_forks:
                config = (
                    fork.get('mode', ''),
                    fork.get('dialectic_ratio', 0),
                    fork.get('entropy', 0),
                )
                configs.add(config)

            config_diversity = len(configs) / len(swarm_forks) if swarm_forks else 0.0
        else:
            config_diversity = 0.0

        # Composite entropy
        entropy = (normalized_shannon + novelty_score + config_diversity) / 3.0

        print(f"Type diversity (Shannon): {normalized_shannon:.3f} ({len(unique_types)} unique types)")
        print(f"Novelty vs baseline (swarm KPI): {novelty_score:.3f}")
        print(f"Config diversity: {config_diversity:.3f}")
        print(f"→ Entropy: {entropy:.3f}")

        return {
            'score': round(entropy, 4),
            'shannon_entropy': round(normalized_shannon, 4),
            'novelty_score': round(novelty_score, 4),
            'config_diversity': round(config_diversity, 4),
            'unique_types': len(unique_types),
            'total_types': len(artifact_types),
        }

    def calculate_nos(self, components: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate composite NOS from components."""
        print("\n=== NOS COMPOSITE CALCULATION ===\n")

        nos_score = (
            components['energy_efficiency']['score'] * self.weights['energy_efficiency'] +
            components['coherence']['score'] * self.weights['coherence'] +
            components['resilience']['score'] * self.weights['resilience'] +
            components['entropy']['score'] * self.weights['entropy']
        )

        print(f"NOS = 0.25*EE + 0.25*C + 0.25*R + 0.25*E")
        print(f"NOS = 0.25*{components['energy_efficiency']['score']:.3f} + "
              f"0.25*{components['coherence']['score']:.3f} + "
              f"0.25*{components['resilience']['score']:.3f} + "
              f"0.25*{components['entropy']['score']:.3f}")
        print(f"NOS = {nos_score:.4f}")

        return {
            'nos_score': round(nos_score, 4),
            'components': {
                'energy_efficiency': components['energy_efficiency']['score'],
                'coherence': components['coherence']['score'],
                'resilience': components['resilience']['score'],
                'entropy': components['entropy']['score'],
            },
            'weights': self.weights,
        }

    def identify_bottleneck(self, components: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """Identify which component is limiting NOS."""
        print("\n=== BOTTLENECK IDENTIFICATION ===\n")

        scores = {
            'energy_efficiency': components['energy_efficiency']['score'],
            'coherence': components['coherence']['score'],
            'resilience': components['resilience']['score'],
            'entropy': components['entropy']['score'],
        }

        sorted_components = sorted(scores.items(), key=lambda x: x[1])

        bottleneck = sorted_components[0][0]
        bottleneck_score = sorted_components[0][1]

        print(f"Component rankings (lowest to highest):")
        for i, (component, score) in enumerate(sorted_components, 1):
            marker = "← BOTTLENECK" if i == 1 else ""
            print(f"  {i}. {component:20s}: {score:.4f} {marker}")

        # Calculate impact of improving bottleneck
        if bottleneck_score < 1.0:
            target_score = min(bottleneck_score + 0.2, 1.0)  # +0.2 improvement
            nos_improvement = (target_score - bottleneck_score) * self.weights[bottleneck]

            print(f"\nBottleneck: {bottleneck}")
            print(f"Current score: {bottleneck_score:.4f}")
            print(f"Target score: {target_score:.4f} (+{target_score - bottleneck_score:.4f})")
            print(f"NOS improvement: +{nos_improvement:.4f}")

        return {
            'bottleneck': bottleneck,
            'bottleneck_score': round(bottleneck_score, 4),
            'ranking': [
                {'component': c, 'score': round(s, 4), 'rank': i}
                for i, (c, s) in enumerate(sorted_components, 1)
            ],
        }

    def suggest_improvements(self,
                           components: Dict[str, Dict[str, Any]],
                           bottleneck: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate targeted improvement suggestions."""
        print("\n=== IMPROVEMENT SUGGESTIONS ===\n")

        suggestions = []
        bn = bottleneck['bottleneck']

        if bn == 'energy_efficiency':
            suggestions.extend([
                {
                    'component': 'energy_efficiency',
                    'action': 'Implement artifact deduplication',
                    'rationale': f"Dedup ratio: {components['energy_efficiency']['dedup_ratio']:.3f}",
                    'expected_impact': '+0.05 to +0.10',
                },
                {
                    'component': 'energy_efficiency',
                    'action': 'Increase building artifact ratio',
                    'rationale': f"Building ratio: {components['energy_efficiency']['building_ratio']:.3f}",
                    'expected_impact': '+0.03 to +0.08',
                },
            ])

        if bn == 'coherence':
            suggestions.extend([
                {
                    'component': 'coherence',
                    'action': 'Implement SEP-0003 lineage schema',
                    'rationale': f"Lineage ratio: {components['coherence']['lineage_ratio']:.3f}",
                    'expected_impact': '+0.10 to +0.20',
                },
                {
                    'component': 'coherence',
                    'action': 'Backfill parent_hashes for existing artifacts',
                    'rationale': f"Only {components['coherence']['lineage_count']} artifacts have lineage",
                    'expected_impact': '+0.05 to +0.15',
                },
            ])

        if bn == 'resilience':
            suggestions.extend([
                {
                    'component': 'resilience',
                    'action': 'Upgrade validator to FAIL mode',
                    'rationale': f"Regression rate: {components['resilience']['regression_pass_rate']:.3f}",
                    'expected_impact': '+0.03 to +0.07',
                },
                {
                    'component': 'resilience',
                    'action': 'Increase validation coverage',
                    'rationale': f"Validation ratio: {components['resilience']['validation_ratio']:.3f}",
                    'expected_impact': '+0.05 to +0.10',
                },
            ])

        if bn == 'entropy':
            suggestions.extend([
                {
                    'component': 'entropy',
                    'action': 'Increase exploration entropy from 0.6 to 0.8-0.9',
                    'rationale': f"Fork F02 (entropy=0.9) achieved 2x novelty of F10 (entropy=0.6)",
                    'expected_impact': '+0.10 to +0.20',
                },
                {
                    'component': 'entropy',
                    'action': 'Diversify swarm fork configurations',
                    'rationale': f"Shannon entropy: {components['entropy']['shannon_entropy']:.3f}",
                    'expected_impact': '+0.05 to +0.10',
                },
            ])

        for i, suggestion in enumerate(suggestions, 1):
            print(f"{i}. [{suggestion['component'].upper()}] {suggestion['action']}")
            print(f"   Rationale: {suggestion['rationale']}")
            print(f"   Impact: {suggestion['expected_impact']}")
            print()

        return suggestions

    def run_analysis(self) -> Dict[str, Any]:
        """Execute complete NOS analysis."""
        print("=" * 70)
        print("NOS (NOVELTY-OPTIMISED SCORE) COMPONENT ANALYSIS")
        print("=" * 70)

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        # Load artifacts
        artifacts = self.load_artifacts()
        print(f"\nLoaded {len(artifacts)} artifacts")

        # Measure components
        energy_efficiency = self.measure_energy_efficiency(artifacts)
        coherence = self.measure_coherence(artifacts)
        resilience = self.measure_resilience(artifacts)
        entropy = self.measure_entropy(artifacts)

        components = {
            'energy_efficiency': energy_efficiency,
            'coherence': coherence,
            'resilience': resilience,
            'entropy': entropy,
        }

        # Calculate NOS
        nos_calculation = self.calculate_nos(components)

        # Identify bottleneck
        bottleneck = self.identify_bottleneck(components)

        # Generate suggestions
        suggestions = self.suggest_improvements(components, bottleneck)

        # Compare with swarm-reported NOS
        swarm_summaries = [a for a in artifacts if a.get('artifact_type') == 'swarm_summary']
        if swarm_summaries:
            latest_swarm = max(swarm_summaries, key=lambda x: x.get('timestamp', ''))
            swarm_nos = latest_swarm.get('kpi_averages', {}).get('nos_score', 0.0)

            print(f"\n=== VALIDATION ===\n")
            print(f"Calculated NOS: {nos_calculation['nos_score']:.4f}")
            print(f"Swarm-reported NOS: {swarm_nos:.4f}")
            print(f"Difference: {abs(nos_calculation['nos_score'] - swarm_nos):.4f}")

        # Compile report
        report = {
            'artifact_type': 'nos_analysis_report',
            'timestamp': timestamp,
            'nos_score': nos_calculation['nos_score'],
            'nos_floor_threshold': 0.05,
            'gate_status': 'UNBLOCKED' if nos_calculation['nos_score'] >= 0.05 else 'GATED',
            'components': {
                'energy_efficiency': energy_efficiency,
                'coherence': coherence,
                'resilience': resilience,
                'entropy': entropy,
            },
            'bottleneck': bottleneck,
            'suggestions': suggestions,
            'artifact_count': len(artifacts),
        }

        # Save report
        report_path = self.artifacts_dir / f"nos_analysis_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Analysis saved to: {report_path.name}")

        return report


def main():
    """Run NOS component analysis."""
    analyzer = NOSAnalyzer()
    report = analyzer.run_analysis()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"NOS Score: {report['nos_score']:.4f}")
    print(f"Threshold: {report['nos_floor_threshold']:.4f}")
    print(f"Status: {report['gate_status']}")
    print(f"Bottleneck: {report['bottleneck']['bottleneck']}")
    print(f"Top Suggestion: {report['suggestions'][0]['action'] if report['suggestions'] else 'None'}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
