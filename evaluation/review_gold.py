"""Walk through unverified gold-set entries one at a time.

Run from the repo root:
    python evaluation/review_gold.py

Keys: c = confirm   f = flip label   e = edit source note   s = skip   q = quit
The file is saved after every action, so you can stop whenever you like.
"""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "data/eval/gold_edges.json"

RULE = (
    "Rule: label 1 only if you NEED A to understand B and NO other concept sits between them.\n"
    "      Otherwise label 0 (reversed, sibling, unrelated, or indirect)."
)


def load():
    return json.loads(PATH.read_text(encoding="utf-8"))


def save(gold):
    tmp = PATH.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(gold, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, PATH)


def ask(prompt):
    try:
        return input(prompt).strip()
    except EOFError:
        return "q"


def main():
    gold = load()
    todo = [i for i, e in enumerate(gold) if e.get("verified") is not True]
    total = len(gold)
    print(f"{total - len(todo)}/{total} verified, {len(todo)} to review.\n")
    print(RULE)

    for n, i in enumerate(todo, 1):
        e = gold[i]
        meaning = "IS a direct prerequisite" if e["label"] == 1 else "is NOT a direct prerequisite"
        print("\n" + "-" * 70)
        print(f"[{n}/{len(todo)}]  entry {i}   split: {e['split']}")
        print(f"  {e['from']}  ->  {e['to']}")
        print(f"  current label: {e['label']}  ({e['from']} {meaning} of {e['to']})")
        print(f"  source: {e['source']}")

        while True:
            k = ask("  [c]onfirm  [f]lip  [e]dit source  [s]kip  [q]uit > ").lower()
            if k == "c":
                e["verified"] = True
                save(gold)
                print("  saved: verified.")
                break
            if k == "f":
                e["label"] = 1 - e["label"]
                note = ask("  Why? (short reason, becomes the new source note) > ")
                e["source"] = note if note else e["source"] + "; relabeled on review"
                e["verified"] = True
                save(gold)
                print(f"  saved: label is now {e['label']}.")
                rev = next((g for g in gold if g["from"] == e["to"] and g["to"] == e["from"]), None)
                if rev is not None:
                    print(f"  note: the reverse pair ({rev['from']} -> {rev['to']}) exists with label "
                          f"{rev['label']}. Make sure it still makes sense.")
                break
            if k == "e":
                note = ask("  New source note > ")
                if note:
                    e["source"] = note
                    save(gold)
                    print("  saved: source updated (still unverified).")
                    print(f"  source: {e['source']}")
                continue
            if k == "s":
                print("  skipped.")
                break
            if k == "q":
                left = sum(1 for g in gold if g.get("verified") is not True)
                print(f"\nStopped. {left} still unverified. Run validate_gold.py before committing.")
                return
            print("  Please press c, f, e, s or q.")

    left = sum(1 for g in gold if g.get("verified") is not True)
    print(f"\nDone. {left} still unverified (skipped entries). Run validate_gold.py before committing.")


if __name__ == "__main__":
    main()