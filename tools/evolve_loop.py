#!/usr/bin/env python3
"""Codex Infinite Evolution Loop watcher."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUERY_FILE = ROOT / "runtime" / "user_query.txt"
MENTOR_FILE = ROOT / "runtime" / "mentor_feedback.txt"
HASH_PATH = ROOT / ".last_query_hash"


def hash_file(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def run_cycle() -> None:
    print("🔁 Starting Ω cycle...")
    subprocess.run([sys.executable, "tools/run_omega_cycle.py"], check=False)
    print("✅ Cycle complete.\n")

    if MENTOR_FILE.exists():
        print("[MENTOR] Reading mentor feedback for next query synthesis")
        feedback = MENTOR_FILE.read_text(encoding="utf-8", errors="ignore")
        subprocess.run(
            [
                sys.executable,
                "tools/run_omega_cycle.py",
                "--mentor",
                feedback,
            ],
            check=False,
        )


def main() -> None:
    if not QUERY_FILE.exists():
        print("No user query file found.")
        return

    last_hash = None
    if HASH_PATH.exists():
        last_hash = HASH_PATH.read_text(encoding="utf-8").strip()

    while True:
        h = hash_file(QUERY_FILE)
        if h != last_hash:
            print(f"⚡ Detected new or modified query in {QUERY_FILE}")
            run_cycle()
            HASH_PATH.write_text(h, encoding="utf-8")
            last_hash = h
        else:
            print("🧘 Waiting for user_query update...")
        time.sleep(60)


if __name__ == "__main__":
    main()
