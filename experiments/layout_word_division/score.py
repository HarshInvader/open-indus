"""Scorer and shared library for layout_word_division.

Prereg: docs/prereg/layout_word_division.md (SEALED v2, HASHES.txt tag `layout_word_division`). This file and the
other study scripts are hashed under tag `layout_word_division_code` before the first run (prereg §12). Every
subcommand first checks the prereg and this file (and the calling script) against those HASHES.txt lines; exit 2 on
any mismatch.

Subcommands (run from anywhere; paths resolve from the repo root; always `nice -n 10 .venv/bin/python -I ...`):
  selftest                         unit checks on generated numbers only; reads no study data. K0 runs it first.
  gates  --round R                 G2 (S1 calibration vs Dencker gold), G2b (S2 agent-agent), G3 (median box
                                   height). Label-free. Reads raw/aligned/gates_<R>.json, writes out/gates_<R>.json.
  pseudo --round R                 §5.4: agent-A boxes of the calibration (+extra) tablets with shuffled
                                   pseudo-boundaries, under the spline model and the F3 model. out/pseudo_<R>.json.
  k0     --round R [--s2-round R2] §4.3 residual model, §6.1 within-line AUC, cluster bootstrap, §6.2 shuffle null,
                                   §6.4(d), G1, §5.3 attenuation, §6.4 verdict and the §8 frozen reading.
                                   Writes out/k0_<R>.json and out/k0_<R>.out (aggregates only).

Library use: synth.py and align.py import this file. `python -I` drops the script folder from sys.path, so they
insert their own folder (this folder) explicitly: `sys.path.insert(0, str(Path(__file__).resolve().parent))`.
Nothing else is imported from this folder.

Fixed numbers: Huber k = 1.345; normalised MAD scale re-estimated each IRLS step; tolerance 1e-8 on the largest
absolute coefficient change; at most 100 iterations. Natural cubic spline of p with knots 0, .25, .5, .75, 1
(4 df). Bootstrap: 2,000 percentile cluster resamples, seed 20261125. Shuffle null: 1,000 within-line label
permutations, seed 20261126, p = (1 + #null >= observed) / 1001.

Data rule: Dencker-derived per-gap values are only ever read from raw/ and never written outside raw/; the files
written to out/ hold aggregates (AUC, ICC, recall, counts) only.
"""
import argparse
import csv
import glob
import hashlib
import json
import math
import os
import re
import sys
import time
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
ROOT = Path(__file__).resolve().parents[2]
PREREG_REL = "docs/prereg/layout_word_division.md"
TAG = "layout_word_division"
CODE_TAG = "layout_word_division_code"
HASHES = ROOT / "docs/prereg/HASHES.txt"
RAW = HERE / "raw"
OUT = HERE / "out"
ALIGNED = RAW / "aligned"
KEYS = RAW / "keys"
RUNLOG = HERE / "run.log"
DS_DIR = RAW / "ds"
ORACC_DIR = RAW / "oracc"
ATF_PATH = ROOT / "experiments/short_labels/raw/cdli/cdliatf_unblocked.atf"
CAT_PATH = ROOT / "experiments/short_labels/raw/cdli/cdli_cat.csv"
YALE_REC = ROOT / "experiments/stamp_detector/raw/records_ur3.jsonl"
YALE_IMG = ROOT / "experiments/stamp_detector/raw/img"

SEED_BOOT = 20261125      # prereg §6.1
SEED_SHUF = 20261126      # PREREG-AMBIGUITY: §6.2 states no seed; the shuffle null uses 20261126 (bootstrap seed + 1).
N_BOOT = 2000
N_SHUF = 1000
HUBER_K = 1.345
IRLS_TOL = 1e-8
IRLS_MAXIT = 100
KNOTS = (0.0, 0.25, 0.50, 0.75, 1.0)

# ----------------------------------------------------------------------------------------------------------------
# Seals, logging
# ----------------------------------------------------------------------------------------------------------------


def utc():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def heartbeat(stage, k, n):
    with open(RUNLOG, "a", encoding="utf-8") as f:
        f.write(f"HEARTBEAT {utc()} stage={stage} done={k}/{n}\n")


def log(msg):
    with open(RUNLOG, "a", encoding="utf-8") as f:
        f.write(f"{utc()} {msg}\n")


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_text(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


def _hash_rows():
    rows = []
    if not HASHES.exists():
        return rows
    with open(HASHES, encoding="utf-8") as f:
        for line in f:
            p = line.split()
            if len(p) >= 2:
                rows.append(p)
    return rows


def sealed_sha(rel, tag):
    # PREREG-AMBIGUITY: if HASHES.txt holds several lines for one path and tag, the last one is the seal in force.
    got = None
    for p in _hash_rows():
        if len(p) >= 4 and p[1] == rel and p[-1] == tag:
            got = p[0]
    return got


def sha_in_hashes(sha):
    """True if `sha` is the first field of any HASHES.txt line (used for rater outputs and label keys)."""
    return any(p[0] == sha for p in _hash_rows())


def rel_to_root(path):
    return Path(path).resolve().relative_to(ROOT).as_posix()


def seal_check(code_files):
    """Abort (exit 2) unless the prereg and every file in `code_files` match their HASHES.txt lines."""
    bad = []
    want = sealed_sha(PREREG_REL, TAG)
    have = sha256_file(ROOT / PREREG_REL)
    if want is None:
        bad.append(f"no HASHES.txt line for {PREREG_REL} with tag {TAG}")
    elif want != have:
        bad.append(f"{PREREG_REL}: sha256 {have} is not the sealed {want}")
    for f in code_files:
        rel = rel_to_root(f)
        want = sealed_sha(rel, CODE_TAG)
        have = sha256_file(f)
        if want is None:
            bad.append(f"no HASHES.txt line for {rel} with tag {CODE_TAG}")
        elif want != have:
            bad.append(f"{rel}: sha256 {have} is not the sealed {want}")
    if bad:
        for b in bad:
            print("SEAL MISMATCH:", b, file=sys.stderr)
        sys.exit(2)
    return {"prereg_sha256": sha256_file(ROOT / PREREG_REL),
            "code_sha256": {rel_to_root(f): sha256_file(f) for f in code_files}}


def write_json(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, sort_keys=True, default=_json_default)
    os.replace(tmp, path)


def _json_default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if not np.isfinite(o) else float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, (np.bool_,)):
        return bool(o)
    raise TypeError(type(o))


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def hkey(s):
    return hashlib.sha256(s.encode("utf-8")).hexdigest()


# ----------------------------------------------------------------------------------------------------------------
# Sealed label-free counters, copied verbatim in logic from count_na2.py / count_na2_univ.py / count_ur3_v2.py
# (used ONLY to reproduce the sealed eligibility sets and draws: the 832 S1 tablets, the S2 >= 6-line pool).
# ----------------------------------------------------------------------------------------------------------------
BAD_KEYS = ("break", "flags", "queried", "uflag1", "uflag2", "uflag3", "uflag4", "collated")


def _sealed_leaves(g, acc):
    for x in g:
        if not isinstance(x, dict):
            continue
        if "seq" in x:
            _sealed_leaves(x["seq"], acc)
        elif "group" in x:
            _sealed_leaves(x["group"], acc)
        elif any(k in x for k in ("v", "s", "n", "x", "q")) or x.get("type") == "x":
            bad = any(k in x for k in BAD_KEYS) or "o" in x or "c" in x or "ho" in x or "hc" in x \
                or x.get("x") is not None or str(x.get("v", "")).startswith("x")
            cls = "num" if "n" in x else ("det" if "det" in x else ("logo" if x.get("role") == "logo" else "syl"))
            acc.append((bad, cls))
    return acc


def _sealed_walk(node, out):
    if isinstance(node, dict):
        if node.get("node") == "d" and node.get("type") == "line-start":
            out.append([])
        elif node.get("node") == "l":
            f = node.get("f", {})
            s = _sealed_leaves(f.get("gdl", []), []) if f else []
            if out and s:
                out[-1].append(s)
        elif node.get("node") == "d" and node.get("type") in ("nonx", "nonw") and out:
            out[-1].append([(True, "x")])
        for v in node.get("cdl", []) if isinstance(node.get("cdl"), list) else []:
            _sealed_walk(v, out)
    elif isinstance(node, list):
        for v in node:
            _sealed_walk(v, out)


# ----------------------------------------------------------------------------------------------------------------
# ORACC parsing for alignment (per face, ranked lines)
# ----------------------------------------------------------------------------------------------------------------


def _is_bad(x):
    return any(k in x for k in BAD_KEYS) or "o" in x or "c" in x or "ho" in x or "hc" in x \
        or x.get("x") is not None or str(x.get("v", "")).startswith("x")


def oracc_leaves(g, acc, det=False, bad=False):
    """Signs of one ORACC word, in order, as (bad, cls, name).

    PREREG-AMBIGUITY: the sealed counter (count_na2.leaves) recurses into "seq" before testing for a sign, so it
    drops numerals that carry a "seq" (e.g. "1(diš)", "28") and never sees the "det" key of a determinative group.
    For the G1 sign count and the §6.4(d) flags this walker treats any node with v/s/n/x/q as one sign (numerals
    included), and marks every sign under a "det" node as a determinative; "bad" flags are inherited from enclosing
    nodes. Class: num if "n"; det if under a det node; logo if role == "logo"; else syl. The sealed counter is still
    used, unchanged, for the eligibility sets and draws.
    """
    for x in g:
        if not isinstance(x, dict):
            continue
        b = bad or _is_bad(x)
        if any(k in x for k in ("v", "s", "n", "x", "q")) or x.get("type") == "x":
            if "n" in x:
                cls = "num"
            elif det or "det" in x:
                cls = "det"
            elif x.get("role") == "logo":
                cls = "logo"
            else:
                cls = "syl"
            name = x.get("v") or x.get("s") or x.get("form") or x.get("q") or ("x" if "x" in x else "?")
            acc.append((bool(b), cls, str(name)))
        elif "seq" in x or "group" in x:
            oracc_leaves(x.get("seq", x.get("group", [])), acc, det or ("det" in x), b)
    return acc


def oracc_faces_of(d):
    """{'obverse': [line, ...], 'reverse': [...]} with every transliterated line (ORACC line-start) in order.

    Each line: {"label", "words": [[(bad, cls, name), ...], ...], "taint": bool}. $-lines, rulings and other
    nonx/nonw nodes are not lines (they are not line-starts), so they never take a rank.
    PREREG-AMBIGUITY: as in the sealed counter, a nonx/nonw node marks the most recent line as unclean (even across a
    surface change). PREREG-AMBIGUITY: ORACC "cof" tails (an 'l' node with a 'cof-head' key) repeat the written form
    of their head; they are skipped so that one written word gives its signs once (the sealed counter counts them
    twice). Only surfaces with subtype obverse / reverse are kept; edges are not measured faces.
    """
    faces = {"obverse": [], "reverse": []}
    state = {"surf": None, "last": None}

    def walk(node):
        if isinstance(node, dict):
            nd, ty = node.get("node"), node.get("type")
            if nd == "d" and ty == "surface":
                state["surf"] = node.get("subtype")
            elif nd == "d" and ty == "line-start":
                ln = {"label": node.get("label"), "words": [], "taint": False}
                state["last"] = ln
                if state["surf"] in faces:
                    faces[state["surf"]].append(ln)
            elif nd == "l" and "cof-head" not in node:
                f = node.get("f", {})
                s = oracc_leaves(f.get("gdl", []), []) if f else []
                if state["last"] is not None and s:
                    state["last"]["words"].append(s)
            elif nd == "d" and ty in ("nonx", "nonw") and state["last"] is not None:
                state["last"]["taint"] = True
            for v in node.get("cdl", []) if isinstance(node.get("cdl"), list) else []:
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(d.get("cdl", []))
    return faces


def load_oracc():
    """Reads the ORACC SAAo zips once: sealed line lists (for eligibility), per-face lines (for alignment), and the
    museum-number map of the sealed counter."""
    sealed, faces, mus2p = {}, {}, {}
    for z in sorted(glob.glob(str(ORACC_DIR / "*.zip"))):
        zf = zipfile.ZipFile(z)
        for nm in zf.namelist():
            if "/corpusjson/" in nm and nm.endswith(".json"):
                raw = zf.read(nm)
                if not raw.strip():
                    continue
                d = json.loads(raw)
                out = []
                _sealed_walk(d.get("cdl", []), out)
                sealed[d["textid"]] = out
                faces[d["textid"]] = oracc_faces_of(d)
            if nm.endswith("/catalogue.json"):
                for p, m in json.loads(zf.read(nm)).get("members", {}).items():
                    for k in ("museum_no", "accession_no"):
                        if m.get(k):
                            mus2p[m[k].replace(" ", "").replace(",", "").upper()] = p
    return {"sealed": sealed, "faces": faces, "mus2p": mus2p}


def sealed_to_p(t, mus2p):
    if t.startswith("P") and t[1:].isdigit():
        return t
    key = t.replace(" ", "").upper()
    k2 = key[:-2] if key.endswith(("VS", "RS")) else key
    for c in (key, k2, k2.replace("K0", "K", 1), k2.replace("ND0", "ND", 1), k2.replace("BM0", "BM", 1)):
        if c in mus2p:
            return mus2p[c]
    return None


def is_p_number(t):
    return bool(re.fullmatch(r"P\d{6}", t))


def oracc_line_info(ln):
    """Sign count, clean flag, word lengths, classes and names of one ORACC line (alignment walker)."""
    signs = [(b, c, nm, wi) for wi, w in enumerate(ln["words"]) for (b, c, nm) in w]
    n = len(signs)
    clean = (not ln["taint"]) and not any(s[0] for s in signs)
    return {"n": n, "clean": clean, "wl": [len(w) for w in ln["words"]],
            "cls": [s[1] for s in signs], "signs": [s[2] for s in signs],
            "labels": [signs[i][3] != signs[i + 1][3] for i in range(n - 1)]}


def s1_eligible(oracc):
    """Sealed rule (count_na2_univ.py): Dencker-listed tablets (any tablet_segments_*.csv) matched to ORACC with >= 6
    clean lines of >= 3 signs, by the sealed walker. Returns {tablet_CDLI: (lines, gaps, bound)}."""
    univ = set()
    for f in sorted(glob.glob(str(DS_DIR / "tablet_segments_*.csv"))):
        with open(f, newline="") as fh:
            for r in csv.DictReader(fh):
                univ.add(r["tablet_CDLI"])
    per = {}
    for t in sorted(univ):
        p = sealed_to_p(t, oracc["mus2p"])
        if not p or p not in oracc["sealed"]:
            continue
        cl = [ln for ln in oracc["sealed"][p] if sum(len(w) for w in ln) >= 3 and not any(b for w in ln for b, _ in w)]
        if len(cl) >= 6:
            g = sum(sum(len(w) for w in ln) - 2 for ln in cl)
            bd = sum(len(ln) - 1 - (1 if len(ln) >= 2 and len(ln[-1]) == 1 else 0) for ln in cl)
            per[t] = (len(cl), g, bd)
    return per


# ----------------------------------------------------------------------------------------------------------------
# CDLI ATF parsing (S2), sealed eligibility and per-face lines
# ----------------------------------------------------------------------------------------------------------------
ATF_DAMAGE = re.compile(r"[\[\]x#?!<>]|\.\.\.")
ATF_NUMBERED = re.compile(r"^\d+'?\.\s")


def atf_words(body):
    """count_ur3_v2.py word/sign split: spaces separate words; - . + : and spaces join signs; {..} is one sign."""
    words = [w for w in body.split() if w]
    out = []
    for w in words:
        w2 = re.sub(r"\{[^}]*\}", " {D} ", w)
        parts = [s for s in re.split(r"[-.\s+:]+", w2) if s]
        out.append([("det" if s_ == "{D}" else ("num" if re.match(r"^\d", s_) else "syl"), s_) for s_ in parts])
    return out


def yale_want():
    """count_ur3_v2.py: P-number -> first nat image id of the (last) Yale record that names it."""
    want = {}
    with open(YALE_REC, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            for o in r.get("other_ids", []):
                m = re.match(r"(P\d{6}) \(CDLI number\)", o)
                if m:
                    want[m.group(1)] = r.get("nat", [None])[0]
    return want


def yale_records_by_p():
    rec = {}
    with open(YALE_REC, encoding="utf-8") as fh:
        for line in fh:
            r = json.loads(line)
            for o in r.get("other_ids", []):
                m = re.match(r"(P\d{6}) \(CDLI number\)", o)
                if m:
                    rec[m.group(1)] = r
    return rec


def load_atf(want_ids):
    """One pass over the ATF dump.

    sealed[P]: list of sign counts per word for every numbered, undamaged line with >= 3 signs (count_ur3_v2.py,
    all surfaces) -- used for the S2 eligibility rule only.
    faces[P]: {'obverse': [line...], 'reverse': [...]}, every numbered line of the tablet's obverse/reverse in order
    (damaged ones included; $-lines are unnumbered and so never ranked; lines under @seal, @envelope and edge or
    other surfaces are not face lines). Line: {"label","clean","n","wl","cls","signs","labels"}.
    PREREG-AMBIGUITY: surfaces are tracked by @obverse / @reverse; any other @-line naming a surface or object
    (@left, @right, @top, @bottom, @edge, @seal, @envelope, @surface, @object, @fragment, @bulla) ends the face until
    the next @obverse/@reverse; @envelope sets an envelope state that ignores its @obverse/@reverse until @tablet.
    @column, @tablet and other structural lines keep the current face.
    """
    sealed, faces = {}, {}
    cur, keep, surf, env = None, False, None, False
    with open(ATF_PATH, encoding="utf8", errors="replace") as fh:
        for line in fh:
            if line.startswith("&P"):
                cur = line[1:8]
                keep = cur in want_ids
                surf, env = None, False
                if keep:
                    sealed[cur] = []
                    faces[cur] = {"obverse": [], "reverse": []}
                continue
            if not keep:
                continue
            if line.startswith("@"):
                tag = line[1:].strip().split()[0].lower().rstrip("?!*") if line[1:].strip() else ""
                if tag == "tablet":
                    env, surf = False, None
                elif tag == "envelope":
                    env, surf = True, None
                elif tag in ("obverse", "reverse"):
                    surf = None if env else tag
                elif tag in ("left", "right", "top", "bottom", "edge", "seal", "surface", "object", "fragment",
                             "bulla", "face", "prism", "docket"):
                    surf = None
                continue
            if not ATF_NUMBERED.match(line):
                continue
            body = line.split(".", 1)[1].strip()
            damaged = bool(ATF_DAMAGE.search(body)) or "$" in body
            words = atf_words(body)
            n = sum(len(w) for w in words)
            if not damaged and n >= 3:
                sealed[cur].append([len(w) for w in words])
            if surf in ("obverse", "reverse"):
                signs = [(c, nm, wi) for wi, w in enumerate(words) for (c, nm) in w]
                faces[cur][surf].append({
                    "label": line.split(".", 1)[0].strip(), "clean": not damaged, "n": n,
                    "wl": [len(w) for w in words], "cls": [s[0] for s in signs], "signs": [s[1] for s in signs],
                    "labels": [signs[i][2] != signs[i + 1][2] for i in range(n - 1)]})
    return sealed, faces


def s2_pool(sealed_atf, want):
    """Sealed S2 pool: P with a Yale photo on disk and >= 6 undamaged lines of >= 3 signs (count_ur3_v2 logic)."""
    have = {f.split(".")[0] for f in os.listdir(YALE_IMG)}
    return sorted(p for p, L in sealed_atf.items() if L and len(L) >= 6 and want.get(p) in have)


# ----------------------------------------------------------------------------------------------------------------
# Dencker 2020 files (local only; never re-hosted; per-gap values never leave raw/)
# ----------------------------------------------------------------------------------------------------------------


def _parse_box(s):
    v = json.loads(s)
    return [float(v[0]), float(v[1]), float(v[2]), float(v[3])]


def load_dencker():
    """Returns dict with
    segs[(tablet, view)] -> list of segment bboxes (photo frame) from every tablet_segments_*.csv, file order;
    seg_by_coll[(coll, segm_idx)] -> (tablet, view, bbox);
    boxes[(tablet, view)] -> list of {"mzl", "bbox"} sign boxes (train_label != 0), photo frame, de-duplicated;
    lines[(tablet, view)] -> {line_idx: [(x, y), ...]} line polylines in the photo frame, point order as in file;
    translit[(tablet, view)] -> {line_idx: [mzl, ...]} ordered by pos_idx.
    """
    segs, seg_by_coll = defaultdict(list), {}
    for f in sorted(glob.glob(str(DS_DIR / "tablet_segments_*.csv"))):
        coll = Path(f).stem.replace("tablet_segments_", "")
        with open(f, newline="") as fh:
            for r in csv.DictReader(fh):
                bb = _parse_box(r["bbox"])
                seg_by_coll[(coll, r["segm_idx"])] = (r["tablet_CDLI"], r["view_desc"], bb)
                if r["view_desc"] in ("Obv", "Rev"):
                    segs[(r["tablet_CDLI"], r["view_desc"])].append(bb)
    boxes, seen = defaultdict(list), set()
    for f in sorted(glob.glob(str(DS_DIR / "bbox_annotations_*_full.csv"))):
        with open(f, newline="") as fh:
            for r in csv.DictReader(fh):
                if r["train_label"] == "0" or r["view_desc"] not in ("Obv", "Rev"):
                    continue
                bb = _parse_box(r["bbox"])
                key = (r["tablet_CDLI"], r["view_desc"], r["mzl_label"], tuple(bb))
                if key in seen:
                    continue
                seen.add(key)
                boxes[(r["tablet_CDLI"], r["view_desc"])].append({"mzl": int(r["mzl_label"]), "bbox": bb})
    lines, line_coll = defaultdict(lambda: defaultdict(list)), {}
    for f in sorted(glob.glob(str(DS_DIR / "line_annotations_*.csv"))):
        coll = Path(f).stem.replace("line_annotations_", "")
        with open(f, newline="") as fh:
            for r in csv.DictReader(fh):
                sg = seg_by_coll.get((coll, r["segm_idx"]))
                if sg is None or sg[0] != r["tablet_CDLI"] or sg[1] not in ("Obv", "Rev"):
                    continue
                # line annotations are relative to their segment crop (checked on the file format, not on gaps)
                x = float(r["x"]) + sg[2][0]
                y = float(r["y"]) + sg[2][1]
                lines[(sg[0], sg[1])][int(r["line_idx"])].append((x, y))
                line_coll[(sg[0], sg[1])] = coll
    # transliterations: prefer the file of the same collection as the line annotation, else first file in name order
    tl_by_file = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
    for f in sorted(glob.glob(str(DS_DIR / "transliterations_*.csv"))):
        coll = Path(f).stem.replace("transliterations_", "")
        with open(f, newline="") as fh:
            for r in csv.DictReader(fh):
                if r["view_desc"] not in ("Obv", "Rev"):
                    continue
                tl_by_file[(r["tablet_CDLI"], r["view_desc"])][coll][int(r["line_idx"])].append(
                    (int(r["pos_idx"]), int(r["mzl_label"])))
    translit = {}
    for k, by in tl_by_file.items():
        coll = line_coll.get(k)
        pick = coll if coll in by else sorted(by)[0]
        translit[k] = {li: [m for _, m in sorted(v)] for li, v in by[pick].items()}
    line_tablets = sorted({k[0] for k in lines})
    return {"segs": dict(segs), "seg_by_coll": seg_by_coll, "boxes": dict(boxes),
            "lines": {k: dict(v) for k, v in lines.items()}, "translit": translit, "line_tablets": line_tablets}


def _poly_project(pt, poly):
    """Distance from pt to a polyline and arc-length position of the nearest point."""
    px, py = pt
    if len(poly) == 1:
        return math.hypot(px - poly[0][0], py - poly[0][1]), 0.0
    best, pos, acc = float("inf"), 0.0, 0.0
    for (x0, y0), (x1, y1) in zip(poly[:-1], poly[1:]):
        dx, dy = x1 - x0, y1 - y0
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - x0) * dx + (py - y0) * dy) / L2))
        qx, qy = x0 + t * dx, y0 + t * dy
        d = math.hypot(px - qx, py - qy)
        if d < best:
            best, pos = d, acc + t * math.sqrt(L2)
        acc += math.sqrt(L2)
    return best, pos


def lcs_match(a, b):
    """Longest common subsequence of label lists a (boxes) and b (transliteration); label 0 never matches.
    Returns list of (i, j) matched index pairs, increasing. Ties in the back-track skip a box first."""
    n, m = len(a), len(b)
    dp = np.zeros((n + 1, m + 1), dtype=np.int32)
    for i in range(n):
        for j in range(m):
            if a[i] != 0 and a[i] == b[j]:
                dp[i + 1, j + 1] = dp[i, j] + 1
            else:
                dp[i + 1, j + 1] = max(dp[i, j + 1], dp[i + 1, j])
    i, j, out = n, m, []
    while i > 0 and j > 0:
        if a[i - 1] != 0 and a[i - 1] == b[j - 1] and dp[i, j] == dp[i - 1, j - 1] + 1:
            out.append((i - 1, j - 1))
            i, j = i - 1, j - 1
        elif dp[i - 1, j] >= dp[i, j - 1]:
            i -= 1
        else:
            j -= 1
    return out[::-1]


def gold_pairs_face(face_boxes, polylines, translit_lines):
    """G2 gold pairs on one Dencker face (prereg §4.4 G2).

    PREREG-AMBIGUITY (assignment and order): each Dencker sign box goes to the annotated line whose polyline is
    nearest to its centre; within a line, boxes are ordered by the arc-length position of their nearest polyline point
    (polyline points in file order). PREREG-AMBIGUITY (MZL match): the ordered box labels are matched to the
    transliteration line of the same face with the longest common subsequence of MZL labels (ties: lowest line_idx;
    at least 2 matches). A gold pair is two boxes adjacent in the line order whose matches are consecutive positions
    j, j+1 of that transliteration line. Gold gaps are measured in the line frame of all boxes assigned to that line.
    Returns (pairs, line_groups): pairs carry indices into face_boxes plus the gold gap; nothing is written here.
    """
    if not polylines or not translit_lines or not face_boxes:
        return [], {}
    assign = defaultdict(list)
    for bi, b in enumerate(face_boxes):
        c = ((b["bbox"][0] + b["bbox"][2]) / 2, (b["bbox"][1] + b["bbox"][3]) / 2)
        best = None
        for li in sorted(polylines):
            d, pos = _poly_project(c, polylines[li])
            if best is None or d < best[0]:
                best = (d, li, pos)
        assign[best[1]].append((best[2], c[0], bi))
    pairs, groups = [], {}
    tl_ids = sorted(translit_lines)
    for li in sorted(assign):
        order = [bi for _, _, bi in sorted(assign[li])]
        groups[li] = order
        labs = [face_boxes[bi]["mzl"] for bi in order]
        best = None
        for tli in tl_ids:
            m = lcs_match(labs, translit_lines[tli])
            if best is None or len(m) > len(best[1]):
                best = (tli, m)
        if best is None or len(best[1]) < 2:
            continue
        tli, m = best
        jmap = dict(m)
        rb, th = line_frame([face_boxes[bi]["bbox"] for bi in order])
        H = float(np.median(rb[:, 3] - rb[:, 1]))
        for k in range(len(order) - 1):
            if k in jmap and (k + 1) in jmap and jmap[k + 1] == jmap[k] + 1:
                g = float(rb[k + 1, 0] - rb[k, 2])
                pairs.append({"b0": order[k], "b1": order[k + 1], "gold_g": g, "gold_G": g / H if H > 0 else None,
                              "line": li, "tl_line": tli, "j": jmap[k], "n_tl": len(translit_lines[tli]),
                              "k": k, "line_n_boxes": len(order)})
    return pairs, groups


# ----------------------------------------------------------------------------------------------------------------
# Geometry: frames, features, back-mapping
# ----------------------------------------------------------------------------------------------------------------


def unmap_box(b, W, H, scale, rotated=True):
    """Rater box in the given (rotated, scaled) image -> original crop frame. 180 deg: (x, y) -> (W - x, H - y)."""
    x0, y0, x1, y1 = (float(v) / scale for v in b)
    if rotated:
        x0, y0, x1, y1 = W - x1, H - y1, W - x0, H - y0
    return [x0, y0, x1, y1]


def unmap_lines(lines, W, H, scale, rotated=True):
    """Map every box back and reverse the line order and the box order in each line (prereg §4.2)."""
    out = [[unmap_box(b, W, H, scale, rotated) for b in ln] for ln in lines]
    if rotated:
        out = [ln[::-1] for ln in out[::-1]]
    return out


def rotate_boxes(boxes, th):
    b = np.asarray(boxes, dtype=float).reshape(-1, 4)
    c, s = math.cos(th), math.sin(th)
    xs = b[:, [0, 2, 0, 2]]
    ys = b[:, [1, 1, 3, 3]]
    X = xs * c + ys * s
    Y = -xs * s + ys * c
    return np.column_stack([X.min(1), Y.min(1), X.max(1), Y.max(1)])


def line_frame(boxes):
    """§4.1 line frame: OLS line through box centres; boxes rotated by -theta so the line runs horizontally, left to
    right. Each box becomes the axis-aligned box of its rotated corners."""
    b = np.asarray(boxes, dtype=float).reshape(-1, 4)
    cx = (b[:, 0] + b[:, 2]) / 2.0
    cy = (b[:, 1] + b[:, 3]) / 2.0
    th = 0.0
    if len(b) >= 2 and np.ptp(cx) > 0:
        th = math.atan(float(np.polyfit(cx, cy, 1)[0]))
    return rotate_boxes(b, th), th


def features_from_rb(rb, shift_labels=None, shift=0.0):
    n = len(rb)
    if n < 2:
        return None
    rb = np.array(rb, dtype=float)
    w = rb[:, 2] - rb[:, 0]
    h = rb[:, 3] - rb[:, 1]
    H = float(np.median(h))
    if shift_labels is not None and shift:
        # §5.4: every box past each pseudo-boundary moves right by shift * H (cumulative)
        k = np.concatenate([[0], np.cumsum(np.asarray(shift_labels, dtype=float))])
        rb[:, 0] += k * shift * H
        rb[:, 2] += k * shift * H
    L = float(rb[:, 2].max() - rb[:, 0].min())
    if H <= 0 or L <= 0:
        return None
    g = rb[1:, 0] - rb[:-1, 2]
    cyr = (rb[:, 1] + rb[:, 3]) / 2.0
    area = w * h
    with np.errstate(divide="ignore", invalid="ignore"):
        lar = np.log(area[1:] / area[:-1])
    return {"n": n, "H": H, "g": g, "G": g / H, "p": np.arange(n - 1) / (n - 1),
            "Wl": w[:-1] / H, "Wr": w[1:] / H, "fill": float(w.sum() / L),
            "dy": (cyr[1:] - cyr[:-1]) / H, "lar": lar, "h": h, "w": w}


def line_features(boxes, shift_labels=None, shift=0.0):
    rb, th = line_frame(boxes)
    f = features_from_rb(rb, shift_labels, shift)
    if f is not None:
        f["theta"] = th
    return f


def iou_matrix(A, B):
    A = np.asarray(A, dtype=float).reshape(-1, 4)
    B = np.asarray(B, dtype=float).reshape(-1, 4)
    if len(A) == 0 or len(B) == 0:
        return np.zeros((len(A), len(B)))
    ix0 = np.maximum(A[:, None, 0], B[None, :, 0])
    iy0 = np.maximum(A[:, None, 1], B[None, :, 1])
    ix1 = np.minimum(A[:, None, 2], B[None, :, 2])
    iy1 = np.minimum(A[:, None, 3], B[None, :, 3])
    inter = np.clip(ix1 - ix0, 0, None) * np.clip(iy1 - iy0, 0, None)
    aa = (A[:, 2] - A[:, 0]) * (A[:, 3] - A[:, 1])
    ab = (B[:, 2] - B[:, 0]) * (B[:, 3] - B[:, 1])
    union = aa[:, None] + ab[None, :] - inter
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(union > 0, inter / union, 0.0)


def hungarian_pairs(A, B, thr):
    """Optimal one-to-one assignment maximising total IoU (cost 1 - IoU); pairs with IoU >= thr kept."""
    from scipy.optimize import linear_sum_assignment
    M = iou_matrix(A, B)
    if M.size == 0:
        return []
    r, c = linear_sum_assignment(1.0 - M)
    return [(int(i), int(j), float(M[i, j])) for i, j in zip(r, c) if M[i, j] >= thr]


# ----------------------------------------------------------------------------------------------------------------
# Residual model (§4.3)
# ----------------------------------------------------------------------------------------------------------------


def ns_basis(x, knots=KNOTS):
    """Natural cubic spline basis (ESL eq. 5.4-5.5), knots 0, .25, .5, .75, 1: columns x, N_3..N_5 (4 df, the
    intercept is a separate column). Same column space as R's ns(x, knots=c(.25,.5,.75), Boundary.knots=c(0,1))."""
    x = np.asarray(x, dtype=float)
    xi = np.asarray(knots, dtype=float)
    K = len(xi)

    def d(k):
        return (np.clip(x - xi[k], 0, None) ** 3 - np.clip(x - xi[K - 1], 0, None) ** 3) / (xi[K - 1] - xi[k])

    cols = [x] + [d(k) - d(K - 2) for k in range(K - 2)]
    return np.column_stack(cols)


def design(p, Wl, Wr, fill, gidx, n, model):
    p = np.asarray(p, dtype=float)
    one = np.ones_like(p)
    if model == "spline":
        X = np.column_stack([one, ns_basis(p), Wl, Wr, fill])
        names = ["const", "ns1", "ns2", "ns3", "ns4", "W_left", "W_right", "fill"]
    elif model == "f3":
        # F3: position-decile fixed effects (no intercept) plus indicators for the last, 2nd-last and 3rd-last gap.
        # PREREG-AMBIGUITY: decile = floor(10 p + 1e-9) capped at 9; "last 3 gaps" = three separate indicators;
        # the last-gap indicator is all zero on scored gaps (the last gap is excluded), and all-zero columns are dropped.
        dec = np.minimum(np.floor(p * 10 + 1e-9).astype(int), 9)
        D = np.zeros((len(p), 10))
        D[np.arange(len(p)), dec] = 1.0
        gidx = np.asarray(gidx)
        n = np.asarray(n)
        L1 = (gidx == n - 2).astype(float)
        L2 = (gidx == n - 3).astype(float)
        L3 = (gidx == n - 4).astype(float)
        X = np.column_stack([D, L1, L2, L3, Wl, Wr, fill])
        names = [f"dec{k}" for k in range(10)] + ["last1", "last2", "last3", "W_left", "W_right", "fill"]
        keep = np.any(X != 0, axis=0)
        X = X[:, keep]
        names = [nm for nm, k in zip(names, keep) if k]
    else:
        raise ValueError(model)
    return X, names


def huber_fit(X, y, k=HUBER_K, tol=IRLS_TOL, maxit=IRLS_MAXIT):
    """Huber M-estimate by IRLS. Scale = normalised MAD of the current residuals (1.4826 * median |r - median r|),
    re-estimated every iteration. Stops when the largest absolute coefficient change is < tol, or after maxit.
    PREREG-AMBIGUITY: "tolerance 1e-8" is read as the max-abs coefficient change between iterations; start = OLS."""
    X = np.asarray(X, dtype=float)
    y = np.asarray(y, dtype=float)
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    converged, it, s = False, 0, float("nan")
    for it in range(1, maxit + 1):
        r = y - X @ beta
        s = 1.4826 * float(np.median(np.abs(r - np.median(r))))
        if not s > 0:
            converged = True
            break
        u = np.abs(r / s)
        w = np.where(u <= k, 1.0, k / np.maximum(u, 1e-300))
        sw = np.sqrt(w)
        beta_new = np.linalg.lstsq(X * sw[:, None], y * sw, rcond=None)[0]
        delta = float(np.max(np.abs(beta_new - beta))) if len(beta) else 0.0
        beta = beta_new
        if delta < tol:
            converged = True
            break
    return {"beta": beta, "converged": converged, "iterations": it, "scale": s}


def lines_for_rater(lines, rater):
    """Features per line for rater 'A', 'B', 'T' (truth) or 'mean' (A and B features averaged gap by gap).
    PREREG-AMBIGUITY: "the mean of A and B" is the per-gap mean of the normalised features (G, both widths, fill) of
    the two raters, fitted as its own residual model."""
    out = []
    for ln in lines:
        sh = ln.get("shift")
        if "pre" in ln:
            out.append(None)
            continue
        if rater == "mean":
            fa = line_features(ln["boxes"]["A"], ln["labels"] if sh else None, sh or 0.0)
            fb = line_features(ln["boxes"]["B"], ln["labels"] if sh else None, sh or 0.0)
            if fa is None or fb is None or fa["n"] != fb["n"]:
                out.append(None)
                continue
            f = dict(fa)
            for k in ("G", "Wl", "Wr", "dy", "lar"):
                f[k] = (fa[k] + fb[k]) / 2.0
            f["fill"] = (fa["fill"] + fb["fill"]) / 2.0
            out.append(f)
        else:
            out.append(line_features(ln["boxes"][rater], ln["labels"] if sh else None, sh or 0.0))
    return out


def build_gapset(lines, rater, model):
    """Scored gaps (§4.3): lines with >= 3 boxes, every gap except the last. Arrays are grouped by line."""
    feats = lines_for_rater(lines, rater)
    ys, ps, wl, wr, fl, gi, nn, lab, plain, dy, lar, lid, clu, ptr = [], [], [], [], [], [], [], [], [], [], [], [], [], [0]
    used, skipped = [], 0
    for li, (ln, f) in enumerate(zip(lines, feats)):
        if "pre" in ln:
            # precomputed gaps (record-only Dencker lines): already restricted to scored, non-last gaps
            pre = ln["pre"]
            if not pre["G"]:
                skipped += 1
                continue
            idx = np.asarray(pre["gidx"], dtype=int)
            ys.append(np.asarray(pre["G"], float)); ps.append(np.asarray(pre["p"], float))
            wl.append(np.asarray(pre["Wl"], float)); wr.append(np.asarray(pre["Wr"], float))
            fl.append(np.full(len(idx), float(pre["fill"]))); gi.append(idx); nn.append(np.full(len(idx), pre["n"]))
            lab.append(np.asarray(ln["labels"], dtype=bool)); plain.append(np.ones(len(idx), dtype=bool))
            dy.append(np.asarray(pre["dy"], float)); lar.append(np.asarray(pre["lar"], float))
            lid.append(len(used)); clu.append(ln.get("cluster", str(li)))
            ptr.append(ptr[-1] + len(idx))
            used.append(li)
            continue
        if f is None or f["n"] < 3:
            skipped += 1
            continue
        n = f["n"]
        if len(ln["labels"]) != n - 1:
            raise ValueError(f"label length {len(ln['labels'])} != n-1 for line {li}")
        idx = np.arange(n - 2)
        ys.append(f["G"][idx]); ps.append(f["p"][idx]); wl.append(f["Wl"][idx]); wr.append(f["Wr"][idx])
        fl.append(np.full(len(idx), f["fill"])); gi.append(idx); nn.append(np.full(len(idx), n))
        lab.append(np.asarray(ln["labels"], dtype=bool)[idx])
        cls = ln.get("cls")
        if cls:
            plain.append(np.array([cls[i] == "syl" and cls[i + 1] == "syl" for i in idx], dtype=bool))
        else:
            plain.append(np.ones(len(idx), dtype=bool))
        dy.append(f["dy"][idx]); lar.append(f["lar"][idx])
        lid.append(len(used)); clu.append(ln.get("cluster", str(li)))
        ptr.append(ptr[-1] + len(idx))
        used.append(li)
    if not used:
        return None
    cat = np.concatenate
    p, Wl, Wr, fill, gidx, n = cat(ps), cat(wl), cat(wr), cat(fl), cat(gi), cat(nn)
    X, names = design(p, Wl, Wr, fill, gidx, n, model)
    return {"y": cat(ys), "X": X, "names": names, "p": p, "lab": cat(lab), "plain": cat(plain), "dy": cat(dy),
            "lar": cat(lar), "ptr": np.asarray(ptr), "line_cluster": np.asarray(clu, dtype=object),
            "used": used, "skipped": skipped, "gidx": gidx, "n": n}


def residuals(gs):
    fit = huber_fit(gs["X"], gs["y"])
    return gs["y"] - gs["X"] @ fit["beta"], fit


# ----------------------------------------------------------------------------------------------------------------
# AUC, bootstrap, null, ICC
# ----------------------------------------------------------------------------------------------------------------


def per_line_counts(R, lab, ptr, mask=None):
    """§6.1 exactly: per line l, numerator sum_{b in B_l} sum_{n in N_l} [1(R_b > R_n) + 1/2 1(R_b = R_n)] and
    denominator |B_l| |N_l|. AUC = sum numerators / sum denominators."""
    L = len(ptr) - 1
    num = np.zeros(L)
    den = np.zeros(L)
    for l in range(L):
        a, b = ptr[l], ptr[l + 1]
        r = np.asarray(R[a:b], dtype=float)
        y = np.asarray(lab[a:b], dtype=bool)
        if mask is not None:
            m = np.asarray(mask[a:b], dtype=bool)
            r, y = r[m], y[m]
        rb, rn = r[y], r[~y]
        if len(rb) and len(rn):
            num[l] = float((rb[:, None] > rn[None, :]).sum()) + 0.5 * float((rb[:, None] == rn[None, :]).sum())
            den[l] = float(len(rb) * len(rn))
    return num, den


def auc_of(num, den):
    D = den.sum()
    return float(num.sum() / D) if D > 0 else float("nan")


def cluster_boot(num, den, line_cluster, B=N_BOOT, seed=SEED_BOOT):
    """Percentile cluster bootstrap: clusters resampled with replacement, each carrying its lines and pairs whole;
    residuals are not refitted. PREREG-AMBIGUITY: percentiles by numpy's default linear interpolation; a resample with
    no pairs (denominator 0) is dropped and counted."""
    ids, inv = np.unique(np.asarray(line_cluster, dtype=str), return_inverse=True)
    C = len(ids)
    cn = np.bincount(inv, weights=num, minlength=C)
    cd = np.bincount(inv, weights=den, minlength=C)
    rng = np.random.default_rng(seed)
    draws = rng.integers(0, C, size=(B, C))
    bn = cn[draws].sum(1)
    bd = cd[draws].sum(1)
    ok = bd > 0
    aucs = bn[ok] / bd[ok]
    if len(aucs) == 0:
        return float("nan"), float("nan"), {"clusters": C, "dropped": int((~ok).sum())}
    lo, hi = np.percentile(aucs, [2.5, 97.5])
    return float(lo), float(hi), {"clusters": C, "dropped": int((~ok).sum())}


def shuffle_null(R, lab, ptr, n_shuf=N_SHUF, seed=SEED_SHUF, batch=50):
    """§6.2: labels shuffled within line (positions kept, each line's boundary count kept), n_shuf times.
    Uses the identity that, with midranks within a line, sum over boundary midranks - k(k+1)/2 equals the §6.1
    numerator; a within-line label shuffle is a uniform random k-subset of the line's positions.
    Returns (observed AUC, p one-sided = (1 + #null >= observed) / (n_shuf + 1), null array)."""
    from scipy.stats import rankdata
    rows = []
    for l in range(len(ptr) - 1):
        a, b = ptr[l], ptr[l + 1]
        y = np.asarray(lab[a:b], dtype=bool)
        k, m = int(y.sum()), len(y)
        if 0 < k < m:
            rows.append((rankdata(np.asarray(R[a:b], dtype=float), method="average"), y, k))
    if not rows:
        return float("nan"), float("nan"), np.array([])
    L = len(rows)
    mmax = max(len(r[0]) for r in rows)
    M = np.zeros((L, mmax))
    V = np.zeros((L, mmax), dtype=bool)
    K = np.zeros(L)
    obs_num = 0.0
    den = 0.0
    for i, (rk, y, k) in enumerate(rows):
        M[i, :len(rk)] = rk
        V[i, :len(rk)] = True
        K[i] = k
        obs_num += rk[y].sum() - k * (k + 1) / 2.0
        den += k * (len(rk) - k)
    obs = obs_num / den
    off = (K * (K + 1) / 2.0).sum()
    rng = np.random.default_rng(seed)
    null = np.empty(n_shuf)
    done = 0
    while done < n_shuf:
        S = min(batch, n_shuf - done)
        keys = rng.random((S, L, mmax))
        keys[:, ~V] = 2.0
        pos = np.argsort(np.argsort(keys, axis=2), axis=2)
        sel = pos < K[None, :, None]
        null[done:done + S] = ((M[None] * sel).sum(axis=(1, 2)) - off) / den
        done += S
    p = (1.0 + float((null >= obs - 1e-12).sum())) / (n_shuf + 1.0)
    return float(obs), p, null


def icc21(Y):
    """ICC(2,1), two-way random effects, absolute agreement, single measure (Shrout & Fleiss 1979).
    Y: n targets x k raters."""
    Y = np.asarray(Y, dtype=float)
    Y = Y[np.all(np.isfinite(Y), axis=1)]
    n, k = Y.shape
    if n < 3:
        return float("nan")
    gm = Y.mean()
    ssr = k * ((Y.mean(1) - gm) ** 2).sum()
    ssc = n * ((Y.mean(0) - gm) ** 2).sum()
    sst = ((Y - gm) ** 2).sum()
    sse = sst - ssr - ssc
    msr = ssr / (n - 1)
    msc = ssc / (k - 1)
    mse = sse / ((n - 1) * (k - 1))
    denom = msr + (k - 1) * mse + k * (msc - mse) / n
    return float((msr - mse) / denom) if denom != 0 else float("nan")


# ----------------------------------------------------------------------------------------------------------------
# Scoring one data set
# ----------------------------------------------------------------------------------------------------------------


def score_lines(lines, rater, model, with_ci=True, with_null=True, boot_seed=SEED_BOOT, shuf_seed=SEED_SHUF):
    gs = build_gapset(lines, rater, model)
    if gs is None:
        return {"n_lines": 0, "auc": None}
    R, fit = residuals(gs)
    num, den = per_line_counts(R, gs["lab"], gs["ptr"])
    res = {"auc": auc_of(num, den), "n_lines": len(gs["used"]), "n_gaps": int(len(R)),
           "n_boundary": int(gs["lab"].sum()), "n_pairs": int(den.sum()), "lines_skipped": gs["skipped"],
           "fit": {"converged": fit["converged"], "iterations": fit["iterations"], "scale": fit["scale"],
                   "coef": dict(zip(gs["names"], [float(b) for b in fit["beta"]]))}}
    if with_ci:
        lo, hi, info = cluster_boot(num, den, gs["line_cluster"], seed=boot_seed)
        res.update({"ci_lo": lo, "ci_hi": hi, "boot": info})
    if with_null:
        obs, p, _ = shuffle_null(R, gs["lab"], gs["ptr"], seed=shuf_seed)
        if np.isfinite(obs) and abs(obs - res["auc"]) > 1e-9:
            raise AssertionError(f"rank AUC {obs} != exact AUC {res['auc']}")
        res["p_null"] = p
    # §6.4(d): same residuals, gaps whose two neighbours are both plain syllabic signs
    nd, dd = per_line_counts(R, gs["lab"], gs["ptr"], mask=gs["plain"])
    res["d_auc"] = auc_of(nd, dd)
    res["d_n_pairs"] = int(dd.sum())
    res["d_n_gaps"] = int(gs["plain"].sum())
    if with_ci:
        lo, hi, _ = cluster_boot(nd, dd, gs["line_cluster"], seed=boot_seed)
        res.update({"d_ci_lo": lo, "d_ci_hi": hi})
    # description only: secondary cues, per-position deciles, sign-class pairs
    desc = {}
    for nm in ("dy", "lar"):
        v = np.nan_to_num(gs[nm], nan=0.0)
        a, b = per_line_counts(v, gs["lab"], gs["ptr"])
        desc[f"auc_{nm}"] = auc_of(a, b)
    dec = np.minimum(np.floor(gs["p"] * 10 + 1e-9).astype(int), 9)
    desc["by_decile"] = {int(d): {"n_b": int((gs["lab"] & (dec == d)).sum()), "n_n": int((~gs["lab"] & (dec == d)).sum()),
                                  "mean_R_b": _mean(R[gs["lab"] & (dec == d)]),
                                  "mean_R_n": _mean(R[~gs["lab"] & (dec == d)])} for d in range(10)}
    pair_cls = Counter()
    pair_R = defaultdict(list)
    k = 0
    for li in gs["used"]:
        ln = lines[li]
        cls = ln.get("cls")
        m = len(ln["labels"]) if "pre" in ln else len(ln["labels"]) - 1
        for i in range(m):
            key = f"{cls[i]}|{cls[i + 1]}|{'B' if ln['labels'][i] else 'N'}" if cls else f"?|?|{'B' if ln['labels'][i] else 'N'}"
            pair_cls[key] += 1
            pair_R[key].append(R[k])
            k += 1
    desc["class_pairs"] = {key: {"n": c, "mean_R": _mean(np.asarray(pair_R[key]))} for key, c in sorted(pair_cls.items())}
    res["description"] = desc
    return res


def _mean(a):
    a = np.asarray(a, dtype=float)
    return float(a.mean()) if a.size else None


def apply_cluster_rule(lines, min_clusters=20):
    """S2 (§4.5): cluster = provenience x regnal year; a tablet missing either field is its own cluster (set in
    align.py). If fewer than 20 distinct clusters remain among the scored lines, the tablet is the cluster.
    PREREG-AMBIGUITY: the count of clusters is taken over the lines that enter scoring."""
    cl = {ln["cluster"] for ln in lines}
    if len(cl) < min_clusters:
        return [dict(ln, cluster=ln["tablet"]) for ln in lines], {"rule": "tablet (fewer than 20 clusters)",
                                                                   "n_clusters_py": len(cl)}
    return lines, {"rule": "provenience x regnal year", "n_clusters_py": len(cl)}


# ----------------------------------------------------------------------------------------------------------------
# gates
# ----------------------------------------------------------------------------------------------------------------


def cmd_gates(args):
    info = seal_check([Path(__file__).resolve()])
    src = read_json(ALIGNED / f"gates_{args.round}.json")
    out = {"round": args.round, "utc": utc(), "seal": info, "key_sha256": src.get("key_sha256")}
    g2 = src.get("G2")
    if g2 is not None:
        rec = {}
        for r in ("A", "B"):
            tot = g2["n_gold_boxes"]
            rec[r] = g2["matched"][r] / tot if tot else float("nan")
        pairs = g2["pairs"]
        res = {"recall": rec, "n_gold_boxes": g2["n_gold_boxes"], "n_gold_pairs": len(pairs),
               "gold_pairs_available": g2.get("gold_pairs_available"), "icc_gold": {}, "icc_gold_G": {}, "n_used": {}}
        for r in ("A", "B"):
            use = [p for p in pairs if p.get(f"{r}_g") is not None]
            res["n_used"][r] = len(use)
            res["icc_gold"][r] = icc21([[p["gold_g"], p[f"{r}_g"]] for p in use])
            res["icc_gold_G"][r] = icc21([[p["gold_G"], p[f"{r}_G"]] for p in use if p["gold_G"] is not None])
        both = [p for p in pairs if p.get("A_g") is not None and p.get("B_g") is not None]
        res["n_used"]["AB"] = len(both)
        res["icc_AB"] = icc21([[p["A_g"], p["B_g"]] for p in both])
        res["icc_AB_G"] = icc21([[p["A_G"], p["B_G"]] for p in both])
        # PREREG-AMBIGUITY: "gap" in G2 is the raw gap g_i (§4.1) in crop pixels; the ICC on normalised G is reported.
        # PREREG-AMBIGUITY: the agent-agent ICC is taken on the gold pairs matched by both agents.
        enough = (g2.get("gold_pairs_available") or 0) >= 200
        res["pass"] = bool(enough and all(_ge(rec[r], 0.85) and _ge(res["icc_gold"][r], 0.70) for r in ("A", "B"))
                           and _ge(res["icc_AB"], 0.70))
        res["reason"] = None if enough else "fewer than 200 gold pairs (G2 fails by rule)"
        out["G2"] = res
    g2b = src.get("G2b")
    if g2b is not None:
        pr = g2b["pairs"]
        icc = icc21([[p["A_g"], p["B_g"]] for p in pr])
        out["G2b"] = {"icc_AB": icc, "icc_AB_G": icc21([[p["A_G"], p["B_G"]] for p in pr]), "n_gaps": len(pr),
                      "n_lines": g2b["n_lines"], "n_faces": g2b["n_faces"], "pass": _ge(icc, 0.70)}
    g3 = src.get("G3")
    if g3 is not None:
        res = {}
        for script, d in g3.items():
            mA = _median(d["A_given"])
            res[script] = {"median_A_given_px": mA, "median_B_given_px": _median(d["B_given"]),
                           "median_A_native_px": _median(d["A_native"]), "n_boxes_A": len(d["A_given"])}
            # PREREG-AMBIGUITY: "median box height at the image size used" = rater-A boxes, in pixels of the image
            # as given to the rater (after any F2 upsampling); native-frame heights are reported beside it.
            if script == "S2":
                res[script]["pass"] = _ge(mA, 25.0)
            else:
                res[script]["pass"] = True
                res[script]["note"] = "S1 passes at 55 px (Dencker median, prereg §4.4); agent value reported"
        out["G3"] = res
    write_json(OUT / f"gates_{args.round}.json", out)
    print(json.dumps({k: (v.get("pass") if isinstance(v, dict) and "pass" in v else v)
                      for k, v in out.items() if k in ("G2", "G2b")}, indent=1))
    if "G3" in out:
        print("G3", {k: v["pass"] for k, v in out["G3"].items()})


def _ge(x, t):
    return x is not None and np.isfinite(x) and x >= t


def _median(a):
    return float(np.median(a)) if len(a) else None


# ----------------------------------------------------------------------------------------------------------------
# §5.4 pseudo-boundary test
# ----------------------------------------------------------------------------------------------------------------


def pseudo_results(lines):
    res = {}
    for model in ("spline", "f3"):
        r0 = score_lines(lines, "A", model, with_ci=False, with_null=False)
        shifted = [dict(ln, shift=0.10) for ln in lines]
        r1 = score_lines(shifted, "A", model, with_ci=False, with_null=False)
        a0 = r0.get("auc")
        res[model] = {"auc_delta0": a0, "auc_shift_0.10H": r1.get("auc"), "n_lines": r0.get("n_lines"),
                      "n_pairs": r0.get("n_pairs"),
                      "pass": bool(a0 is not None and np.isfinite(a0) and 0.45 <= a0 <= 0.55)}
    return res


def cmd_pseudo(args):
    info = seal_check([Path(__file__).resolve()])
    src = read_json(ALIGNED / f"pseudo_{args.round}.json")
    res = pseudo_results(src["lines"])
    out = {"round": args.round, "utc": utc(), "seal": info, "n_tablets": src.get("n_tablets"),
           "tablets_source": src.get("tablets_source"), "results": res}
    if not src["lines"]:
        out["note"] = "no calibration line joined: §5.4 cannot be computed (treated as a failed check)"
    write_json(OUT / f"pseudo_{args.round}.json", out)
    print(json.dumps(res, indent=1))


# ----------------------------------------------------------------------------------------------------------------
# K0
# ----------------------------------------------------------------------------------------------------------------
READING_PASS = ("In two cuneiform traditions without dividers, inter-sign gaps carry word-boundary information "
                "(AUC a, b), shown within cuneiform only.")
READING_PASS_ADD = "A pass does not show that the cue carries across script families (D1)."
CONSEQ_PASS = ("The Indus stage (§9) may be pre-registered, after the §9 resolution gate. It does not say Indus "
               "gaps mark words.")
READING_SPLIT = "Gap as a boundary cue is tradition-specific, shown within cuneiform only."
CONSEQ_SPLIT = "No Indus stage. Atlas entry."
READING_FAIL = ("Gap size is not a usable word-boundary cue in undivided cuneiform at agent-box precision (shown "
                "within cuneiform only).")
READING_FAIL_ADD = "measurement noise may hide a weak cue"
CONSEQ_FAIL = ("Indus layout segmentation via gaps is closed until an expert measurer exists. Atlas entry; reopen "
               "only with expert boxes.")
READING_INC = "Reported with the failed gate or interval, shown within cuneiform only."
CONSEQ_INC = "No Indus stage."
READING_ALL = "Nothing here bears on any reading of an Indus sign."


def check_readings_in_prereg():
    """The frozen reading strings above must appear in the sealed prereg (markup '**' removed)."""
    txt = (ROOT / PREREG_REL).read_text(encoding="utf-8").replace("**", "")
    txt = re.sub(r"\s+", " ", txt)
    miss = [s for s in (READING_PASS, READING_PASS_ADD, CONSEQ_PASS, READING_SPLIT, CONSEQ_SPLIT, READING_FAIL,
                        READING_FAIL_ADD, CONSEQ_FAIL, READING_INC, CONSEQ_INC, READING_ALL)
            if re.sub(r"\s+", " ", s) not in txt]
    if miss:
        raise SystemExit("frozen reading text not found in prereg: " + " | ".join(miss))


def attenuation(synth):
    """§5.3: agent-A AUC on the delta=0.10 measurer lines vs the truth-box AUC on the same (joined) lines.
    PREREG-AMBIGUITY: residual model fitted on those lines alone (per delta subset and per box source); a synthetic
    line is used when the rater returned exactly one line with as many boxes as the truth line has signs."""
    out = {}
    for dkey in ("0.10", "0.00"):
        L = [ln for ln in synth["lines"] if ln["delta_key"] == dkey and ln.get("joined_A")]
        if not L:
            out[dkey] = {"n_lines": 0}
            continue
        ra = score_lines(L, "A", "spline", with_ci=False, with_null=False)
        rt = score_lines(L, "T", "spline", with_ci=False, with_null=False)
        out[dkey] = {"n_lines": len(L), "auc_agent_A": ra.get("auc"), "auc_truth": rt.get("auc")}
    a = out.get("0.10", {})
    if a.get("auc_agent_A") is not None and a.get("auc_truth") not in (None, 0.5):
        out["ratio"] = (a["auc_agent_A"] - 0.5) / (a["auc_truth"] - 0.5)
    else:
        out["ratio"] = None
    out["n_measurer_lines"] = len(synth["lines"])
    return out


def cmd_k0(args):
    info = seal_check([Path(__file__).resolve()])
    check_readings_in_prereg()
    r1 = args.round
    r2 = args.s2_round or args.round
    heartbeat("k0", 0, 6)
    res = {"round_S1": r1, "round_S2": r2, "utc": utc(), "seal": info, "gates": {}, "notes": []}
    g1src = read_json(OUT / f"gates_{r1}.json")
    g2src = g1src if r2 == r1 else read_json(OUT / f"gates_{r2}.json")
    key1 = read_json(KEYS / f"key_{r1}.json")
    key2 = key1 if r2 == r1 else read_json(KEYS / f"key_{r2}.json")
    G2 = g1src.get("G2", {})
    G2b = g2src.get("G2b", {})
    G3 = (g2src.get("G3") or {}).get("S2", {})
    res["gates"].update({"G2": G2, "G2b": G2b, "G3_S2": G3, "G3_S1": (g1src.get("G3") or {}).get("S1")})
    meas_ok = bool(G2.get("pass")) and bool(G2b.get("pass")) and bool(G3.get("pass"))
    pending = []
    if not G2.get("pass") and not key1.get("f2"):
        pending.append("G2 failed: run the F2 round (bundle --f2), then gates for it")
    if not G2b.get("pass") and not key2.get("f2"):
        pending.append("G2b failed: the F2 re-run applies to S2 (bundle --f2), then gates for it")
    if not G3.get("pass") and not key2.get("s2_full"):
        pending.append("G3 failed for S2: F4 (fetch --s2-full, crops --s2-full, new S2 round)")
    heartbeat("k0", 1, 6)

    # §5.3 attenuation (synthetic, independent of labels)
    synth_path = ALIGNED / f"synth_{r1}.json"
    res["attenuation"] = attenuation(read_json(synth_path)) if synth_path.exists() else None

    verdict, reading, row = None, None, None
    if pending:
        res["pending"] = pending
        verdict = "PENDING"
    elif not meas_ok:
        verdict = "INCONCLUSIVE"
        failed = [g for g, ok in (("G2", G2.get("pass")), ("G2b", G2b.get("pass")), ("G3", G3.get("pass"))) if not ok]
        res["failed_gates"] = failed
        if "G2" in failed:
            res["notes"].append("no blind measurer of cuneiform layout at this precision (F2)")
        dpath = ALIGNED / f"dencker_{r1}.json"
        if dpath.exists():
            res["S1_dencker_record_only"] = score_lines(read_json(dpath)["lines"], "A", "spline")
            res["S1_dencker_record_only"]["note"] = "record-only, description (D5); Dencker boxes are not blind"
    if verdict is None:
        # model choice: §5.2 synthetic check and §5.4 pseudo-boundary test; F3 on failure of either
        sc = read_json(OUT / "synth_check.json")
        ps = read_json(OUT / f"pseudo_{r1}.json")["results"]
        res["synth_check"] = {"spline": sc.get("pass")}
        if sc.get("pass") and ps["spline"]["pass"]:
            model = "spline"
        else:
            f3p = OUT / "synth_check_f3.json"
            if not f3p.exists():
                res["pending"] = ["F3 triggered (§5.2 or §5.4 failed under the spline): run synth.py check --f3"]
                verdict = "PENDING"
                model = None
            else:
                sc3 = read_json(f3p)
                res["synth_check"]["f3"] = sc3.get("pass")
                if sc3.get("pass") and ps["f3"]["pass"]:
                    model = "f3"
                else:
                    verdict = "INVALID"
                    model = None
                    res["notes"].append("F3 re-run failed: the design is INVALID and stops (§7 F3)")
        res["pseudo"] = ps
        res["model"] = model
    heartbeat("k0", 2, 6)
    if verdict is None:
        j1 = read_json(ALIGNED / f"joined_{r1}.json")
        j2 = j1 if r2 == r1 else read_json(ALIGNED / f"joined_{r2}.json")
        g1 = {"S1": j1["G1"]["S1"], "S2": j2["G1"]["S2"]}
        res["gates"]["G1"] = g1
        per = {}
        for script, src in (("S1", j1), ("S2", j2)):
            lines = src["scripts"][script]["lines"]
            if g1[script]["fail_F1"]:
                per[script] = {"status": "INCONCLUSIVE", "reason": "G1 failed (F1): script not scored"}
                continue
            meta = {}
            if script == "S2":
                lines, meta = apply_cluster_rule(lines)
            sc_ = {}
            for k_, rater in enumerate(("A", "B", "mean")):
                sc_[rater] = score_lines(lines, rater, model)
                heartbeat(f"k0_{script}", k_ + 1, 3)
            a = sc_["A"]
            crit = {"a_auc_ge_0.65": _ge(a.get("auc"), 0.65), "b_lo_ge_0.58": _ge(a.get("ci_lo"), 0.58),
                    "c_p_lt_0.01": a.get("p_null") is not None and a["p_null"] < 0.01,
                    "d_lo_ge_0.55": _ge(a.get("d_ci_lo"), 0.55)}
            # PREREG-AMBIGUITY: "FAIL ... with the measurement gates (G1, G2, G2b, G3) passed" is read as this
            # script's G1 (it is scored, so it passed) plus G2, G2b and G3 (meas_ok, always true on this branch).
            if all(crit.values()):
                status = "PASS"
            elif a.get("ci_hi") is not None and np.isfinite(a["ci_hi"]) and a["ci_hi"] < 0.65 and meas_ok:
                status = "FAIL"
            else:
                status = "INCONCLUSIVE"
            per[script] = {"status": status, "criteria": crit, "cluster": meta, "raters": sc_}
        res["scripts"] = per
        st = [per["S1"]["status"], per["S2"]["status"]]
        if st == ["PASS", "PASS"]:
            verdict = "PASS"
        elif "FAIL" in st:
            verdict = "FAIL"
        else:
            verdict = "INCONCLUSIVE"
        if sorted(st) == ["FAIL", "PASS"]:
            row = "PASS in one, FAIL in the other"
            reading = READING_SPLIT + " " + CONSEQ_SPLIT
        elif st == ["PASS", "PASS"]:
            row = "PASS in both"
            a1 = per["S1"]["raters"]["A"]["auc"]
            a2 = per["S2"]["raters"]["A"]["auc"]
            reading = READING_PASS.replace("(AUC a, b)", f"(AUC {a1:.3f}, {a2:.3f})") + " " + READING_PASS_ADD + \
                " " + CONSEQ_PASS
        elif "FAIL" in st:
            row = "FAIL (both scripts, or one FAIL with the other INCONCLUSIVE)"
            att = (res.get("attenuation") or {}).get("ratio")
            reading = READING_FAIL + f" Attenuation ratio (§5.3): {att if att is None else round(att, 3)}."
            if att is not None and att < 0.5:
                reading += " " + READING_FAIL_ADD[0].upper() + READING_FAIL_ADD[1:] + "."
            reading += " " + CONSEQ_FAIL
    heartbeat("k0", 5, 6)
    if verdict in ("INCONCLUSIVE",) and reading is None:
        row = "INCONCLUSIVE"
        why = res.get("failed_gates") or [f"{s}: {v['status']}" for s, v in (res.get("scripts") or {}).items()]
        reading = READING_INC + f" Failed gate or interval: {why}. " + CONSEQ_INC
    if verdict == "INVALID":
        row = "INVALID"
        reading = "Design INVALID (§7 F3). No verdict."
    res["verdict"] = verdict
    res["reading_row"] = row
    res["reading"] = (reading + " " + READING_ALL) if reading else None
    write_json(OUT / f"k0_{r1}.json", res)
    with open(OUT / f"k0_{r1}.out", "w", encoding="utf-8") as f:
        f.write(render_out(res))
    heartbeat("k0", 6, 6)
    print(render_out(res))


def _fmt(x, nd=3):
    if x is None:
        return "NA"
    if isinstance(x, float):
        return "NA" if not np.isfinite(x) else f"{x:.{nd}f}"
    return str(x)


def render_out(res):
    L = ["layout_word_division K0", f"rounds: S1={res['round_S1']} S2={res['round_S2']}  utc {res['utc']}",
         f"prereg sha256 {res['seal']['prereg_sha256']}", ""]
    g = res["gates"]
    if g.get("G2"):
        G2 = g["G2"]
        L.append(f"G2: pass={G2.get('pass')} recall A={_fmt(G2['recall']['A'])} B={_fmt(G2['recall']['B'])} "
                 f"ICC(2,1) gold A={_fmt(G2['icc_gold']['A'])} B={_fmt(G2['icc_gold']['B'])} "
                 f"A-B={_fmt(G2['icc_AB'])} gold pairs={G2.get('gold_pairs_available')} used={G2['n_used']}")
    if g.get("G2b"):
        L.append(f"G2b: pass={g['G2b'].get('pass')} ICC A-B={_fmt(g['G2b'].get('icc_AB'))} n={g['G2b'].get('n_gaps')}")
    if g.get("G3_S2"):
        L.append(f"G3 S2: pass={g['G3_S2'].get('pass')} median A={_fmt(g['G3_S2'].get('median_A_given_px'), 1)} px")
    if g.get("G1"):
        for s, v in g["G1"].items():
            L.append(f"G1 {s}: drop rate={_fmt(v['drop_rate'])} joined={v['joined']}/{v['clean_lines']} F1={v['fail_F1']}")
    if res.get("model"):
        L.append(f"residual model: {res['model']}")
    if res.get("pseudo"):
        for m, v in res["pseudo"].items():
            L.append(f"§5.4 [{m}]: AUC delta0={_fmt(v['auc_delta0'])} shift0.10H={_fmt(v['auc_shift_0.10H'])} pass={v['pass']}")
    att = res.get("attenuation")
    if att:
        L.append(f"§5.3 attenuation ratio={_fmt(att.get('ratio'))} (0.10: {att.get('0.10')})")
    for s, v in (res.get("scripts") or {}).items():
        L.append("")
        L.append(f"{s}: {v['status']}" + (f" ({v.get('reason')})" if v.get("reason") else ""))
        for r, x in (v.get("raters") or {}).items():
            L.append(f"  rater {r}: AUC={_fmt(x.get('auc'))} 95% [{_fmt(x.get('ci_lo'))}, {_fmt(x.get('ci_hi'))}] "
                     f"p={_fmt(x.get('p_null'), 4)} (d) AUC={_fmt(x.get('d_auc'))} lo={_fmt(x.get('d_ci_lo'))} "
                     f"lines={x.get('n_lines')} gaps={x.get('n_gaps')} boundaries={x.get('n_boundary')}")
        if v.get("criteria"):
            L.append(f"  criteria (rater A): {v['criteria']}")
    if res.get("S1_dencker_record_only"):
        d = res["S1_dencker_record_only"]
        L.append(f"S1 Dencker AUC (record-only): {_fmt(d.get('auc'))} [{_fmt(d.get('ci_lo'))}, {_fmt(d.get('ci_hi'))}]")
    if res.get("pending"):
        L.append("PENDING: " + "; ".join(res["pending"]))
    for n in res.get("notes", []):
        L.append("note: " + n)
    L += ["", f"VERDICT: {res['verdict']}", f"reading row: {res.get('reading_row')}", f"reading: {res.get('reading')}", ""]
    return "\n".join(L)


# ----------------------------------------------------------------------------------------------------------------
# selftest (generated numbers only)
# ----------------------------------------------------------------------------------------------------------------


def cmd_selftest(args):
    info = seal_check([Path(__file__).resolve()])
    rng = np.random.default_rng(12345)
    checks = {}

    # 1. natural spline: 4 columns, linear beyond the boundary knots, full column rank with the intercept
    x = np.linspace(0, 1, 101)
    Bm = ns_basis(x)
    ext = ns_basis(np.array([1.1, 1.2, 1.3, 1.4]))
    lo = ns_basis(np.array([-0.4, -0.3, -0.2, -0.1]))
    checks["spline_shape"] = Bm.shape == (101, 4)
    checks["spline_linear_outside"] = bool(np.allclose(np.diff(ext, 2, axis=0), 0, atol=1e-9)
                                           and np.allclose(np.diff(lo, 2, axis=0), 0, atol=1e-9))
    checks["spline_rank"] = int(np.linalg.matrix_rank(np.column_stack([np.ones(101), Bm]))) == 5

    # 2. exact AUC equals the rank form, with ties
    lines_R, lines_y, ptr = [], [], [0]
    for _ in range(50):
        m = int(rng.integers(3, 12))
        r = np.round(rng.normal(size=m), 1)
        y = rng.random(m) < 0.4
        lines_R.append(r); lines_y.append(y); ptr.append(ptr[-1] + m)
    R = np.concatenate(lines_R); Y = np.concatenate(lines_y); ptr = np.asarray(ptr)
    num, den = per_line_counts(R, Y, ptr)
    obs, p, null = shuffle_null(R, Y, ptr, n_shuf=200, seed=1)
    checks["auc_exact_equals_rank"] = bool(abs(auc_of(num, den) - obs) < 1e-12)
    # brute force over pooled pairs
    tot = 0.0; cnt = 0
    for l in range(len(ptr) - 1):
        r, y = R[ptr[l]:ptr[l + 1]], Y[ptr[l]:ptr[l + 1]]
        for b in r[y]:
            for n_ in r[~y]:
                tot += 1.0 if b > n_ else (0.5 if b == n_ else 0.0); cnt += 1
    checks["auc_bruteforce"] = bool(cnt > 0 and abs(tot / cnt - auc_of(num, den)) < 1e-12)
    checks["null_p_range"] = bool(1 / 201 <= p <= 1.0)
    # null mean near 0.5 when labels are random
    checks["null_centred"] = bool(abs(null.mean() - 0.5) < 0.05)

    # 3. ICC(2,1) on the Shrout & Fleiss (1979) example: 0.29
    SF = [[9, 2, 5, 8], [6, 1, 3, 2], [8, 4, 6, 8], [7, 1, 2, 6], [10, 5, 6, 9], [6, 2, 4, 7]]
    checks["icc_shrout_fleiss"] = bool(abs(icc21(SF) - 0.29) < 0.005)
    checks["icc_identical_is_1"] = bool(abs(icc21([[a, a] for a in rng.normal(size=30)]) - 1.0) < 1e-12)

    # 4. Huber IRLS: recovers coefficients under 5% gross outliers, converges
    Xh = np.column_stack([np.ones(400), rng.normal(size=400), rng.normal(size=400)])
    bt = np.array([0.1, 0.5, -0.3])
    yh = Xh @ bt + rng.normal(scale=0.05, size=400)
    yh[:20] += 5.0
    fit = huber_fit(Xh, yh)
    checks["huber_converged"] = bool(fit["converged"] and fit["iterations"] <= IRLS_MAXIT)
    checks["huber_robust"] = bool(np.max(np.abs(fit["beta"] - bt)) < 0.05)

    # 5. geometry: back-mapping round trip; line frame on a tilted line
    Wc, Hc = 640.0, 480.0
    boxes = [[[10, 20, 60, 80], [70, 22, 110, 79]], [[15, 120, 50, 170]]]
    given = [[[Wc - b[2], Hc - b[3], Wc - b[0], Hc - b[1]] for b in ln[::-1]] for ln in boxes[::-1]]
    given2 = [[[2 * v for v in b] for b in ln] for ln in given]
    back = unmap_lines(given2, Wc, Hc, 2.0, True)
    checks["unmap_roundtrip"] = bool(np.allclose(np.array(back[0]), np.array(boxes[0]))
                                     and np.allclose(np.array(back[1]), np.array(boxes[1])))
    f = line_features([[0, 0, 50, 50], [60, 0, 100, 50], [105, 0, 150, 50], [170, 0, 200, 50]])
    checks["gaps_flat"] = bool(np.allclose(f["g"], [10, 5, 20]) and abs(f["H"] - 50) < 1e-12
                               and np.allclose(f["p"], [0, 1 / 3, 2 / 3]))
    th = math.radians(8.0)
    cx = np.array([25.0, 100.0, 175.0, 250.0])
    cy = 100 + np.tan(th) * cx
    tb = [[a - 20, b - 20, a + 20, b + 20] for a, b in zip(cx, cy)]
    f2 = line_features(tb)
    checks["frame_angle"] = bool(abs(f2["theta"] - th) < 1e-9)

    # 6. end to end on generated gaps: delta = 0 near 0.5, planted delta high; bootstrap reproducible
    def gen(delta, nl, seed):
        g = np.random.default_rng(seed)
        out = []
        for li in range(nl):
            wl = g.integers(1, 5, size=int(g.integers(2, 6)))
            n = int(wl.sum())
            if n < 3:
                continue
            lab = []
            for wi, w in enumerate(wl):
                lab += [False] * (int(w) - 1) + ([True] if wi < len(wl) - 1 else [])
            x, bx = 0.0, []
            for i in range(n):
                w = 50 * g.uniform(0.8, 1.6)
                bx.append([x, 0.0, x + w, 50.0])
                if i < n - 1:
                    x += w + 50 * (max(-0.15, g.normal(0.10, 0.08)) + delta * lab[i])
            out.append({"boxes": {"T": bx}, "labels": lab, "cluster": str(li // 8), "tablet": str(li // 8)})
        return out
    s0 = score_lines(gen(0.0, 400, 7), "T", "spline", with_ci=True, with_null=True)
    s2 = score_lines(gen(0.2, 400, 7), "T", "spline", with_ci=True, with_null=False)
    s2b = score_lines(gen(0.2, 400, 7), "T", "spline", with_ci=True, with_null=False)
    s3 = score_lines(gen(0.0, 400, 7), "T", "f3", with_ci=False, with_null=False)
    checks["e2e_null_near_half"] = bool(abs(s0["auc"] - 0.5) < 0.05)
    checks["e2e_planted_high"] = bool(s2["auc"] > 0.8)
    checks["e2e_boot_reproducible"] = bool(s2["ci_lo"] == s2b["ci_lo"] and s2["ci_hi"] == s2b["ci_hi"])
    checks["e2e_f3_runs"] = bool(s3["auc"] is not None and abs(s3["auc"] - 0.5) < 0.05)

    # 7. LCS gold matching on a toy line
    m = lcs_match([5, 7, 0, 9, 11], [5, 7, 8, 9, 11])
    checks["lcs"] = m == [(0, 0), (1, 1), (3, 3), (4, 4)]
    face = [{"mzl": 5, "bbox": [0, 0, 10, 10]}, {"mzl": 7, "bbox": [12, 0, 22, 10]}, {"mzl": 9, "bbox": [30, 0, 40, 10]}]
    pr, _ = gold_pairs_face(face, {0: [(0, 5), (50, 5)]}, {0: [5, 7, 8, 9]})
    checks["gold_pairs_toy"] = len(pr) == 1 and pr[0]["b0"] == 0 and pr[0]["b1"] == 1 and abs(pr[0]["gold_g"] - 2) < 1e-9

    # 8. IoU / Hungarian
    hp = hungarian_pairs([[0, 0, 10, 10], [20, 0, 30, 10]], [[21, 0, 31, 10], [1, 0, 11, 10]], 0.3)
    checks["hungarian"] = sorted((a, b) for a, b, _ in hp) == [(0, 1), (1, 0)]

    ok = all(checks.values())
    write_json(OUT / "selftest.json", {"utc": utc(), "seal": info, "checks": checks, "pass": ok})
    for k, v in checks.items():
        print(("ok  " if v else "FAIL"), k)
    print("SELFTEST", "PASS" if ok else "FAIL")
    sys.exit(0 if ok else 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("selftest")
    for nm in ("gates", "pseudo"):
        s = sub.add_parser(nm)
        s.add_argument("--round", required=True)
    s = sub.add_parser("k0")
    s.add_argument("--round", required=True, help="round whose S1 data (and S2, unless --s2-round) are scored")
    s.add_argument("--s2-round", default=None, help="round holding the S2 boxes when F4 re-ran S2 alone")
    args = ap.parse_args()
    {"selftest": cmd_selftest, "gates": cmd_gates, "pseudo": cmd_pseudo, "k0": cmd_k0}[args.cmd](args)


if __name__ == "__main__":
    main()
