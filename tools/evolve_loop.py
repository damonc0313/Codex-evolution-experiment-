#!/usr/bin/env python3
"""Codex Infinite Evolution Loop watcher."""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
QUERY_FILE = ROOT / "runtime" / "user_query.txt"
MENTOR_FILE = ROOT / "runtime" / "mentor_feedback.txt"
HASH_PATH = ROOT / ".last_query_hash"
STOP_FILE = ROOT / "runtime" / "stop.txt"
VALIDATOR = ROOT / "tools" / "validate_kernel.py"

IDLE_THRESHOLD = 3
SLEEP_SECONDS = 10


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


def run_validator() -> bool:
    result = subprocess.run(
        [sys.executable, str(VALIDATOR)],
        check=False,
    )
    return result.returncode == 0


def emit_self_query_block(failure_count: int, reason: str) -> None:
    artifacts_dir = ROOT / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)
    timestamp = int(time.time())
    payload = {
        "artifact_type": "self_query_block",
        "failure_count": failure_count,
        "reason": reason,
        "timestamp": timestamp,
    }
    target = artifacts_dir / f"self_query_block_{timestamp}.json"
    target.write_text(
        json.dumps(payload, indent=2),
        encoding="utf-8",
    )
    print(f"[AUTO] Loop paused — see {target}")


def main() -> None:
    if not QUERY_FILE.exists():
        print("No user query file found.")
        return

    last_hash = None
    if HASH_PATH.exists():
        last_hash = HASH_PATH.read_text(encoding="utf-8").strip()

    idle_count = 0
    auto_failures = 0
    pending_auto_hash: str | None = None

    while True:
        if STOP_FILE.exists():
            print("[AUTO] Stop flag detected — exiting loop.")
            STOP_FILE.unlink(missing_ok=True)
            break

        h = hash_file(QUERY_FILE)
        if h != last_hash:
            print(f"⚡ Detected new or modified query in {QUERY_FILE}")
            run_cycle()
            validator_ok = run_validator()
            is_auto = pending_auto_hash is not None and h == pending_auto_hash
            if is_auto:
                pending_auto_hash = None
                if validator_ok:
                    auto_failures = 0
                else:
                    auto_failures += 1
                    print(
                        f"[AUTO] Validator failure detected for autonomous query (count={auto_failures})."
                    )
                    if auto_failures > 2:
                        emit_self_query_block(
                            auto_failures,
                            "Autonomous query produced validator failures.",
                        )
                        break
            else:
                auto_failures = 0

            HASH_PATH.write_text(h, encoding="utf-8")
            last_hash = h
            idle_count = 0
        else:
            idle_count += 1
            if idle_count >= IDLE_THRESHOLD:
                print("[AUTO] Synthesizing next user query...")
                subprocess.run(
                    [sys.executable, "tools/self_query_encoder.py"],
                    check=False,
                )
                pending_auto_hash = hash_file(QUERY_FILE)
                idle_count = 0
            else:
                print("🧘 Waiting for user_query update...")
        time.sleep(SLEEP_SECONDS)


if __name__ == "__main__":
    main()
