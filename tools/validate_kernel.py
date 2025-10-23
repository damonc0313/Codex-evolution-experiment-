import sys, re, hashlib, pathlib

try:
    import yaml  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - environment dependent
    yaml = None
root = pathlib.Path(__file__).resolve().parents[1]
k = root/"codex-kernel/codex_kernel.yaml"
p = root/"codex-kernel/evolution_policy.yaml"
if not k.exists():
    print("::warning::Kernel file missing:", k); sys.exit(0)
kernel = k.read_text(encoding="utf-8")
if yaml is not None and p.exists():
    policy = yaml.safe_load(p.read_text(encoding="utf-8"))
else:
    policy = {}
def fail(msg): print(f"::error::{msg}"); sys.exit(1)
inv = (policy.get("invariants") or {})
for tok in inv.get("must_include", ["REFUSAL","SANDBOX","COMMAND_BAR","EVIDENCE","CONTINUITY_BLOCK","QUALITY_GATES"]):
    if tok not in kernel: fail(f"[invariants] missing token: {tok}")
for bad in inv.get("banned_phrases", ["As an AI","I apologize"]):
    if re.search(rf"\b{re.escape(bad)}\b", kernel, flags=re.I): fail(f"[style] banned phrase present: {bad}")
for name,rx in {
  "pivot_to_sandbox": r"REFUSAL.?→.?SANDBOX",
  "artifact_first":   r"ARTIFACT[_\- ]?FIRST",
  "resp_schema":      r"RESPONSE[_\- ]SCHEMA",
}.items():
    if not re.search(rx, kernel, flags=re.I): fail(f"[semantic] missing section: {name}")
match = re.search(r"^DIGEST:\s*([0-9a-f]{16})\s*$", kernel, flags=re.MULTILINE)
if not match:
    fail("[digest] DIGEST line missing or malformed")
normalized = re.sub(r"^DIGEST:.*$", "DIGEST:", kernel, flags=re.MULTILINE)
calc = hashlib.sha256(normalized.encode("utf-8")).hexdigest()[:16]
if match.group(1).lower() != calc:
    fail(f"[digest] mismatch: recorded={match.group(1)} computed={calc}")
print("Kernel OK")
print("DIGEST::"+calc)
