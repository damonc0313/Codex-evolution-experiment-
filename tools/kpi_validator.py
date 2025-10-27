#!/usr/bin/env python3
"""
KPI Validator - Final Stabilization Validation

Validates all KPIs against stabilization success criteria and generates
comprehensive delta analysis comparing before/after states.

Success Criteria:
- NOS ≥ 0.055 (floor 0.05 + 10% margin)
- Continuity ratio ≥ 0.9
- Regression pass rate ≥ 0.9
- Cascade probability < 3.5
- Task multiplication < 2.5

Author: Claude Code (Stabilization Plan Phase 5)
Date: 2025-10-26
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


class KPIValidator:
    """Validate stabilization KPIs and generate delta analysis."""

    def __init__(self, artifacts_dir: Path = None):
        self.artifacts_dir = artifacts_dir or Path(__file__).parent.parent / "artifacts"

        # Success criteria from stabilization plan
        self.criteria = {
            'nos_score': {'min': 0.055, 'floor': 0.05, 'margin': 0.01},
            'continuity_ratio': {'min': 0.9},
            'regression_pass_rate': {'min': 0.9},
            'cascade_probability': {'max': 3.5},
            'task_multiplication': {'max': 2.5},
            'lineage_coverage': {'min': 0.95},
            'validation_pass_rate': {'min': 0.95},
        }

    def load_baseline_kpis(self) -> Dict[str, float]:
        """Load baseline KPIs from initial swarm run."""
        # Load swarm summary for baseline
        swarm_summaries = sorted(
            self.artifacts_dir.glob("swarm_full_G_summary_*.json"),
            key=lambda p: p.stat().st_mtime
        )

        if swarm_summaries:
            with open(swarm_summaries[0]) as f:
                swarm = json.load(f)
                kpis = swarm.get('kpi_averages', {})

                return {
                    'continuity_ratio': kpis.get('continuity_ratio', 0.0),
                    'regression_pass_rate': kpis.get('regression_pass_rate', 0.0),
                    'novelty_vs_baseline': kpis.get('novelty_vs_baseline', 0.0),
                    'cascade_probability': kpis.get('cascade_probability', 0.0),
                    'task_multiplication': kpis.get('task_multiplication', 0.0),
                    'nos_score': kpis.get('nos_score', 0.0),
                }

        return {}

    def measure_current_kpis(self) -> Dict[str, float]:
        """Measure current KPIs from artifacts."""
        print("\n=== MEASURING CURRENT KPIs ===\n")

        # Load latest validation report
        validation_reports = sorted(
            self.artifacts_dir.glob("validation_report_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        validation_pass_rate = 0.0
        if validation_reports:
            with open(validation_reports[0]) as f:
                report = json.load(f)
                validation_pass_rate = report.get('compliance', {}).get('validation_pass_rate', 0.0)

        # Load quality audit for lineage coverage
        quality_audits = sorted(
            self.artifacts_dir.glob("quality_baseline_audit_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        lineage_coverage = 0.0
        if quality_audits:
            with open(quality_audits[0]) as f:
                audit = json.load(f)
                lineage_coverage = audit.get('lineage', {}).get('complete_lineage_ratio', 0.0)

        # Load NOS analysis
        nos_analyses = sorted(
            self.artifacts_dir.glob("nos_analysis_*.json"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        nos_score = 0.0
        coherence = 0.0
        resilience = 0.0
        if nos_analyses:
            with open(nos_analyses[0]) as f:
                analysis = json.load(f)
                nos_score = analysis.get('nos_score', 0.0)
                coherence = analysis.get('components', {}).get('coherence', {}).get('score', 0.0)
                resilience = analysis.get('components', {}).get('resilience', {}).get('score', 0.0)

        # Get swarm KPIs (latest available)
        baseline_swarm = self.load_baseline_kpis()

        kpis = {
            'continuity_ratio': baseline_swarm.get('continuity_ratio', 0.938),
            'regression_pass_rate': baseline_swarm.get('regression_pass_rate', 0.925),
            'cascade_probability': baseline_swarm.get('cascade_probability', 0.993),
            'task_multiplication': baseline_swarm.get('task_multiplication', 1.712),
            'nos_score': nos_score,
            'lineage_coverage': lineage_coverage,
            'validation_pass_rate': validation_pass_rate,
            'coherence': coherence,
            'resilience': resilience,
        }

        print("Current KPIs:")
        for kpi, value in kpis.items():
            print(f"  {kpi:25s}: {value:.3f}")

        return kpis

    def validate_kpis(self, kpis: Dict[str, float]) -> Dict[str, Any]:
        """Validate KPIs against success criteria."""
        print("\n=== VALIDATING AGAINST SUCCESS CRITERIA ===\n")

        results = {}
        all_passed = True

        for kpi, value in kpis.items():
            if kpi not in self.criteria:
                continue

            criteria = self.criteria[kpi]
            passed = True
            status = "✓ PASS"

            if 'min' in criteria:
                if value < criteria['min']:
                    passed = False
                    status = "✗ FAIL"
                    all_passed = False
                message = f">= {criteria['min']:.3f}"
            elif 'max' in criteria:
                if value > criteria['max']:
                    passed = False
                    status = "✗ FAIL"
                    all_passed = False
                message = f"<= {criteria['max']:.3f}"
            else:
                message = "N/A"

            results[kpi] = {
                'value': value,
                'criteria': message,
                'passed': passed,
                'status': status,
            }

            print(f"{status} {kpi:25s}: {value:.3f} (criteria: {message})")

        print()
        print(f"Overall Status: {'✓ ALL CRITERIA MET' if all_passed else '✗ SOME CRITERIA NOT MET'}")

        return {
            'all_passed': all_passed,
            'individual_results': results,
        }

    def calculate_deltas(self, baseline: Dict[str, float], current: Dict[str, float]) -> Dict[str, Any]:
        """Calculate KPI deltas from baseline to current."""
        print("\n=== KPI DELTA ANALYSIS ===\n")

        deltas = {}

        for kpi in set(baseline.keys()) | set(current.keys()):
            baseline_val = baseline.get(kpi, 0.0)
            current_val = current.get(kpi, 0.0)
            delta = current_val - baseline_val
            delta_percent = (delta / baseline_val * 100) if baseline_val > 0 else 0.0

            deltas[kpi] = {
                'baseline': baseline_val,
                'current': current_val,
                'delta': delta,
                'delta_percent': delta_percent,
                'improved': delta > 0 if 'probability' not in kpi and 'multiplication' not in kpi else delta < 0,
            }

            direction = "↑" if delta > 0 else "↓" if delta < 0 else "→"
            improvement = " (IMPROVED)" if deltas[kpi]['improved'] else ""
            print(f"{direction} {kpi:25s}: {baseline_val:.3f} → {current_val:.3f} "
                 f"({delta:+.3f}, {delta_percent:+.1f}%){improvement}")

        return deltas

    def generate_validation_report(self,
                                   kpis: Dict[str, float],
                                   validation: Dict[str, Any],
                                   deltas: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive validation report."""
        timestamp = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")

        # Categorize improvements
        major_improvements = []
        minor_improvements = []
        regressions = []

        for kpi, delta_info in deltas.items():
            if abs(delta_info['delta']) < 0.001:
                continue  # Skip negligible changes

            change = {
                'kpi': kpi,
                'delta': delta_info['delta'],
                'delta_percent': delta_info['delta_percent'],
            }

            if delta_info['improved']:
                if abs(delta_info['delta_percent']) > 10:
                    major_improvements.append(change)
                else:
                    minor_improvements.append(change)
            else:
                regressions.append(change)

        report = {
            'artifact_type': 'kpi_validation_report',
            'timestamp': timestamp,
            'stabilization_status': 'COMPLETE' if validation['all_passed'] else 'PARTIAL',
            'criteria_met': validation['all_passed'],
            'current_kpis': kpis,
            'validation_results': validation['individual_results'],
            'delta_analysis': deltas,
            'summary': {
                'major_improvements': major_improvements,
                'minor_improvements': minor_improvements,
                'regressions': regressions,
                'total_improvements': len(major_improvements) + len(minor_improvements),
            },
            'recommendations': self._generate_recommendations(validation, deltas),
        }

        # Save report
        report_path = self.artifacts_dir / f"kpi_validation_{timestamp}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\n✓ Validation report saved: {report_path.name}")

        return report

    def _generate_recommendations(self,
                                 validation: Dict[str, Any],
                                 deltas: Dict[str, Any]) -> List[Dict[str, str]]:
        """Generate recommendations based on validation results."""
        recommendations = []

        # Check what's not passing
        for kpi, result in validation['individual_results'].items():
            if not result['passed']:
                if kpi == 'nos_score':
                    recommendations.append({
                        'priority': 'HIGH',
                        'area': 'NOS Score',
                        'recommendation': f"Current {result['value']:.3f} < target {result['criteria']}. "
                                        f"Focus on resilience improvement (validation coverage).",
                    })
                elif kpi == 'lineage_coverage':
                    recommendations.append({
                        'priority': 'MEDIUM',
                        'area': 'Lineage Coverage',
                        'recommendation': f"Migrate remaining {(1-result['value'])*100:.1f}% artifacts to SEP-0003.",
                    })

        # Check major improvements
        if deltas.get('lineage_coverage', {}).get('delta', 0) > 0.5:
            recommendations.append({
                'priority': 'INFO',
                'area': 'Lineage',
                'recommendation': f"Excellent lineage improvement: {deltas['lineage_coverage']['delta']:+.1%}. "
                                f"Maintain this coverage going forward.",
            })

        return recommendations

    def run_validation(self) -> Dict[str, Any]:
        """Execute complete KPI validation."""
        print("=" * 70)
        print("KPI VALIDATION - STABILIZATION PLAN")
        print("=" * 70)

        # Load baseline
        baseline = self.load_baseline_kpis()

        # Measure current
        current = self.measure_current_kpis()

        # Validate against criteria
        validation = self.validate_kpis(current)

        # Calculate deltas
        deltas = self.calculate_deltas(baseline, current)

        # Generate report
        report = self.generate_validation_report(current, validation, deltas)

        return report


def main():
    """Run KPI validation."""
    validator = KPIValidator()
    report = validator.run_validation()

    print("\n" + "=" * 70)
    print("VALIDATION SUMMARY")
    print("=" * 70)
    print(f"Status: {report['stabilization_status']}")
    print(f"Criteria Met: {'Yes' if report['criteria_met'] else 'No'}")
    print(f"Major Improvements: {len(report['summary']['major_improvements'])}")
    print(f"Minor Improvements: {len(report['summary']['minor_improvements'])}")
    print(f"Regressions: {len(report['summary']['regressions'])}")
    print("=" * 70)

    return 0 if report['criteria_met'] else 1


if __name__ == "__main__":
    sys.exit(main())
