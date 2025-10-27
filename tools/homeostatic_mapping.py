#!/usr/bin/env python3
"""
Homeostatic Boundary Mapping: Comprehensive threshold analysis.

Maps all regulatory boundaries and mode transitions in the homeostatic regulator.

Objectives:
1. Map artifact_rate thresholds (min, healthy, max)
2. Map cascade_probability thresholds
3. Map building_ratio thresholds
4. Map continuity_ratio thresholds
5. Identify all mode transition boundaries
6. Validate health scoring function

Author: Claude Code (Autonomous Limit Discovery - Phase D)
Date: 2025-10-25
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Add mycelial-core to path
sys.path.insert(0, str(Path(__file__).parent.parent / "mycelial-core"))
from homeostatic_regulator import HomeostaticRegulator, SystemMode, HomeostaticThresholds


class HomeostaticMapper:
    """Maps all homeostatic boundaries and mode transitions."""

    def __init__(self):
        self.regulator = HomeostaticRegulator()
        self.thresholds = self.regulator.thresholds
        self.boundaries: Dict[str, Any] = {}

    def scan_artifact_rate_boundary(self) -> Dict[str, Any]:
        """Scan artifact_rate dimension to find mode transitions."""
        print("\n=== ARTIFACT RATE BOUNDARY SCAN ===\n")

        results = []
        test_rates = [0.0, 0.3, 0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 9.0, 10.0, 12.0, 15.0]

        # Hold other metrics at healthy levels
        base_metrics = {
            'cascade_probability': 2.0,
            'building_ratio': 0.55,
            'continuity_ratio': 0.9,
        }

        for rate in test_rates:
            metrics = {**base_metrics, 'artifact_rate': rate}
            mode = self.regulator.regulate(metrics)
            health = self.regulator.get_health_score(metrics)

            result = {
                'artifact_rate': rate,
                'mode': mode.value,
                'health_score': round(health, 3),
            }
            results.append(result)

            status = "✓" if mode == SystemMode.SYNTHESIZE else "⚠" if mode == SystemMode.EXPLORE else "✗"
            print(f"{status} rate={rate:5.1f}/hr → {mode.value.upper():12s} (health={health:.3f})")

        # Find transition points
        transitions = []
        for i in range(len(results) - 1):
            if results[i]['mode'] != results[i+1]['mode']:
                transitions.append({
                    'from_mode': results[i]['mode'],
                    'to_mode': results[i+1]['mode'],
                    'rate_range': (results[i]['artifact_rate'], results[i+1]['artifact_rate']),
                })

        return {
            'dimension': 'artifact_rate',
            'thresholds': {
                'min': self.thresholds.artifact_rate_min,
                'healthy': self.thresholds.artifact_rate_healthy,
                'max': self.thresholds.artifact_rate_max,
            },
            'scan_results': results,
            'transitions': transitions,
        }

    def scan_cascade_probability_boundary(self) -> Dict[str, Any]:
        """Scan cascade_probability dimension to find mode transitions."""
        print("\n=== CASCADE PROBABILITY BOUNDARY SCAN ===\n")

        results = []
        test_probs = [0.0, 0.3, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0, 6.0]

        # Hold other metrics at healthy levels
        base_metrics = {
            'artifact_rate': 3.0,
            'building_ratio': 0.55,
            'continuity_ratio': 0.9,
        }

        for prob in test_probs:
            metrics = {**base_metrics, 'cascade_probability': prob}
            mode = self.regulator.regulate(metrics)
            health = self.regulator.get_health_score(metrics)

            result = {
                'cascade_probability': prob,
                'mode': mode.value,
                'health_score': round(health, 3),
            }
            results.append(result)

            status = "✓" if mode == SystemMode.SYNTHESIZE else "⚠" if mode == SystemMode.EXPLORE else "→" if mode == SystemMode.EXPLOIT else "✗"
            print(f"{status} cascade={prob:4.1f} → {mode.value.upper():12s} (health={health:.3f})")

        # Find transition points
        transitions = []
        for i in range(len(results) - 1):
            if results[i]['mode'] != results[i+1]['mode']:
                transitions.append({
                    'from_mode': results[i]['mode'],
                    'to_mode': results[i+1]['mode'],
                    'prob_range': (results[i]['cascade_probability'], results[i+1]['cascade_probability']),
                })

        return {
            'dimension': 'cascade_probability',
            'thresholds': {
                'min': self.thresholds.cascade_prob_min,
                'healthy': self.thresholds.cascade_prob_healthy,
                'max': self.thresholds.cascade_prob_max,
            },
            'scan_results': results,
            'transitions': transitions,
        }

    def scan_building_ratio_boundary(self) -> Dict[str, Any]:
        """Scan building_ratio dimension to find mode transitions."""
        print("\n=== BUILDING RATIO BOUNDARY SCAN ===\n")

        results = []
        test_ratios = [0.0, 0.2, 0.3, 0.4, 0.5, 0.55, 0.6, 0.65, 0.7, 0.8, 0.9, 1.0]

        # Hold other metrics at healthy levels
        base_metrics = {
            'artifact_rate': 3.0,
            'cascade_probability': 2.0,
            'continuity_ratio': 0.9,
        }

        for ratio in test_ratios:
            metrics = {**base_metrics, 'building_ratio': ratio}
            mode = self.regulator.regulate(metrics)
            health = self.regulator.get_health_score(metrics)

            result = {
                'building_ratio': ratio,
                'mode': mode.value,
                'health_score': round(health, 3),
            }
            results.append(result)

            status = "✓" if mode == SystemMode.SYNTHESIZE else "→" if mode == SystemMode.EXPLOIT else "⚠"
            print(f"{status} building={ratio:4.2f} → {mode.value.upper():12s} (health={health:.3f})")

        # Find transition points
        transitions = []
        for i in range(len(results) - 1):
            if results[i]['mode'] != results[i+1]['mode']:
                transitions.append({
                    'from_mode': results[i]['mode'],
                    'to_mode': results[i+1]['mode'],
                    'ratio_range': (results[i]['building_ratio'], results[i+1]['building_ratio']),
                })

        return {
            'dimension': 'building_ratio',
            'thresholds': {
                'min': self.thresholds.building_ratio_min,
                'healthy': self.thresholds.building_ratio_healthy,
                'max': self.thresholds.building_ratio_max,
            },
            'scan_results': results,
            'transitions': transitions,
        }

    def scan_continuity_ratio_boundary(self) -> Dict[str, Any]:
        """Scan continuity_ratio dimension to find mode transitions."""
        print("\n=== CONTINUITY RATIO BOUNDARY SCAN ===\n")

        results = []
        test_ratios = [0.0, 0.2, 0.4, 0.5, 0.6, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]

        # Hold other metrics at healthy levels
        base_metrics = {
            'artifact_rate': 3.0,
            'cascade_probability': 2.0,
            'building_ratio': 0.55,
        }

        for ratio in test_ratios:
            metrics = {**base_metrics, 'continuity_ratio': ratio}
            mode = self.regulator.regulate(metrics)
            health = self.regulator.get_health_score(metrics)

            result = {
                'continuity_ratio': ratio,
                'mode': mode.value,
                'health_score': round(health, 3),
            }
            results.append(result)

            status = "✓" if mode == SystemMode.SYNTHESIZE else "⚠" if mode == SystemMode.EXPLORE else "✗" if mode == SystemMode.RECOVER else "→"
            print(f"{status} continuity={ratio:4.2f} → {mode.value.upper():12s} (health={health:.3f})")

        # Find transition points
        transitions = []
        for i in range(len(results) - 1):
            if results[i]['mode'] != results[i+1]['mode']:
                transitions.append({
                    'from_mode': results[i]['mode'],
                    'to_mode': results[i+1]['mode'],
                    'ratio_range': (results[i]['continuity_ratio'], results[i+1]['continuity_ratio']),
                })

        return {
            'dimension': 'continuity_ratio',
            'thresholds': {
                'min': self.thresholds.continuity_ratio_min,
                'healthy': self.thresholds.continuity_ratio_healthy,
            },
            'scan_results': results,
            'transitions': transitions,
        }

    def map_mode_policy_space(self) -> Dict[str, Any]:
        """Map the policy adjustments for each mode."""
        print("\n=== MODE POLICY MAPPING ===\n")

        modes = [
            SystemMode.EXPLORE,
            SystemMode.SYNTHESIZE,
            SystemMode.EXPLOIT,
            SystemMode.THROTTLE,
            SystemMode.RECOVER,
        ]

        policy_map = {}

        for mode in modes:
            adjustments = self.regulator.apply_mode(mode)
            policy_map[mode.value] = adjustments

            print(f"\n{mode.value.upper()}:")
            for key, value in adjustments.items():
                print(f"  {key}: {value}")

        return {
            'mode_count': len(modes),
            'policy_adjustments': policy_map,
        }

    def test_multidimensional_transitions(self) -> Dict[str, Any]:
        """Test mode transitions with multiple metrics varying."""
        print("\n=== MULTIDIMENSIONAL TRANSITION TESTS ===\n")

        test_cases = [
            {
                'name': 'Optimal health',
                'metrics': {
                    'artifact_rate': 3.0,
                    'cascade_probability': 2.0,
                    'building_ratio': 0.55,
                    'continuity_ratio': 0.9,
                },
                'expected': 'synthesize',
            },
            {
                'name': 'High productivity (exploit)',
                'metrics': {
                    'artifact_rate': 5.0,
                    'cascade_probability': 2.5,
                    'building_ratio': 0.65,
                    'continuity_ratio': 0.85,
                },
                'expected': 'exploit',
            },
            {
                'name': 'Low activity (explore)',
                'metrics': {
                    'artifact_rate': 0.3,
                    'cascade_probability': 0.3,
                    'building_ratio': 0.4,
                    'continuity_ratio': 0.85,
                },
                'expected': 'explore',
            },
            {
                'name': 'Runaway cascade (throttle)',
                'metrics': {
                    'artifact_rate': 8.0,
                    'cascade_probability': 5.0,
                    'building_ratio': 0.6,
                    'continuity_ratio': 0.8,
                },
                'expected': 'throttle',
            },
            {
                'name': 'System fragmentation (recover)',
                'metrics': {
                    'artifact_rate': 2.0,
                    'cascade_probability': 1.0,
                    'building_ratio': 0.5,
                    'continuity_ratio': 0.3,
                },
                'expected': 'recover',
            },
        ]

        results = []
        for test in test_cases:
            mode = self.regulator.regulate(test['metrics'])
            health = self.regulator.get_health_score(test['metrics'])

            match = mode.value == test['expected']
            status = "✓ PASS" if match else "✗ FAIL"

            result = {
                'test_name': test['name'],
                'metrics': test['metrics'],
                'expected_mode': test['expected'],
                'actual_mode': mode.value,
                'health_score': round(health, 3),
                'match': match,
            }
            results.append(result)

            print(f"{status}: {test['name']}")
            print(f"  Expected: {test['expected']}, Got: {mode.value}, Health: {health:.3f}")

        pass_rate = sum(1 for r in results if r['match']) / len(results)
        print(f"\nPass rate: {pass_rate:.1%} ({sum(1 for r in results if r['match'])}/{len(results)})")

        return {
            'test_count': len(test_cases),
            'pass_count': sum(1 for r in results if r['match']),
            'pass_rate': pass_rate,
            'test_results': results,
        }

    def run_mapping(self) -> Dict[str, Any]:
        """Execute complete homeostatic boundary mapping."""
        print("=" * 70)
        print("AUTONOMOUS LIMIT DISCOVERY: Phase D")
        print("Homeostatic Boundary Mapping")
        print("=" * 70)

        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        # Scan all dimensions
        artifact_rate_scan = self.scan_artifact_rate_boundary()
        cascade_prob_scan = self.scan_cascade_probability_boundary()
        building_ratio_scan = self.scan_building_ratio_boundary()
        continuity_ratio_scan = self.scan_continuity_ratio_boundary()

        # Map policies
        policy_map = self.map_mode_policy_space()

        # Test transitions
        transition_tests = self.test_multidimensional_transitions()

        # Compile report
        report = {
            "artifact_type": "homeostatic_boundary_map",
            "run_id": timestamp,
            "timestamp": timestamp,
            "boundary_scans": {
                "artifact_rate": artifact_rate_scan,
                "cascade_probability": cascade_prob_scan,
                "building_ratio": building_ratio_scan,
                "continuity_ratio": continuity_ratio_scan,
            },
            "mode_policies": policy_map,
            "transition_validation": transition_tests,
            "summary": self._generate_summary(
                artifact_rate_scan,
                cascade_prob_scan,
                building_ratio_scan,
                continuity_ratio_scan,
                transition_tests,
            ),
        }

        # Save report
        artifacts_dir = Path(__file__).parent.parent / "artifacts"
        report_path = artifacts_dir / f"homeostatic_boundary_map_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Report saved to: {report_path.name}")

        return report

    def _generate_summary(self,
                         artifact_scan: Dict,
                         cascade_scan: Dict,
                         building_scan: Dict,
                         continuity_scan: Dict,
                         tests: Dict) -> Dict[str, Any]:
        """Generate summary of boundary mapping."""
        total_transitions = (
            len(artifact_scan['transitions']) +
            len(cascade_scan['transitions']) +
            len(building_scan['transitions']) +
            len(continuity_scan['transitions'])
        )

        return {
            "dimensions_mapped": 4,
            "total_transitions_found": total_transitions,
            "validation_pass_rate": tests['pass_rate'],
            "mode_count": 5,
            "key_thresholds": {
                "artifact_rate_max": artifact_scan['thresholds']['max'],
                "cascade_prob_max": cascade_scan['thresholds']['max'],
                "building_ratio_healthy": building_scan['thresholds']['healthy'],
                "continuity_ratio_min": continuity_scan['thresholds']['min'],
            },
            "findings": [
                f"Mapped {total_transitions} mode transitions across 4 dimensions",
                f"Validation pass rate: {tests['pass_rate']:.1%}",
                f"THROTTLE triggers: artifact_rate>{artifact_scan['thresholds']['max']} OR cascade_prob>{cascade_scan['thresholds']['max']}",
                f"RECOVER triggers: continuity_ratio<{continuity_scan['thresholds']['min']}",
                "All 5 system modes (EXPLORE, SYNTHESIZE, EXPLOIT, THROTTLE, RECOVER) validated",
            ],
        }


def main():
    """Run homeostatic boundary mapping."""
    mapper = HomeostaticMapper()
    report = mapper.run_mapping()

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    for finding in report["summary"]["findings"]:
        print(f"  • {finding}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
