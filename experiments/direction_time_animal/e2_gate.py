"""E2 gate: how many minority-direction (L-R) texts have a direction that could not come from slot signs or copies?
Run: .venv/bin/python experiments/direction_time_animal/e2_gate.py"""
import json
from collections import Counter
from dta_lib import OUT, icit_texts, m77_lines, signs, to_m, W2M


def slot_marked(rl_seqs, min_n=10, thr=0.4):
    n, ini, fin = Counter(), Counter(), Counter()
    for s in rl_seqs:
        for x in s: n[x] += 1
        ini[s[0]] += 1; fin[s[-1]] += 1
    return {x for x in n if n[x] >= min_n and (ini[x] / n[x] >= thr or fin[x] / n[x] >= thr)}


def gate(lr, rl, jar):
    rl = [s for s in rl if len(s) >= 2]
    marked = slot_marked(rl)
    rlset = {tuple(s) for s in rl}
    lr = sorted({tuple(s) for s in lr if len(s) >= 2})
    steps = {"distinct_LR_len2plus": len(lr)}
    a = [s for s in lr if not (set(s) & jar)]; steps["no_jar"] = len(a)
    b = [s for s in a if s[0] not in marked and s[-1] not in marked]; steps["ends_not_slot_marked"] = len(b)
    c = [s for s in b if s not in rlset and tuple(reversed(s)) not in rlset]; steps["not_copy_of_RL"] = len(c)
    return steps, c, len(marked)


def main():
    res = {}
    # M77, line level
    L = m77_lines()
    lr = [l["signs"] for l in L if l["direction"] == "left-to-right"]
    rl = [l["signs"] for l in L if l["direction"] == "right-to-left"]
    s77, keep77, nm77 = gate(lr, rl, {"M342"})
    res["M77"] = dict(steps=s77, n_slot_marked_signs=nm77)
    # ICIT, text level (line breaks dropped)
    I = icit_texts()
    jarW = {"W740"} | {w for w, m in W2M.items() if m == "M342"}
    lr = [signs(t["seq"]) for t in I if t["direction"] == "L/R"]
    rl = [signs(t["seq"]) for t in I if t["direction"] == "R/L"]
    si, keepi, nmi = gate(lr, rl, jarW)
    res["ICIT"] = dict(steps=si, n_slot_marked_signs=nmi)
    # union by bridged sequence
    u = {tuple(s) for s in keep77} | {tuple(to_m(x) for x in s) for s in keepi}
    res["G1_strict_recorded_criterion"] = 0
    res["G2_union_distinct"] = len(u)
    res["G2_types_ICIT"] = dict(Counter(t["type"].split(":")[0] for t in I if t["direction"] == "L/R"
                                        and tuple(signs(t["seq"])) in set(keepi)))
    # G3 cross-editor: ICIT L/R texts whose bridged sequence is also an M77 L-R line
    m77lr = {tuple(l["signs"]) for l in L if l["direction"] == "left-to-right"}
    res["G3_LR_in_both_editors_by_sequence"] = len({tuple(to_m(x) for x in signs(t["seq"])) for t in I
                                                     if t["direction"] == "L/R"} & m77lr)
    res["gate_threshold"] = 100
    res["decision"] = "RUN" if res["G2_union_distinct"] >= 100 else "DROPPED"
    print(json.dumps(res, indent=1))
    json.dump(res, open(OUT / "e2_gate.json", "w"), indent=1)


if __name__ == "__main__":
    main()
