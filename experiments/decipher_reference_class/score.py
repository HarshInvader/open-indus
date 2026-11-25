"""Decipherment reference class: quotation check, agreement, majority table and readouts.

Sealed prereg: docs/prereg/decipher_reference_class.md (v2). This script follows it; every
choice the prereg leaves open is marked PREREG-AMBIGUITY and written into scores.json.

DO NOT RUN until the coder CSVs exist. It was compile-checked only when written.

Step 1, after coders 1 and 2:
  python3 -I experiments/decipher_reference_class/score.py agree PACKET_DIR
    reads   codes_coder1.csv, codes_coder2.csv (in this folder), PACKET_DIR/texts/*.txt
    writes  third_coder_cells.csv, scores.json (agreement part only)
Step 2, after coder 3 has coded the cells in third_coder_cells.csv:
  python3 -I experiments/decipher_reference_class/score.py final PACKET_DIR
    reads   the same, plus codes_coder3.csv (not needed if no cell differs)
    writes  table_majority.csv, scores.json, RESULTS_TABLE.csv

PACKET_DIR is the directory build_packets.py wrote to (outside the repo). Its texts are
checked against packets.sha256 first.

Coder CSV columns: row_id, script, LANG_PRIOR, LANG_HIND, ANCHOR, VALUES, WORDDIV, CORPUS,
<feature>_quote for each of the six, and an optional notes column. Coder 3 fills only the
cells listed in third_coder_cells.csv (code and quote) and leaves the others empty.

Exit: 0 = done, 2 = prereg or text hash mismatch, 3 = bad or missing input.
Standard library only, no network.
"""
import csv
import hashlib
import json
import math
import os
import sys
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)  # python -I leaves the script folder off the path
from build_packets import ROWS, FEATURES, text_names  # noqa: E402

PREREG_REL = "docs/prereg/decipher_reference_class.md"
HASHES_REL = "docs/prereg/HASHES.txt"
SHA_FILE = os.path.join(HERE, "packets.sha256")

ROW_IDS = [r["row_id"] for r in ROWS]
SET_OF = {r["row_id"]: r["set"] for r in ROWS}
NAME = {r["row_id"]: r["script"] for r in ROWS}
D1 = [r["row_id"] for r in ROWS if r["set"] == "D1"]
D2 = [r["row_id"] for r in ROWS if r["set"] == "D2"]
U = [r["row_id"] for r in ROWS if r["set"] == "U"]
C = [r["row_id"] for r in ROWS if r["set"] == "C"]
INDUS = [r["row_id"] for r in ROWS if r["set"] == "TARGET"][0]
D1_NUM = {r["num"]: r["row_id"] for r in ROWS if r["set"] == "D1"}

# ---- numbers and wordings frozen by the prereg ------------------------------------------
KAPPA_BAR = 0.8
RAW_BAR = 0.90
RARE_N = 5
BAR_D1 = 24            # 90% of 26
BAR_D1_D2 = 27         # 30 rows
VALID = {"LANG_PRIOR": ["0", "1"], "LANG_HIND": ["0", "1"], "ANCHOR": ["0", "1", "2"],
         "VALUES": ["0", "1", "2"], "WORDDIV": ["0", "1", "2"], "CORPUS": ["A", "B", "C", "D"]}
ORDERED = ["ANCHOR", "VALUES", "WORDDIV", "CORPUS"]
RULE_FEATURES = ["LANG_PRIOR", "ANCHOR", "VALUES", "WORDDIV"]
INDUS_STATED = {"LANG_PRIOR": "0", "ANCHOR": "0", "VALUES": "0", "WORDDIV": "0", "CORPUS": "C"}
FAMILIES = {"Egyptian": [4, 6], "cuneiform": [7, 12, 18],
            "Aramaic-derived and its neighbours": [1, 2, 3, 10], "Indic": [8, 9]}

R1_READING = {
    "PASS": "The rule holds for the listed decipherments. The project may say: \"every listed "
            "decipherment but k had outside names or values, or a known language with word "
            "division\". The misses are named. See readout 1b for the project's own sentence.",
    "MISS": "The sentence \"Every past decipherment rested on names fixed from outside the "
            "texts plus a known language\" is withdrawn from `docs/RESEARCH_STATE.md`, the "
            "briefs' standing text and the site. It is replaced by the measured count and the "
            "list of misses. \"Only a digraphic find changes the odds\" is flagged as "
            "unsupported until each miss is read in a primary source.",
    "INCONCLUSIVE": "The sentence is marked \"not checked: the accounts do not settle it\" "
                    "wherever it stands. The rows that decide it are listed.",
}
R1B_READING = {"STANDS": "The sentence stands as written.",
               "REPLACED": "The sentence is replaced by the rule's wording."}
R1C_READING = {
    "SEPARATES": "The rule separates read from unread scripts in this list.",
    "WEAK": "The rule separates weakly.",
    "NONE": "The rule does not separate. Having these features is common among unread scripts "
            "too, so the rule is at most a necessary condition.",
}
R2_READING = {
    "NOT_READ": "Indus's profile is not seen among the 26 listed decipherments. k_U unread "
                "scripts share it, and they are named. With 0 of 26, the upper 95% limit on "
                "the share of listed decipherments that came from this profile is 10.9% (exact "
                "binomial, one-sided).",
    "NO_CLASS": "No listed script, read or unread, has Indus's profile. The outside view has "
                "no reference class for Indus and the project says so.",
    "READ": "Indus's profile has been read k_D times. Those scripts are named. Each is then "
            "read in a primary source to learn how, as a new study. \"Only a digraphic find "
            "changes the odds\" is withdrawn until that is done.",
}

AMBIGUITIES = []


def amb(text):
    if text not in AMBIGUITIES:
        AMBIGUITIES.append(text)


def stop(code, msg):
    print(msg)
    sys.exit(code)


def sha_file(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def check_prereg():
    digest = sha_file(os.path.join(ROOT, PREREG_REL))
    sealed = None
    with open(os.path.join(ROOT, HASHES_REL), encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == PREREG_REL:
                sealed = parts[0]
    if sealed != digest:
        stop(2, "prereg hash mismatch")


# ---- saved texts and the quotation check ------------------------------------------------
def norm(s):
    # PREREG-AMBIGUITY: "each quotation must be found in the saved account text" does not say
    # how exact the match is. Used: Unicode NFC, runs of whitespace as one space, and
    # quotation marks wrapped around the whole quote removed. Case, punctuation and every
    # other character must match. No fuzzy matching.
    s = unicodedata.normalize("NFC", s).replace(" ", " ")
    s = " ".join(s.split())
    while len(s) >= 2 and s[0] in "\"'“‘" and s[-1] in "\"'”’":
        s = s[1:-1].strip()
    return s


def load_texts(packet_dir):
    want = {}
    with open(SHA_FILE, encoding="utf-8") as f:
        for line in f:
            if line.startswith("#") or not line.strip():
                continue
            parts = line.split()
            want[parts[1]] = parts[0]
    texts = {}
    for row in ROWS:
        chunks = []
        for stem in text_names(row):
            rel = "texts/%s.txt" % stem
            path = os.path.join(packet_dir, "texts", stem + ".txt")
            if rel not in want or not os.path.exists(path):
                stop(3, "saved text missing: %s" % rel)
            if sha_file(path) != want[rel]:
                stop(2, "saved text does not match packets.sha256: %s" % rel)
            with open(path, encoding="utf-8") as f:
                chunks.append(norm(f.read()))
        texts[row["row_id"]] = chunks
    return texts


def read_codes(name, texts, cells=None):
    """Read one coder CSV, validate it and apply the mechanical quotation check.

    cells: for coder 3, the set of (row_id, feature) to read; everything else is ignored.
    Returns (table, log). table[row_id][feature] is a code string.
    """
    path = os.path.join(HERE, "codes_%s.csv" % name)
    if not os.path.exists(path):
        stop(3, "missing codes_%s.csv" % name)
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    need = ["row_id"] + FEATURES + [x + "_quote" for x in FEATURES]
    if not rows or any(c not in rows[0] for c in need):
        stop(3, "codes_%s.csv: missing columns" % name)
    seen = {}
    for r in rows:
        rid = (r["row_id"] or "").strip()
        if rid not in SET_OF or rid in seen:
            stop(3, "codes_%s.csv: unknown or repeated row_id %r" % (name, rid))
        seen[rid] = r
    table, log = {}, []
    for rid in ROW_IDS:
        table[rid] = {}
        for feat in FEATURES:
            if cells is not None and (rid, feat) not in cells:
                continue
            if rid not in seen:
                stop(3, "codes_%s.csv: row %s is missing" % (name, rid))
            code = (seen[rid][feat] or "").strip().upper()
            quote = norm(seen[rid][feat + "_quote"] or "")
            hind_na = feat == "LANG_HIND" and SET_OF[rid] not in ("D1", "D2")
            if hind_na:
                if code not in ("NA", ""):
                    log.append({"coder": name, "row_id": rid, "feature": feat, "given": code,
                                "set_to": "NA", "why": "LANG_HIND is NA outside D1 and D2"})
                table[rid][feat] = "NA"
                continue
            if code == "NA":
                # PREREG-AMBIGUITY: a coder who writes NA for LANG_HIND on a D1 or D2 row has
                # given no code. Treated as NS, and logged.
                amb("LANG_HIND given as NA on a D1/D2 row is treated as NS.")
                log.append({"coder": name, "row_id": rid, "feature": feat, "given": "NA",
                            "set_to": "NS", "why": "NA on a row where LANG_HIND is coded"})
                code = "NS"
            if code != "NS" and code not in VALID[feat]:
                stop(3, "codes_%s.csv: %s %s has invalid code %r" % (name, rid, feat, code))
            if code != "NS":
                # PREREG-AMBIGUITY: "Every code needs one quoted sentence", yet NS means the
                # accounts do not say. NS (and NA) therefore need no quotation. The prereg sets
                # no minimum length for a quotation, so none is enforced; short ones are logged.
                if not quote or not any(quote in t for t in texts[rid]):
                    log.append({"coder": name, "row_id": rid, "feature": feat, "given": code,
                                "set_to": "NS",
                                "why": "quotation empty" if not quote else "quotation not found in the saved texts"})
                    code = "NS"
                elif len(quote) < 20:
                    log.append({"coder": name, "row_id": rid, "feature": feat, "given": code,
                                "set_to": code, "why": "quotation under 20 characters (kept)"})
            table[rid][feat] = code
    return table, log


# ---- agreement --------------------------------------------------------------------------
def collapse(feat, code):
    """The form the rule uses. NS stays a category of its own."""
    if code in ("NS", "NA"):
        return code
    if feat in ("ANCHOR", "VALUES"):
        return "1" if int(code) >= 1 else "0"
    if feat == "WORDDIV":
        return "1" if code == "2" else "0"
    if feat == "CORPUS":
        return "1" if code in ("C", "D") else "0"   # 1 = 10,000 or more
    # PREREG-AMBIGUITY: step 2 names a collapsed form for the four ordered features only.
    # LANG_PRIOR and LANG_HIND are already two-level, so their collapsed form is their full
    # form and step 2 repeats step 1 for them.
    return code


def kappa(a, b, dist):
    """Cohen's kappa as 1 - observed/expected disagreement. None if undefined."""
    n = len(a)
    cats = sorted(set(a) | set(b))
    pa = {c: a.count(c) / n for c in cats}
    pb = {c: b.count(c) / n for c in cats}
    obs = sum(dist(x, y) for x, y in zip(a, b)) / n
    exp = sum(pa[x] * pb[y] * dist(x, y) for x in cats for y in cats)
    if exp <= 1e-12:
        return None
    return 1.0 - obs / exp


def nominal(x, y):
    return 0.0 if x == y else 1.0


def linear_dist(feat):
    levels = VALID[feat]
    # PREREG-AMBIGUITY: linear weights are scaled by the codebook's number of levels (3 for
    # ANCHOR, VALUES and WORDDIV, 4 for CORPUS), not by the levels the coders happened to use.
    span = float(len(levels) - 1)

    def d(x, y):
        if x == y:
            return 0.0
        if x == "NS" or y == "NS":
            return 1.0          # NS is a full disagreement with any level
        return abs(levels.index(x) - levels.index(y)) / span
    return d


def agreement(t1, t2):
    out = {}
    for feat in FEATURES:
        rows = D1 + D2 if feat == "LANG_HIND" else ROW_IDS
        rows = [r for r in ROW_IDS if r in set(rows)]
        a = [t1[r][feat] for r in rows]
        b = [t2[r][feat] for r in rows]
        res = {"n_rows": len(rows), "weighted": feat in ORDERED}
        k_full = kappa(a, b, linear_dist(feat) if feat in ORDERED else nominal)
        res["kappa_full"] = k_full
        res["raw_agreement_full"] = sum(x == y for x, y in zip(a, b)) / len(rows)
        ca = [collapse(feat, x) for x in a]
        cb = [collapse(feat, x) for x in b]
        k_col = kappa(ca, cb, nominal)
        raw_col = sum(x == y for x, y in zip(ca, cb)) / len(rows)
        res["kappa_collapsed"] = k_col
        res["raw_agreement_collapsed"] = raw_col
        res["both_constant"] = len(set(a)) == 1 and len(set(b)) == 1
        # Step 3. PREREG-AMBIGUITY: "the smaller class" is not defined when the two coders
        # disagree on which class is smaller. Used: the collapsed class (0 or 1, never NS)
        # with fewer rows summed over both coders; a tie goes to class 1. "Either coder put
        # fewer than 5 rows" in it is tested per coder. If both coders are constant on the
        # same class, the smaller class is empty, no row is shared, and step 3 cannot pass.
        tot = {c: ca.count(c) + cb.count(c) for c in ("0", "1")}
        small = "1" if tot["1"] <= tot["0"] else "0"
        n_a, n_b = ca.count(small), cb.count(small)
        shared = sum(x == small and y == small for x, y in zip(ca, cb))
        res.update({"smaller_class": small, "smaller_class_rows": [n_a, n_b],
                    "smaller_class_shared_rows": shared})
        if k_full is not None and k_full >= KAPPA_BAR:
            res["status"] = "pass_full"
        elif k_col is not None and k_col >= KAPPA_BAR:
            res["status"] = "pass_collapsed_only"
        elif min(n_a, n_b) < RARE_N and shared >= 1 and raw_col >= RAW_BAR:
            res["status"] = "pass_rare_class_flagged"
        else:
            res["status"] = "fail"
        res["passed"] = res["status"] != "fail"
        out[feat] = res
    return out


def differing_cells(t1, t2):
    # PREREG-AMBIGUITY: the third coder gets "the cells where the two differ". Used: cells
    # that differ at full level after the quotation check, so a code turned to NS by the
    # check counts as differing from the other coder's code. Also: the prereg says the third
    # coder works "from the same packet" without saying which shuffle; that is the lead's call.
    cells = []
    for rid in ROW_IDS:
        for feat in FEATURES:
            if t1[rid][feat] != t2[rid][feat]:
                cells.append((rid, feat))
    return cells


def majority(t1, t2, t3, cells):
    # PREREG-AMBIGUITY: the vote is on full-level codes even for a feature that passed in
    # collapsed form only, so 1 / 2 / 0 is a three-way split (NS) although two of the three
    # agree on "at least 1".
    table = {}
    cellset = set(cells)
    for rid in ROW_IDS:
        table[rid] = {}
        for feat in FEATURES:
            a, b = t1[rid][feat], t2[rid][feat]
            if (rid, feat) not in cellset:
                table[rid][feat] = a
                continue
            c = t3[rid][feat]
            table[rid][feat] = c if c in (a, b) else "NS"   # three-way split is NS
    return table


# ---- the rule ---------------------------------------------------------------------------
def truth(code, test, helpful):
    """A cell's truth value; NS takes the helpful or the hurtful value."""
    if code in ("NS", "NA"):
        return helpful
    return test(code)


def fits(row, helpful, strict_values=False, lang="LANG_PRIOR"):
    a = truth(row["ANCHOR"], lambda c: int(c) >= 1, helpful)
    v = truth(row["VALUES"], (lambda c: c == "2") if strict_values else (lambda c: int(c) >= 1), helpful)
    lg = truth(row[lang], lambda c: c == "1", helpful)
    w = truth(row["WORDDIV"], lambda c: c == "2", helpful)
    return a or v or (lg and w)


def fits_sentence(row, helpful):
    return (truth(row["ANCHOR"], lambda c: int(c) >= 1, helpful)
            and truth(row["LANG_HIND"], lambda c: c == "1", helpful))


def count(table, rows, bar, fn=fits, **kw):
    best = [r for r in rows if fn(table[r], True, **kw)]
    worst = [r for r in rows if fn(table[r], False, **kw)]
    if len(best) >= bar and len(worst) >= bar:
        verdict = "PASS"
    elif len(best) < bar and len(worst) < bar:
        verdict = "MISS"
    else:
        verdict = "INCONCLUSIVE"
    return {"n": len(rows), "bar": bar, "fit_ns_helps": len(best), "fit_ns_hurts": len(worst),
            "verdict": verdict,
            "misses_under_both": [NAME[r] for r in rows if r not in best],
            "deciding_rows_ns": [NAME[r] for r in rows if r in best and r not in worst]}


def fisher_two_sided(a, b, c, d):
    """Two-sided Fisher exact p for the table [[a, b], [c, d]]."""
    n1, n2, k = a + b, c + d, a + c

    def p(x):
        return math.comb(n1, x) * math.comb(n2, k - x) / math.comb(n1 + n2, k)
    p0 = p(a)
    lo, hi = max(0, k - n2), min(k, n1)
    return min(1.0, sum(p(x) for x in range(lo, hi + 1) if p(x) <= p0 * (1 + 1e-9)))


def profile(row, feats):
    return tuple(collapse(f, row[f]) for f in feats)


def readouts(tm, t1, t2, agr):
    out = {}
    # ---- readout 1
    r1 = {"majority": count(tm, D1, BAR_D1)}
    failed = [f for f in RULE_FEATURES if not agr[f]["passed"]]
    verdict = r1["majority"]["verdict"]
    if failed:
        r1["coder1"] = count(t1, D1, BAR_D1)
        r1["coder2"] = count(t2, D1, BAR_D1)
        vs = {r1["majority"]["verdict"], r1["coder1"]["verdict"], r1["coder2"]["verdict"]}
        # PREREG-AMBIGUITY: "a verdict stands only if all three agree" is read as: the three
        # tables give the same verdict label (PASS, MISS or INCONCLUSIVE).
        verdict = verdict if len(vs) == 1 else "INCONCLUSIVE"
    r1.update({"rule_features_failing_agreement": failed, "verdict": verdict,
               "frozen_reading": R1_READING[verdict],
               "k_misses": [26 - r1["majority"]["fit_ns_helps"], 26 - r1["majority"]["fit_ns_hurts"]]})
    out["readout_1"] = r1

    # ---- readout 1b
    b = count(tm, D1, BAR_D1, fn=fits_sentence)
    r1b = {"count": b}
    if verdict != "PASS":
        r1b.update({"status": "count only (readout 1 is %s)" % verdict, "frozen_reading": None})
    elif not agr["LANG_HIND"]["passed"]:
        r1b.update({"status": "not reported as a verdict (LANG_HIND failed agreement)", "frozen_reading": None})
    elif b["verdict"] == "PASS":
        r1b.update({"status": "STANDS", "frozen_reading": R1B_READING["STANDS"]})
    elif b["verdict"] == "MISS":
        r1b.update({"status": "REPLACED", "frozen_reading": R1B_READING["REPLACED"]})
    else:
        # PREREG-AMBIGUITY: readout 1b has two rows (24 or more, 23 or fewer) and none for
        # the case where the two NS settings fall on opposite sides of 24. Reported as "not
        # settled", with no frozen reading. Readout 1b is taken from the majority table only,
        # also when ANCHOR failed agreement; the prereg sets no three-table rule for it.
        r1b.update({"status": "not settled (the NS settings straddle 24)", "frozen_reading": None})
    out["readout_1b"] = r1b

    # ---- readout 1c (NS set against fitting)
    u_fit = [r for r in U if fits(tm[r], False)]
    d_fit = [r for r in D1 if fits(tm[r], False)]
    key = "SEPARATES" if len(u_fit) <= 3 else ("WEAK" if len(u_fit) <= 7 else "NONE")
    # PREREG-AMBIGUITY: the Fisher p is "for D1 against U" with no NS setting and no sidedness
    # named. Used: NS set against fitting on both sides, two-sided. It decides nothing.
    out["readout_1c"] = {
        "u_fit": len(u_fit), "u_n": len(U), "u_fit_rows": [NAME[r] for r in u_fit],
        "frozen_reading": R1C_READING[key],
        "fisher_exact_p_two_sided": fisher_two_sided(len(d_fit), len(D1) - len(d_fit),
                                                     len(u_fit), len(U) - len(u_fit)),
        "d1_fit_ns_hurts": len(d_fit)}

    # ---- readout 2
    ind = dict(tm[INDUS])
    flags = []
    for f in RULE_FEATURES + ["CORPUS"]:
        if ind[f] == "NS":
            flags.append("%s is NS for Indus in the majority table; the project's stated value %s is used" % (f, INDUS_STATED[f]))
            ind[f] = INDUS_STATED[f]
    diffs = ["%s: coders %s, project %s" % (f, tm[INDUS][f], INDUS_STATED[f])
             for f in RULE_FEATURES + ["CORPUS"] if tm[INDUS][f] != INDUS_STATED[f]]

    def match(feats):
        target = profile(ind, feats)
        res = {"indus_profile": dict(zip(feats, target))}
        for label, rows in (("k_D", D1), ("k_U", U)):
            same, possible = [], []
            for r in rows:
                p = profile(tm[r], feats)
                if "NS" in p:
                    # PREREG-AMBIGUITY: "a row with NS on a core feature counts as a possible
                    # match". Listed as possible only if its stated features all equal
                    # Indus's; an NS row that already differs on a stated feature cannot match.
                    if all(x == "NS" or x == y for x, y in zip(p, target)):
                        possible.append(NAME[r])
                elif p == target:
                    same.append(NAME[r])
            res[label] = len(same)
            res[label + "_rows"] = same
            res[label + "_possible_matches"] = possible
        return res

    core = match(RULE_FEATURES)
    key = "READ" if core["k_D"] >= 1 else ("NOT_READ" if core["k_U"] >= 1 else "NO_CLASS")
    r2 = {"first_line": ("The coders' Indus row differs from the project's stated row: " + "; ".join(diffs))
          if diffs else "The coders' Indus row equals the project's stated row.",
          "indus_flags": flags, "core": core, "frozen_reading": R2_READING[key]}
    if agr["CORPUS"]["passed"]:
        # PREREG-AMBIGUITY: "the five-feature profile" does not say whether the corpus band
        # enters as A to D or as under/over 10,000. Used: the form the rule uses (under 10,000
        # against 10,000 or more), like the other four. A record, with no reading attached.
        r2["with_corpus_band"] = match(RULE_FEATURES + ["CORPUS"])
    else:
        r2["with_corpus_band"] = "not given: CORPUS failed its agreement bar"
    out["readout_2"] = r2

    # ---- sensitivity (record only)
    sens = {"d1_plus_d2": count(tm, D1 + D2, BAR_D1_D2)}
    # PREREG-AMBIGUITY: "each contested row counted as deciphered, then as undeciphered" gives
    # no bar and no count for the second half. Used: as deciphered, readout 1 on D1 plus that
    # row with the bar at 90% rounded up (25 of 27); as undeciphered, readout 1c on U plus
    # that row (15 rows, same cut points).
    cont = {}
    for r in C:
        rows = D1 + [r]
        uf = [x for x in U + [r] if fits(tm[x], False)]
        cont[NAME[r]] = {"as_deciphered": count(tm, rows, math.ceil(0.9 * len(rows))),
                         "as_undeciphered_u_fit": len(uf), "as_undeciphered_u_n": len(U) + 1}
    sens["contested"] = cont
    sens["values_equal_2"] = count(tm, D1, BAR_D1, strict_values=True)
    sens["lang_hind_for_lang_prior"] = count(tm, D1, BAR_D1, lang="LANG_HIND")
    grouped = set()
    groups = []
    for fam, nums in FAMILIES.items():
        groups.append((fam, [D1_NUM[n] for n in nums]))
        grouped.update(D1_NUM[n] for n in nums)
    groups += [(NAME[r], [r]) for r in D1 if r not in grouped]
    # PREREG-AMBIGUITY: the family row has no bar. Recorded: the number of the 19 groups that
    # fit under each NS setting; 90% of 19 rounded up is 18, shown for reference only.
    sens["by_family"] = {
        "groups": len(groups),
        "fit_ns_helps": sum(all(fits(tm[r], True) for r in rs) for _, rs in groups),
        "fit_ns_hurts": sum(all(fits(tm[r], False) for r in rs) for _, rs in groups),
        "reference_bar": math.ceil(0.9 * len(groups)),
        "groups_not_fitting_ns_hurts": [g for g, rs in groups if not all(fits(tm[r], False) for r in rs)]}
    loo = {}
    for label, helpful in (("ns_helps", True), ("ns_hurts", False)):
        c = sum(fits(tm[r], helpful) for r in D1)
        lo, hi = (c - 1 if c > 0 else c), (c + 1 if c < len(D1) else c)
        loo[label] = {"count": c, "lowest_if_one_row_flips": lo, "highest_if_one_row_flips": hi,
                      "side_of_bar_can_change": (lo >= BAR_D1) != (hi >= BAR_D1) or (lo >= BAR_D1) != (c >= BAR_D1)}
    sens["leave_one_out"] = loo
    out["sensitivity"] = sens
    return out


# ---- output -----------------------------------------------------------------------------
def write_csv(name, header, rows):
    with open(os.path.join(HERE, name), "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(header)
        w.writerows(rows)


def write_json(obj):
    obj["prereg_ambiguities"] = AMBIGUITIES + [
        "Quotation match: NFC, whitespace runs as one space, outer quotation marks removed; otherwise exact.",
        "NS and NA need no quotation; no minimum quotation length.",
        "LANG_PRIOR and LANG_HIND have no separate collapsed form; step 2 repeats step 1.",
        "Linear weights use the codebook's level count.",
        "Smaller class for step 3: pooled over both coders, 0 or 1 only, tie to class 1.",
        "Third-coder cells: full-level differences after the quotation check.",
        "Majority vote on full-level codes.",
        "Three-table rule read as equal verdict labels.",
        "Readout 1b: no reading when the NS settings straddle 24; majority table only.",
        "Fisher p: NS against fitting, two-sided.",
        "Possible matches: NS rows whose stated core features equal Indus's.",
        "Five-feature profile uses the corpus band collapsed at 10,000.",
        "Contested rows: bar 25 of 27 as deciphered; readout 1c on 15 rows as undeciphered.",
        "Family sensitivity has no bar; 18 of 19 shown for reference.",
        "T for rows off the timeline (in build_packets.py): date of the Wikipedia revision.",
        "Saved text (in build_packets.py): full rendered page without navigation boxes and footnote markers.",
    ]
    with open(os.path.join(HERE, "scores.json"), "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1, ensure_ascii=False, sort_keys=True)
        f.write("\n")


def results_table(agr, ro):
    rows = []
    for feat in FEATURES:
        a = agr[feat]
        rows.append(["agreement", feat, a["status"],
                     "kappa full %s; kappa collapsed %s; raw collapsed %.3f; rows %d" % (
                         a["kappa_full"], a["kappa_collapsed"], a["raw_agreement_collapsed"], a["n_rows"])])
    r1 = ro["readout_1"]
    for k in ("majority", "coder1", "coder2"):
        if k in r1:
            rows.append(["readout_1", k + " table", r1[k]["verdict"],
                         "fit %d (NS helps) / %d (NS hurts) of %d, bar %d; misses: %s" % (
                             r1[k]["fit_ns_helps"], r1[k]["fit_ns_hurts"], r1[k]["n"], r1[k]["bar"],
                             ", ".join(r1[k]["misses_under_both"]) or "none")])
    rows.append(["readout_1", "verdict", r1["verdict"], r1["frozen_reading"]])
    b = ro["readout_1b"]
    rows.append(["readout_1b", "sentence as written", b["status"],
                 "fit %d / %d of 26; %s" % (b["count"]["fit_ns_helps"], b["count"]["fit_ns_hurts"],
                                           b["frozen_reading"] or "no reading")])
    c = ro["readout_1c"]
    rows.append(["readout_1c", "U rows that fit", "%d of %d" % (c["u_fit"], c["u_n"]),
                 "%s Fisher p %.4g (decides nothing)" % (c["frozen_reading"], c["fisher_exact_p_two_sided"])])
    r2 = ro["readout_2"]
    rows.append(["readout_2", "first line", "", r2["first_line"]])
    rows.append(["readout_2", "core profile", "k_D %d, k_U %d" % (r2["core"]["k_D"], r2["core"]["k_U"]),
                 "%s Named D1: %s. Named U: %s. Possible matches: %s" % (
                     r2["frozen_reading"], ", ".join(r2["core"]["k_D_rows"]) or "none",
                     ", ".join(r2["core"]["k_U_rows"]) or "none",
                     ", ".join(r2["core"]["k_D_possible_matches"] + r2["core"]["k_U_possible_matches"]) or "none")])
    w = r2["with_corpus_band"]
    rows.append(["readout_2", "with corpus band",
                 w if isinstance(w, str) else "k_D %d, k_U %d" % (w["k_D"], w["k_U"]), "record only"])
    s = ro["sensitivity"]
    for label, key in (("D1 plus D2", "d1_plus_d2"), ("VALUES = 2", "values_equal_2"),
                       ("LANG_HIND for LANG_PRIOR", "lang_hind_for_lang_prior")):
        rows.append(["sensitivity", label, s[key]["verdict"],
                     "fit %d / %d of %d, bar %d; record only" % (
                         s[key]["fit_ns_helps"], s[key]["fit_ns_hurts"], s[key]["n"], s[key]["bar"])])
    for name, v in s["contested"].items():
        d = v["as_deciphered"]
        rows.append(["sensitivity", name + " as deciphered", d["verdict"],
                     "fit %d / %d of %d, bar %d; record only" % (d["fit_ns_helps"], d["fit_ns_hurts"], d["n"], d["bar"])])
        rows.append(["sensitivity", name + " as undeciphered",
                     "%d of %d U rows fit" % (v["as_undeciphered_u_fit"], v["as_undeciphered_u_n"]), "record only"])
    f = s["by_family"]
    rows.append(["sensitivity", "by family", "%d / %d of %d groups" % (f["fit_ns_helps"], f["fit_ns_hurts"], f["groups"]),
                 "not fitting: %s; record only" % (", ".join(f["groups_not_fitting_ns_hurts"]) or "none")])
    for label, v in s["leave_one_out"].items():
        rows.append(["sensitivity", "leave one out, " + label,
                     "%d to %d" % (v["lowest_if_one_row_flips"], v["highest_if_one_row_flips"]),
                     "count %d; side of the bar can change: %s; record only" % (v["count"], v["side_of_bar_can_change"])])
    write_csv("RESULTS_TABLE.csv", ["section", "item", "value", "note"], rows)


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("agree", "final"):
        stop(3, __doc__)
    check_prereg()
    texts = load_texts(sys.argv[2])
    t1, log1 = read_codes("coder1", texts)
    t2, log2 = read_codes("coder2", texts)
    agr = agreement(t1, t2)
    cells = differing_cells(t1, t2)
    result = {"stage": sys.argv[1], "agreement": agr, "quotation_check_log": log1 + log2,
              "third_coder_cells": len(cells)}
    if sys.argv[1] == "agree":
        # The list names cells only. It carries neither coder's code.
        write_csv("third_coder_cells.csv", ["row_id", "script", "feature"],
                  [[rid, NAME[rid], feat] for rid, feat in cells])
        write_json(result)
        print("agreement written; %d cells go to the third coder" % len(cells))
        return
    t3 = {rid: {} for rid in ROW_IDS}
    if cells:
        t3, log3 = read_codes("coder3", texts, cells=set(cells))
        result["quotation_check_log"] += log3
    tm = majority(t1, t2, t3, cells)
    write_csv("table_majority.csv",
              ["row_id", "script", "set"] + FEATURES + ["fits_rule_ns_helps", "fits_rule_ns_hurts"],
              [[rid, NAME[rid], SET_OF[rid]] + [tm[rid][f] for f in FEATURES]
               + [int(fits(tm[rid], True)), int(fits(tm[rid], False))] for rid in ROW_IDS])
    ro = readouts(tm, t1, t2, agr)
    result.update(ro)
    result["failure_effects"] = {
        "CORPUS": "passed" if agr["CORPUS"]["passed"] else "failed: readout 2 uses the four-feature profile only",
        "LANG_HIND": "passed" if agr["LANG_HIND"]["passed"] else "failed: readout 1b is not reported as a verdict",
        "rule_features": ro["readout_1"]["rule_features_failing_agreement"]}
    write_json(result)
    results_table(agr, ro)
    print("readout 1: %s" % ro["readout_1"]["verdict"])


if __name__ == "__main__":
    main()
