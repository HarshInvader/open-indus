"""Photos, draws, crops and blind rater bundles for layout_word_division.

Prereg: docs/prereg/layout_word_division.md (SEALED v2, tag `layout_word_division`); this file is hashed under tag
`layout_word_division_code`. Every subcommand checks the prereg, this file and score.py against HASHES.txt (exit 2).
Shared parsing and Dencker readers come from score.py in this folder, imported after an explicit
`sys.path.insert(0, <this folder>)` (python -I drops the script folder). Nothing else is imported from here.

Subcommands (repo root; `nice -n 10 .venv/bin/python -I experiments/layout_word_division/make_crops.py ...`):
  fetch --stage DIR [--reserve 15] [--s2-full]
        S1: CDLI photos of every line-annotated Dencker tablet that is a P-number (calibration candidates) and of the
        first 60 + reserve S1 tablets in hash order. --s2-full (F4): Yale IIIF full-size images of the 60 drawn S2
        tablets. One request per second, User-Agent "open-research-site/1.0", resumable. Downloads go first to
        DIR, which must be outside the repo and new/empty (a marker file allows resuming); verified copies go to
        raw/photos/. Writes `HEARTBEAT <utc> stage=fetch done=k/n` to run.log.
  crops [--unregistered ID,ID] [--override FILE] [--s2-full]
        Calibration set (§4.4), §5.4 set, S1 draw (§4.5), S2 draw (§4.5), S2 clusters, label-free yields;
        crops every measured face (obverse, reverse) to raw/crops/. Writes raw/draws.json and
        raw/crops_manifest.json. --s2-full (F4) re-cuts the same S2 faces from the full-size images (same boxes
        scaled), nothing else.
  r2sheet
        Contact sheets of every crop (and Dencker gold-box overlays on the calibration crops) to raw/r2/, for the
        R2 bad-crop check by the coordinator before raters start. Never put in a bundle.
  bundle --round R [--f2] [--sets cal,s54,S1,S2,synth] [--s2-full]
        One fresh bundle directory per rater (raw/bundles/<R>/A, raw/bundles/<R>/B) holding only the crops C1..Cn
        (rotated 180 deg; --f2 also upsamples 2x bicubic) and PROTOCOL.txt (§10 text, verbatim; F2 paragraph only
        with --f2). Writes the label key raw/keys/key_<R>.json and prints its sha256 line for HASHES.txt; the key
        must be hashed before the raters start (align.py refuses otherwise).

Fixed rules:
  * Draw keys: calibration sha256("layout_word_division:cal:<id>"), S1 sha256("layout_word_division:S1:<id>"),
    S2 sha256("layout_word_division:S2:<P-number>"), crop labels sha256("layout_word_division:crop:<rater>:<id>"),
    all hex-ascending. <id> for cal and S1 is the Dencker tablet_CDLI string, exactly as in count_na2_univ.py.
  * S1 face crop: the Dencker tablet_segments bbox of that view (Obv / Rev; first row in file-name order) cut from
    the CDLI photo, so the crop frame equals Dencker's photo frame shifted by the bbox origin.
  * S2 face crop (Yale six-view sheet), one fixed rule: grey-scale copy downscaled to 400 px wide; background =
    median of a 4-px border frame; foreground = |pixel - background| > max(20, 4 x normalised MAD of the border);
    binary opening (1 iteration), closing (3 iterations), hole filling; connected components; components below 1%
    of the image area or with a bounding-box aspect ratio above 3 are dropped; candidates = components with area >=
    25% of the largest; the two largest candidates are the two faces; the upper one is the obverse, unless the two
    centres differ vertically by less than half the smaller height (side by side), then the left one is the obverse;
    each face box = component bounding box padded by 2% of its width/height, mapped back to full image pixels.
    A sheet with fewer than two candidates fails the rule (R2) and the next tablet in hash order is taken.
"""
import argparse
import csv
import json
import math
import re
import shutil
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))  # explicit: import score.py from this folder (python -I removes it from sys.path)
import score as S  # noqa: E402

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

ME = Path(__file__).resolve()
SCORE = HERE / "score.py"
PHOTOS = S.RAW / "photos"
CDLI_DIR = PHOTOS / "cdli"
YALE_FULL = PHOTOS / "yale_full"
MANIFEST = PHOTOS / "manifest.jsonl"
FAILS = PHOTOS / "fetch_failures.jsonl"
CROPS = S.RAW / "crops"
BUNDLES = S.RAW / "bundles"
R2DIR = S.RAW / "r2"
SYN = S.RAW / "synth"
DRAWS = S.RAW / "draws.json"
CROPMAN = S.RAW / "crops_manifest.json"
KEYS = S.KEYS
UA = "open-research-site/1.0"
CDLI_BASE = "https://cdli.mpiwg-berlin.mpg.de/dl/photo/"
YALE_MANIFEST = "https://manifests.collections.yale.edu/ypm/nat/"
N_CAL, N_S1, N_S2, GOLD_MIN = 10, 60, 60, 200
VIEWS = (("Obv", "obverse", "obv"), ("Rev", "reverse", "rev"))
STAGE_MARK = ".layout_word_division_stage"


def calkey(t):
    return S.hkey(f"layout_word_division:cal:{t}")


def s1key(t):
    return S.hkey(f"layout_word_division:S1:{t}")


def s2key(p):
    return S.hkey(f"layout_word_division:S2:{p}")


def cropkey(rater, cid):
    return S.hkey(f"layout_word_division:crop:{rater}:{cid}")


# ----------------------------------------------------------------------------------------------------------------
# fetch
# ----------------------------------------------------------------------------------------------------------------
_last = [0.0]


def http_get(url, tries=3):
    err = None
    for k in range(tries):
        wait = 1.0 - (time.time() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.time()
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=90) as r:
                return r.read(), None
        except urllib.error.HTTPError as e:
            err = f"HTTP {e.code}"
            if e.code in (403, 404, 410):
                return None, err
        except Exception as e:  # noqa: BLE001
            err = f"{type(e).__name__}: {e}"
        time.sleep(5 * (k + 1))
    return None, err


def read_manifest():
    got = {}
    if MANIFEST.exists():
        for line in MANIFEST.read_text(encoding="utf-8").splitlines():
            if line.strip():
                r = json.loads(line)
                if (S.ROOT / r["file"]).exists():
                    got[(r["kind"], r["id"])] = r
    return got


def s1_fetch_ids(reserve):
    oracc = S.load_oracc()
    den = S.load_dencker()
    cal = [t for t in sorted(den["line_tablets"], key=calkey) if S.is_p_number(t)]
    per = S.s1_eligible(oracc)
    order = [t for t in sorted(per, key=s1key) if S.is_p_number(t)]
    ids = list(dict.fromkeys(cal + order[:N_S1 + reserve]))
    return ids


def cmd_fetch(args):
    S.seal_check([ME, SCORE])
    stage = Path(args.stage).expanduser().resolve()
    if stage == S.ROOT or S.ROOT in stage.parents:
        raise SystemExit("--stage must be outside the repository (prereg §3: downloads go to a new empty directory "
                         "outside the repo first)")
    if stage.exists() and any(stage.iterdir()) and not (stage / STAGE_MARK).exists():
        raise SystemExit("--stage exists and is not empty, and is not a previous fetch stage of this study")
    stage.mkdir(parents=True, exist_ok=True)
    (stage / STAGE_MARK).write_text("layout_word_division fetch stage\n", encoding="utf-8")
    CDLI_DIR.mkdir(parents=True, exist_ok=True)
    YALE_FULL.mkdir(parents=True, exist_ok=True)
    have = read_manifest()
    jobs = []
    if args.s2_full:
        dr = S.read_json(DRAWS)
        want = S.yale_want()
        for p in dr["S2"]["tablets"]:
            jobs.append(("yale_full", p, want[p]))
    else:
        for t in s1_fetch_ids(args.reserve):
            jobs.append(("cdli", t, None))
    n = len(jobs)
    S.log(f"fetch start kind={'yale_full' if args.s2_full else 'cdli'} n={n}")
    for k, (kind, pid, nat) in enumerate(jobs):
        S.heartbeat("fetch", k, n)
        if (kind, pid) in have:
            continue
        if kind == "cdli":
            url = CDLI_BASE + f"{pid}.jpg"
            data, err = http_get(url)
            dest = CDLI_DIR / f"{pid}.jpg"
        else:
            man, err = http_get(YALE_MANIFEST + str(nat))
            data, url, dest = None, None, YALE_FULL / f"{pid}.jpg"
            if man is not None:
                m = json.loads(man)
                if "publicdomain/zero" not in str(m.get("rights", "")):
                    err = f"not CC0: {m.get('rights')}"
                else:
                    svc = m["items"][0]["items"][0]["items"][0]["body"]["service"][0]
                    sid = svc.get("@id") or svc.get("id")
                    for size in ("max", "full"):
                        url = f"{sid}/full/{size}/0/default.jpg"
                        data, err = http_get(url)
                        if data:
                            break
        if not data or data[:2] != b"\xff\xd8":
            with open(FAILS, "a", encoding="utf-8") as f:
                f.write(json.dumps({"kind": kind, "id": pid, "url": url, "err": err or "not a JPEG", "utc": S.utc()}) + "\n")
            continue
        tmp = stage / f"{kind}_{pid}.jpg"
        tmp.write_bytes(data)
        shutil.copyfile(tmp, dest)
        with Image.open(dest) as im:
            w, h = im.size
        rec = {"kind": kind, "id": pid, "nat": nat, "url": url, "file": S.rel_to_root(dest),
               "sha256": S.sha256_file(dest), "bytes": len(data), "w": w, "h": h, "utc": S.utc()}
        with open(MANIFEST, "a", encoding="utf-8") as f:
            f.write(json.dumps(rec) + "\n")
    S.heartbeat("fetch", n, n)
    S.log("fetch done")
    print("fetch done", n, "jobs; failures (if any) in", S.rel_to_root(FAILS) if FAILS.exists() else "none")


# ----------------------------------------------------------------------------------------------------------------
# S2 crop rule
# ----------------------------------------------------------------------------------------------------------------


def s2_face_boxes(path):
    """The fixed S2 rule of the module docstring. PREREG-AMBIGUITY: §4.5 leaves the rule to make_crops.py; this
    foreground-component rule is the one fixed here, before any sheet is cropped. Returns ({'obverse': box, 'reverse': box}, info) or (None, info)."""
    from scipy import ndimage
    with Image.open(path) as im0:
        im = im0.convert("L")
        W, H = im.size
        s = 400.0 / W
        small = im.resize((400, max(1, int(round(H * s)))), Image.BILINEAR)
    a = np.asarray(small, dtype=float)
    border = np.concatenate([a[:4].ravel(), a[-4:].ravel(), a[:, :4].ravel(), a[:, -4:].ravel()])
    bg = float(np.median(border))
    mad = 1.4826 * float(np.median(np.abs(border - bg)))
    thr = max(20.0, 4.0 * mad)
    fg = np.abs(a - bg) > thr
    fg = ndimage.binary_opening(fg, iterations=1)
    fg = ndimage.binary_closing(fg, iterations=3)
    fg = ndimage.binary_fill_holes(fg)
    lab, k = ndimage.label(fg)
    comps = []
    total = a.size
    for i, sl in enumerate(ndimage.find_objects(lab), start=1):
        if sl is None:
            continue
        area = int((lab[sl] == i).sum())
        hh, ww = sl[0].stop - sl[0].start, sl[1].stop - sl[1].start
        asp = max(hh, ww) / max(1, min(hh, ww))
        if area < 0.01 * total or asp > 3.0:
            continue
        comps.append({"area": area, "y0": sl[0].start, "y1": sl[0].stop, "x0": sl[1].start, "x1": sl[1].stop})
    comps.sort(key=lambda c: -c["area"])
    info = {"n_components": len(comps), "threshold": thr, "bg": bg}
    if not comps:
        return None, info
    cand = [c for c in comps if c["area"] >= 0.25 * comps[0]["area"]]
    info["n_candidates"] = len(cand)
    if len(cand) < 2:
        return None, info
    c1, c2 = cand[0], cand[1]
    cy1, cy2 = (c1["y0"] + c1["y1"]) / 2, (c2["y0"] + c2["y1"]) / 2
    h1, h2 = c1["y1"] - c1["y0"], c2["y1"] - c2["y0"]
    if abs(cy1 - cy2) >= 0.5 * min(h1, h2):
        obv, rev = (c1, c2) if cy1 < cy2 else (c2, c1)
        info["layout"] = "stacked"
    else:
        obv, rev = (c1, c2) if c1["x0"] < c2["x0"] else (c2, c1)
        info["layout"] = "side by side"

    def full(c):
        pw, ph = 0.02 * (c["x1"] - c["x0"]), 0.02 * (c["y1"] - c["y0"])
        x0 = max(0, int(math.floor((c["x0"] - pw) / s)))
        y0 = max(0, int(math.floor((c["y0"] - ph) / s)))
        x1 = min(W, int(math.ceil((c["x1"] + pw) / s)))
        y1 = min(H, int(math.ceil((c["y1"] + ph) / s)))
        return [x0, y0, x1, y1]

    return {"obverse": full(obv), "reverse": full(rev)}, info


# ----------------------------------------------------------------------------------------------------------------
# draws and crops
# ----------------------------------------------------------------------------------------------------------------


def load_catalogue(pids):
    csv.field_size_limit(10 ** 9)
    want = {p[1:].lstrip("0") or "0": p for p in pids}
    out = {}
    with open(S.CAT_PATH, encoding="utf8", errors="replace", newline="") as fh:
        for row in csv.DictReader(fh):
            k = (row.get("id_text") or "").lstrip("0")
            if k in want:
                out[want[k]] = {"provenience": row.get("provenience", ""), "date_of_origin": row.get("date_of_origin", "")}
    return out


def regnal_year(s):
    parts = (s or "").strip().split(".")
    if len(parts) >= 2 and parts[0] and parts[0] not in ("--", "00", "") and re.fullmatch(r"0*[1-9]\d*[a-z]?", parts[1]):
        return f"{parts[0]}.{parts[1]}"
    return None


def s2_cluster(p, cat, yrec):
    """Provenience x regnal year (§4.5). PREREG-AMBIGUITY: the CDLI catalogue fields `provenience` and
    `date_of_origin` (king.year) are used first; the year falls back to the Yale record's "Date = ..." attribute
    (king written as in the record, e.g. "$.39"); the slim Yale record has no provenience field, so provenience comes
    from CDLI only. A provenience that is empty or contains "uncertain", or a year that is missing, "--" or 00,
    counts as missing; a tablet missing either field is its own cluster."""
    c = cat.get(p) or {}
    prov = (c.get("provenience") or "").strip()
    if not prov or "uncertain" in prov.lower():
        prov = None
    yr = regnal_year(c.get("date_of_origin"))
    if yr is None:
        for t in (yrec.get(p) or {}).get("texts", []):
            m = re.search(r"Date = ([^,]+)", t)
            if m:
                yr = regnal_year(m.group(1))
                break
    return (f"{prov}|{yr}", True) if (prov and yr) else (f"tablet:{p}", False)


def face_yield(lines):
    """Label-free count over clean lines with >= 3 signs: lines, gaps excluding the last, boundaries among them."""
    L = G = B = 0
    for x in lines:
        if x["clean"] and x["n"] >= 3:
            L += 1
            G += x["n"] - 2
            B += sum(x["labels"][:-1])
    return L, G, B


def cmd_crops(args):
    info = S.seal_check([ME, SCORE])
    CROPS.mkdir(parents=True, exist_ok=True)
    photos = read_manifest()
    unreg = set(filter(None, (args.unregistered or "").split(",")))
    override, override_sha = {}, None
    if args.override:
        op = (S.ROOT / args.override).resolve()
        override = S.read_json(op)
        override_sha = S.sha256_file(op)
    bad_crop = {cid for cid, v in override.items() if v is None}
    bad_tab = {cid.split(".")[0] for cid in bad_crop}

    if args.s2_full:
        return crops_s2_full(info, photos)

    S.heartbeat("crops", 0, 5)
    oracc = S.load_oracc()
    den = S.load_dencker()

    def reg(t):
        """PREREG-AMBIGUITY (frame registration): a Dencker tablet is usable only if its id is a CDLI P-number (the
        Dencker boxes of other ids are in other photo frames), its CDLI photo was fetched, every Dencker segment bbox
        of it lies inside the photo, it has an Obv or Rev segment, and the R2 check did not flag it."""
        if t in unreg or t in bad_tab:
            return False, "R2 flag"
        if not S.is_p_number(t):
            return False, "Dencker id is not a CDLI P-number"
        ph = photos.get(("cdli", t))
        if ph is None:
            return False, "no CDLI photo"
        sg = [bb for v, _, _ in VIEWS for bb in den["segs"].get((t, v), [])]
        if not sg:
            return False, "no Obv/Rev segment"
        if any(bb[0] < -1 or bb[1] < -1 or bb[2] > ph["w"] + 1 or bb[3] > ph["h"] + 1 for bb in sg):
            return False, "segment outside photo"
        return True, ""

    def gold_count(t):
        return sum(len(S.gold_pairs_face(den["boxes"].get((t, v), []), den["lines"].get((t, v), {}),
                                         den["translit"].get((t, v), {}))[0]) for v, _, _ in VIEWS)

    # calibration set (§4.4 G2): first 10 by hash among Dencker tablets with line annotations; tablets are added in
    # hash order while the registered ones give fewer than 200 gold pairs. PREREG-AMBIGUITY: an unregistered
    # tablet still takes its calibration slot (and stays out of S1) but adds no gold pair and is not measured.
    cal_order = sorted(den["line_tablets"], key=calkey)
    cal, total, cal_info = [], 0, {}
    for t in cal_order:
        if len(cal) >= N_CAL and total >= GOLD_MIN:
            break
        ok, why = reg(t)
        g = gold_count(t) if ok else 0
        cal.append(t)
        total += g
        cal_info[t] = {"registered": ok, "why": why, "gold_pairs": g}
    cal_set = set(cal)
    # §5.4 set: calibration tablets with ORACC text; if fewer than 5, every remaining ORACC-matched
    # line-annotated tablet is added in hash order (registered ones only: they must be boxed in the same frame).
    s54 = [t for t in cal if cal_info[t]["registered"] and t in oracc["faces"]]
    s54_src = "calibration"
    if len(s54) < 5:
        s54_src = "calibration + remaining ORACC-matched line-annotated tablets (hash order)"
        for t in cal_order:
            if t in s54 or t not in oracc["faces"] or not reg(t)[0]:
                continue
            s54.append(t)
    S.heartbeat("crops", 1, 5)

    # S1 draw
    per = S.s1_eligible(oracc)
    s1, s1_skip = [], []
    for t in sorted(per, key=s1key):
        if len(s1) >= N_S1:
            break
        if t in cal_set:
            s1_skip.append([t, "calibration tablet"])
            continue
        ok, why = reg(t)
        if not ok or t not in oracc["faces"]:
            # PREREG-AMBIGUITY: §4.5 names only the calibration skip; a tablet that cannot be cut in the Dencker frame
            # (non-P id, no photo, segment outside photo, R2 flag) is skipped the same way, next in hash order.
            s1_skip.append([t, why or "no ORACC faces"])
            continue
        s1.append(t)
    S.heartbeat("crops", 2, 5)

    # S2 draw
    want = S.yale_want()
    sealed_atf, faces_atf = S.load_atf(set(want))
    pool = S.s2_pool(sealed_atf, want)
    s2, s2_skip, s2_boxes = [], [], {}
    for p in sorted(pool, key=s2key):
        if len(s2) >= N_S2:
            break
        if p in bad_tab:
            s2_skip.append([p, "R2 flag"])
            continue
        src = S.YALE_IMG / f"{want[p]}.jpg"
        fb, finfo = s2_face_boxes(src)
        if fb is None:
            s2_skip.append([p, f"S2 crop rule failed: {finfo}"])
            continue
        for face, cid_suf in (("obverse", "obv"), ("reverse", "rev")):
            cid = f"{p}.{cid_suf}"
            if cid in override and override[cid] is not None:
                fb[face] = [int(v) for v in override[cid]]
        s2.append(p)
        s2_boxes[p] = (src, fb, finfo)
    cat = load_catalogue(s2)
    yrec = S.yale_records_by_p()
    clusters, cl_ok = {}, {}
    for p in s2:
        clusters[p], cl_ok[p] = s2_cluster(p, cat, yrec)
    S.heartbeat("crops", 3, 5)

    # crops
    man = {}
    for setname, tabs in (("cal", [t for t in cal if cal_info[t]["registered"]]), ("s54", s54), ("S1", s1)):
        for t in tabs:
            ph = photos[("cdli", t)]
            src = S.ROOT / ph["file"]
            for v, face, suf in VIEWS:
                segs = den["segs"].get((t, v), [])
                if not segs:
                    continue
                cid = f"{t}.{suf}"
                if cid in man:
                    man[cid]["sets"] = sorted(set(man[cid]["sets"]) | {setname})
                    continue
                bb = segs[0]
                box = [int(math.floor(bb[0])), int(math.floor(bb[1])), int(math.ceil(bb[2])), int(math.ceil(bb[3]))]
                if cid in override and override[cid] is not None:
                    box = [int(x) for x in override[cid]]
                man[cid] = cut(src, box, cid, setname, t, face, ph["sha256"],
                               "Dencker segment bbox" + (" (R2 override)" if cid in override else ""),
                               variants=len({tuple(b) for b in segs}))
    for p in s2:
        src, fb, finfo = s2_boxes[p]
        for face, suf in (("obverse", "obv"), ("reverse", "rev")):
            cid = f"{p}.{suf}"
            man[cid] = cut(src, fb[face], cid, "S2", p, face, S.sha256_file(src),
                           "S2 sheet rule" + (" (R2 override)" if cid in override else ""), rule_info=finfo)
    S.heartbeat("crops", 4, 5)

    # label-free yields (§4.5 expected yield; S2 checked against M2/M3 before measurement)
    y1 = [0, 0, 0]
    for t in s1:
        for v, face, suf in VIEWS:
            if f"{t}.{suf}" in man:
                ln = [S.oracc_line_info(x) for x in oracc["faces"][t][face]]
                for i, z in enumerate(face_yield(ln)):
                    y1[i] += z
    y2 = [0, 0, 0]
    for p in s2:
        for face in ("obverse", "reverse"):
            for i, z in enumerate(face_yield(faces_atf[p][face])):
                y2[i] += z
    m23 = {"M2_gaps_ge_1500": y2[1] >= 1500, "M3_boundaries_ge_300": y2[2] >= 300,
           "M3_nonboundaries_ge_300": (y2[1] - y2[2]) >= 300}
    draws = {
        "utc": S.utc(), "seal": info, "override_sha256": override_sha, "unregistered_flagged": sorted(unreg),
        "cal": {"set": cal, "info": cal_info, "gold_pairs_available": total, "g2_feasible": total >= GOLD_MIN,
                "order_head": cal_order[:len(cal) + 5]},
        "s54": {"tablets": s54, "source": s54_src},
        "S1": {"tablets": s1, "skipped": s1_skip, "eligible": len(per),
               "yield_clean_faces": dict(zip(("lines", "gaps", "boundaries"), y1))},
        "S2": {"tablets": s2, "first10": s2[:10], "skipped": s2_skip, "pool": len(pool), "clusters": clusters,
               "cluster_fields_complete": cl_ok, "n_clusters": len(set(clusters.values())),
               "yield_faces": dict(zip(("lines", "gaps", "boundaries"), y2)), "M2_M3": m23},
    }
    S.write_json(DRAWS, draws)
    S.write_json(CROPMAN, man)
    S.heartbeat("crops", 5, 5)
    print(json.dumps({"cal": len(cal), "gold_pairs": total, "s54": len(s54), "S1": len(s1), "S2": len(s2),
                      "S1_yield": draws["S1"]["yield_clean_faces"], "S2_yield": draws["S2"]["yield_faces"],
                      "S2_M2_M3": m23, "crops": len(man)}, indent=1))
    if not all(m23.values()):
        print("WARNING: the S2 label-free yield misses M2/M3 (§4.5 says it is checked before measurement)")


def cut(src, box, cid, setname, tablet, face, src_sha, rule, variants=1, rule_info=None, suffix=""):
    with Image.open(src) as im:
        W, H = im.size
        x0, y0 = max(0, box[0]), max(0, box[1])
        x1, y1 = min(W, box[2]), min(H, box[3])
        c = im.crop((x0, y0, x1, y1))
        c = c.convert("RGB") if c.mode not in ("RGB", "L") else c
        dest = CROPS / f"{cid}{suffix}.png"
        c.save(dest, format="PNG")
    return {"crop_id": cid + suffix, "sets": [setname], "tablet": tablet, "face": face, "source": S.rel_to_root(src),
            "source_sha256": src_sha, "box": [x0, y0, x1, y1], "W": x1 - x0, "H": y1 - y0,
            "file": S.rel_to_root(dest), "sha256": S.sha256_file(dest), "rule": rule, "segment_variants": variants,
            "rule_info": rule_info}


def crops_s2_full(info, photos):
    """F4: the same 60 S2 faces, boxes scaled from the on-disk image to the full-size image. Nothing else changes."""
    dr = S.read_json(DRAWS)
    man = S.read_json(CROPMAN)
    add = {}
    for p in dr["S2"]["tablets"]:
        ph = photos.get(("yale_full", p))
        if ph is None:
            raise SystemExit(f"F4: no full-size image for {p}; run fetch --s2-full first")
        src = S.ROOT / ph["file"]
        for suf in ("obv", "rev"):
            m = man[f"{p}.{suf}"]
            with Image.open(S.ROOT / m["source"]) as im:
                w0, h0 = im.size
            sx, sy = ph["w"] / w0, ph["h"] / h0
            b = m["box"]
            box = [int(math.floor(b[0] * sx)), int(math.floor(b[1] * sy)), int(math.ceil(b[2] * sx)),
                   int(math.ceil(b[3] * sy))]
            e = cut(src, box, f"{p}.{suf}", "S2", p, m["face"], ph["sha256"], "S2 sheet rule, F4 full size",
                    suffix=".full")
            add[e["crop_id"]] = e
    man.update(add)
    S.write_json(CROPMAN, man)
    print("F4 crops", len(add))


# ----------------------------------------------------------------------------------------------------------------
# R2 contact sheets (coordinator only)
# ----------------------------------------------------------------------------------------------------------------


def cmd_r2sheet(args):
    S.seal_check([ME, SCORE])
    man = S.read_json(CROPMAN)
    den = S.load_dencker()
    R2DIR.mkdir(parents=True, exist_ok=True)
    ids = sorted(man)
    per = 16
    for k in range(0, len(ids), per):
        sheet = Image.new("RGB", (4 * 320, 4 * 340), "white")
        d = ImageDraw.Draw(sheet)
        for i, cid in enumerate(ids[k:k + per]):
            with Image.open(S.ROOT / man[cid]["file"]) as im:
                im = im.convert("RGB")
                im.thumbnail((300, 300))
                x, y = (i % 4) * 320 + 10, (i // 4) * 340 + 30
                sheet.paste(im, (x, y))
                d.text((x, y - 20), f"{cid} [{','.join(man[cid]['sets'])}]", fill="black")
        sheet.save(R2DIR / f"sheet_{k // per:03d}.png")
    for cid, m in man.items():
        if "cal" not in m["sets"] and "s54" not in m["sets"]:
            continue
        view = "Obv" if m["face"] == "obverse" else "Rev"
        with Image.open(S.ROOT / m["file"]) as im:
            im = im.convert("RGB")
            d = ImageDraw.Draw(im)
            ox, oy = m["box"][0], m["box"][1]
            for b in den["boxes"].get((m["tablet"], view), []):
                bb = b["bbox"]
                d.rectangle([bb[0] - ox, bb[1] - oy, bb[2] - ox, bb[3] - oy], outline=(255, 0, 0), width=2)
            im.save(R2DIR / f"cal_overlay_{cid}.png")
    print("R2 sheets written to", S.rel_to_root(R2DIR), "(coordinator check only; never in a bundle)")


# ----------------------------------------------------------------------------------------------------------------
# bundles
# ----------------------------------------------------------------------------------------------------------------


def protocol_text(f2):
    """§10 text, verbatim: the blockquote lines of the section with the markdown quote marker removed.
    PREREG-AMBIGUITY: without --f2 the F2 line (marker and paragraph, which share one line) and the blank line after
    it are left out; with --f2 the paragraph is kept and only its italic marker "(F2 paragraph, used only in the F2
    re-run:)" is removed, so the rater is not told it is a re-run."""
    lines = (S.ROOT / S.PREREG_REL).read_text(encoding="utf-8").splitlines()
    i = next(k for k, ln in enumerate(lines) if ln.startswith("## 10."))
    body = []
    for ln in lines[i + 1:]:
        if ln.startswith("## "):
            break
        if ln.startswith(">"):
            body.append(ln[2:] if ln.startswith("> ") else ln[1:])
    out, skip_blank = [], False
    marker = re.compile(r"^\*\(F2 paragraph[^)]*\)\*\s*")
    for ln in body:
        if marker.match(ln):
            if f2:
                out.append(marker.sub("", ln))
            else:
                skip_blank = True
            continue
        if skip_blank and ln.strip() == "":
            skip_blank = False
            continue
        skip_blank = False
        out.append(ln)
    while out and not out[0].strip():
        out.pop(0)
    while out and not out[-1].strip():
        out.pop()
    return "\n".join(out) + "\n"


def cmd_bundle(args):
    info = S.seal_check([ME, SCORE])
    man = S.read_json(CROPMAN)
    sets = [s for s in args.sets.split(",") if s]
    entries = {}
    for cid, m in man.items():
        is_full = cid.endswith(".full")
        if "S2" in m["sets"] and (is_full != bool(args.s2_full)):
            continue
        if set(m["sets"]) & set(sets):
            entries[cid] = {"file": m["file"], "W": m["W"], "H": m["H"], "sets": m["sets"]}
    if "synth" in sets:
        ms = S.read_json(SYN / "measurer_set.json")
        for e in ms["lines"]:
            entries[e["id"]] = {"file": e["file"], "W": e["W"], "H": e["H"], "sets": ["synth"]}
    rdir = BUNDLES / args.round
    if rdir.exists():
        raise SystemExit(f"{S.rel_to_root(rdir)} exists: every round gets fresh, empty bundle directories")
    kp = KEYS / f"key_{args.round}.json"
    if kp.exists():
        raise SystemExit(f"{S.rel_to_root(kp)} exists")
    scale = 2.0 if args.f2 else 1.0
    proto = protocol_text(args.f2)
    key = {"round": args.round, "utc": S.utc(), "seal": info, "f2": bool(args.f2), "s2_full": bool(args.s2_full),
           "sets": sets, "scale": scale, "rotation_deg": 180, "protocol_sha256": S.sha256_text(proto),
           "n_crops": len(entries), "raters": {}}
    for rater in ("A", "B"):
        d = rdir / rater
        d.mkdir(parents=True)
        # PREREG-AMBIGUITY: "renamed by sha256 of layout_word_division:crop:<rater>:<id>" is read as in
        # foreign_transcribe3: crops sorted by that hash and labelled C1..Cn (the §10 sheet names images C1...Cn);
        # <id> is the crop id (<tablet>.obv / <tablet>.rev, synth.dXXX.NNN, F4 crops with .full).
        order = sorted(entries, key=lambda c: cropkey(rater, c))
        key["raters"][rater] = {}
        for k, cid in enumerate(order, start=1):
            e = entries[cid]
            lab = f"C{k}"
            with Image.open(S.ROOT / e["file"]) as im:
                im = im.convert("RGB") if im.mode not in ("RGB", "L") else im.copy()
                im = im.transpose(Image.ROTATE_180)
                if args.f2:
                    im = im.resize((2 * e["W"], 2 * e["H"]), Image.BICUBIC)
                im.save(d / f"{lab}.png", format="PNG")
            key["raters"][rater][lab] = {"crop_id": cid, "sets": e["sets"], "W": e["W"], "H": e["H"], "scale": scale,
                                         "rotated": True, "sha256": S.sha256_file(d / f"{lab}.png")}
            if k % 20 == 0:
                S.heartbeat(f"bundle_{rater}", k, len(order))
        (d / "PROTOCOL.txt").write_text(proto, encoding="utf-8")
    S.write_json(kp, key)
    sha = S.sha256_file(kp)
    print("bundles:", S.rel_to_root(rdir / "A"), S.rel_to_root(rdir / "B"), f"({len(entries)} crops each)")
    print("Append to docs/prereg/HASHES.txt BEFORE any rater starts:")
    print(f"{sha}  {S.rel_to_root(kp)}  {S.utc()}  layout_word_division_key_{args.round}")


def main():
    ap = argparse.ArgumentParser(description="layout_word_division: photos, draws, crops, rater bundles")
    sub = ap.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("fetch")
    s.add_argument("--stage", required=True, help="new empty download directory outside the repository")
    s.add_argument("--reserve", type=int, default=15, help="extra S1 tablets in hash order beyond the 60")
    s.add_argument("--s2-full", action="store_true", help="F4: Yale full-size images of the 60 drawn S2 tablets")
    s = sub.add_parser("crops")
    s.add_argument("--unregistered", default="", help="comma list of Dencker ids the R2 check found misregistered")
    s.add_argument("--override", default=None, help="R2 fixes, JSON {crop_id: [x0,y0,x1,y1] | null}, repo-relative")
    s.add_argument("--s2-full", action="store_true", help="F4: re-cut the same S2 faces from full-size images")
    sub.add_parser("r2sheet")
    s = sub.add_parser("bundle")
    s.add_argument("--round", required=True)
    s.add_argument("--f2", action="store_true", help="F2 re-run: 2x bicubic upsampling and the F2 paragraph")
    s.add_argument("--sets", default="cal,s54,S1,S2,synth")
    s.add_argument("--s2-full", action="store_true", help="use the F4 full-size S2 crops")
    args = ap.parse_args()
    {"fetch": cmd_fetch, "crops": cmd_crops, "r2sheet": cmd_r2sheet, "bundle": cmd_bundle}[args.cmd](args)


if __name__ == "__main__":
    main()
