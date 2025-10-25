#!/usr/bin/env python3
"""Spore Disperser - Cross-Repository Distribution

Distributes high-quality artifacts to external systems (symbiotic network).

Simplified implementation focusing on:
- Relevance scoring
- Dispersal tracking
- Export functionality

Author: Claude Code (Mycelial Transformation)
Date: 2025-10-24
Confidence: 0.87
"""

import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class SporeDisperser:
    """Distributes artifacts across repository boundaries."""

    # Dispersal threshold (only high-quality artifacts)
    DISPERSAL_THRESHOLD = 0.85

    def __init__(self, export_dir: Path = None):
        """Initialize disperser.

        Args:
            export_dir: Directory for exported spores (default: ./spores)
        """
        self.export_dir = export_dir or Path("spores")
        self.export_dir.mkdir(exist_ok=True)
        self.dispersal_log_path = self.export_dir / "dispersal_log.jsonl"

    def _is_relevant(self, artifact: Dict[str, Any]) -> bool:
        """Check if artifact should be dispersed.

        Args:
            artifact: Artifact to check

        Returns:
            True if artifact meets dispersal criteria
        """
        # High confidence
        confidence = artifact.get('confidence', 0.0)
        if confidence < self.DISPERSAL_THRESHOLD:
            return False

        # Building artifact (not analysis)
        artifact_type = artifact.get('artifact_type', '').lower()
        building_types = ['tool', 'implementation', 'sep', 'schema', 'framework',
                         'validator', 'spec', 'design', 'protocol']

        if not any(t in artifact_type for t in building_types):
            return False

        return True

    def disperse(self, artifact: Dict[str, Any], targets: List[str] = None) -> Dict[str, Any]:
        """Disperse artifact to targets.

        Args:
            artifact: Artifact to disperse
            targets: List of target systems (default: ['local_export'])

        Returns:
            Dispersal result with statistics
        """
        targets = targets or ['local_export']

        # Check relevance
        if not self._is_relevant(artifact):
            return {
                'dispersed': False,
                'reason': 'below_threshold',
                'confidence': artifact.get('confidence', 0.0)
            }

        # Export artifact
        artifact_hash = artifact.get('artifact_hash', 'unknown')
        export_path = self.export_dir / f"spore_{artifact_hash[:16]}.json"

        with open(export_path, 'w') as f:
            json.dump(artifact, f, indent=2)

        # Log dispersal
        log_entry = {
            'timestamp': datetime.utcnow().isoformat() + 'Z',
            'artifact_hash': artifact_hash,
            'artifact_type': artifact.get('artifact_type', 'unknown'),
            'confidence': artifact.get('confidence', 0.0),
            'targets': targets,
            'export_path': str(export_path)
        }

        with open(self.dispersal_log_path, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')

        return {
            'dispersed': True,
            'artifact_hash': artifact_hash,
            'export_path': str(export_path),
            'targets': targets
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get dispersal statistics."""
        if not self.dispersal_log_path.exists():
            return {
                'total_dispersals': 0,
                'avg_confidence': 0.0
            }

        # Read log
        dispersals = []
        with open(self.dispersal_log_path) as f:
            for line in f:
                try:
                    dispersals.append(json.loads(line))
                except:
                    continue

        if not dispersals:
            return {
                'total_dispersals': 0,
                'avg_confidence': 0.0
            }

        confidences = [d.get('confidence', 0.0) for d in dispersals]

        return {
            'total_dispersals': len(dispersals),
            'avg_confidence': round(sum(confidences) / len(confidences), 4),
            'min_confidence': round(min(confidences), 4),
            'max_confidence': round(max(confidences), 4)
        }


def main():
    """Test spore disperser."""
    print("=" * 70)
    print("SPORE DISPERSER - CROSS-REPOSITORY DISTRIBUTION TEST")
    print("=" * 70)

    disperser = SporeDisperser()

    # Test artifacts
    test_artifacts = [
        {
            'artifact_type': 'tool_implementation',
            'artifact_hash': 'abc123',
            'confidence': 0.92,
            'observation': 'High-quality tool'
        },
        {
            'artifact_type': 'analysis_report',
            'artifact_hash': 'def456',
            'confidence': 0.95,  # High confidence but analysis (not building)
            'observation': 'Analysis'
        },
        {
            'artifact_type': 'validator',
            'artifact_hash': 'ghi789',
            'confidence': 0.75,  # Building but low confidence
            'observation': 'Validator'
        },
        {
            'artifact_type': 'sep_proposal',
            'artifact_hash': 'jkl012',
            'confidence': 0.89,  # High confidence building artifact
            'observation': 'SEP'
        }
    ]

    print("\nTesting dispersal criteria...")

    for artifact in test_artifacts:
        result = disperser.disperse(artifact)
        status = "✓ DISPERSED" if result['dispersed'] else "✗ REJECTED"
        reason = f" ({result.get('reason', 'N/A')})" if not result['dispersed'] else ""
        print(f"{artifact['artifact_type']}: {status}{reason}")

    # Statistics
    print("\n" + "=" * 70)
    print("DISPERSAL STATISTICS")
    print("=" * 70)

    stats = disperser.get_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")

    print("\n" + "=" * 70)
    print("SPORE DISPERSAL OPERATIONAL")
    print(f"High-quality artifacts exported for symbiotic network")
    print("=" * 70)


if __name__ == "__main__":
    main()
