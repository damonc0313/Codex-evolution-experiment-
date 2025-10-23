#!/usr/bin/env python3
"""
Codex kernel/policy/artifacts validator
- Computes canonical kernel digest (sha256[:16] of full file text with digest slots neutralized)
- Confirms identity.digest and trailing DIGEST match canonical
- Checks policy invariants and refusal pivot
- Lints artifacts/ for minimal schema
Exits 0 on success, 1 on any failure.
"""

from __future__ import annotations
import sys, re, json, hashlib
from pathlib import Path

try:
    import yaml
except Exception:
    print("ERROR: PyYAML not installed; run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
KERNEL = ROOT / "codex-kernel" / "codex_kernel.yaml"
POLICY = ROOT / "codex-kernel" / "evolution_policy.yaml"
ARTIFACTS_DIR = ROOT / "artifacts"

def sha16_text(s: str) -> str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()[:16]

def read_text(p: Path) -> str:
    if not p.exists():
        fail(f"Missing file: {p}")
    return p.read_text(encoding="utf-8", errors="replace")

errors: list[str] = []
def fail(msg: str) -> None:
    errors.append(msg)

def main() -> int:
    # --- Kernel digest checks ---
    ktxt = read_text(KERNEL)
    canonical_view = re.sub(r'^(\s*digest:\s*)([0-9a-fA-F]{16})(.*)$', r"\1{{DIGEST16}}\3", ktxt, count=1, flags=re.M)
    canonical_view = re.sub(r'^(\s*DIGEST:\s*)([0-9a-fA-F]{16})(\s*)$', r"\1{{DIGEST16}}\3", canonical_view, count=1, flags=re.M)
    digest_calc = sha16_text(canonical_view)

    m_field = re.search(r'^\s*digest:\s*([0-9a-fA-F]{16})', ktxt, flags=re.M)
    m_tail_all = re.findall(r'^\s*DIGEST:\s*([0-9a-fA-F]{16})\s*$', ktxt, flags=re.M)

    digest_field = m_field.group(1) if m_field else None
    digest_tail = m_tail_all[-1] if m_tail_all else None

    if not digest_field:
        fail("Kernel: identity.digest missing")
    if not digest_tail:
        fail("Kernel: trailing DIGEST line missing")

    if digest_field and digest_field != digest_calc:
        fail(f"Kernel: identity.digest mismatch (identity={digest_field} vs calc={digest_calc})")
    if digest_tail and digest_tail != digest_calc:
        fail(f"Kernel: DIGEST tail mismatch (tail={digest_tail} vs calc={digest_calc})")

    # --- Policy checks ---
    ptxt = read_text(POLICY)
    req_tokens = ["REFUSAL","SANDBOX","COMMAND_BAR","EVIDENCE","CONTINUITY_BLOCK","QUALITY_GATES"]
    for tok in req_tokens:
        if tok not in ptxt:
            fail(f"Policy: missing required invariant token: {tok}")

    if not re.search(r'refusal_policy:\s*"?pivot_to_sandbox"?', ptxt):
        fail('Policy: refusal_policy must be "pivot_to_sandbox"')

    # --- Artifacts sanity ---
    if not ARTIFACTS_DIR.exists():
        fail(f"Artifacts dir missing: {ARTIFACTS_DIR}")
    else:
        for p in sorted(ARTIFACTS_DIR.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
            except Exception as e:
                fail(f"Artifact {p.name}: invalid JSON ({e})")
                continue
            if not isinstance(data, dict):
                fail(f"Artifact {p.name}: top-level must be object")
            elif "artifact_type" not in data:
                fail(f"Artifact {p.name}: missing 'artifact_type' field")

    # --- Result ---
    if errors:
        print("VALIDATION: FAIL")
        for e in errors:
            print(" -", e)
        print(f"Canonical kernel digest: {digest_calc}")
        return 1

    print("VALIDATION: OK")
    print(f"Kernel digest: {digest_calc} (identity + DIGEST match)")
    print("Policy: invariants present; pivot_to_sandbox ON")
    print(f"Artifacts: {len(list(ARTIFACTS_DIR.glob('*.json')))} json files OK")
    return 0

if __name__ == "__main__":
    sys.exit(main())
