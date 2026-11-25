"""crossread_coins: the comparer for the two blind transcribers.

Prereg: docs/prereg/crossread_coins.md, sealed v2 (tag `crossread_coins`), sections "The table: two blind
transcribers", "Protocol sheet for transcriber B" and "Symbols and sounds". This file is hashed into
docs/prereg/HASHES.txt (tag `crossread_coins_compare`) before any table from transcriber B exists.

Run (from the repo root; single process, no network, no T, no score, no Indus file):
  nice -n 20 python -I experiments/crossread_coins/compare.py \
      --a experiments/crossread_coins/table_a/bigr_rows.csv experiments/crossread_coins/table_a/wikipedia_rows.csv \
      --b <B's CSV> --out <new empty directory> [--later-titles <hashed word list, one word per line>]

Inputs
  --a   one or more files of transcriber A, all with the columns
          row_id, source, name_id, greek_legend, indic_form, indic_aksharas, n_types, same_person, ref
        greek_legend     the Greek legend as the source gives it, words separated by spaces
        indic_form       `unicode` or `latin`
        indic_aksharas   A's aksharas in reading order, separated by single spaces (cut by A under the sealed rule)
        n_types          the number of types (BIGR) or passages (Wikipedia) that carry this pair of legends
        same_person      `yes` or `no`
        name_id          A's label for the distinct name; rulers who share a name share it
        The files are kept apart by licence and are joined here in memory only.
  --b   B's CSV, the five columns of the protocol sheet in the sheet's order:
          1 ruler heading and page, 2 Greek legend, 3 second legend in Latin letters, 4 number of coin entries,
          5 whether the catalogue says the two sides name different people (yes, no, not stated)
        A file with six columns is read as heading and page in two columns. Any other width stops the script.
        The first row is taken as a header if its count field holds no digit and its Greek field no Greek letter.

Outputs (written to --out, which must be new or empty)
  checked_table.csv        one row per name that passes. It names A's row and gives the read flag of each of A's
                           aksharas. It holds no legend text and no key, so the licences stay apart and no sound
                           label reaches the run. Run symbols are A's aksharas, read from A's own files.
  rm.csv                   real mismatches: rows where a transcriber says the sides name different people
  rm2.csv                  rows whose Greek legend holds zero or two or more non-title words
  alignment_<source>.csv   the aligned keys, one file per source of A. COMPARISON ONLY. The run never opens them.
  report.txt               counts, the gate, the share of aksharas agreed

The sealed rules, in the order they are applied
  1. Greek words. Brackets ( ) and [ ] and what they hold are dropped. Upper case. The forms of sigma and omega
     are folded. Words not in the title list are name words. A legend with zero or 2+ name words gives no pair
     (RM2).
  2. Same person. A row that either transcriber marks as naming different people goes to RM.
  3. One pair per distinct name, from the legend on the most types (A) or the most coin entries (B).
  4. Greek name. B's name word must equal A's letter for letter after the fold. If no row of B does, the pair is
     dropped. Nothing is corrected.
  5. Keys. Unicode key from character names; Latin key lower case, NFD, marks dropped; both drop retroflex.
  6. The two key sequences are aligned by edit distance. An akshara is read if the two keys in its column are
     equal. An unmatched akshara, on either side, is unread.
  7. A legend passes with 80% or more of its aksharas read.
  8. Gate: 30 or more names pass. The share agreed over the checked table is reported, and flagged under 90%.

Choices the sealed text leaves open, fixed here before B exists (each is repeated in report.txt)
  a. B's "not stated" counts as "same person". Only an answer that starts with "yes" sends a B row to RM.
  b. B's legend for a name is the pair of legends with the most coin entries among B's rows whose name word equals
     A's, summed over headings. Ties go to the earlier row. A's is the pair on the most types, ties to the earlier
     row. The two are then compared. No row is picked because it agrees better. The best share over B's other rows
     with the same name is printed as a record-only column and changes nothing.
  c. "Its aksharas" are the columns of the alignment: A's aksharas plus the aksharas only B has. So an akshara that
     only one transcriber records counts as unread for the 80% rule. The share over A's aksharas alone is printed
     beside it, record only.
  d. Among alignments of least edit distance, the one with the most equal columns is used.
  e. Greek letters typed as look-alike Latin capitals (A B E Z H I K M N O P T Y X) are read as the Greek letter.
     Latin C counts as a form of sigma and Latin W as a form of omega. The count of such letters is reported.
  f. In a Latin legend an anusvara is an m with a dot or other mark, or a plain m that stands after a vowel and
     before a consonant or the end of the word. The sealed digraph list does not move an akshara boundary or change
     a key, so it is not needed here. A `?` stays in its akshara and never matches.
  g. Two name_ids of A that pick the same Greek name word give one pair, the one on more types.
  h. The title list is the sealed list. `--later-titles` adds a hashed list of later title words if the coordinator
     rules that they apply at this step. The script never builds that list itself.
"""
import argparse
import csv
import os
import re
import sys
import unicodedata

SEALED_TITLES = ("ΒΑΣΙΛΕΩΣ ΒΑΣΙΛΕΩΝ ΒΑΣΙΛΙΣΣΗΣ ΜΕΓΑΛΟΥ ΣΩΤΗΡΟΣ ΔΙΚΑΙΟΥ ΝΙΚΗΦΟΡΟΥ ΑΝΙΚΗΤΟΥ ΕΠΙΦΑΝΟΥΣ ΝΙΚΑΤΟΡΟΣ "
                 "ΕΥΕΡΓΕΤΟΥ ΦΙΛΟΠΑΤΟΡΟΣ ΘΕΟΤΡΟΠΟΥ ΚΑΙ ΦΙΛ").split()
A_COLUMNS = ["row_id", "source", "name_id", "greek_legend", "indic_form", "indic_aksharas", "n_types",
             "same_person", "ref"]
GATE = 30
LATIN_TO_GREEK = {"A": "Α", "B": "Β", "E": "Ε", "Z": "Ζ", "H": "Η", "I": "Ι", "K": "Κ", "M": "Μ", "N": "Ν",
                  "O": "Ο", "P": "Ρ", "T": "Τ", "Y": "Υ", "X": "Χ", "C": "Σ", "W": "Ω"}
SIGMA_FORMS = {"Σ", "Ϲ", "ϲ", "σ", "ς", "Ͻ", "ͻ"}
OMEGA_FORMS = {"Ω", "ω"}
RETROFLEX = {"TTA": "TA", "TTHA": "THA", "DDA": "DA", "DDHA": "DHA", "NNA": "NA", "SSA": "SA"}
KH_MARKS_DROPPED = {"KHAROSHTHI VOWEL LENGTH MARK", "KHAROSHTHI SIGN DOUBLE RING BELOW", "KHAROSHTHI SIGN BAR ABOVE",
                    "KHAROSHTHI SIGN CAUDA", "KHAROSHTHI SIGN DOT BELOW"}
VOWELS = set("aeiou")


# ---------------------------------------------------------------- Greek side
def greek_words(text):
    """Sealed unit rule, step 1, and the word list. Returns (words, number of Latin look-alikes folded)."""
    s = re.sub(r"\([^()]*\)|\[[^\[\]]*\]", " ", text)
    out = []
    folded = 0
    for ch in s:
        if ch in SIGMA_FORMS:
            out.append("Σ")
            continue
        if ch in OMEGA_FORMS:
            out.append("Ω")
            continue
        up = ch.upper()
        if len(up) != 1:
            up = ch
        if up in SIGMA_FORMS:
            up = "Σ"
        if up in LATIN_TO_GREEK:
            up = LATIN_TO_GREEK[up]
            folded += 1
        cat = unicodedata.category(up)
        if up != "?" and cat[0] in "ZPC":
            out.append(" ")
        else:
            out.append(up)
    return "".join(out).split(), folded


def name_words(words, titles):
    return [w for w in words if w not in titles]


# ---------------------------------------------------------------- keys
def unicode_key(akshara):
    """Key from character names. KA + VOWEL SIGN I gives ki. No vowel sign gives a. ANUSVARA gives m."""
    cons = []
    vowel = ""
    anusvara = False
    visarga = False
    dead = False
    other = []
    for ch in akshara:
        name = unicodedata.name(ch, "")
        if name.startswith("KHAROSHTHI LETTER "):
            t = name[len("KHAROSHTHI LETTER "):]
            t = RETROFLEX.get(t, t)
            cons.append(t[:-1].lower() if t.endswith("A") else t.lower())
            dead = False
        elif name.startswith("KHAROSHTHI VOWEL SIGN "):
            v = name[len("KHAROSHTHI VOWEL SIGN "):]
            vowel = "r" if v == "VOCALIC R" else v.lower()
        elif name == "KHAROSHTHI SIGN ANUSVARA":
            anusvara = True
        elif name == "KHAROSHTHI SIGN VISARGA":
            visarga = True
        elif name == "KHAROSHTHI VIRAMA":
            dead = True
        elif name in KH_MARKS_DROPPED:
            pass
        else:
            other.append(ch.lower())
    key = "".join(cons)
    if vowel:
        key += vowel
    elif cons and not dead:
        key += "a"
    if anusvara:
        key += "m"
    if visarga:
        key += "h"
    return key + "".join(other)


def latin_letters(text):
    """Lower case, NFD. Returns words; a word is a list of [letter, has_mark]. Marks, punctuation and symbols are
    dropped; a mark flags the letter before it. Whitespace breaks words. `?` is kept as a letter."""
    words = []
    cur = []
    for ch in unicodedata.normalize("NFD", text).lower():
        cat = unicodedata.category(ch)
        if ch == "?":
            cur.append(["?", False])
        elif cat[0] == "Z" or ch in "\t\n\r":
            if cur:
                words.append(cur)
            cur = []
        elif cat[0] == "L" and cat != "Lm":
            cur.append([ch, False])
        elif cat[0] == "M" or cat in ("Lm", "Sk"):
            if cur:
                cur[-1][1] = True
        else:
            pass
    if cur:
        words.append(cur)
    return words


def latin_aksharas(text):
    """Sealed rule for a Latin-only source: a run of consonants, one vowel and an optional anusvara. A consonant run
    left at the end of a word is an akshara with no vowel. Returns keys (marks are already dropped)."""
    out = []
    for word in latin_letters(text):
        n = len(word)
        run = []
        i = 0
        while i < n:
            ch = word[i][0]
            if ch in VOWELS:
                ak = run + [ch]
                run = []
                i += 1
                if i < n and word[i][0] == "m" and (word[i][1] or i + 1 == n or word[i + 1][0] not in VOWELS):
                    ak.append("m")
                    i += 1
                out.append("".join(ak))
            else:
                run.append(ch)
                i += 1
        if run:
            out.append("".join(run))
    return out


def latin_key(akshara):
    """Key of one Latin akshara of A: lower case, NFD, marks dropped."""
    return "".join(l[0] for w in latin_letters(akshara) for l in w)


def a_keys(form, aksharas):
    if form == "unicode":
        return [unicode_key(a) for a in aksharas]
    if form == "latin":
        return [latin_key(a) for a in aksharas]
    raise SystemExit("unknown indic_form: %r" % form)


# ---------------------------------------------------------------- alignment
def align(a, b):
    """Edit-distance alignment of two key sequences (insert, delete and substitute cost 1 each). Among alignments
    of least cost the one with the most equal columns is taken. Returns a list of (i, j, read): i indexes a or is
    None, j indexes b or is None."""
    n, m = len(a), len(b)
    d = [[None] * (m + 1) for _ in range(n + 1)]
    d[0][0] = (0, 0)
    for i in range(1, n + 1):
        d[i][0] = (i, 0)
    for j in range(1, m + 1):
        d[0][j] = (j, 0)

    def same(i, j):
        return a[i] == b[j] and a[i] != "" and "?" not in a[i]

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            eq = same(i - 1, j - 1)
            diag = (d[i - 1][j - 1][0] + (0 if eq else 1), d[i - 1][j - 1][1] - (1 if eq else 0))
            up = (d[i - 1][j][0] + 1, d[i - 1][j][1])
            left = (d[i][j - 1][0] + 1, d[i][j - 1][1])
            d[i][j] = min(diag, up, left)
    cols = []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0:
            eq = same(i - 1, j - 1)
            diag = (d[i - 1][j - 1][0] + (0 if eq else 1), d[i - 1][j - 1][1] - (1 if eq else 0))
            if d[i][j] == diag:
                cols.append((i - 1, j - 1, eq))
                i, j = i - 1, j - 1
                continue
        if i > 0 and d[i][j] == (d[i - 1][j][0] + 1, d[i - 1][j][1]):
            cols.append((i - 1, None, False))
            i -= 1
            continue
        cols.append((None, j - 1, False))
        j -= 1
    cols.reverse()
    return cols


def compare(keys_a, keys_b):
    cols = align(keys_a, keys_b)
    read = sum(1 for c in cols if c[2])
    return cols, read


def passes(read, total):
    return total > 0 and read * 5 >= total * 4


# ---------------------------------------------------------------- input
def read_a(paths):
    rows = []
    for p in paths:
        with open(p, encoding="utf-8", newline="") as f:
            rd = csv.DictReader(f)
            if rd.fieldnames != A_COLUMNS:
                raise SystemExit("A file %s: columns are %r, expected %r" % (p, rd.fieldnames, A_COLUMNS))
            for r in rd:
                if r["same_person"] not in ("yes", "no"):
                    raise SystemExit("A file %s row %s: same_person must be yes or no" % (p, r["row_id"]))
                r["n"] = int(r["n_types"])
                r["aks"] = r["indic_aksharas"].split(" ") if r["indic_aksharas"] else []
                if not r["aks"] or "" in r["aks"]:
                    raise SystemExit("A file %s row %s: empty akshara" % (p, r["row_id"]))
                r["order"] = len(rows)
                rows.append(r)
    ids = [r["row_id"] for r in rows]
    if len(set(ids)) != len(ids):
        raise SystemExit("A: row_id is not unique")
    return rows


def has_greek(s):
    return any(0x370 <= ord(c) <= 0x3FF or 0x1F00 <= ord(c) <= 0x1FFF for c in s)


def read_b(path):
    with open(path, encoding="utf-8-sig", newline="") as f:
        raw = [r for r in csv.reader(f) if any(x.strip() for x in r)]
    rows = []
    header = False
    for k, r in enumerate(raw):
        r = [x.strip() for x in r]
        if len(r) == 6:
            r = [r[0] + ", " + r[1]] + r[2:]
        if len(r) != 5:
            raise SystemExit("B: row %d has %d columns; the protocol sheet asks for five" % (k + 1, len(r)))
        if k == 0 and not re.search(r"\d", r[3]) and not has_greek(r[1]):
            header = True
            continue
        m = re.search(r"\d+", r[3])
        rows.append({"b_row": k + 1, "heading": r[0], "greek": r[1], "latin": r[2], "count_raw": r[3],
                     "count": int(m.group(0)) if m else 0, "different_raw": r[4],
                     "different": r[4].strip().lower().startswith("yes"), "order": len(rows)})
    return rows, header


def read_titles(path):
    titles = set(SEALED_TITLES)
    extra = []
    if path:
        with open(path, encoding="utf-8") as f:
            for line in f:
                w, _ = greek_words(line)
                extra.extend(w)
        titles.update(extra)
    return titles, extra


# ---------------------------------------------------------------- main
def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_") or "source"


def main():
    ap = argparse.ArgumentParser(description="crossread_coins comparer (sealed protocol)")
    ap.add_argument("--a", nargs="+", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--later-titles", default=None)
    args = ap.parse_args()
    if os.path.exists(args.out) and os.listdir(args.out):
        raise SystemExit("--out exists and is not empty; nothing is overwritten")
    os.makedirs(args.out, exist_ok=True)

    titles, extra_titles = read_titles(args.later_titles)
    a_rows = read_a(args.a)
    b_rows, b_header = read_b(args.b)
    rm = []      # (who, source, row, reason)
    rm2 = []
    folded_latin = 0

    # ---- A: rules 1 to 3
    a_cand = {}  # name_id -> {pair key -> pooled record}
    name_order = []
    for r in a_rows:
        words, k = greek_words(r["greek_legend"])
        folded_latin += k
        names = name_words(words, titles)
        r["words"] = words
        if r["same_person"] == "no":
            rm.append(("A", r["source"], r["row_id"], "A marks the sides as different people", r["n"]))
            continue
        if len(names) != 1:
            rm2.append(("A", r["source"], r["row_id"], "%d non-title words" % len(names), r["n"]))
            continue
        r["name"] = names[0]
        if r["name_id"] not in a_cand:
            a_cand[r["name_id"]] = {}
            name_order.append(r["name_id"])
        key = (tuple(words), r["indic_form"], tuple(r["aks"]))
        pool = a_cand[r["name_id"]]
        if key in pool:
            pool[key]["n"] += r["n"]
        else:
            pool[key] = {"row": r, "n": r["n"], "order": r["order"]}
    a_pick = {}
    for nid in name_order:
        best = sorted(a_cand[nid].values(), key=lambda p: (-p["n"], p["order"]))[0]
        a_pick[nid] = best
    # choice g: one pair per Greek name word
    by_word = {}
    dup = []
    for nid in name_order:
        w = a_pick[nid]["row"]["name"]
        if w in by_word:
            old = by_word[w]
            if (-a_pick[nid]["n"], a_pick[nid]["order"]) < (-a_pick[old]["n"], a_pick[old]["order"]):
                dup.append(old)
                by_word[w] = nid
            else:
                dup.append(nid)
        else:
            by_word[w] = nid
    names_a = [nid for nid in name_order if nid not in dup]

    # ---- B: rules 1 to 3
    b_cand = {}  # name word -> {pair key -> pooled record}
    b_different_values = {}
    b_bad_count = 0
    for r in b_rows:
        words, k = greek_words(r["greek"])
        folded_latin += k
        r["words"] = words
        r["keys"] = latin_aksharas(r["latin"])
        v = r["different_raw"].strip().lower()
        b_different_values[v] = b_different_values.get(v, 0) + 1
        if not re.search(r"\d", r["count_raw"]):
            b_bad_count += 1
        names = name_words(words, titles)
        if r["different"]:
            rm.append(("B", "gardner1886", "b%d" % r["b_row"], "B: the catalogue says different people", r["count"]))
            continue
        if len(names) != 1:
            rm2.append(("B", "gardner1886", "b%d" % r["b_row"], "%d non-title words" % len(names), r["count"]))
            continue
        key = (tuple(words), " ".join(unicodedata.normalize("NFC", r["latin"]).split()))
        pool = b_cand.setdefault(names[0], {})
        if key in pool:
            pool[key]["n"] += r["count"]
        else:
            pool[key] = {"row": r, "n": r["count"], "order": r["order"]}

    # ---- rules 4 to 7
    results = []
    for nid in names_a:
        pa = a_pick[nid]
        ra = pa["row"]
        ka = a_keys(ra["indic_form"], ra["aks"])
        res = {"name_id": nid, "a": ra, "a_n": pa["n"], "keys_a": ka, "status": "", "cols": [], "read": 0,
               "b": None, "b_n": 0, "best_other": None}
        pool = b_cand.get(ra["name"])
        if not pool:
            res["status"] = "dropped: no row of B has this Greek name"
            results.append(res)
            continue
        ranked = sorted(pool.values(), key=lambda p: (-p["n"], p["order"]))
        pb = ranked[0]
        cols, read = compare(ka, pb["row"]["keys"])
        res.update(cols=cols, read=read, b=pb["row"], b_n=pb["n"])
        best = None
        for other in ranked[1:]:
            c2, r2 = compare(ka, other["row"]["keys"])
            share = r2 / len(c2) if c2 else 0.0
            if best is None or share > best:
                best = share
        res["best_other"] = best
        res["status"] = "pass" if passes(read, len(cols)) else "fail: under 80% of aksharas read"
        results.append(res)
    passed = [r for r in results if r["status"] == "pass"]
    compared = [r for r in results if r["b"] is not None]

    # ---- outputs
    def out(name):
        return open(os.path.join(args.out, name), "w", encoding="utf-8", newline="")

    with out("checked_table.csv") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(["name_id", "a_source", "a_row_id", "a_n_types", "n_aksharas_a", "read_flags_a", "aksharas_b_only",
                    "read", "columns", "share", "b_row", "b_heading", "b_entries"])
        for r in passed:
            flags = ["0"] * len(r["keys_a"])
            for i, j, ok in r["cols"]:
                if i is not None and ok:
                    flags[i] = "1"
            b_only = sum(1 for i, j, ok in r["cols"] if i is None)
            w.writerow([r["name_id"], r["a"]["source"], r["a"]["row_id"], r["a_n"], len(r["keys_a"]), "".join(flags),
                        b_only, r["read"], len(r["cols"]), "%.4f" % (r["read"] / len(r["cols"])),
                        r["b"]["b_row"], r["b"]["heading"], r["b_n"]])
    for fname, rows in (("rm.csv", rm), ("rm2.csv", rm2)):
        with out(fname) as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["transcriber", "source", "row", "reason", "types_or_entries"])
            w.writerows(rows)
    by_source = {}
    for r in compared:
        by_source.setdefault(slug(r["a"]["source"]), []).append(r)
    for s, rs in sorted(by_source.items()):
        with out("alignment_%s.csv" % s) as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["name_id", "a_row_id", "b_row", "column", "a_akshara", "a_key", "b_key", "read"])
            for r in rs:
                for c, (i, j, ok) in enumerate(r["cols"]):
                    w.writerow([r["name_id"], r["a"]["row_id"], r["b"]["b_row"], c,
                                r["a"]["aks"][i] if i is not None else "", r["keys_a"][i] if i is not None else "",
                                r["b"]["keys"][j] if j is not None else "", int(ok)])

    def share(rs):
        tot = sum(len(r["cols"]) for r in rs)
        return (sum(r["read"] for r in rs) / tot) if tot else None, tot

    def share_a(rs):
        tot = sum(len(r["keys_a"]) for r in rs)
        return (sum(r["read"] for r in rs) / tot) if tot else None, tot

    def fmt(x):
        return "n/a" if x is None else "%.4f" % x

    sh_t, n_t = share(passed)
    sh_c, n_c = share(compared)
    sha_t, _ = share_a(passed)
    sha_c, _ = share_a(compared)
    n_pass = len(passed)
    L = []
    L.append("crossread_coins comparer report (prereg docs/prereg/crossread_coins.md, sealed v2)")
    L.append("No T, no score and no pairing statistic is computed here.")
    L.append("")
    L.append("Inputs")
    L.append("  A files: %s" % ", ".join(args.a))
    L.append("  B file: %s (%d rows%s)" % (args.b, len(b_rows), ", header row skipped" if b_header else ""))
    L.append("  title list: sealed, %d words%s" % (len(SEALED_TITLES), "" if not extra_titles else
             "; plus %d later title words from %s" % (len(set(extra_titles)), args.later_titles)))
    L.append("")
    L.append("Transcriber A")
    L.append("  rows: %d" % len(a_rows))
    L.append("  rows to RM (different people): %d" % sum(1 for x in rm if x[0] == "A"))
    L.append("  rows to RM2 (zero or 2+ non-title words): %d" % sum(1 for x in rm2 if x[0] == "A"))
    L.append("  distinct names with a pair: %d" % len(names_a))
    for s in sorted({r["source"] for r in a_rows}):
        L.append("    from %s: %d" % (s, sum(1 for nid in names_a if a_pick[nid]["row"]["source"] == s)))
    L.append("  name_ids merged because they pick the same Greek name word: %d %s" % (len(dup), dup if dup else ""))
    L.append("")
    L.append("Transcriber B")
    L.append("  rows: %d" % len(b_rows))
    L.append("  rows to RM (catalogue says different people): %d" % sum(1 for x in rm if x[0] == "B"))
    L.append("  rows to RM2 (zero or 2+ non-title words): %d" % sum(1 for x in rm2 if x[0] == "B"))
    L.append("  distinct Greek name words with a pair: %d" % len(b_cand))
    L.append("  answers in column 5: %s" % ", ".join("%r x%d" % kv for kv in sorted(b_different_values.items())))
    L.append("  count fields with no digit (read as 0): %d" % b_bad_count)
    L.append("")
    L.append("Lists")
    L.append("  RM: %d rows, %d types or entries" % (len(rm), sum(x[4] for x in rm)))
    L.append("  RM2: %d rows, %d types or entries" % (len(rm2), sum(x[4] for x in rm2)))
    L.append("")
    L.append("Comparison (one pair per distinct name)")
    L.append("  names of A: %d" % len(names_a))
    L.append("  dropped, no row of B has the Greek name: %d" % sum(1 for r in results if r["b"] is None))
    L.append("  compared: %d" % len(compared))
    L.append("  pass (80%% or more of the aksharas read): %d" % n_pass)
    L.append("  fail: %d" % (len(compared) - n_pass))
    L.append("")
    L.append("GATE: N = %d names pass. Sealed gate is %d or more. %s" % (
        n_pass, GATE, "GATE MET" if n_pass >= GATE else "GATE NOT MET (F4: the study does not run)"))
    L.append("")
    L.append("Share of aksharas agreed")
    L.append("  checked table: %s of %d alignment columns" % (fmt(sh_t), n_t))
    L.append("  all compared names: %s of %d alignment columns" % (fmt(sh_c), n_c))
    L.append("  record only, over A's aksharas alone: checked table %s, all compared %s" % (fmt(sha_t), fmt(sha_c)))
    if sh_t is not None and sh_t < 0.90:
        L.append("  FLAG TO THE COORDINATOR: the share over the checked table is under 90%.")
    L.append("")
    L.append("Greek letters typed as Latin look-alikes and folded (choice e): %d" % folded_latin)
    L.append("")
    L.append("Per name (best_other is record only: the best share over B's other rows with the same name)")
    L.append("  name_id | A source | A row | A types | status | read/columns | share | B row | B entries | best_other")
    for r in results:
        if r["b"] is not None:
            L.append("  %s | %s | %s | %d | %s | %d/%d | %.4f | %s | %d | %s" % (
                r["name_id"], r["a"]["source"], r["a"]["row_id"], r["a_n"], r["status"], r["read"], len(r["cols"]),
                r["read"] / len(r["cols"]), r["b"]["b_row"], r["b_n"], fmt(r["best_other"])))
        else:
            L.append("  %s | %s | %s | %d | %s" % (r["name_id"], r["a"]["source"], r["a"]["row_id"], r["a_n"],
                                                  r["status"]))
    L.append("")
    L.append("Choices the sealed text leaves open, fixed in this script before B's table existed")
    L.append("  a. B's 'not stated' counts as same person; only an answer starting with 'yes' goes to RM.")
    L.append("  b. B's legend for a name is its pair with the most coin entries; A's is the pair on the most types.")
    L.append("  c. An akshara that only one transcriber records counts as unread for the 80% rule.")
    L.append("  d. Among least-distance alignments the one with the most equal columns is used.")
    L.append("  e. Latin look-alike capitals are read as Greek letters; C as sigma, W as omega.")
    L.append("  f. Latin anusvara: a marked m, or a plain m after a vowel and before a consonant or the word end.")
    L.append("  g. Two name_ids with the same Greek name word give one pair.")
    L.append("  h. Later title words are used only if given with --later-titles.")
    with out("report.txt") as f:
        f.write("\n".join(L) + "\n")
    sys.stdout.write("\n".join(L[:40]) + "\n")


if __name__ == "__main__":
    main()
