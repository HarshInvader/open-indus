"""Markdown tables for docs/GRAMMAR.md and RESULTS.md from grammar.json, sign_classes.csv and dev texts."""
import csv, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from glib import *  # noqa

g = json.load(open(HERE / "grammar.json"))
SC = list(csv.DictReader(open(HERE / "sign_classes.csv")))
dev = m77_units("dev")
K = g["K"]
cls_of = {}
for c in g["classes"]:
    for w in c["emissions"]:
        cls_of[w] = c["id"]
out = []
out.append("| fine class | label | share of dev tokens | P(start) | P(end) | initial / medial / final | main signs (P within class) |")
out.append("|---|---|---|---|---|---|---|")
tot = sum(sum(c["positional_profile"].values()) for c in g["classes"])
ntok = Counter()
for u in dev:
    for r, _, _ in u["runs"]:
        for x in r:
            ntok[cls_of.get(x, g["unk_class"])] += 1
NT = sum(ntok.values())
order = sorted(range(K), key=lambda c: (LABELS.index(g["classes"][c]["label"]), -ntok[c]))
for c in order:
    C = g["classes"][c]
    pp = C["positional_profile"]; s = pp["initial"] + pp["medial"] + pp["final"]
    mem = ", ".join(f"{w} {p:.2f}" for w, p in list(C["emissions"].items())[:7])
    out.append(f"| c{c} | {C['label']} | {ntok[c]/NT:.3f} | {C['start_prob']:.2f} | {C['end_prob']:.2f} | "
               f"{pp['initial']/s:.2f} / {pp['medial']/s:.2f} / {pp['final']/s:.2f} | {mem} |")
open(HERE / "table_classes.md", "w").write("\n".join(out) + "\n")

# validated classes table
rows = ["| validated class | signs | share of dev tokens | signs (dev tokens, bootstrap stability) |", "|---|---|---|---|"]
tok = Counter(); members = defaultdict(list)
for r in SC:
    tok[r["final_class"]] += int(r["dev_tokens"])
    members[r["final_class"]].append(r)
N = sum(tok.values())
for L in LABELS:
    mem = members[L]
    if not mem:
        rows.append(f"| {L} | 0 | 0 | - |"); continue
    ex = ", ".join(f"{r['sign']} ({r['dev_tokens']}, {float(r['confidence']):.2f})" for r in mem[:12])
    rows.append(f"| {L} | {len(mem)} | {tok[L]/N:.3f} | {ex}{' ...' if len(mem) > 12 else ''} |")
open(HERE / "table_validated.md", "w").write("\n".join(rows) + "\n")

# example parses: most common complete dev seal texts of length 3-7, with fine class and label
ex = []
seen = 0
cands = [u for u in dev if u["full"] and u["register"] == "seal" and 3 <= len(u["signs"]) <= 7]
random.Random(4).shuffle(cands)
for u in cands[:14]:
    t = u["runs"][0][0]
    parts = []
    for x in t:
        c = cls_of.get(x, g["unk_class"])
        parts.append(f"{x}/{g['classes'][c]['label'][:4]}")
    ex.append("    " + "  ".join(parts))
open(HERE / "table_examples.txt", "w").write("\n".join(ex) + "\n")
print(open(HERE / "table_classes.md").read()); print(open(HERE / "table_validated.md").read()); print("\n".join(ex))
