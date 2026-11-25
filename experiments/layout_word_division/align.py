"""Back-mapping, gates input, G1 join and the record-only Dencker lines for layout_word_division.

Prereg: docs/prereg/layout_word_division.md (SEALED v2, tag `layout_word_division`); this file is hashed under tag
`layout_word_division_code`. Every subcommand checks the prereg, this file and score.py against HASHES.txt (exit 2),
and refuses to run unless the label key of the round and both rater output files have their sha256 in HASHES.txt.
Shared code comes from score.py in this folder, imported after an explicit `sys.path.insert(0, <this folder>)`
(python -I drops the script folder). Nothing else is imported from here.

Subcommands (repo root; `nice -n 10 .venv/bin/python -I experiments/layout_word_division/align.py ...`):
  validate --round R --file F [--file F2]  R1 format check of rater output(s) against the key. No geometry, no labels.
  measure  --round R --a FA --b FB        Maps every box back from the rotated (and, for F2, 2x) image to the crop
                                          frame and reverses line and box order (§4.2). raw/aligned/boxes_<R>.json,
                                          and the §5.3 synthetic lines raw/aligned/synth_<R>.json.
  g2       --round R                      Label-free gate inputs: G2 (calibration agent boxes vs Dencker gold),
                                          G2b (S2 first 10, agent vs agent), G3 (box heights).
                                          raw/aligned/gates_<R>.json. Then: score.py gates --round R.
  pseudo   --round R                      §5.4 lines: calibration (+extra) tablets joined by G1, labels from each
                                          line's own ORACC word lengths, shuffled (seed 20261127).
                                          raw/aligned/pseudo_<R>.json. Then: score.py pseudo --round R.
  join     --round R [--g2-round R0]      G1 (§4.4) for S1 (ORACC) and S2 (CDLI ATF), with the drop rate and the
                                          40% F1 rule, plus sign-class flags. Refuses unless the gates of the round
                                          passed (out/gates_*.json), §5.2 (out/synth_check.json) and §5.4
                                          (out/pseudo_*.json) were run. raw/aligned/joined_<R>.json, out/g1_<R>.json.
  dencker  --round R                      Record-only S1 Dencker lines (D5, description): Dencker gold boxes of the
                                          line-annotated ORACC tablets, joined to ORACC word boundaries.
                                          raw/aligned/dencker_<R>.json (per-gap values stay in raw/).
Dencker boxes are used only in g2 (G2 gold) and dencker (record-only AUC).
"""
import argparse
import json
import math
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # explicit: import score.py from this folder (python -I removes it from sys.path)
import score as S  # noqa: E402

import numpy as np  # noqa: E402

ME = Path(__file__).resolve()
SCORE = HERE / "score.py"
DRAWS = S.RAW / "draws.json"
CROPMAN = S.RAW / "crops_manifest.json"
SYN_LINES = S.RAW / "synth" / "lines.json"
SEED_PSEUDO = 20261127
VIEW = {"obverse": "Obv", "reverse": "Rev"}
IOU_G1 = 0.5
IOU_G2 = 0.3


def seal():
    return S.seal_check([ME, SCORE])


def load_key(rnd):
    kp = S.KEYS / f"key_{rnd}.json"
    sha = S.sha256_file(kp)
    if not S.sha_in_hashes(sha):
        raise SystemExit(f"label key {S.rel_to_root(kp)} (sha256 {sha}) is not in docs/prereg/HASHES.txt")
    return S.read_json(kp), sha


def require_hashed(path):
    p = Path(path).resolve()
    sha = S.sha256_file(p)
    if not S.sha_in_hashes(sha):
        raise SystemExit(f"rater file {p.name} (sha256 {sha}) is not in docs/prereg/HASHES.txt; refusing to run")
    return sha


def load_boxes(rnd):
    """boxes_<R>.json, re-checking that the key and both rater files it came from are still hashed."""
    b = S.read_json(S.ALIGNED / f"boxes_{rnd}.json")
    for r in ("A", "B"):
        if not S.sha_in_hashes(b["rater_sha256"][r]):
            raise SystemExit(f"rater {r} output of round {rnd} is not in HASHES.txt; refusing to run")
    if not S.sha_in_hashes(b["key_sha256"]):
        raise SystemExit(f"label key of round {rnd} is not in HASHES.txt; refusing to run")
    return b


# ----------------------------------------------------------------------------------------------------------------
# validate / measure
# ----------------------------------------------------------------------------------------------------------------


def format_problems(out, key, rater):
    bad = []
    if not isinstance(out, dict) or not isinstance(out.get("crops"), dict):
        return ["top level must be an object with a 'crops' object"]
    if out.get("rater") != rater:
        bad.append(f"rater field is {out.get('rater')!r}, expected {rater!r}")
    labels = key["raters"][rater]
    for lab in out["crops"]:
        if lab not in labels:
            bad.append(f"unknown crop label {lab}")
    for lab in labels:
        c = out["crops"].get(lab)
        if c is None:
            bad.append(f"{lab}: missing")
            continue
        if not isinstance(c, dict) or not isinstance(c.get("lines"), list):
            bad.append(f"{lab}: no 'lines' list")
            continue
        for li, ln in enumerate(c["lines"]):
            if not isinstance(ln, list):
                bad.append(f"{lab} line {li}: not a list")
                continue
            for bi, b in enumerate(ln):
                ok = isinstance(b, list) and len(b) == 4 and all(
                    isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v) for v in b)
                if not ok or not (b[2] > b[0] and b[3] > b[1]):
                    bad.append(f"{lab} line {li} box {bi}: not [x0,y0,x1,y1] with x1>x0, y1>y0")
    return bad


def cmd_validate(args):
    seal()
    key, _ = load_key(args.round)
    rep = {}
    for f in args.file:
        require_hashed(f)
        out = S.read_json(f)
        rater = out.get("rater") if isinstance(out, dict) else None
        if rater not in ("A", "B"):
            rep[Path(f).name] = ["rater field must be 'A' or 'B'"]
            continue
        rep[Path(f).name] = format_problems(out, key, rater)
    for k, v in rep.items():
        print(k, "OK" if not v else f"BAD FORMAT ({len(v)} problems; R1: re-run once with the same model)")
        for p in v[:20]:
            print("   ", p)
    S.write_json(S.ALIGNED / f"validate_{args.round}.json", {"utc": S.utc(), "files": rep})
    sys.exit(0 if all(not v for v in rep.values()) else 1)


def cmd_measure(args):
    info = seal()
    key, ksha = load_key(args.round)
    shas, outs = {}, {}
    for r, f in (("A", args.a), ("B", args.b)):
        shas[r] = require_hashed(f)
        outs[r] = S.read_json(f)
        probs = format_problems(outs[r], key, r)
        if probs:
            raise SystemExit(f"rater {r} output fails the format check ({len(probs)} problems): run validate (R1)")
    man = S.read_json(CROPMAN)
    boxes = {}
    for r in ("A", "B"):
        for lab, e in key["raters"][r].items():
            cid = e["crop_id"]
            got = outs[r]["crops"].get(lab, {}).get("lines", [])
            lines = S.unmap_lines(got, e["W"], e["H"], e["scale"], rotated=e.get("rotated", True))
            lines = [ln for ln in lines if ln]  # an empty line list carries no box
            m = man.get(cid, {})
            d = boxes.setdefault(cid, {"tablet": m.get("tablet", cid), "face": m.get("face"), "sets": e["sets"],
                                       "W": e["W"], "H": e["H"], "scale": e["scale"]})
            d[r] = lines
            d[f"{r}_label"] = lab
    res = {"round": args.round, "utc": S.utc(), "seal": info, "key_sha256": ksha, "rater_sha256": shas,
           "rater_files": {r: Path(f).name for r, f in (("A", args.a), ("B", args.b))},
           "f2": key.get("f2"), "s2_full": key.get("s2_full"), "crops": boxes}
    S.write_json(S.ALIGNED / f"boxes_{args.round}.json", res)
    # §5.3 synthetic measurer lines (truth from synth.py)
    syn = [cid for cid, d in boxes.items() if "synth" in d["sets"]]
    if syn:
        truth = {e["id"]: e for e in S.read_json(SYN_LINES)["lines"]}
        L = []
        for cid in sorted(syn):
            t = truth[cid]
            ln = {"id": cid, "delta_key": t["delta_key"], "labels": t["labels"], "tablet": cid, "cluster": cid,
                  "boxes": {"T": t["boxes_T"]}}
            for r in ("A", "B"):
                got = boxes[cid][r]
                ok = len(got) == 1 and len(got[0]) == t["n"]
                ln[f"joined_{r}"] = ok
                if ok:
                    ln["boxes"][r] = got[0]
                ln[f"n_lines_{r}"] = len(got)
                ln[f"n_boxes_{r}"] = sum(len(x) for x in got)
            L.append(ln)
        S.write_json(S.ALIGNED / f"synth_{args.round}.json", {"round": args.round, "utc": S.utc(), "lines": L})
    print(f"measured {len(boxes)} crops; synthetic {len(syn)}; wrote raw/aligned/boxes_{args.round}.json")


# ----------------------------------------------------------------------------------------------------------------
# g2: G2 / G2b / G3 inputs (label-free)
# ----------------------------------------------------------------------------------------------------------------


def flat(lines):
    return [(li, k, b) for li, ln in enumerate(lines) for k, b in enumerate(ln)]


def gap_in_line(line_boxes, i0, i1):
    """Gap from box i0 to box i1, both rotated by the line frame of `line_boxes` (raw px, and over the line's H)."""
    rb, th = S.line_frame(line_boxes)
    H = float(np.median(rb[:, 3] - rb[:, 1]))
    g = float(rb[i1, 0] - rb[i0, 2])
    return g, (g / H if H > 0 else None)


def agent_gap(lines, a0, a1):
    """PREREG-AMBIGUITY: the agent gap of a gold pair is measured in the line frame of the agent line holding the
    match of the pair's first box; if the second box's match sits in another agent line, it is rotated by that
    same frame (its own line's frame is not used)."""
    l0, k0 = a0
    l1, k1 = a1
    if l0 == l1:
        return gap_in_line(lines[l0], k0, k1)
    rb0, th = S.line_frame(lines[l0])
    H = float(np.median(rb0[:, 3] - rb0[:, 1]))
    two = S.rotate_boxes([lines[l0][k0], lines[l1][k1]], th)
    g = float(two[1, 0] - two[0, 2])
    return g, (g / H if H > 0 else None)


def cmd_g2(args):
    info = seal()
    B = load_boxes(args.round)
    dr = S.read_json(DRAWS)
    man = S.read_json(CROPMAN)
    crops = B["crops"]
    out = {"round": args.round, "utc": S.utc(), "seal": info, "key_sha256": B["key_sha256"]}
    cal_crops = [c for c, d in crops.items() if "cal" in d["sets"]]
    if cal_crops:
        den = S.load_dencker()
        n_gold, matched, pairs, avail = 0, {"A": 0, "B": 0}, [], 0
        for cid in sorted(cal_crops):
            d = crops[cid]
            t, view = d["tablet"], VIEW[d["face"]]
            ox, oy = man[cid]["box"][0], man[cid]["box"][1]
            fb = den["boxes"].get((t, view), [])
            gold = [[b["bbox"][0] - ox, b["bbox"][1] - oy, b["bbox"][2] - ox, b["bbox"][3] - oy] for b in fb]
            gp, _ = S.gold_pairs_face(fb, den["lines"].get((t, view), {}), den["translit"].get((t, view), {}))
            avail += len(gp)
            n_gold += len(gold)
            maps = {}
            for r in ("A", "B"):
                fl = flat(d[r])
                hp = S.hungarian_pairs(gold, [b for _, _, b in fl], IOU_G2)
                matched[r] += len(hp)
                maps[r] = {gi: (fl[ai][0], fl[ai][1]) for gi, ai, _ in hp}
            for p in gp:
                rec = {"gold_g": p["gold_g"], "gold_G": p["gold_G"], "crop": cid}
                for r in ("A", "B"):
                    m0, m1 = maps[r].get(p["b0"]), maps[r].get(p["b1"])
                    if m0 is not None and m1 is not None:
                        rec[f"{r}_g"], rec[f"{r}_G"] = agent_gap(d[r], m0, m1)
                    else:
                        rec[f"{r}_g"], rec[f"{r}_G"] = None, None
                pairs.append(rec)
        S.heartbeat("g2", 1, 3)
        out["G2"] = {"n_gold_boxes": n_gold, "matched": matched, "pairs": pairs, "gold_pairs_available": avail,
                     "n_faces": len(cal_crops), "draws_gold_pairs_available": dr["cal"]["gold_pairs_available"]}
    # G2b: first 10 S2 tablets of the draw, both faces, agent vs agent.
    # PREREG-AMBIGUITY: A and B boxes are paired one-to-one by IoU >= 0.5 (Hungarian, the G1 threshold); a gap pair
    # is two consecutive boxes of one A line whose partners are consecutive boxes of one B line; every such gap
    # (last gap included) enters, each rater's gap in its own line frame.
    first10 = set(dr["S2"]["first10"])
    s2c = [c for c, d in crops.items() if "S2" in d["sets"] and d["tablet"] in first10]
    if s2c:
        pr, nl, nf = [], set(), 0
        for cid in sorted(s2c):
            d = crops[cid]
            fa, fb_ = flat(d["A"]), flat(d["B"])
            if not fa or not fb_:
                continue
            nf += 1
            hp = S.hungarian_pairs([b for _, _, b in fa], [b for _, _, b in fb_], IOU_G1)
            amap = {(fa[i][0], fa[i][1]): (fb_[j][0], fb_[j][1]) for i, j, _ in hp}
            for li, ln in enumerate(d["A"]):
                for k in range(len(ln) - 1):
                    m0, m1 = amap.get((li, k)), amap.get((li, k + 1))
                    if m0 is None or m1 is None or m0[0] != m1[0] or m1[1] != m0[1] + 1:
                        continue
                    ga, Ga = gap_in_line(ln, k, k + 1)
                    gb, Gb = gap_in_line(d["B"][m0[0]], m0[1], m1[1])
                    pr.append({"A_g": ga, "A_G": Ga, "B_g": gb, "B_G": Gb})
                    nl.add((cid, li))
        out["G2b"] = {"pairs": pr, "n_lines": len(nl), "n_faces": nf, "tablets": sorted(first10)}
    S.heartbeat("g2", 2, 3)
    # G3: box heights (axis-aligned, crop frame) and at the image size given to the rater
    g3 = {}
    for script, pick in (("S1", lambda d: "S1" in d["sets"] or "cal" in d["sets"]),
                         ("S2", lambda d: "S2" in d["sets"] and d["tablet"] in first10)):
        hA, hB, hN = [], [], []
        for cid, d in crops.items():
            if not pick(d):
                continue
            sc = d["scale"]
            for ln in d["A"]:
                for b in ln:
                    hN.append(b[3] - b[1])
                    hA.append((b[3] - b[1]) * sc)
            for ln in d["B"]:
                for b in ln:
                    hB.append((b[3] - b[1]) * sc)
        if hA or hB:
            g3[script] = {"A_given": hA, "B_given": hB, "A_native": hN}
    out["G3"] = g3
    S.write_json(S.ALIGNED / f"gates_{args.round}.json", out)
    S.heartbeat("g2", 3, 3)
    print(f"wrote raw/aligned/gates_{args.round}.json; next: score.py gates --round {args.round}")


# ----------------------------------------------------------------------------------------------------------------
# G1 join
# ----------------------------------------------------------------------------------------------------------------


def in_order_iou_ok(a, b):
    if len(a) != len(b):
        return False
    M = S.iou_matrix(a, b)
    return bool(np.all(np.diag(M) >= IOU_G1))


def join_face(d, tlines, info_of):
    """G1 on one face. tlines: ranked transliteration lines (all numbered lines, damaged included, $-lines and
    rulings never ranked). Returns (joined [(rank, line_info, A, B)], n_clean, face_dropped).
    PREREG-AMBIGUITY: "clean lines" for the drop rate are the clean transliteration lines with >= 3 signs (the
    scored lines) on measured faces; a dropped face drops all of its clean lines. Faces without a crop (no Dencker
    segment for that view) were not measured and are not counted."""
    infos = [info_of(x) for x in tlines]
    clean = [k for k, x in enumerate(infos) if x["clean"] and x["n"] >= 3]
    A, Bl = d["A"], d["B"]
    if len(A) != len(tlines) or len(Bl) != len(tlines):
        return [], len(clean), True
    out = []
    for k in clean:
        n = infos[k]["n"]
        if len(A[k]) == n and len(Bl[k]) == n and in_order_iou_ok(A[k], Bl[k]):
            out.append((k, infos[k], A[k], Bl[k]))
    return out, len(clean), False


def g1_script(crops, tablets, faces_of, info_of, cluster_of, label_fn=None):
    lines, n_clean, n_join, dropped, faces = [], 0, 0, [], 0
    for t in tablets:
        for face in ("obverse", "reverse"):
            cid = next((c for c, d in sorted(crops.items()) if d["tablet"] == t and d["face"] == face), None)
            if cid is None:
                continue
            tl = faces_of(t, face)
            if tl is None:
                continue
            faces += 1
            got, nc, drop = join_face(crops[cid], tl, info_of)
            n_clean += nc
            if drop:
                dropped.append(f"{t}.{face}")
            for k, inf, a, b in got:
                labels = label_fn(inf) if label_fn else inf["labels"]
                lines.append({"tablet": t, "face": face, "rank": k, "cluster": cluster_of(t), "n": inf["n"],
                              "labels": labels, "cls": inf["cls"], "signs": inf["signs"],
                              "boxes": {"A": a, "B": b}})
                n_join += 1
    drop_rate = (1.0 - n_join / n_clean) if n_clean else None
    g1 = {"clean_lines": n_clean, "joined": n_join, "drop_rate": drop_rate, "faces": faces,
          "faces_dropped": len(dropped), "faces_dropped_ids": dropped,
          "fail_F1": bool(drop_rate is None or drop_rate > 0.40)}
    return lines, g1


def cmd_pseudo(args):
    info = seal()
    B = load_boxes(args.round)
    dr = S.read_json(DRAWS)
    oracc = S.load_oracc()
    crops = {c: d for c, d in B["crops"].items() if "s54" in d["sets"]}
    rng = np.random.default_rng(SEED_PSEUDO)

    def faces_of(t, face):
        f = oracc["faces"].get(t)
        return None if f is None else f[face]

    def pseudo_labels(inf):
        # PREREG-AMBIGUITY (§5.4): the line's own ORACC word-length sequence is permuted (rng seed 20261127, lines in
        # tablet-hash / face / rank order) and pseudo-boundaries are placed after each word of the permuted sequence.
        wl = list(inf["wl"])
        wl = [w for w in wl if w > 0]
        perm = [wl[i] for i in rng.permutation(len(wl))]
        lab = []
        for wi, m in enumerate(perm):
            lab += [False] * (m - 1) + ([True] if wi < len(perm) - 1 else [])
        return lab

    lines, g1 = g1_script(crops, dr["s54"]["tablets"], faces_of, S.oracc_line_info, lambda t: t, pseudo_labels)
    for ln in lines:
        ln.pop("signs", None)
        ln["cls"] = None
    S.write_json(S.ALIGNED / f"pseudo_{args.round}.json",
                 {"round": args.round, "utc": S.utc(), "seal": info, "lines": lines, "G1": g1,
                  "n_tablets": len({ln["tablet"] for ln in lines}), "tablets_source": dr["s54"]["source"]})
    print(f"§5.4 lines joined: {len(lines)} (G1 drop rate {g1['drop_rate']}); next: score.py pseudo --round {args.round}")


def gates_ok(rnd, need):
    p = S.OUT / f"gates_{rnd}.json"
    if not p.exists():
        raise SystemExit(f"out/gates_{rnd}.json missing: run align.py g2 and score.py gates first")
    g = S.read_json(p)
    bad = []
    if "G2" in need and not (g.get("G2") or {}).get("pass"):
        bad.append("G2")
    if "G2b" in need and not (g.get("G2b") or {}).get("pass"):
        bad.append("G2b")
    if "G3" in need and not ((g.get("G3") or {}).get("S2") or {}).get("pass"):
        bad.append("G3(S2)")
    return bad


def cmd_join(args):
    info = seal()
    B = load_boxes(args.round)
    dr = S.read_json(DRAWS)
    g2r = args.g2_round or args.round
    crops = B["crops"]
    has_s1 = any("S1" in d["sets"] for d in crops.values())
    has_s2 = any("S2" in d["sets"] for d in crops.values())
    # order (§5): the planted checks run before any real gap is joined to a label
    if not (S.OUT / "synth_check.json").exists():
        raise SystemExit("out/synth_check.json missing: run synth.py check (§5.2) before joining labels")
    if not (S.OUT / f"pseudo_{g2r}.json").exists():
        raise SystemExit(f"out/pseudo_{g2r}.json missing: run align.py pseudo and score.py pseudo (§5.4) first")
    bad = gates_ok(g2r, ["G2"])
    if has_s2:
        bad += gates_ok(args.round, ["G2b", "G3"])
    if bad:
        raise SystemExit(f"measurement gates not passed ({', '.join(bad)}): no label join (K0 is INCONCLUSIVE "
                         "or a fallback round is due)")
    res = {"round": args.round, "utc": S.utc(), "seal": info, "G1": {"S1": None, "S2": None},
           "scripts": {"S1": None, "S2": None}}
    if has_s1:
        oracc = S.load_oracc()

        def faces_of(t, face):
            f = oracc["faces"].get(t)
            return None if f is None else f[face]

        L, g1 = g1_script({c: d for c, d in crops.items() if "S1" in d["sets"]}, dr["S1"]["tablets"], faces_of,
                          S.oracc_line_info, lambda t: t)
        res["G1"]["S1"], res["scripts"]["S1"] = g1, {"lines": L}
    S.heartbeat("join", 1, 2)
    if has_s2:
        want = S.yale_want()
        _, faces_atf = S.load_atf(set(dr["S2"]["tablets"]) & set(want))
        clusters = dr["S2"]["clusters"]

        def faces_of2(p, face):
            f = faces_atf.get(p)
            return None if f is None else f[face]

        L, g1 = g1_script({c: d for c, d in crops.items() if "S2" in d["sets"]}, dr["S2"]["tablets"], faces_of2,
                          lambda x: x, lambda p: clusters[p])
        res["G1"]["S2"], res["scripts"]["S2"] = g1, {"lines": L}
    S.heartbeat("join", 2, 2)
    S.write_json(S.ALIGNED / f"joined_{args.round}.json", res)
    S.write_json(S.OUT / f"g1_{args.round}.json", {"round": args.round, "utc": S.utc(), "seal": info,
                                                   "G1": {k: (None if v is None else {kk: vv for kk, vv in v.items()})
                                                          for k, v in res["G1"].items()}})
    print(json.dumps({k: (None if v is None else {"drop_rate": v["drop_rate"], "fail_F1": v["fail_F1"],
                                                  "joined": v["joined"]}) for k, v in res["G1"].items()}, indent=1))
    print(f"next: score.py k0 --round {args.round}")


# ----------------------------------------------------------------------------------------------------------------
# record-only Dencker S1 lines (D5)
# ----------------------------------------------------------------------------------------------------------------


def cmd_dencker(args):
    """PREREG-AMBIGUITY (record-only S1 Dencker AUC): tablets = the Dencker line-annotated tablets matched to ORACC.
    Each Dencker line (boxes assigned and ordered as in G2 gold) is LCS-matched to a Dencker transliteration line;
    that transliteration line's rank (sorted line_idx of the face) is taken as the ORACC rank, and is used only if
    its sign count equals the ORACC line's sign count and the ORACC line is clean with >= 3 signs. Only gold pairs
    (consecutive boxes matched to consecutive signs j, j+1) enter, the last gap (j = n - 2) excluded; p = j/(n-1),
    with n the ORACC sign count; widths, fill, dy and size ratio come from the Dencker line frame. Calibration
    tablets are included (this AUC is description only and never decisive)."""
    info = seal()
    load_boxes(args.round)  # agent measurement of this round is frozen (hashed) before any Dencker label join
    if not (S.OUT / f"gates_{args.round}.json").exists():
        raise SystemExit("run the gates for this round first")
    den = S.load_dencker()
    oracc = S.load_oracc()
    out = []
    for t in den["line_tablets"]:
        p = S.sealed_to_p(t, oracc["mus2p"])
        if p is None or p not in oracc["faces"]:
            continue
        for face, view in VIEW.items():
            fb = den["boxes"].get((t, view), [])
            tl = den["translit"].get((t, view), {})
            pairs, groups = S.gold_pairs_face(fb, den["lines"].get((t, view), {}), tl)
            if not pairs:
                continue
            ranks = {li: r for r, li in enumerate(sorted(tl))}
            olines = oracc["faces"][p][face]
            by_line = {}
            for pr in pairs:
                by_line.setdefault((pr["line"], pr["tl_line"]), []).append(pr)
            for (li, tli), prs in sorted(by_line.items()):
                r = ranks[tli]
                if r >= len(olines):
                    continue
                inf = S.oracc_line_info(olines[r])
                if not inf["clean"] or inf["n"] < 3 or inf["n"] != len(tl[tli]):
                    continue
                order = groups[li]
                rb, _ = S.line_frame([fb[bi]["bbox"] for bi in order])
                w = rb[:, 2] - rb[:, 0]
                h = rb[:, 3] - rb[:, 1]
                H = float(np.median(h))
                Lx = float(rb[:, 2].max() - rb[:, 0].min())
                cy = (rb[:, 1] + rb[:, 3]) / 2.0
                n = inf["n"]
                pre = {"G": [], "p": [], "Wl": [], "Wr": [], "gidx": [], "dy": [], "lar": [], "n": n,
                       "fill": float(w.sum() / Lx) if Lx > 0 else float("nan")}
                labs = []
                for pr in prs:
                    j, k = pr["j"], pr["k"]
                    if j >= n - 2 or pr["gold_G"] is None:
                        continue
                    pre["G"].append(pr["gold_G"])
                    pre["p"].append(j / (n - 1))
                    pre["Wl"].append(float(w[k] / H))
                    pre["Wr"].append(float(w[k + 1] / H))
                    pre["gidx"].append(j)
                    pre["dy"].append(float((cy[k + 1] - cy[k]) / H))
                    pre["lar"].append(float(np.log((w[k + 1] * h[k + 1]) / (w[k] * h[k]))))
                    labs.append(bool(inf["labels"][j]))
                if pre["G"]:
                    out.append({"tablet": t, "face": face, "rank": r, "cluster": t, "labels": labs, "cls": None,
                                "pre": pre})
    S.write_json(S.ALIGNED / f"dencker_{args.round}.json", {"round": args.round, "utc": S.utc(), "seal": info,
                                                            "lines": out, "record_only": True})
    print(f"record-only Dencker lines: {len(out)} (raw/aligned only; scored as description by score.py k0)")


def main():
    ap = argparse.ArgumentParser(description="layout_word_division: back-mapping, gates input, G1 join")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("validate")
    s.add_argument("--round", required=True)
    s.add_argument("--file", action="append", required=True)
    s = sub.add_parser("measure")
    s.add_argument("--round", required=True)
    s.add_argument("--a", required=True, help="rater A output JSON (its sha256 must be in HASHES.txt)")
    s.add_argument("--b", required=True, help="rater B output JSON (its sha256 must be in HASHES.txt)")
    for nm in ("g2", "pseudo", "dencker"):
        s = sub.add_parser(nm)
        s.add_argument("--round", required=True)
    s = sub.add_parser("join")
    s.add_argument("--round", required=True)
    s.add_argument("--g2-round", default=None, help="round whose G2 and §5.4 results apply (F4 S2-only rounds)")
    args = ap.parse_args()
    {"validate": cmd_validate, "measure": cmd_measure, "g2": cmd_g2, "pseudo": cmd_pseudo, "join": cmd_join,
     "dencker": cmd_dencker}[args.cmd](args)


if __name__ == "__main__":
    main()
