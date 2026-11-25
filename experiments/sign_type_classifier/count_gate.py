"""sign_type_classifier count gate. LABEL-FREE in the sense required by the brief: it counts
tokens, sign types and label shares only. No feature is built, no classifier is fitted and no
accuracy is computed. Minimum: MINIMUM.txt (written and hashed first).

Usage (from anywhere):
  python3 -I experiments/sign_type_classifier/count_gate.py --ja <dir of Japanese extracts>
The Japanese extracts live outside the repo (CC BY-SA, not committed); only counts and the
pinned revision ids are written. Output: experiments/sign_type_classifier/count_gate.json
"""
import argparse
import collections
import json
import random
import statistics
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import tokenise as T  # noqa: E402

REPO = T.REPO
SEED = 0
DRAW = 10000
MIN_OCC = 3
CLASSES = ("SYL", "LOGO", "DET", "NUM", "MEAS")


def sign_labels(lines):
    """Cell-level label per sign = its modal role over all clean tokens. Also returns the
    share of the modal role (purity) per sign."""
    by = collections.defaultdict(collections.Counter)
    for ln in lines:
        for sid, role in ln:
            by[sid][role] += 1
    lab, pur = {}, {}
    for sid, c in by.items():
        (r, n), = c.most_common(1)
        lab[sid] = r
        pur[sid] = n / sum(c.values())
    return lab, pur, by


def describe(name, family, lines, stats, licence, label_source, rng_lengths):
    toks = [t for ln in lines for t in ln]
    lab, pur, by = sign_labels(lines)
    role_tok = collections.Counter(r for _, r in toks)
    type_lab = collections.Counter(lab.values())
    poly = [s for s in lab if pur[s] < 0.8]
    poly_tok = sum(sum(by[s].values()) for s in poly)
    rng = random.Random(SEED)
    pieces = T.cut_to_indus_shape(lines, rng_lengths, rng)
    ds = T.draws(pieces, random.Random(SEED + 1), DRAW)
    per_draw = []
    for d in ds:
        occ = collections.Counter(sid for p in d for sid, _ in p)
        scored = [s for s, n in occ.items() if n >= MIN_OCC]
        cls = collections.Counter(lab[s] for s in scored)
        per_draw.append({"tokens": sum(occ.values()), "types": len(occ),
                         "scored_types": len(scored),
                         "scored_by_label": {c: cls.get(c, 0) for c in CLASSES},
                         "mean_text_len": round(sum(len(p) for p in d) / len(d), 2)})

    def med(key, sub=None):
        v = [(x[key][sub] if sub else x[key]) for x in per_draw]
        return (statistics.median(v), min(v)) if v else (None, None)

    sc = {c: med("scored_by_label", c) for c in CLASSES}
    scored_draw = [x["scored_types"] for x in per_draw]
    maj = None
    if per_draw:
        # majority-class share among scored SYL+LOGO types, median over draws (stated
        # baseline for the gated two-class target; counts only, no prediction)
        sh = []
        for x in per_draw:
            a, b = x["scored_by_label"]["SYL"], x["scored_by_label"]["LOGO"]
            if a + b:
                sh.append(max(a, b) / (a + b))
        maj = round(statistics.median(sh), 3) if sh else None
    out = {
        "cell": name, "family": family, "licence": licence, "label_source": label_source,
        "clean_lines": len(lines), "clean_tokens": len(toks), "sign_types": len(lab),
        "line_stats": {k: v for k, v in stats.items() if k != "revids"},
        "token_share_by_role": {c: round(role_tok.get(c, 0) / max(1, len(toks)), 4)
                                for c in CLASSES},
        "type_count_by_label": {c: type_lab.get(c, 0) for c in CLASSES},
        "polyvalent_signs_purity_lt_0.8": len(poly),
        "token_share_on_polyvalent_signs": round(poly_tok / max(1, len(toks)), 4),
        "indus_shape": {"n_draws": len(per_draw),
                        "types_per_draw_median_min": med("types"),
                        "scored_types_per_draw_median_min": med("scored_types"),
                        "scored_by_label_median_min": sc,
                        "mean_text_len_median": med("mean_text_len")[0],
                        "majority_share_SYL_vs_LOGO_median": maj},
    }
    e = {
        "E1_labels_ge_90pct": True,   # every clean token carries an edition role by construction
        "E2_reading_free_ids": True,  # glyph / sign-list name; see tokenise.py
        "E3_ge_20000_clean_tokens": len(toks) >= 2 * DRAW,
        "E4_ge_20_scored_SYL_and_LOGO": bool(per_draw) and sc["SYL"][1] is not None
        and sc["SYL"][0] >= 20 and sc["LOGO"][0] >= 20,
        "E5_licence_ok": True,
    }
    out["eligibility"] = e
    out["eligible"] = all(e.values())
    out["DET_ge_20_scored"] = bool(per_draw) and (sc["DET"][0] or 0) >= 20
    return out


def linear_a_record_only():
    d = json.load(open(REPO / "sources/paragorth_Indus-/other-scripts/linear-a/data/corpus_ra.json"))
    lines, cur, bad = [], [], False
    seen = dropped = 0
    for x in d:
        for t in x["tokens"] + [{"t": "nl"}]:
            if t["t"] == "nl":
                if cur or bad:
                    seen += 1
                    if bad:
                        dropped += 1
                    else:
                        lines.append(cur)
                cur, bad = [], False
                continue
            if t["t"] == "div":
                continue
            if t.get("st") not in (None, "read") or t["t"] == "unk":
                bad = True
                continue
            if t["t"] == "word":
                cur += [(s, "SYL") for s in t["s"]]
            elif t["t"] == "logo":
                cur.append((t["v"], "LOGO"))
            elif t["t"] == "num":
                cur += T._lb_place_tokens(int(t["v"])) if t["v"] else []
                if t.get("frac"):
                    cur += [("FRAC_" + str(f), "NUM") for f in t["frac"]]
    return lines, {"lines_seen": seen, "lines_dropped": dropped}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ja", required=True, help="directory of Japanese Wikipedia extracts")
    a = ap.parse_args()

    ind = T.indus_lines()
    lengths = [len(r) for r in ind]
    itok = [t for r in ind for t in r]
    iocc = collections.Counter(s for s, _ in itok)
    inum = T.indus_numeral_signs()
    indus = {"source": "data/m77_texts.jsonl, distinct texts, split at | and # (corpus.load.runs)",
             "runs": len(ind), "tokens": len(itok), "sign_types": len(iocc),
             "mean_run_len": round(statistics.mean(lengths), 2),
             "median_run_len": statistics.median(lengths),
             "len_hist_1_to_10plus": [sum(1 for x in lengths if x == k) for k in range(1, 10)]
             + [sum(1 for x in lengths if x >= 10)],
             "scored_types_ge3": sum(1 for n in iocc.values() if n >= MIN_OCC),
             "numeral_sign_types_in_list": len(inum),
             "numeral_types_attested": sum(1 for s in iocc if s in inum),
             "numeral_scored_types_ge3": sum(1 for s, n in iocc.items() if s in inum and n >= MIN_OCC),
             "numeral_token_share": round(sum(1 for s, _ in itok if s in inum) / len(itok), 4)}

    cells = []
    saao = sorted((REPO / "experiments/layout_word_division/raw/oracc").glob("saao-saa*.zip"))
    cl, cs = T.oracc_lines(saao, "akk")
    cells.append(describe("cun_saao_neoassyrian", "cuneiform", cl, cs, "CC0 (Oracc metadata.json)",
                          "Oracc GDL markup: role=logo / v / det / n", lengths))
    oakk = [REPO / "experiments/meaning_classes/raw/oracc/oakk.zip"]
    ol, os_ = T.oracc_lines(oakk, "akk")
    cells.append(describe("cun_oakk_akkadian_lines", "cuneiform", ol, os_, "CC0 (Oracc)",
                          "Oracc GDL markup", lengths))
    ll, ls = T.linearb_lines()
    cells.append(describe("aegean_linearb_damos", "Aegean", ll, ls, "CC BY-NC-SA 4.0 (DAMOS; local use)",
                          "DAMOS edition convention: lowercase = phonetic, uppercase = ideogram,"
                          " metric letters, digits", lengths))
    ul, us = T.linearb_lines(keep_underdot=True)
    lbu = describe("aegean_linearb_damos_SENS_underdot_kept", "Aegean", ul, us,
                   "CC BY-NC-SA 4.0 (DAMOS; local use)",
                   "as above; RECORD-ONLY sensitivity: underdotted (damaged but read) signs kept",
                   lengths)
    lbu["record_only"] = True
    lbu["eligible"] = False
    cells.append(lbu)
    al, as_ = linear_a_record_only()
    la = describe("aegean_lineara_record_only", "Aegean", al, as_,
                  "lineara.xyz (code public-domain dedication; transcription licence unverified)",
                  "lineara.xyz token kinds (word / logo / num), via SigLA-checked corpus_ra", lengths)
    la["eligibility"]["E5_licence_ok"] = False
    la["eligible"] = False
    cells.append(la)
    jl, js = T.japanese_lines(a.ja)
    jc = describe("sino_japanese_wikipedia", "Sinographic", jl, js,
                  "CC BY-SA 4.0 (Wikipedia; counts only, text not committed)",
                  "Unicode block: kanji = LOGO, kana = SYL, digits = NUM", lengths)
    jc["pinned_revisions"] = js["revids"]
    cells.append(jc)

    fams = collections.defaultdict(list)
    for c in cells:
        if c["eligible"]:
            fams[c["family"]].append(c["cell"])
    det_fams = sorted({c["family"] for c in cells if c["eligible"] and c["DET_ge_20_scored"]})
    gate = {"eligible_families": {k: v for k, v in sorted(fams.items())},
            "n_eligible_families": len(fams),
            "F1_ge_3_families": len(fams) >= 3,
            "F2_ge_4_families": len(fams) >= 4,
            "F3_DET_families": det_fams,
            "F3_DET_gated": len(det_fams) >= 2,
            "held_out_unit": "family"}
    res = {"minimum_file": "experiments/sign_type_classifier/MINIMUM.txt",
           "seed": SEED, "draw_tokens": DRAW, "min_occ_scored": MIN_OCC,
           "indus": indus, "cells": cells, "gate": gate}
    (HERE / "count_gate.json").write_text(json.dumps(res, indent=1, ensure_ascii=False))
    print(json.dumps(gate, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
