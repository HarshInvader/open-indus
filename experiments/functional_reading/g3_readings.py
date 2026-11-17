"""Produce readings.csv (every M77 object-side text) and lexicon.csv, plus a candidate list of
informative inscriptions. Grammar and lexicon are the frozen dev-only model."""
import csv, json
from collections import Counter, defaultdict
import numpy as np
from fr import *

dev, ho, dev_g, lex, comps, G = load_model()
ho_keys = {" ".join(t["seq"]) for t in ho}
dev_keys = {" ".join(t["seq"]) for t in dev}

W = {"A": 1.0, "B": 0.7, "C": 0.4, "-": 0.1}


def sign_w(s):
    e = lex.get(s)
    if not e: return 0.05
    if e["source"] == "dev-positional": return 0.3
    return W.get(e["grade"], 0.1)


rows = []; label_counts = Counter(); n_ok = 0
for t in m77_texts():
    key = " ".join(t["seq"])
    lines_c, roles_s, ok_all, n_cut = [], [], True, 0
    for (r, so, eo) in clean_runs(t):
        p = G.viterbi(r, so, eo)
        ok = p is not None
        roles, cuts = G.robust_parse(r, so, eo)
        if not ok: ok_all = False; n_cut += len(cuts)
        cs = read_line(r, roles, lex, comps)
        if so: cs = [dict(label="BREAK", signs=["#"], gloss="(damaged: text missing before)", grade="-")] + cs
        if eo: cs = cs + [dict(label="BREAK", signs=["#"], gloss="(damaged: text missing after)", grade="-")]
        lines_c.append(cs); roles_s.append(" ".join(f"{s}/{ro}" for s, ro in zip(r, roles)) + (" !cut@" + ",".join(map(str, cuts)) if cuts else ""))
        for c in cs: label_counts[c["label"]] += 1
    allsigns = [s for s in t["seq"] if s not in ("|", "#")]
    conf = float(np.mean([sign_w(s) for s in allsigns])) if allsigns else 0.0
    if not ok_all: conf *= 0.5
    n_ok += ok_all
    rows.append(dict(text_no=t["text_no"], side=t["side"], site=t["site"], object_type=t["object_type"],
                     split="heldout" if key in ho_keys else "dev" if key in dev_keys else "dup",
                     signs=" ".join(t["seq"]), parse_roles=" || ".join(roles_s), reading=fmt_reading(lines_c),
                     gloss=gloss_text(lines_c), parsed_by_grammar=int(ok_all),
                     confidence=round(conf, 3), confidence_band="high" if conf >= 0.7 else "medium" if conf >= 0.45 else "low"))

with open(OUT / "readings.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print("readings:", len(rows), "texts; parsed by the grammar:", n_ok, f"({n_ok / len(rows):.1%})")
print("confidence bands:", Counter(r["confidence_band"] for r in rows))

# ---------------------------------------------------------------- lexicon
_, _, _, ntext = positional_profile(dev_g)
lexrows = []
for s, e in sorted(lex.items(), key=lambda kv: -ntext.get(kv[0], 0)):
    mass = {r: G.ecount.get((s, r), 0.0) for r in e["roles"]}
    tot = sum(mass.values()) or 1
    lexrows.append(dict(item=s, kind="sign", dev_texts=ntext.get(s, 0),
                        roles="; ".join(f"{ROLE_NAME[r]} {mass[r] / tot:.2f}" for r in sorted(e["roles"], key=lambda r: -mass[r])),
                        meaning_category=e["category"], evidence=e["evidence"],
                        role_grade=e["grade"] if e["grade"] != "-" else "unassigned",
                        meaning_grade=e["mgrade"] if e["mgrade"] != "-" else "none", source=e["source"]))
big = Counter()
for t in dev_g:
    for r in runs(t["seq"]):
        big.update(zip(r, r[1:]))
for k in sorted(set(comps) | set(NAMED_COMPOUNDS), key=lambda k: -big.get(k, 0)):
    if k in NAMED_COMPOUNDS:
        kind, cat, ev, g, gm = NAMED_COMPOUNDS[k]
        src = "hand (evidence from other teams)"
    else:
        kind, cat, ev, g, gm = "FORMULA", "recurrent fixed unit; meaning unknown", f"dev bigram n={big[k]}, conditional share >=0.5", "B", "-"
        src = "dev"
    lexrows.append(dict(item="-".join(k), kind="sequence:" + kind, dev_texts=big.get(k, 0), roles="", meaning_category=cat,
                        evidence=ev, role_grade=g, meaning_grade=gm if gm != "-" else "none", source=src))
with open(OUT / "lexicon.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(lexrows[0].keys())); w.writeheader(); w.writerows(lexrows)
gr = Counter((r["kind"].split(":")[0], r["role_grade"]) for r in lexrows)
print("lexicon entries:", len(lexrows), dict(gr))
mg = Counter(r["meaning_grade"] for r in lexrows if r["kind"] == "sign"); print("sign meaning grades:", dict(mg))
# token coverage of graded assignments (distinct texts, all M77)
tok = Counter(); tot = 0
for t in distinct(m77_texts()):
    for s in t["seq"]:
        if s in ("|", "#"): continue
        tot += 1
        e = lex.get(s)
        tok["unseen" if not e else e["grade"] if e["source"] == "hand" else ("dev-positional C" if e["grade"] == "C" else "unknown noun")] += 1
cov = {k: round(v / tot, 3) for k, v in tok.items()}
print("token share by role grade (distinct M77 texts):", cov)
mtok = Counter()
for t in distinct(m77_texts()):
    for s in t["seq"]:
        if s in ("|", "#"): continue
        e = lex.get(s); mtok[e["mgrade"] if e else "-"] += 1
print("token share by meaning grade:", {k: round(v / tot, 3) for k, v in mtok.items()})
json.dump(dict(n_readings=len(rows), parsed=n_ok, bands=Counter(r["confidence_band"] for r in rows),
               label_counts=label_counts, token_share_role_grade=cov,
               token_share_meaning_grade={k: round(v / tot, 3) for k, v in mtok.items()},
               lexicon_counts={f"{a}|{b}": v for (a, b), v in gr.items()}),
          open(OUT / "g3_readings.json", "w"), indent=1)

# ---------------------------------------------------------------- candidates for the write-up
seen = set(); cand = []
for r in rows:
    if r["signs"] in seen: continue
    seen.add(r["signs"])
    labs = set(x.split(":")[0].strip("[") for x in r["reading"].split("] ["))
    labs -= {"NOUN", "BREAK"}
    score = len(labs) * r["confidence"] * (1 if r["parsed_by_grammar"] else 0.5)
    cand.append((score, r))
cand.sort(key=lambda x: -x[0])
with open(OUT / "candidates.txt", "w") as f:
    for sc, r in cand[:150]:
        f.write(f"{sc:.2f}\t{r['text_no']}/{r['side']}\t{r['site']}\t{r['object_type']}\t{r['split']}\t{r['signs']}\n\t{r['reading']}\n\t{r['gloss']}\n")
