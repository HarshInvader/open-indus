"""Unread-sealer shortlist: rank sealed tablets whose seal legend nobody has read.

Sealed prereg: docs/prereg/unread_sealer_shortlist.md (v2). The section "Rules made exact at
review" overrides looser wording elsewhere in that file, and this script follows it.

Run: nice -n 20 python3 -I experiments/unread_sealer_shortlist/run.py
Reads  experiments/short_labels/raw/cdli/cdli_cat.csv and cdliatf_unblocked.atf (text only).
Writes experiments/unread_sealer_shortlist/kill.json, and shortlist.csv if the readings allow it.
Exit:  2 = prereg hash mismatch, 1 = planned stop (reading 1 or 4), 0 = otherwise.
Single process, standard library only, no network.
"""
import csv
import hashlib
import json
import os
import re
import sys
import unicodedata
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
RAW = os.path.join(ROOT, "experiments", "short_labels", "raw", "cdli")
PREREG_REL = "docs/prereg/unread_sealer_shortlist.md"
HASHES_REL = "docs/prereg/HASHES.txt"
KILL_JSON = os.path.join(HERE, "kill.json")
SHORTLIST = os.path.join(HERE, "shortlist.csv")

# ---- numbers fixed by the prereg -------------------------------------------------------
EXPECT_POOL_W = 1909
EXPECT_KISZIB = {"Ur III": 669, "EOB+OB": 62, "Old Assyrian": 32}
CUT = 95            # top 5% of 1,909, rounded down
F1_CAP = 150        # F1: a tie block at the cut is listed only up to 150 rows in all
K0A = "P306518"     # YBC 5447, the one true positive
K0B = "P453801"     # Nisaba 15 0371, the Ur III check
NOT_RANKED = "P516366"  # CUSAS 40 1582, no text on disk

FEATURES = ["site", "period", "seal_note", "gulf_word", "trade_word", "named_sealer"]

SITE_2 = {"Ur", "Larsa", "Irisagrig", "Irisaĝrig", "Susa", "Ešnunna"}
SITE_1 = {"Girsu"}

NOTE_0 = ("broken", "abraded", "seal of")
NOTE_2 = ("not given", "not copied", "to do")

# PREREG-AMBIGUITY: "a Meluhhan name" is not listed in the feature table; the three names are taken from the count-gate table.
GULF_WORDS = ["me-luh-ha", "dilmun", "tilmun", "ni-tuk{ki}", "ma2-gan",
              "na-na-sa3", "na-na-za", "sa6-ma-ar"]
TRADE_WORDS = ["dam-gar3", "kaskal", "nam-tab-ba", "tab-ba", "ga-esz8", "uruda", "zabar",
               "gug", "za-gin3"]

READING_TEXT = {
    1: "K0a fails. Stop. No list is written. Metadata does not put the one known Gulf-stamped "
       "tablet in the top 5% of unread sealed tablets.",
    2: "K0a passes and K0b passes. The list is the top 95 rows of pool W.",
    3: "K0a passes and K0b fails. The list holds only Early Old Babylonian and Old Babylonian "
       "rows from the top 95. Ur III rows are dropped.",
    4: "The recount differs by even one row. Stop and redraft. This is an integrity stop.",
}

# PREREG-AMBIGUITY: lines are tested as stored (only the line ending is removed); leading spaces are not stripped before "^".
NUMBERED = re.compile(r"^\d+[a-z']*\.")
DELETE = str.maketrans("", "", "[]#?!<>")
DETERMINATIVE = re.compile(r"\{[^}]*\}")


def to_signs(word):
    """Split one space-delimited word into its hyphen-joined signs."""
    # PREREG-AMBIGUITY: a determinative {x} is its own sign, so dilmun{ki} holds the sign dilmun and ni-tuk{ki} is ni, tuk, {ki}.
    # PREREG-AMBIGUITY: only the seven listed characters are deleted; case and the Akkadian logogram underscores are left as they are.
    word = DETERMINATIVE.sub(lambda m: "-" + m.group(0) + "-", word)
    return [s for s in word.split("-") if s]


GULF = [to_signs(w) for w in GULF_WORDS]
TRADE = [to_signs(w) for w in TRADE_WORDS]


def has_run(signs, target):
    """True if target is a contiguous run of whole signs inside one word."""
    # PREREG-AMBIGUITY: "a whole run of hyphen-joined signs" is read as a contiguous run inside a longer word, not the whole word (the e2-kiszib3-ba exception implies this).
    n = len(target)
    for i in range(len(signs) - n + 1):
        if signs[i:i + n] == target:
            return True
    return False


def sealer_hit(signs):
    """True if the word holds the sign kiszib or kiszib3, not as part of e2-kiszib3-ba."""
    for i, s in enumerate(signs):
        if s == "kiszib":
            return True
        if s == "kiszib3":
            if i > 0 and i + 1 < len(signs) and signs[i - 1] == "e2" and signs[i + 1] == "ba":
                continue
            return True
    return False


# ---- step 1: hash check ----------------------------------------------------------------
def check_hash():
    with open(os.path.join(ROOT, PREREG_REL), "rb") as f:
        got = hashlib.sha256(f.read()).hexdigest()
    want = None
    with open(os.path.join(ROOT, HASHES_REL), encoding="utf-8", errors="replace") as f:
        for line in f:
            parts = line.split()
            # PREREG-AMBIGUITY: if HASHES.txt ever holds more than one line for the prereg, the last one is taken as the sealed hash.
            if len(parts) >= 2 and parts[1] == PREREG_REL:
                want = parts[0]
    return got, want


# ---- loaders ---------------------------------------------------------------------------
def load_catalogue():
    """P-number -> catalogue row (only the columns used). Same keying as the existing loaders."""
    csv.field_size_limit(10 ** 9)
    keep = ("period", "provenience", "primary_publication", "photo_up", "lineart_up", "seal_id")
    cat = {}
    with open(os.path.join(RAW, "cdli_cat.csv"), encoding="utf-8", errors="replace", newline="") as f:
        for r in csv.DictReader(f):
            pid = (r.get("id_text") or "").strip()
            if pid.isdigit():
                # PREREG-AMBIGUITY: a P-number with several catalogue rows takes the last row, as the existing loaders do.
                cat["P" + pid.zfill(6)] = {k: (r.get(k) or "") for k in keep}
    return cat


def load_texts():
    """P-number -> {legend, notes, body} for every text block that has a seal section.

    Seal section: from an @seal line to the next @ line that is not @surface or @column.
    Legend line: a line in a seal section that matches ^\\d+[a-z']*\\.
    Notes: the $ and # lines inside seal sections, lowercased.
    Body: numbered lines outside seal sections, label removed, the characters [ ] # ? ! < > deleted.
    Duplicate P-number blocks: the last block wins.
    """
    texts = {}
    state = {"pid": None}

    def start(pid):
        state.update(pid=pid, in_seal=False, has_seal=False, legend=False, notes=[], body=[])

    def finish():
        pid = state["pid"]
        if pid is None:
            return
        if state["has_seal"]:
            texts[pid] = {"legend": state["legend"], "notes": state["notes"], "body": state["body"]}
        else:
            texts.pop(pid, None)   # the last block wins, even when it has no seal section

    with open(os.path.join(RAW, "cdliatf_unblocked.atf"), encoding="utf-8", errors="replace") as f:
        for line in f:
            line = line.rstrip("\r\n")
            if line.startswith("&"):
                finish()
                if re.match(r"^&P\d{6}", line):
                    start(line[1:8])
                else:
                    state["pid"] = None
                continue
            if state["pid"] is None or not line:
                continue
            if line.startswith("@"):
                parts = line.split()
                tag = parts[0] if parts else ""
                # PREREG-AMBIGUITY: "an @seal line" is a line whose first token is exactly "@seal" (so "@seal 1" counts and "@sealing" does not).
                if tag == "@seal":
                    state["in_seal"] = True
                    state["has_seal"] = True
                elif tag not in ("@surface", "@column"):
                    state["in_seal"] = False
                continue
            if state["in_seal"]:
                if NUMBERED.match(line):
                    state["legend"] = True
                elif line[0] in "$#":
                    state["notes"].append(line.lower())
            else:
                m = NUMBERED.match(line)
                # PREREG-AMBIGUITY: a "numbered line" of the body is one that matches the legend-line pattern.
                if m:
                    state["body"].append(line[m.end():].translate(DELETE))
        finish()
    return texts


# ---- feature rules ---------------------------------------------------------------------
def period_of(period):
    """Catalogue period by prefix; a trailing "?" counts as the period."""
    p = period.strip()
    for name in ("Ur III", "Early Old Babylonian", "Old Babylonian", "Old Assyrian"):
        if p.startswith(name):
            return name
    return None


def site_text(provenience):
    # PREREG-AMBIGUITY: both sides are put in Unicode NFC before the exact match, so Irisaĝrig and Ešnunna match however the catalogue encodes the accent.
    s = unicodedata.normalize("NFC", provenience).split("(", 1)[0].replace("?", "").strip()
    return s


def site_score(provenience):
    s = site_text(provenience)
    if s in SITE_2:
        return 2
    if s in SITE_1:
        return 1
    return 0


def note_score(notes):
    if not notes:
        return 1
    best = 0
    for n in notes:
        if any(k in n for k in NOTE_0):
            sc = 0
        elif any(k in n for k in NOTE_2):
            sc = 2
        else:
            sc = 1
        best = max(best, sc)
    return best


def body_features(body):
    """Return (gulf 0/2, trade 0/1, named sealer 0/1, name on the kiszib line)."""
    gulf = trade = sealer = 0
    name = ""
    for content in body:
        words = content.split()
        signs_per_word = [to_signs(w) for w in words]
        for i, signs in enumerate(signs_per_word):
            if not gulf and any(has_run(signs, t) for t in GULF):
                gulf = 2
            if not trade and any(has_run(signs, t) for t in TRADE):
                trade = 1
            if not sealer and sealer_hit(signs):
                sealer = 1
                # PREREG-AMBIGUITY: "the name on the kiszib line" is the rest of the first such line after the word that holds the sign, as written.
                name = " ".join(words[i + 1:])
    return gulf, trade, sealer, name


def kiszib_line(body):
    # PREREG-AMBIGUITY: brief 10's "body line containing kiszib" is a plain substring test on the cleaned numbered lines outside seal sections, case as written.
    return any("kiszib" in content for content in body)


def worst_case_ranks(totals):
    """rank = the number of pool rows that score the same or higher."""
    hist = Counter(totals.values())
    at_or_above = {}
    run = 0
    for score in sorted(hist, reverse=True):
        run += hist[score]
        at_or_above[score] = run
    return {pid: at_or_above[t] for pid, t in totals.items()}


def write_json(obj):
    with open(KILL_JSON, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")


def main():
    # ---- step 1 ------------------------------------------------------------------------
    got, want = check_hash()
    if want is None or got != want:
        print("prereg hash mismatch: file %s, HASHES line %s" % (got, want), file=sys.stderr)
        return 2

    cat = load_catalogue()
    texts = load_texts()

    # ---- step 2: recount, before any score ---------------------------------------------
    pool = []                                   # pool W, P-numbers
    period_name = {}
    kiszib_counts = {"Ur III": 0, "EOB+OB": 0, "Old Assyrian": 0}
    for pid in sorted(texts):
        t = texts[pid]
        if t["legend"] or pid not in cat:
            continue
        per = period_of(cat[pid]["period"])
        if per is None:
            continue
        group = "EOB+OB" if per in ("Early Old Babylonian", "Old Babylonian") else per
        if kiszib_line(t["body"]):
            kiszib_counts[group] += 1
        if per != "Old Assyrian":
            pool.append(pid)
            period_name[pid] = per
    pool_by_period = dict(Counter(period_name[p] for p in pool))
    counts = {
        "pool_W": len(pool),
        "pool_W_expected": EXPECT_POOL_W,
        "pool_W_by_period": pool_by_period,
        "brief10_kiszib_pools": kiszib_counts,
        "brief10_kiszib_pools_expected": EXPECT_KISZIB,
        "texts_with_seal_section_on_disk": len(texts),
    }
    if len(pool) != EXPECT_POOL_W or kiszib_counts != EXPECT_KISZIB:
        write_json({
            "status": "stop",
            "prereg_sha256": got,
            "counts": counts,
            "reading": 4,
            "reading_text": READING_TEXT[4],
        })
        print("recount differs: reading 4, integrity stop")
        return 1

    # ---- step 3: features, exactly as sealed -------------------------------------------
    scores = {}
    names = {}
    for pid in pool:
        t = texts[pid]
        gulf, trade, sealer, name = body_features(t["body"])
        scores[pid] = {
            "site": site_score(cat[pid]["provenience"]),
            "period": 1 if period_name[pid] in ("Ur III", "Early Old Babylonian") else 0,
            "seal_note": note_score(t["notes"]),
            "gulf_word": gulf,
            "trade_word": trade,
            "named_sealer": sealer,
        }
        names[pid] = name

    # ---- step 4: worst-case ranks ------------------------------------------------------
    total = {pid: sum(s.values()) for pid, s in scores.items()}
    rank = worst_case_ranks(total)
    total_nogulf = {pid: total[pid] - scores[pid]["gulf_word"] for pid in pool}
    rank_nogulf = worst_case_ranks(total_nogulf)

    # ---- steps 5 to 7: controls --------------------------------------------------------
    # PREREG-AMBIGUITY: a control that is missing from pool W cannot be ranked and counts as failing its bar.
    def control(pid, table_total, table_rank, zero_gulf):
        if pid not in scores:
            return {"p_number": pid, "in_pool_W": False, "scores": None, "total": None,
                    "worst_case_rank": None, "bar": CUT, "pass": False}
        sc = dict(scores[pid])
        if zero_gulf:
            sc["gulf_word"] = 0
        return {"p_number": pid, "in_pool_W": True, "scores": sc, "total": table_total[pid],
                "worst_case_rank": table_rank[pid], "bar": CUT, "pass": table_rank[pid] <= CUT}

    k0a = control(K0A, total, rank, False)
    k0b = control(K0B, total_nogulf, rank_nogulf, True)
    k0b["gulf_word_feature"] = "set to zero in every row"
    k0b["record_only_with_gulf_word_on"] = {
        "scores": dict(scores[K0B]) if K0B in scores else None,
        "total": total.get(K0B),
        "worst_case_rank": rank.get(K0B),
        "note": "for the record; decides nothing",
    }
    not_ranked = {"p_number": NOT_RANKED, "ranked": False,
                  "reason": "no text on disk; not ranked",
                  "text_block_with_seal_section_on_disk": NOT_RANKED in texts}

    # ---- step 8: dead features (F2) ----------------------------------------------------
    n = len(pool)
    feature_report = {}
    for feat in FEATURES:
        scored = sum(1 for pid in pool if scores[pid][feat] > 0)
        dead = None
        if scored == 0:
            dead = "scores no row"
        elif 2 * scored > n:
            dead = "scores more than half the pool"
        feature_report[feat] = {
            "rows_scored": scored,
            "by_points": {str(k): v for k, v in sorted(Counter(scores[p][feat] for p in pool).items())},
            "dead": dead is not None,
            "dead_reason": dead,
        }
    dead_features = [f for f in FEATURES if feature_report[f]["dead"]]

    # ---- step 9: readings and F1 -------------------------------------------------------
    if not k0a["pass"]:
        reading = 1
    elif k0b["pass"]:
        reading = 2
    else:
        reading = 3

    listed = []
    f1 = {"applied": False, "cut": CUT, "cap": F1_CAP}
    list_status = "no list (reading 1)"
    if reading in (2, 3):
        order = sorted(pool, key=lambda p: (-total[p], p))
        cut_score = total[order[CUT - 1]]
        block_end = sum(1 for p in pool if total[p] >= cut_score)   # worst-case rank of the tie block at the cut
        f1["tie_block_score"] = cut_score
        f1["tie_block_size"] = sum(1 for p in pool if total[p] == cut_score)
        f1["tie_block_worst_case_rank"] = block_end
        if block_end == CUT:
            listed = order[:CUT]
            f1["outcome"] = "the tie block ends at the cut; top 95 listed"
        elif block_end <= F1_CAP:
            listed = order[:block_end]
            f1["applied"] = True
            f1["outcome"] = "the tie block runs past the cut; the whole block is listed"
        else:
            listed = [p for p in order if total[p] > cut_score]
            f1["applied"] = True
            f1["outcome"] = "the tie block would pass 150 rows; the block is left out"
        f1["rows_after_F1"] = len(listed)
        if reading == 3:
            # PREREG-AMBIGUITY: F1 is applied to the whole pool first, then reading 3 drops the Ur III rows (the 150 cap is not re-applied after the drop).
            listed = [p for p in listed if period_name[p] != "Ur III"]
        list_status = "list written" if listed else "empty list"

    photo = [p for p in listed if cat[p]["photo_up"].strip()]
    no_photo = [p for p in listed if not cat[p]["photo_up"].strip()]

    # ---- step 10: kill.json ------------------------------------------------------------
    counts["score_histogram"] = {str(k): v for k, v in sorted(Counter(total.values()).items())}
    counts["score_histogram_gulf_word_zeroed"] = {
        str(k): v for k, v in sorted(Counter(total_nogulf.values()).items())}
    counts["pool_W_with_photo_flag"] = sum(1 for p in pool if cat[p]["photo_up"].strip())
    counts["pool_W_with_lineart_flag"] = sum(1 for p in pool if cat[p]["lineart_up"].strip())
    counts["pool_W_with_seal_id"] = sum(1 for p in pool if cat[p]["seal_id"].strip())
    counts["listed_rows"] = len(listed)
    counts["listed_rows_with_photo_flag"] = len(photo)
    counts["listed_rows_without_photo_flag"] = len(no_photo)
    counts["listed_rows_by_period"] = dict(Counter(period_name[p] for p in listed))
    write_json({
        "status": "done",
        "prereg": PREREG_REL,
        "prereg_sha256": got,
        "counts": counts,
        "features": feature_report,
        "dead_features_F2": dead_features,
        "controls": {"K0a": k0a, "K0b": k0b, "P516366": not_ranked},
        "F1": f1,
        "reading": reading,
        "reading_text": READING_TEXT[reading],
        "list_status": list_status,
    })

    # ---- step 11: shortlist.csv, only if the readings allow it -------------------------
    if listed:
        # PREREG-AMBIGUITY: "publication" is the catalogue's primary_publication, and "site" and "period" are the catalogue fields as written.
        # PREREG-AMBIGUITY: the two blocks share one file: rows with a photo flag first, then rows without; the photo_flag column marks the block.
        # PREREG-AMBIGUITY: the photo and line-art flags are written as 1 when the catalogue's photo_up / lineart_up field is not empty, else 0.
        cols = ["p_number", "cdli_link", "publication", "site", "period",
                "site_score", "period_score", "seal_note_score", "gulf_word_score",
                "trade_word_score", "named_sealer_score", "total", "worst_case_rank",
                "photo_flag", "lineart_flag", "kiszib_name", "seal_id"]
        with open(SHORTLIST, "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(cols)
            for block in (photo, no_photo):
                for pid in sorted(block, key=lambda p: (rank[p], p)):
                    c = cat[pid]
                    s = scores[pid]
                    w.writerow([
                        pid, "https://cdli.earth/artifacts/%d" % int(pid[1:]),
                        c["primary_publication"], c["provenience"], c["period"],
                        s["site"], s["period"], s["seal_note"], s["gulf_word"],
                        s["trade_word"], s["named_sealer"], total[pid], rank[pid],
                        1 if c["photo_up"].strip() else 0, 1 if c["lineart_up"].strip() else 0,
                        names[pid], c["seal_id"],
                    ])

    print("reading %d: %s" % (reading, list_status))
    # ---- step 12 -----------------------------------------------------------------------
    # PREREG-AMBIGUITY: an "empty list" under reading 3 or F1 is a result, not a planned stop, so it exits 0.
    return 1 if reading == 1 else 0


if __name__ == "__main__":
    sys.exit(main())
