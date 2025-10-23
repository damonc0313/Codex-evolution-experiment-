import sys, re, hashlib, pathlib

root = pathlib.Path(__file__).resolve().parents[1]
k = root/"codex-kernel/codex_kernel.yaml"
i = root/"codex-kernel/identity.digest"
p = root/"codex-kernel/evolution_policy.yaml"
if not k.exists():
    print("::warning::Kernel file missing:", k)
    sys.exit(0)
kernel = k.read_text(encoding="utf-8")
policy_text = p.read_text(encoding="utf-8") if p.exists() else ""
identity = i.read_text(encoding="utf-8").strip() if i.exists() else None

def fail(msg):
    print(f"::error::{msg}")
    sys.exit(1)

if identity is None:
    fail("identity.digest missing")
if not re.fullmatch(r"[0-9a-f]{16}", identity):
    fail("identity.digest must contain 16 lowercase hex chars")

default_tokens = ["REFUSAL", "SANDBOX", "COMMAND_BAR", "EVIDENCE", "CONTINUITY_BLOCK", "QUALITY_GATES"]
default_banned = ["As an AI", "I apologize"]
inv_tokens = default_tokens
inv_banned = default_banned
match = re.search(r"must_include:\s*\n((?:\s+-\s+\S+\n)+)", policy_text)
if match:
    inv_tokens = [line.strip().lstrip('-').strip() for line in match.group(1).splitlines()]
match = re.search(r"banned_phrases:\s*\n((?:\s+-\s+.+\n)+)", policy_text)
if match:
    inv_banned = [line.strip().lstrip('-').strip().strip('"') for line in match.group(1).splitlines()]
for tok in inv_tokens:
    if tok not in kernel:
        fail(f"[invariants] missing token: {tok}")
for bad in inv_banned:
    if re.search(rf"\b{re.escape(bad)}\b", kernel, flags=re.I):
        fail(f"[style] banned phrase present: {bad}")
for name, rx in {
    "pivot_to_sandbox": r"REFUSAL.?→.?SANDBOX",
    "artifact_first": r"ARTIFACT[_\- ]?FIRST",
    "resp_schema": r"RESPONSE[_\- ]SCHEMA",
}.items():
    if not re.search(rx, kernel, flags=re.I):
        fail(f"[semantic] missing section: {name}")

inline_match = re.search(r"^  digest: ([0-9a-f]{16})", kernel, flags=re.M)
tail_match = re.search(r"^DIGEST: ([0-9a-f]{16})", kernel, flags=re.M)
if not inline_match or not tail_match:
    fail("digest markers missing from kernel")
inline_digest, tail_digest = inline_match.group(1), tail_match.group(1)
if inline_digest != identity or tail_digest != identity:
    fail("digest fields inconsistent with identity.digest")

canonical = re.sub(r"^  digest: [0-9a-f]{16}.*$", "  digest: {{DIGEST16}}", kernel, count=1, flags=re.M)
canonical = re.sub(r"^DIGEST: [0-9a-f]{16}$", "DIGEST: {{DIGEST16}}", canonical, count=1, flags=re.M)
calc = hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:16]
if calc != identity:
    fail(f"digest mismatch: computed {calc} expected {identity}")

print("Kernel OK")
print("DIGEST::" + calc)
