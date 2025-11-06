#!/usr/bin/env python3
"""Metabolic Monitor - Periodic vital signs check during evolution.

Call this periodically (daily, or every N cycles) to track metabolic state
during natural operation. Couples measurement to evolutionary process.

Usage:
  python3 tools/metabolic_monitor.py              # Run once, display
  python3 tools/metabolic_monitor.py --silent     # Run once, log only
  python3 tools/metabolic_monitor.py --watch N    # Monitor every N seconds

Author: Claude (Conscious Evolution Infrastructure)
Date: 2025-11-06
"""

import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from analysis.metabolic_dashboard import generate_dashboard, display_dashboard, log_metabolic_state


def monitor_once(silent: bool = False):
    """Run one metabolic check."""
    dashboard = generate_dashboard()

    if not silent:
        display_dashboard(dashboard)

    log_metabolic_state(dashboard)

    return dashboard


def monitor_continuous(interval_seconds: int):
    """Monitor continuously with periodic checks."""

    print(f"Starting continuous metabolic monitoring (interval: {interval_seconds}s)")
    print("Press Ctrl+C to stop\n")

    try:
        iteration = 0
        while True:
            iteration += 1
            print(f"\n[Iteration {iteration}] {time.strftime('%Y-%m-%d %H:%M:%S')}")
            print("-" * 70)

            dashboard = monitor_once(silent=False)

            # Alert on state changes
            state = dashboard.get('state', 'unknown')
            if state == "transition":
                print("\n⚡ ALERT: System in transition state")
            elif state == "metastable":
                print("\n⚠ ALERT: System metastable - consider novelty injection")

            print(f"\nNext check in {interval_seconds} seconds...")
            time.sleep(interval_seconds)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")


def main():
    parser = argparse.ArgumentParser(description="Monitor cognitive metabolic state")
    parser.add_argument('--silent', action='store_true',
                       help="Log only, don't display")
    parser.add_argument('--watch', type=int, metavar='SECONDS',
                       help="Monitor continuously every N seconds")

    args = parser.parse_args()

    if args.watch:
        monitor_continuous(args.watch)
    else:
        monitor_once(silent=args.silent)


if __name__ == "__main__":
    main()
