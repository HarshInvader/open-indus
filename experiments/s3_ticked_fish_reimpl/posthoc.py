"""S3 post hoc (NOT pre-registered): definition variants tried after the main run, only to explain why my
counts differ from the reported ones. Run from the repo root:
    .venv/bin/python -I experiments/s3_ticked_fish_reimpl/posthoc.py      -> posthoc.json
"""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]; HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(HERE))
import run as r
from corpus.load import dev_heldout, icit_texts, distinct, runs

T, P = set(r.TICKED), set(r.PLAIN)
P12 = {"M59", "M61", "M62", "M63", "M64", "M65", "M67", "M69", "M70", "M72", "M74", "M75"}  # list in ledger/v2_reruns.py


def lines_complete(texts):
    out = []
    for t in texts:
        if t["site"] == "West Asian finds" or not t["complete"] or "#" in t["seq"]: continue
        cur = []
        for s in t["seq"] + ["|"]:
            if s == "|":
                if cur: out.append(cur)
                cur = []
            else: cur.append(s)
    return out


def both(seqs, plain=P):
    return dict(fisher=r.fisher(r.tokens(seqs, T), r.tokens(seqs, plain)), length_matched=r.length_matched(r.tokens(seqs, T)))


OUT = {}
for v in (1, 2):
    _, ho = dev_heldout(version=v)
    OUT[f"split_v{v}"] = dict(single_line_clean=both(r.clean_m77(ho)), complete_line_final=both(lines_complete(ho)),
                             all_breakfree_runs=both([x for t in ho if t["site"] != "West Asian finds" for x in runs(t["seq"])]))
_, ho = dev_heldout(version=2)
OUT["split_v2_plain12"] = dict(single_line_clean=both(r.clean_m77(ho), P12),
                               all_breakfree_runs=both([x for t in ho if t["site"] != "West Asian finds" for x in runs(t["seq"])], P12))
I = [t for t in icit_texts() if t["region"] not in r.NONNATIVE_REGIONS]
for lab, II in (("distinct", distinct(I)), ("all_objects", I)):
    clean = [t["seq"] for t in II if t["complete"] and len(t["segments"]) == 1 and "#" not in t["seq"] and "|" not in t["seq"] and t["seq"]]
    OUT[f"icit_{lab}_clean"] = r.length_matched(r.tokens(clean, set(r.W_TICKED)))
    OUT[f"icit_{lab}_all_segments"] = r.length_matched(r.tokens([s for t in II for s in t["segments"] if s], set(r.W_TICKED)))
json.dump(OUT, open(HERE / "posthoc.json", "w"), indent=1)
print(json.dumps(OUT, indent=1))

# Added after reading experiments/audit_followups/RESULTS.md (post hoc, after my own run): the original team
# maps M73 -> W234, which is not in bridge_WM.json. Same ICIT counts with W234 counted as ticked.
WT5 = set(r.W_TICKED) | {"W234"}
for lab, II in (("distinct", distinct(I)), ("all_objects", I)):
    clean = [t["seq"] for t in II if t["complete"] and len(t["segments"]) == 1 and "#" not in t["seq"] and "|" not in t["seq"] and t["seq"]]
    OUT[f"icit_{lab}_clean_withW234"] = r.length_matched(r.tokens(clean, WT5))
    OUT[f"icit_{lab}_all_segments_withW234"] = r.length_matched(r.tokens([s for t in II for s in t["segments"] if s], WT5))
    new = [t["seq"] for t in II if t["complete"] and len(t["segments"]) == 1 and "#" not in t["seq"] and "|" not in t["seq"] and t["seq"]
           and not any(k in t["site"].lower().replace("-", "") for k in r.M77_SITE_KEYS)]
    OUT[f"icit_{lab}_sites_not_in_M77_withW234"] = r.length_matched(r.tokens(new, WT5))
json.dump(OUT, open(HERE / "posthoc.json", "w"), indent=1)
