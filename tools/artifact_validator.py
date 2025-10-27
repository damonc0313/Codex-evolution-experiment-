#!/usr/bin/env python3
"""
Artifact Validator - SEP-0003 Lineage Enforcement

Validates artifacts against quality standards with configurable enforcement modes.
Upgrades from WARN mode (log issues) to FAIL mode (enforce compliance).

Validation Rules:
1. SEP-0003 Lineage: lineage_root, parent_hashes, artifact_hash required
2. Metadata Completeness: artifact_type, timestamp required
3. Confidence Threshold: minimum confidence score (if present)
4. DAG Integrity: parent references must exist

Enforcement Modes:
- WARN: Log violations but allow all artifacts (current)
- FAIL: Reject artifacts that violate critical rules (target)
- STRICT: Enforce all rules including optional ones

Author: Claude Code (Stabilization Plan Phase 2)
Date: 2025-10-25
Version: 2.0.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from datetime import datetime
from enum import Enum


class ValidationMode(Enum):
    """Validation enforcement modes."""
    WARN = "warn"      # Log violations, allow all
    FAIL = "fail"      # Reject critical violations
    STRICT = "strict"  # Enforce all rules


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    CRITICAL = "critical"  # Must fix (FAIL mode rejects)
    ERROR = "error"        # Should fix (STRICT mode rejects)
    WARNING = "warning"    # Nice to have


class ArtifactValidator:
    """Production-grade artifact validator with enforcement modes."""

    def __init__(self,
                 artifacts_dir: Path = None,
                 mode: ValidationMode = ValidationMode.FAIL):
        self.artifacts_dir = artifacts_dir or Path(__file__).parent.parent / "artifacts"
        self.mode = mode
        self.violations: List[Dict[str, Any]] = []

    def validate_lineage_compliance(self, artifact: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate SEP-0003 lineage compliance."""
        issues = []

        # Critical: lineage_root required
        if 'lineage_root' not in artifact:
            issues.append({
                'rule': 'SEP-0003-lineage_root',
                'severity': ValidationSeverity.CRITICAL,
                'message': 'Missing required field: lineage_root',
            })

        # Critical: parent_hashes required (can be empty list for roots)
        if 'parent_hashes' not in artifact:
            issues.append({
                'rule': 'SEP-0003-parent_hashes',
                'severity': ValidationSeverity.CRITICAL,
                'message': 'Missing required field: parent_hashes',
            })

        # Critical: artifact_hash required
        if 'artifact_hash' not in artifact:
            issues.append({
                'rule': 'SEP-0003-artifact_hash',
                'severity': ValidationSeverity.CRITICAL,
                'message': 'Missing required field: artifact_hash',
            })

        return issues

    def validate_metadata_completeness(self, artifact: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate basic metadata completeness."""
        issues = []

        # Critical: artifact_type required
        if 'artifact_type' not in artifact:
            issues.append({
                'rule': 'metadata-artifact_type',
                'severity': ValidationSeverity.CRITICAL,
                'message': 'Missing required field: artifact_type',
            })

        # Error: timestamp highly recommended
        if 'timestamp' not in artifact:
            issues.append({
                'rule': 'metadata-timestamp',
                'severity': ValidationSeverity.ERROR,
                'message': 'Missing recommended field: timestamp',
            })

        return issues

    def validate_confidence_threshold(self, artifact: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Validate confidence score meets threshold."""
        issues = []

        # Warning: confidence score recommended for quality tracking
        if 'confidence' not in artifact:
            issues.append({
                'rule': 'quality-confidence',
                'severity': ValidationSeverity.WARNING,
                'message': 'Missing quality indicator: confidence',
            })
        else:
            confidence = artifact['confidence']
            # Warning: very low confidence
            if confidence < 0.3:
                issues.append({
                    'rule': 'quality-confidence-low',
                    'severity': ValidationSeverity.WARNING,
                    'message': f'Very low confidence score: {confidence:.3f} < 0.3',
                })

        return issues

    def validate_dag_integrity(self,
                               artifact: Dict[str, Any],
                               all_artifacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate parent references exist (DAG integrity)."""
        issues = []

        if 'parent_hashes' not in artifact:
            return issues

        parent_hashes = artifact.get('parent_hashes', [])
        if not isinstance(parent_hashes, list):
            parent_hashes = [parent_hashes] if parent_hashes else []

        # Build hash index
        hash_index = {a.get('artifact_hash'): a for a in all_artifacts if 'artifact_hash' in a}

        for parent_hash in parent_hashes:
            if not isinstance(parent_hash, str):
                continue
            if parent_hash and parent_hash not in hash_index:
                issues.append({
                    'rule': 'dag-parent_exists',
                    'severity': ValidationSeverity.ERROR,
                    'message': f'Parent hash not found: {parent_hash[:16]}...',
                })

        return issues

    def validate_artifact(self,
                         artifact: Dict[str, Any],
                         all_artifacts: List[Dict[str, Any]] = None) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate a single artifact.

        Returns:
            (is_valid, issues) tuple
            - is_valid: True if artifact passes validation for current mode
            - issues: List of all validation issues found
        """
        all_issues = []

        # Run all validation checks
        all_issues.extend(self.validate_lineage_compliance(artifact))
        all_issues.extend(self.validate_metadata_completeness(artifact))
        all_issues.extend(self.validate_confidence_threshold(artifact))

        if all_artifacts:
            all_issues.extend(self.validate_dag_integrity(artifact, all_artifacts))

        # Determine if valid based on mode
        is_valid = True

        if self.mode == ValidationMode.FAIL:
            # Reject if any CRITICAL issues
            critical_issues = [i for i in all_issues if i['severity'] == ValidationSeverity.CRITICAL]
            is_valid = len(critical_issues) == 0

        elif self.mode == ValidationMode.STRICT:
            # Reject if any CRITICAL or ERROR issues
            blocking_issues = [i for i in all_issues
                             if i['severity'] in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]]
            is_valid = len(blocking_issues) == 0

        # WARN mode always returns valid=True

        return is_valid, all_issues

    def validate_all_artifacts(self) -> Dict[str, Any]:
        """Validate all artifacts in the corpus."""
        print(f"\n=== VALIDATING ARTIFACTS (Mode: {self.mode.value.upper()}) ===\n")

        # Load all artifacts
        artifacts = []
        for path in sorted(self.artifacts_dir.glob("*.json")):
            try:
                with open(path) as f:
                    artifact = json.load(f)
                    artifact['_source_path'] = str(path)
                    artifact['_filename'] = path.name
                    artifacts.append(artifact)
            except Exception as e:
                print(f"Error loading {path.name}: {e}", file=sys.stderr)

        print(f"Loaded {len(artifacts)} artifacts\n")

        # Validate each artifact
        results = []
        stats = {
            'total': len(artifacts),
            'valid': 0,
            'invalid': 0,
            'critical_issues': 0,
            'error_issues': 0,
            'warning_issues': 0,
        }

        for artifact in artifacts:
            is_valid, issues = self.validate_artifact(artifact, artifacts)

            if is_valid:
                stats['valid'] += 1
            else:
                stats['invalid'] += 1

            # Count issues by severity
            for issue in issues:
                if issue['severity'] == ValidationSeverity.CRITICAL:
                    stats['critical_issues'] += 1
                elif issue['severity'] == ValidationSeverity.ERROR:
                    stats['error_issues'] += 1
                else:
                    stats['warning_issues'] += 1

            results.append({
                'filename': artifact.get('_filename', 'unknown'),
                'artifact_type': artifact.get('artifact_type', 'unknown'),
                'is_valid': is_valid,
                'issues': issues,
            })

        # Print summary
        print(f"Validation Results:")
        print(f"  Valid:   {stats['valid']:3d} ({stats['valid']/stats['total']*100:.1f}%)")
        print(f"  Invalid: {stats['invalid']:3d} ({stats['invalid']/stats['total']*100:.1f}%)")
        print()
        print(f"Issues by Severity:")
        print(f"  CRITICAL: {stats['critical_issues']:3d}")
        print(f"  ERROR:    {stats['error_issues']:3d}")
        print(f"  WARNING:  {stats['warning_issues']:3d}")

        # Show failed artifacts
        if stats['invalid'] > 0:
            print(f"\nFailed Artifacts ({stats['invalid']}):")
            for result in results:
                if not result['is_valid']:
                    critical = [i for i in result['issues'] if i['severity'] == ValidationSeverity.CRITICAL]
                    print(f"  ✗ {result['filename']:50s} ({len(critical)} critical)")

        # Show top issues
        issue_counts = {}
        for result in results:
            for issue in result['issues']:
                rule = issue['rule']
                issue_counts[rule] = issue_counts.get(rule, 0) + 1

        if issue_counts:
            print(f"\nTop Issues:")
            top_issues = sorted(issue_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            for rule, count in top_issues:
                print(f"  {rule:40s}: {count:3d} occurrences")

        return {
            'mode': self.mode.value,
            'statistics': stats,
            'results': results,
        }

    def generate_report(self, validation_results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate validation report artifact."""
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        report = {
            'artifact_type': 'validation_report',
            'timestamp': timestamp,
            'validator_version': '2.0.0',
            'mode': validation_results['mode'],
            'statistics': validation_results['statistics'],
            'compliance': {
                'sep_0003_compliant': validation_results['statistics']['critical_issues'] == 0,
                'validation_pass_rate': validation_results['statistics']['valid'] / validation_results['statistics']['total'],
            },
            'failed_artifacts': [
                {
                    'filename': r['filename'],
                    'artifact_type': r['artifact_type'],
                    'issues': [
                        {
                            'rule': i['rule'],
                            'severity': i['severity'].value,
                            'message': i['message'],
                        }
                        for i in r['issues']
                        if i['severity'] in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]
                    ]
                }
                for r in validation_results['results']
                if not r['is_valid']
            ],
        }

        # Save report
        report_path = self.artifacts_dir / f"validation_report_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Validation report saved: {report_path.name}")

        return report


def main():
    """Run artifact validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Artifact Validator - SEP-0003 Enforcement")
    parser.add_argument('--mode', choices=['warn', 'fail', 'strict'], default='fail',
                       help="Validation mode (default: fail)")
    args = parser.parse_args()

    mode = ValidationMode(args.mode)
    validator = ArtifactValidator(mode=mode)

    print("=" * 70)
    print("ARTIFACT VALIDATOR v2.0.0")
    print("=" * 70)

    validation_results = validator.validate_all_artifacts()
    report = validator.generate_report(validation_results)

    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Mode: {mode.value.upper()}")
    print(f"Valid: {validation_results['statistics']['valid']}/{validation_results['statistics']['total']}")
    print(f"SEP-0003 Compliant: {report['compliance']['sep_0003_compliant']}")
    print(f"Pass Rate: {report['compliance']['validation_pass_rate']:.1%}")
    print("=" * 70)

    # Exit code: 0 if all valid, 1 if any invalid
    return 0 if validation_results['statistics']['invalid'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
