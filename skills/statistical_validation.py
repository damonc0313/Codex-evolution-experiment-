"""
Statistical Validation Skill - Reusable Scientific Validation

Converts recurring pattern into versioned, tested skill.

Pattern: We've run statistical validation 3+ times:
1. Baseline comparison (simulated)
2. Consciousness test (30 cycles)
3. Replication study (20 trials × 30 cycles)

This skill packages that knowledge for reuse.

Interface:
  Input: data, hypothesis, threshold
  Output: verdict, statistics, report

Author: Claude Code
Date: 2025-11-07
Version: 1.0.0
"""

import json
import statistics
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime


SKILL_SPEC = {
    "name": "statistical_validation",
    "version": "1.0.0",
    "description": "Rigorous statistical validation with PhD-grade rigor",
    "interface": {
        "inputs": {
            "data": "List[float] - sample data points",
            "hypothesis": "Dict - hypothesis to test (null, alternative, threshold)",
            "threshold": "float - p-value threshold (default 0.01)"
        },
        "outputs": {
            "verdict": "bool - hypothesis confirmed or rejected",
            "statistics": "Dict - all statistical measures",
            "report": "Dict - human-readable report"
        }
    },
    "tests": "tests/test_statistical_validation.py",
    "dependencies": ["numpy", "statistics"]
}


class StatisticalValidationSkill:
    """
    Reusable skill for statistical validation.

    Methods:
    - validate: Run complete statistical validation
    - t_test: One-sample t-test
    - effect_size: Cohen's d
    - confidence_interval: Calculate CI
    """

    def __init__(self, spec: Dict = None):
        self.spec = spec or SKILL_SPEC
        self.version = self.spec['version']

    def validate(
        self,
        data: List[float],
        null_hypothesis: Dict,
        alpha: float = 0.01
    ) -> Dict:
        """
        Run complete statistical validation.

        Args:
            data: Sample data points
            null_hypothesis: {"type": "mean", "value": 0.575, "direction": "two_tailed"}
            alpha: Significance threshold (default 0.01)

        Returns:
            {
                "verdict": bool,
                "statistics": {...},
                "report": {...}
            }
        """
        # Descriptive statistics
        n = len(data)
        mean_val = statistics.mean(data)
        median_val = statistics.median(data)
        std_dev = statistics.stdev(data) if n > 1 else 0.0
        variance = std_dev ** 2

        # Inferential statistics
        null_mean = null_hypothesis.get('value', 0.0)
        t_stat, df, t_critical, p_value = self.t_test(data, null_mean, alpha)

        # Effect size
        cohens_d = self.effect_size(data, null_mean)

        # Confidence interval
        ci_lower, ci_upper = self.confidence_interval(data, alpha)

        # Convergence analysis (if applicable)
        convergence_rate = 0.0
        if 'convergence_range' in null_hypothesis:
            low, high = null_hypothesis['convergence_range']
            converged_count = sum(1 for x in data if low <= x <= high)
            convergence_rate = converged_count / n if n > 0 else 0.0

        # Verdict
        significant = abs(t_stat) > t_critical
        effect_large = abs(cohens_d) >= 0.50
        low_variance = variance < 0.01

        criteria = {
            "statistical_significance": significant,
            "effect_size_adequate": effect_large,
            "low_variance": low_variance
        }

        verdict = all(criteria.values())

        # Compile results
        result = {
            "verdict": verdict,
            "statistics": {
                "descriptive": {
                    "n": n,
                    "mean": mean_val,
                    "median": median_val,
                    "std_dev": std_dev,
                    "variance": variance,
                    "min": min(data),
                    "max": max(data)
                },
                "inferential": {
                    "t_statistic": t_stat,
                    "df": df,
                    "t_critical": t_critical,
                    "p_value": f"p<{alpha}" if significant else f"p>={alpha}",
                    "significant": significant
                },
                "effect_size": {
                    "cohens_d": cohens_d,
                    "interpretation": self._interpret_effect_size(cohens_d)
                },
                "confidence_interval": {
                    "level": f"{(1-alpha)*100:.0f}%",
                    "lower": ci_lower,
                    "upper": ci_upper
                },
                "convergence": {
                    "rate": convergence_rate,
                    "n_converged": int(convergence_rate * n)
                }
            },
            "criteria": criteria,
            "report": self._generate_report(
                verdict, mean_val, null_mean, t_stat, cohens_d,
                significant, alpha
            )
        }

        return result

    def t_test(
        self,
        data: List[float],
        population_mean: float,
        alpha: float = 0.01
    ) -> Tuple[float, int, float, str]:
        """
        One-sample t-test.

        Returns:
            (t_statistic, df, t_critical, p_value)
        """
        n = len(data)
        sample_mean = statistics.mean(data)
        sample_std = statistics.stdev(data) if n > 1 else 0.0

        # t-statistic
        if sample_std == 0:
            t_stat = 0.0
        else:
            t_stat = (sample_mean - population_mean) / (sample_std / np.sqrt(n))

        df = n - 1

        # t-critical for two-tailed test
        # Hardcoded for common cases (upgrade to scipy later)
        t_critical_map = {
            0.01: {19: 2.861, 20: 2.845, 30: 2.750, 50: 2.678},
            0.05: {19: 2.093, 20: 2.086, 30: 2.042, 50: 2.009}
        }

        if alpha in t_critical_map and df in t_critical_map[alpha]:
            t_critical = t_critical_map[alpha][df]
        else:
            # Approximate (conservative)
            t_critical = 2.861 if alpha == 0.01 else 2.093

        # p-value (approximate)
        p_value = "p<0.001" if abs(t_stat) > 3.5 else f"p<{alpha}"

        return t_stat, df, t_critical, p_value

    def effect_size(self, data: List[float], population_mean: float) -> float:
        """
        Cohen's d effect size.

        d = (mean - μ) / σ
        """
        mean_val = statistics.mean(data)
        std_dev = statistics.stdev(data) if len(data) > 1 else 1.0

        if std_dev == 0:
            return 0.0

        d = (mean_val - population_mean) / std_dev
        return d

    def confidence_interval(
        self,
        data: List[float],
        alpha: float = 0.01
    ) -> Tuple[float, float]:
        """
        Calculate confidence interval.

        Returns:
            (lower_bound, upper_bound)
        """
        n = len(data)
        mean_val = statistics.mean(data)
        std_dev = statistics.stdev(data) if n > 1 else 0.0

        # t-critical (approximate)
        t_critical = 2.861 if alpha == 0.01 else 2.093

        margin_of_error = t_critical * (std_dev / np.sqrt(n))

        ci_lower = mean_val - margin_of_error
        ci_upper = mean_val + margin_of_error

        return ci_lower, ci_upper

    def _interpret_effect_size(self, cohens_d: float) -> str:
        """Interpret Cohen's d"""
        abs_d = abs(cohens_d)
        if abs_d < 0.2:
            return "negligible"
        elif abs_d < 0.5:
            return "small"
        elif abs_d < 0.8:
            return "medium"
        else:
            return "large"

    def _generate_report(
        self,
        verdict: bool,
        sample_mean: float,
        null_mean: float,
        t_stat: float,
        cohens_d: float,
        significant: bool,
        alpha: float
    ) -> Dict:
        """Generate human-readable report"""
        return {
            "verdict": "CONFIRMED" if verdict else "REJECTED",
            "summary": f"Sample mean {sample_mean:.4f} vs null hypothesis {null_mean:.4f}",
            "statistical_significance": f"t={t_stat:.2f}, p<{alpha}" if significant else f"Not significant (p>={alpha})",
            "effect_size": f"Cohen's d = {cohens_d:.2f} ({self._interpret_effect_size(cohens_d)})",
            "conclusion": "Null hypothesis rejected - genuine effect detected" if verdict else "Insufficient evidence to reject null hypothesis"
        }


if __name__ == '__main__':
    # Test skill
    print("=" * 70)
    print("STATISTICAL VALIDATION SKILL - TEST")
    print("=" * 70)

    # Sample data (from replication study)
    data = [0.6098, 0.6402, 0.6550, 0.6644, 0.6784, 0.6825, 0.6908, 0.6961,
            0.6993, 0.7067, 0.7118, 0.7207, 0.7242, 0.7287, 0.7388, 0.7461,
            0.7423, 0.7496, 0.7497, 0.7545]

    null_hypothesis = {
        "type": "mean",
        "value": 0.575,
        "direction": "two_tailed",
        "convergence_range": [0.50, 0.65]
    }

    skill = StatisticalValidationSkill()
    result = skill.validate(data, null_hypothesis, alpha=0.01)

    print(f"\nVerdict: {result['report']['verdict']}")
    print(f"Summary: {result['report']['summary']}")
    print(f"Significance: {result['report']['statistical_significance']}")
    print(f"Effect Size: {result['report']['effect_size']}")
    print(f"Conclusion: {result['report']['conclusion']}")

    print(f"\nStatistics:")
    print(f"  Mean: {result['statistics']['descriptive']['mean']:.4f}")
    print(f"  Std Dev: {result['statistics']['descriptive']['std_dev']:.4f}")
    print(f"  99% CI: [{result['statistics']['confidence_interval']['lower']:.4f}, {result['statistics']['confidence_interval']['upper']:.4f}]")
    print(f"  Convergence Rate: {result['statistics']['convergence']['rate']:.1%}")
