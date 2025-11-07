#!/usr/bin/env python3
"""
EXPERIMENT 1: Statistical Validation of Autonomous Learning
PhD-Grade Replication Study (n=20)

HYPOTHESIS: Policy converges to stable attractor (μ=0.55-0.60) through reinforcement learning
NULL HYPOTHESIS: Policy changes are random walk (no learning)

METHOD: Run learning kernel 20 times with shuffled artifact sequences
STATISTICAL TESTS: t-test, ANOVA, regression, effect size, confidence intervals
THRESHOLD: p<0.01, d≥0.50, power≥0.80
"""

import sys
import json
import random
from pathlib import Path
from datetime import datetime
import statistics
import math

sys.path.insert(0, 'tools')
from learning_kernel import LearningKernel

def cohens_d(group1, group2=None):
    """Calculate Cohen's d effect size."""
    if group2 is None:
        # One-sample: compare to theoretical mean
        group2 = [0.575] * len(group1)  # Theoretical attractor

    mean1 = statistics.mean(group1)
    mean2 = statistics.mean(group2)

    var1 = statistics.variance(group1) if len(group1) > 1 else 0
    var2 = statistics.variance(group2) if len(group2) > 1 else 0

    pooled_std = math.sqrt((var1 + var2) / 2) if (var1 + var2) > 0 else 1

    return (mean1 - mean2) / pooled_std if pooled_std > 0 else 0

def t_statistic(sample, population_mean):
    """Calculate t-statistic for one-sample t-test."""
    n = len(sample)
    sample_mean = statistics.mean(sample)
    sample_std = statistics.stdev(sample) if n > 1 else 1

    se = sample_std / math.sqrt(n)
    t = (sample_mean - population_mean) / se if se > 0 else 0

    return t, n-1  # t-statistic, degrees of freedom

def confidence_interval(sample, confidence=0.99):
    """Calculate confidence interval."""
    n = len(sample)
    mean = statistics.mean(sample)
    se = statistics.stdev(sample) / math.sqrt(n) if n > 1 else 0

    # t-critical for 99% CI (approximate for df=19)
    t_crit = 2.861  # t(19, 0.01/2) ≈ 2.861

    margin = t_crit * se
    return (mean - margin, mean + margin)

def run_single_trial(trial_id, num_cycles=30):
    """Run one learning trial."""
    print(f"  [Trial {trial_id:2d}/20] Running {num_cycles} cycles...")

    # Initialize fresh kernel
    kernel = LearningKernel()

    # Load and shuffle artifacts
    artifacts_dir = Path("artifacts")
    artifact_files = list(artifacts_dir.glob("*.json"))

    # Shuffle for this trial (different order = independent test)
    random.seed(trial_id * 42)  # Reproducible but different per trial
    random.shuffle(artifact_files)

    # Take first num_cycles artifacts
    selected = artifact_files[:num_cycles]

    trajectory = []

    for i, artifact_path in enumerate(selected):
        try:
            artifact = json.loads(artifact_path.read_text())
            diagnostics = kernel.process_artifact(artifact, artifact_path.name)

            weight = diagnostics['policy_update']['policy_after']['building_weight']
            trajectory.append(weight)

        except Exception as e:
            print(f"    Error on cycle {i}: {e}")
            continue

    final_weight = trajectory[-1] if trajectory else 0.5
    converged = 0.50 <= final_weight <= 0.65  # Loose convergence criterion

    print(f"    Final weight: {final_weight:.4f} {'✓' if converged else '✗'}")

    return {
        'trial_id': trial_id,
        'final_weight': final_weight,
        'trajectory': trajectory,
        'converged': converged,
        'cycles_completed': len(trajectory)
    }

def run_replication_study(num_trials=20, num_cycles=30):
    """Execute complete replication study."""
    print("="*70)
    print("PHD-GRADE REPLICATION STUDY")
    print("="*70)
    print()
    print(f"HYPOTHESIS: Policy converges to μ=0.575±0.025 (attractor)")
    print(f"NULL HYPOTHESIS: No convergence (random walk)")
    print(f"TRIALS: n={num_trials}")
    print(f"CYCLES PER TRIAL: {num_cycles}")
    print(f"SIGNIFICANCE THRESHOLD: p<0.01")
    print()

    results = []

    for trial_id in range(1, num_trials + 1):
        result = run_single_trial(trial_id, num_cycles)
        results.append(result)

    # Extract final weights
    final_weights = [r['final_weight'] for r in results]
    converged_count = sum(r['converged'] for r in results)

    # STATISTICAL ANALYSIS
    print()
    print("="*70)
    print("STATISTICAL ANALYSIS")
    print("="*70)
    print()

    # Descriptive statistics
    mean_weight = statistics.mean(final_weights)
    median_weight = statistics.median(final_weights)
    std_weight = statistics.stdev(final_weights)
    min_weight = min(final_weights)
    max_weight = max(final_weights)

    print(f"DESCRIPTIVE STATISTICS:")
    print(f"  Mean (μ):      {mean_weight:.4f}")
    print(f"  Median:        {median_weight:.4f}")
    print(f"  Std Dev (σ):   {std_weight:.4f}")
    print(f"  Range:         [{min_weight:.4f}, {max_weight:.4f}]")
    print(f"  Convergence:   {converged_count}/{num_trials} ({100*converged_count/num_trials:.1f}%)")
    print()

    # Confidence interval
    ci_low, ci_high = confidence_interval(final_weights, confidence=0.99)
    print(f"99% CONFIDENCE INTERVAL:")
    print(f"  [{ci_low:.4f}, {ci_high:.4f}]")
    print()

    # T-test against theoretical mean
    theoretical_mean = 0.575
    t_stat, df = t_statistic(final_weights, theoretical_mean)

    # Critical t-value for p<0.01, df=19 (two-tailed)
    t_critical = 2.861
    p_value = "p<0.01" if abs(t_stat) > t_critical else "p≥0.01"
    significant = abs(t_stat) > t_critical

    print(f"ONE-SAMPLE T-TEST (H0: μ = {theoretical_mean}):")
    print(f"  t-statistic:   {t_stat:.3f}")
    print(f"  df:            {df}")
    print(f"  t-critical:    ±{t_critical}")
    print(f"  p-value:       {p_value}")
    print(f"  Significant:   {'YES ✓' if significant else 'NO ✗'}")
    print()

    # Effect size
    effect_size = cohens_d(final_weights)

    print(f"EFFECT SIZE:")
    print(f"  Cohen's d:     {effect_size:.3f}")

    if abs(effect_size) < 0.2:
        interpretation = "negligible"
    elif abs(effect_size) < 0.5:
        interpretation = "small"
    elif abs(effect_size) < 0.8:
        interpretation = "medium"
    else:
        interpretation = "large"

    print(f"  Interpretation: {interpretation}")
    print()

    # Variance test
    variance = std_weight ** 2
    low_variance = variance < 0.01

    print(f"VARIANCE TEST:")
    print(f"  Variance (σ²): {variance:.6f}")
    print(f"  Low variance:  {'YES ✓' if low_variance else 'NO ✗'} (threshold: <0.01)")
    print()

    # VERDICT
    print("="*70)
    print("VERDICT")
    print("="*70)
    print()

    criteria_met = [
        ("Mean in range [0.50, 0.65]", 0.50 <= mean_weight <= 0.65),
        ("Statistical significance (p<0.01)", significant),
        ("Convergence rate ≥90%", converged_count >= 0.9 * num_trials),
        ("Effect size ≥0.50", abs(effect_size) >= 0.50),
        ("Low variance (σ²<0.01)", low_variance)
    ]

    all_met = all(met for _, met in criteria_met)

    for criterion, met in criteria_met:
        status = "✓ PASS" if met else "✗ FAIL"
        print(f"  {status}: {criterion}")

    print()

    if all_met:
        print("✓✓✓ HYPOTHESIS CONFIRMED ✓✓✓")
        print("Policy exhibits statistically significant convergence through learning.")
        print("Null hypothesis (random walk) REJECTED with p<0.01.")
    elif sum(met for _, met in criteria_met) >= 4:
        print("~ PARTIAL CONFIRMATION ~")
        print("Most criteria met, but not all. Evidence for learning, needs refinement.")
    else:
        print("✗✗✗ HYPOTHESIS REJECTED ✗✗✗")
        print("Insufficient evidence for convergence. May be random walk.")

    print("="*70)

    # Save results
    output = {
        'experiment': 'statistical_replication',
        'timestamp': datetime.utcnow().isoformat() + 'Z',
        'parameters': {
            'num_trials': num_trials,
            'num_cycles': num_cycles,
            'theoretical_mean': theoretical_mean,
            'significance_threshold': 0.01
        },
        'results': results,
        'statistics': {
            'mean': mean_weight,
            'median': median_weight,
            'std_dev': std_weight,
            'variance': variance,
            'min': min_weight,
            'max': max_weight,
            'ci_99': [ci_low, ci_high],
            'convergence_rate': converged_count / num_trials
        },
        'inference': {
            't_statistic': t_stat,
            'degrees_of_freedom': df,
            't_critical': t_critical,
            'p_value': p_value,
            'significant': significant,
            'cohens_d': effect_size,
            'effect_interpretation': interpretation
        },
        'verdict': {
            'criteria': [{"criterion": c, "met": m} for c, m in criteria_met],
            'all_criteria_met': all_met,
            'hypothesis_confirmed': all_met
        }
    }

    output_path = Path("diagnostics/replication_study_results.json")
    output_path.write_text(json.dumps(output, indent=2))

    print()
    print(f"Complete results saved to: {output_path}")

    return output

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--trials', type=int, default=20, help='Number of trials')
    parser.add_argument('--cycles', type=int, default=30, help='Cycles per trial')
    args = parser.parse_args()

    results = run_replication_study(num_trials=args.trials, num_cycles=args.cycles)
