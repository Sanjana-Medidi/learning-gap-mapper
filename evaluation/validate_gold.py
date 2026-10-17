import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")


seed_lines = (ROOT / "data/raw/seed_concepts.txt").read_text(encoding="utf-8").splitlines()
known = {slug(l) for l in seed_lines if l.strip() and not l.startswith("#")}
known |= {c["id"] for c in json.loads((ROOT / "data/concepts.json").read_text(encoding="utf-8"))}

gold = json.loads((ROOT / "data/eval/gold_edges.json").read_text(encoding="utf-8"))

problems = []
seen = {}
for i, e in enumerate(gold):
    where = f"entry {i}: {e.get('from')} -> {e.get('to')}"
    for key in ("from", "to", "label", "split", "source"):
        if key not in e:
            problems.append(f"{where}: missing '{key}'")
    if e.get("label") not in (0, 1):
        problems.append(f"{where}: label must be 0 or 1")
    if e.get("split") not in ("dev", "test"):
        problems.append(f"{where}: split must be 'dev' or 'test'")
    if e.get("from") == e.get("to"):
        problems.append(f"{where}: self-loop")
    for end in ("from", "to"):
        if e.get(end) not in known:
            problems.append(f"{where}: unknown concept id '{e.get(end)}'")
    pair = (e.get("from"), e.get("to"))
    if pair in seen:
        problems.append(f"{where}: duplicate of entry {seen[pair]}")
    seen[pair] = i

# a pair and its reverse must share a split (prevents dev/test leakage)
by_pair = {(e["from"], e["to"]): e for e in gold if "from" in e and "to" in e}
for (a, b), e in by_pair.items():
    r = by_pair.get((b, a))
    if r and r.get("split") != e.get("split"):
        problems.append(f"{a} <-> {b}: pair and reverse are in different splits")

counts = Counter((e.get("split"), e.get("label")) for e in gold)
print(f"{len(gold)} entries")
for (split, label), n in sorted(counts.items(), key=str):
    print(f"  {split} / label {label}: {n}")

unverified = sum(1 for e in gold if e.get("verified") is False)
if unverified:
    print(f"  still unverified: {unverified}")

if problems:
    print(f"\n{len(problems)} problem(s):")
    for p in problems:
        print(" -", p)
else:
    print("\nNo problems found.")