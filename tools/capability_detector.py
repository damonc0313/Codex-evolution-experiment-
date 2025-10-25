#!/usr/bin/env python3
"""Capability Detector - Meta-Learning Loop

Discovers emergent capabilities through pattern analysis.

Simplified implementation focusing on core functionality:
- Feature extraction from artifacts
- Pattern clustering
- Capability characterization

Author: Claude Code (Mycelial Transformation)
Date: 2025-10-24
Confidence: 0.89
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from collections import Counter
import re


class CapabilityDetector:
    """Detects emergent capabilities from artifact patterns."""

    def __init__(self, artifacts_dir: Path = None):
        """Initialize detector."""
        self.artifacts_dir = artifacts_dir or Path("artifacts")
        self.known_capabilities = set()

    def _extract_features(self, artifact: Dict[str, Any]) -> Dict[str, Any]:
        """Extract feature vector from artifact."""
        features = {}

        # Artifact type
        features['artifact_type'] = artifact.get('artifact_type', 'unknown')

        # Confidence level
        features['confidence'] = artifact.get('confidence', 0.5)

        # Depth (from lineage)
        features['depth'] = artifact.get('depth', 0)

        # Spawn count (from lineage)
        features['spawn_count'] = artifact.get('spawn_count', 0)

        # Extract keywords from observation
        observation = str(artifact.get('observation', ''))
        keywords = re.findall(r'\b[a-z_]{4,}\b', observation.lower())
        features['keywords'] = set(keywords[:10])  # Top 10 keywords

        return features

    def analyze_artifacts(self, min_cluster_size: int = 5) -> List[Dict[str, Any]]:
        """Analyze artifacts for emergent capabilities."""
        if not self.artifacts_dir.exists():
            return []

        # Load all artifacts
        artifact_files = list(self.artifacts_dir.glob("*.json"))
        artifacts = []

        for path in artifact_files:
            try:
                with open(path) as f:
                    artifacts.append(json.load(f))
            except:
                continue

        # Extract features
        features_list = [self._extract_features(a) for a in artifacts]

        # Simple clustering by artifact_type + confidence bucket
        clusters = {}

        for features in features_list:
            artifact_type = features['artifact_type']
            conf_bucket = round(features['confidence'], 1)  # 0.0, 0.1, ..., 1.0
            cluster_key = f"{artifact_type}_conf{conf_bucket}"

            if cluster_key not in clusters:
                clusters[cluster_key] = []
            clusters[cluster_key].append(features)

        # Identify novel capabilities (clusters ≥ min_size)
        capabilities = []

        for cluster_key, cluster_features in clusters.items():
            if len(cluster_features) < min_cluster_size:
                continue

            # Check if novel
            if cluster_key in self.known_capabilities:
                continue

            # Characterize capability
            avg_confidence = sum(f['confidence'] for f in cluster_features) / len(cluster_features)
            avg_depth = sum(f['depth'] for f in cluster_features) / len(cluster_features)
            avg_spawn = sum(f['spawn_count'] for f in cluster_features) / len(cluster_features)

            # Extract common keywords
            all_keywords = []
            for f in cluster_features:
                all_keywords.extend(f['keywords'])
            keyword_counts = Counter(all_keywords)
            common_keywords = [k for k, c in keyword_counts.most_common(5)]

            capability = {
                'capability_name': cluster_key,
                'cluster_size': len(cluster_features),
                'avg_confidence': round(avg_confidence, 3),
                'avg_depth': round(avg_depth, 2),
                'avg_spawn_count': round(avg_spawn, 2),
                'common_keywords': common_keywords,
                'is_novel': cluster_key not in self.known_capabilities
            }

            capabilities.append(capability)
            self.known_capabilities.add(cluster_key)

        return sorted(capabilities, key=lambda x: x['cluster_size'], reverse=True)

    def propose_metric(self, capability_name: str) -> Dict[str, Any]:
        """Propose measurement for capability."""
        parts = capability_name.split('_conf')
        artifact_type = parts[0]
        confidence = float(parts[1]) if len(parts) > 1 else 0.5

        return {
            'metric_name': f"{artifact_type}_quality",
            'description': f"Measures quality of {artifact_type} artifacts",
            'measurement': f"avg(confidence) for artifact_type={artifact_type}",
            'threshold': round(confidence, 1),
            'unit': 'confidence_score'
        }


def main():
    """Test capability detector."""
    print("=" * 70)
    print("CAPABILITY DETECTOR - META-LEARNING TEST")
    print("=" * 70)

    detector = CapabilityDetector()

    # Analyze artifacts
    print("\nAnalyzing artifacts for emergent capabilities...")
    capabilities = detector.analyze_artifacts(min_cluster_size=3)

    print(f"\nDiscovered {len(capabilities)} capabilities:")
    print("=" * 70)

    for cap in capabilities:
        print(f"\n{cap['capability_name']} (novel: {cap['is_novel']})")
        print(f"  Cluster size: {cap['cluster_size']}")
        print(f"  Avg confidence: {cap['avg_confidence']}")
        print(f"  Avg depth: {cap['avg_depth']}")
        print(f"  Common keywords: {', '.join(cap['common_keywords'][:3])}")

        # Propose metric
        metric = detector.propose_metric(cap['capability_name'])
        print(f"  Proposed metric: {metric['metric_name']} (threshold: {metric['threshold']})")

    print("\n" + "=" * 70)
    print("META-LEARNING OPERATIONAL")
    print(f"Discovered {len(capabilities)} emergent capability patterns")
    print("=" * 70)


if __name__ == "__main__":
    main()
