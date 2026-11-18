"""Step 1b: corrected M77 -> Wells (ICIT) concordance.

Start: the harness ICIT mapping (bridge_WM.json + harness.py's font-verified overrides).
Evidence: out/cooc.json "pos" counts = mapping-FREE same-position co-occurrence on the 395 register-matched
pairs whose two readings have equal length (cooc.py). Rules, applied in order:

  R1 re-pair   the current W partner(s) never co-occur with M, another W co-occurs >= 3 times and makes
               >= 75% of M's positional co-occurrences -> replace the partner.
  R2 add       M has no bridge entry; modal W co-occurs >= 3 times and >= 2/3 of M's co-occurrences -> add.
               (2 co-occurrences and share 1.0 -> 'provisional' tier, kept separately.)
  R3 alternate current partner co-occurs; another W co-occurs >= 3 times and is not 'owned' by a different
               M sign (no other M with >= 3 positional co-occurrences with that W) -> add as an alternate
               (Wells splits the sign). 2 co-occurrences -> provisional.
  R4 narrow    M has >= 2 partners; one partner never co-occurs with M (>= 5 co-occurrences in all) and
               co-occurs >= 5 times with another M sign -> drop it from M (it belongs to that sign).
  R5 analogy   ticked fish follow the corrected plain-fish order (Wells numbers each ticked fish one
               after its plain form); only where the matched texts have no contrary evidence.

Writes out/concordance.json (primary map, provisional map, changes with evidence) and
corrected_concordance.csv (one row per M sign: primary partners, provisional partners, rule, evidence).
"""
import sys, json, csv
from pathlib import Path
from collections import Counter, defaultdict

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "signlist_robustness"))
import harness as H  # noqa

PLAIN_FIX = {"M59": "W220", "M65": "W235", "M67": "W240", "M70": "W231", "M72": "W233"}
TICK_ANALOGY = {"M60": "W226", "M66": "W236", "M68": "W241", "M71": "W232", "M73": "W234"}


def build():
    V = H.Variant("ICIT")
    d = json.load(open(HERE / "out" / "cooc.json"))
    pos = defaultdict(Counter); posW = defaultdict(Counter)
    for m, w, c in d["pos"]:
        pos[m][w] += c; posW[w][m] += c
    allM = sorted(set(V.inv) | set(pos), key=lambda s: int(s[1:]))
    cur = {m: set(V.inv.get(m, set())) for m in allM}
    prim = {m: set(v) for m, v in cur.items()}
    prov = defaultdict(set)
    changes = []

    def owned(w, m):
        return [x for x, c in posW[w].items() if x != m and c >= 3]

    for m in allM:
        ctr = pos.get(m, Counter()); tot = sum(ctr.values())
        if not tot:
            continue
        (w1, c1), = ctr.most_common(1)
        incur = sum(c for w, c in ctr.items() if w in cur[m])
        ev = dict(positional=dict(ctr.most_common(6)), total=tot, current=sorted(cur[m]))
        if cur[m] and incur == 0 and c1 >= 3 and c1 / tot >= 0.75:
            prim[m] = {w1}; changes.append(dict(m=m, rule="R1 re-pair", old=sorted(cur[m]), new=[w1], tier="primary", **ev))
        elif not cur[m] and c1 / tot >= 2 / 3 and c1 >= 2:
            if c1 >= 3:
                prim[m] = {w1}; changes.append(dict(m=m, rule="R2 add", old=[], new=[w1], tier="primary", **ev))
            elif c1 / tot == 1.0:
                prov[m].add(w1); changes.append(dict(m=m, rule="R2 add", old=[], new=[w1], tier="provisional", **ev))
        elif incur > 0:
            for w, c in ctr.items():
                if w in cur[m] or c < 2 or owned(w, m):
                    continue
                if c >= 3:
                    prim[m].add(w); changes.append(dict(m=m, rule="R3 alternate", old=sorted(cur[m]), new=sorted(prim[m]), tier="primary", **ev))
                else:
                    prov[m].add(w); changes.append(dict(m=m, rule="R3 alternate", old=sorted(cur[m]), new=sorted(cur[m] | {w}), tier="provisional", **ev))
    # R4 narrow
    for m in allM:
        if len(prim[m]) < 2:
            continue
        ctr = pos.get(m, Counter())
        if sum(ctr.values()) < 5:
            continue
        for w in sorted(prim[m]):
            if ctr[w] == 0 and len(prim[m]) > 1:
                others = {x: c for x, c in posW[w].items() if x != m and c >= 5}
                if others:
                    old = sorted(prim[m]); prim[m].discard(w)
                    changes.append(dict(m=m, rule="R4 narrow", old=old, new=sorted(prim[m]), tier="primary",
                                        positional=dict(ctr.most_common(6)), total=sum(ctr.values()), current=old,
                                        note=f"{w} co-occurs with {others}"))
    # R5 ticked fish by analogy (plain-fish fix is already applied by R1 above)
    for m, w in TICK_ANALOGY.items():
        ctr = pos.get(m, Counter())
        contrary = {x: c for x, c in ctr.items() if x != w}
        if prim.get(m) != {w} and not (contrary and max(contrary.values()) >= ctr[w]):
            old = sorted(prim.get(m, set()))
            prim[m] = {w}
            changes.append(dict(m=m, rule="R5 analogy" if m != "M66" else "R1 re-pair (3/3) + R5", old=old, new=[w], tier="primary",
                                positional=dict(ctr.most_common(6)), total=sum(ctr.values()), current=old))
    for m, w in PLAIN_FIX.items():
        assert prim[m] == {w}, (m, prim[m])
    return V, cur, prim, prov, changes, pos


def main():
    V, cur, prim, prov, changes, pos = build()
    # dedupe changes per (m, tier) keeping the last (R3 can fire twice)
    seen = {}
    for c in changes:
        seen[(c["m"], c["rule"], c["tier"])] = c
    changes = list(seen.values())
    out = dict(primary={m: sorted(v) for m, v in prim.items() if v},
               provisional={m: sorted(prim.get(m, set()) | prov[m]) for m in prov},
               harness_original={m: sorted(v) for m, v in cur.items() if v},
               changes=changes)
    json.dump(out, open(HERE / "out" / "concordance.json", "w"), indent=1)
    rows = []
    chg = defaultdict(list)
    for c in changes: chg[c["m"]].append(c)
    for m in sorted(set(prim) | set(prov), key=lambda s: int(s[1:])):
        if not prim.get(m) and not prov.get(m):
            continue
        rows.append(dict(m77=m, wells_primary=";".join(sorted(prim.get(m, []))),
                         wells_provisional_extra=";".join(sorted(prov.get(m, set()) - prim.get(m, set()))),
                         harness_original=";".join(sorted(cur.get(m, []))),
                         changed="; ".join(f"{c['rule']} [{c['tier']}]" for c in chg[m]),
                         positional_cooccurrence=" ".join(f"{w}:{n}" for w, n in pos.get(m, Counter()).most_common(5))))
    with open(HERE / "corrected_concordance.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    for c in sorted(changes, key=lambda c: (c["tier"], c["rule"], c["m"])):
        print(c["tier"], c["rule"], c["m"], c["old"], "->", c["new"], c.get("positional"), c.get("note", ""))
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
