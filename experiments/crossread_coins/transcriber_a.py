"""crossread_coins: transcriber A.

Prereg: docs/prereg/crossread_coins.md, sealed v2 (tag `crossread_coins`), sections "Data sources and licences",
"The table: two blind transcribers" and "Symbols and sounds".

A works from the BIGR type export and, for names BIGR lacks, from Wikipedia ruler pages at pinned revisions.
A never opens Gardner 1886 and never sees a table from transcriber B. This script computes no T, no score, no
pairing statistic and no comparison with B. It opens no Indus file.

Run (from the repo root; single process, no network):
  nice -n 20 python -I experiments/crossread_coins/transcriber_a.py \
      --bigr experiments/crossread_coins/raw/bigr/query.csv \
      --wiki <directory outside the repo>/revisions.json \
      --out experiments/crossread_coins/table_a

`revisions.json` is the answer to one MediaWiki API request for the pinned revision ids (the request is given in
`table_a/wikipedia_rows.LICENCE.md`). The script stops unless every pinned revision is present with the pinned SHA-1
of its wikitext, and unless the BIGR export has the SHA-256 sealed in the prereg.

Output (to --out, which must be new or empty). The two sources stay in separate files, by licence.
  bigr_rows.csv        rows from BIGR (ODbL 1.0)
  wikipedia_rows.csv   rows from Wikipedia (CC BY-SA 4.0)
  summary.txt          counts only
Both CSV files have the columns the comparer reads:
  row_id, source, name_id, greek_legend, indic_form, indic_aksharas, n_types, same_person, ref

BIGR rows (a script, as sealed)
  - A type row is used if one side holds Greek letters and no Kharosthi and the other side holds Kharosthi and no
    Greek letters. Brahmi stays out of the study.
  - One output row per distinct (name_id, Greek legend, akshara sequence, same_person). n_types counts the type
    rows. The comparer takes the pair on the most types for each name.
  - The Greek legend is copied as given, with its notes in brackets. Only white space is tidied.
  - name_id is the first word of the row's authority (`Authority`, or `Stated Authority` where that is empty), in
    lower case. So Strato I and Strato II share a name_id, and the two spellings of Zoilus do too. A row with two
    authorities gets both, joined by `+`.
  - same_person. A script cannot read the Indic side, so the mark follows from BIGR's own fields: `no` if the row
    has two or more authorities and its Greek legend holds exactly one non-title word (one side names one of the
    two, so the other side can name the other). Joint legends with two names in the Greek keep `yes`; the comparer
    sends them to RM2. One exception is marked by hand, from reading the legend: RecordIds in NOT_A_PERSON, where
    the Indic side names a city deity and no person.

Wikipedia rows (hand-picked passages, copied by the script)
  - A row is a passage that gives a Greek legend and a Kharosthi legend of the same coin. A page that gives only a
    name form in each script gives no row: a name form is not a legend.
  - Each passage is listed in PASSAGES with the two strings as the page prints them. The script takes a row only
    if both strings stand verbatim in the pinned wikitext (after `<big>` tags are removed). Nothing is corrected,
    not a mixed-in Latin letter and not a blundered legend.
  - n_types is the number of pinned pages that carry both strings.
  - same_person is A's reading of the page's own translation of the two legends.

Aksharas (sealed cutting rules)
  - All Z* and P* characters are deleted before cutting. No word break is stored.
  - Unicode: one base character, plus any combining marks (Mn, Mc), plus any character joined by the virama
    U+10A3F.
  - Latin-only: a run of consonants, one vowel and an optional anusvara. Lower case, NFC, marks kept (the comparer's
    key drops them). The sealed digraph list moves no boundary. The script stops if a Latin word ends in a
    consonant, so that deleting the spaces cannot change a cut.
"""
import argparse
import csv
import hashlib
import json
import os
import re
import sys
import unicodedata

BIGR_SHA256 = "847add2aebcc64ac2907cca31d58c0e13968f00db003c92e13e036e9e26ad8bc"
SEALED_TITLES = set(("ΒΑΣΙΛΕΩΣ ΒΑΣΙΛΕΩΝ ΒΑΣΙΛΙΣΣΗΣ ΜΕΓΑΛΟΥ ΣΩΤΗΡΟΣ ΔΙΚΑΙΟΥ ΝΙΚΗΦΟΡΟΥ ΑΝΙΚΗΤΟΥ ΕΠΙΦΑΝΟΥΣ ΝΙΚΑΤΟΡΟΣ "
                     "ΕΥΕΡΓΕΤΟΥ ΦΙΛΟΠΑΤΟΡΟΣ ΘΕΟΤΡΟΠΟΥ ΚΑΙ ΦΙΛ").split())
COLUMNS = ["row_id", "source", "name_id", "greek_legend", "indic_form", "indic_aksharas", "n_types", "same_person",
           "ref"]
VIRAMA = "\U00010A3F"
NOT_A_PERSON = {"bigr.eucratides_i.28", "bigr.eucratides_i.28.1"}

# Pinned Wikipedia revisions: title -> (revision id, SHA-1 of the wikitext). English Wikipedia, CC BY-SA 4.0.
REVISIONS = {
    "Abdagases I": (1381234186, "45a3dcb3e46053f30d8ba04f8b0b6070c64f0785"),
    "Arta (Kamuia)": (1358068536, "ae273700d19b39ac9c892fbe2d69631ec903bb9a"),
    "Aspavarma": (1382534177, "ff14e4e7c41b616c822c417b3d413577fc1915ac"),
    "Azes I": (1358748801, "6dcbb9f75d5e23b175a5b651f267d280f9314e35"),
    "Azes II": (1358748804, "5e7fc59e6d6f15e171b1ab9655ab6906fb48ce69"),
    "Azilises": (1358748808, "dc49522c3f42a90634e9006fd0b041e37a7b23e3"),
    "Bhumaka": (1359985380, "d3952bdebac65ee342cbe81630251539f27c3366"),
    "Chashtana": (1358751547, "43d3dbeb355eeb66e942c36c0ee637c49896ce19"),
    "Gondophares": (1383209160, "f4ce96b8a91b57f71d0161be27f7ef1dc214b540"),
    "Hagana (satrap)": (1328846766, "a6d30ca57e298437c312446de0c6ff87c36f6591"),
    "Indravarma": (1358757511, "196ed8bb043571a60d48609427c4937e6ca82964"),
    "Kharahostes": (1358759400, "f18e077e75e8e60afe446ca4d578eb13cbb7f56c"),
    "Kujula Kadphises": (1371524053, "5962b37916ec2326e4aacc72042d08618e98b6d3"),
    "Liaka Kusulaka": (1288827786, "f3a30287201663af3fe16f76600e9dd6f30d5048"),
    "Maues": (1362867327, "15a42633dd9022a1e90d8ea4949f44b822eacb44"),
    "Nahapana": (1358597747, "d02cd968fc6c07e53664faf3a0f4b59aa6cb6694"),
    "Pacores": (1356673019, "aba30f6e82b00f5f9c7c76d4caee7bf36cf80fe5"),
    "Rajuvula": (1361592437, "e769a3ab28be85e93054573441d7f3e0840450f0"),
    "Sases": (1381234523, "a789e5c1142bb4845197e3924a6a16fb24b38443"),
    "Spalagadames": (1288818538, "4c82b9890af7a636014bf04bbb3015df9ba1a7a3"),
    "Spalahores": (1358897325, "6fa82524f0993f0f199a4e22d0bc0cb88e95a87e"),
    "Spalirisos": (1288811012, "c0ccb67ece3e3c7c50d9336c3fc841135f1eb191"),
    "Vijayamitra": (1358901808, "1f71f073a508f732823c85a10b42bf5b37eb22d0"),
    "Vima Kadphises": (1381610209, "e5ec40a3cbae5fcd3e9f5b0a1b786357cfe2b11e"),
    "Vima Takto": (1371524207, "daced5b716b7e6ba9af97581c2ae35a62362a4b9"),
    "Vonones of Sakastan": (1358738489, "96dfbe735e88e39888c1d46c1266ee27633c5bac"),
    "Zeionises": (1288793306, "e612581b883e8c06de24176baa091c49b3f9eebe"),
}

# Passages with a Greek legend and a Kharosthi legend of the same coin.
# (name_id, Greek legend as printed, Kharosthi legend as printed, form, same_person)
PASSAGES = [
    ("azes", "ΒΑΣΙΛΕΩΣ ΒΑΣΙΛΕΩΝ ΜΕΓΑΛΟΥ ΑΖΟΥ", "MAHARAJASA RAJADIRAJASA MAHATASA AYASA", "latin", "yes"),
    # The page prints the blundered legend of the coin and then the reading it stands for. The coin's own legend is
    # copied; the reading is the page's correction.
    ("azes", "ωΕΙΛΟN ωΕΟΛΛωN ΙΟϹΑΑϹ", "Maharajasa mahatasa Dhramakisa Rajatirajasa Ayasa", "latin", "yes"),
    ("azilises", "ΒΑΣΙΛΕΩΣ ΒΑΣΙΛΕΩΝ ΜΕΓΑΛΟΥ ΑΖΙΛΙΣΟΥ", "Maharajasa rajarajasa mahatasa Ayilisasa", "latin", "yes"),
    # Greek side names Azes, Kharosthi side names Aspavarma.
    ("azes+aspavarma", "ΒΑΣΙΛΕΩΣ ΒΑΣΙΛΕΩΝ ΜΕΓΑΛΟΥ / ΑΖΟΥ", "Iṃdravarmaputrasa Aśpavarmasa strategasa jayatasa",
     "latin", "no"),
    # Greek side names queen Machene, Kharosthi side names Maues.
    ("machene+maues", "ΒΑΣΙΛΙΣΣΗΣ ΘEOTPOΠOY MAXHNHΣ", "Rajatirajasa mahatasa Moasa", "latin", "no"),
    ("kharahostes", "ΧΑΡΑΗωϹΤΕΙ ϹΑΤΡΑΠΕΙ ΑΡΤΑΥΟΥ", "Chatrapasa pra Kharaustasa Artasa putrasa", "latin", "yes"),
    ("kharahostes", "XAPAHWCTEI CATPAΠEI ARTAYOY", "Chatrapasa pra Kharaustasa Artasa putrasa", "latin", "yes"),
    ("kharahostes", "XAPAHWCTEI ϹΑΤΡΑΠΕΙ ARTAYOY", "Kṣatrapasa  Pra Kharaoṣtasa Artasa Putrasa", "latin", "yes"),
    # The page calls the second legend "Legend" and does not name its script.
    ("kujula", "ΚΟΖΟΛΑ ΚΑΔΑΦΕϹ XOPANOV ZAOOV", "Khushanasa Yauasa Kuyula Kaphasa Sacha Dhramatidasa", "latin", "yes"),
    ("kujula", "ΚΟΖΟΛΑ XOPANOY ZAOOY", "Kuyula Kadaphasa Kushanasa", "latin", "yes"),
    ("vima", "ΒΑΣΙΛΕΥΣ ΟΟΗΜΟ ΚΑΔΦΙΣΗΣ",
     "MAHARAJASA RAJADIRAJASA SARVALOGA ISVARASA MAHISVARASA VIMA KATHPHISASA TRADARA", "latin", "yes"),
    # The page prints these two Greek legends in Latin letters. They are copied as printed.
    ("zeionises", "MANNOLOU UIOU SATRAPY ZEIONISOU", "MANIGULASA CHATRAPASA PUTRASA CHATRAPASA JIHUNIASA", "latin",
     "yes"),
    ("rajuvula", "BASILEOS BASILEON SOTEROS RAZU", "Chatrapasa apratihatachakrasa rajuvulasa", "latin", "yes"),
    # Obverse and reverse stand in two neighbouring gallery captions.
    ("nahapana", "ΡΑΝΝΙ (ω ΙΑΗΑΡΑΤΑϹ) ΝΑΗΑΠΑ (ΝΑϹ)", "Rano Chaharatasa Nahapanasa", "latin", "yes"),
]


# ---------------------------------------------------------------- shared small rules
def greek_words(text):
    """Sealed unit rule, step 1: drop brackets, upper case, fold sigma and omega. For counts and the BIGR
    same_person rule only. The stored Greek legend is the source's own string."""
    s = re.sub(r"\([^()]*\)|\[[^\[\]]*\]", " ", text)
    s = s.replace("Ϲ", "Σ").replace("ϲ", "Σ").replace("ς", "Σ").replace("σ", "Σ").replace("ω", "Ω").upper()
    s = s.replace("Ϲ", "Σ")
    return ["".join(c for c in w if unicodedata.category(c)[0] not in "PC") for w in s.split()]


def name_words(text):
    return [w for w in greek_words(text) if w and w not in SEALED_TITLES]


def tidy(s):
    return " ".join(s.replace("\xa0", " ").split())


def is_kh(c):
    return 0x10A00 <= ord(c) <= 0x10A5F


def has_greek(s):
    return any(0x370 <= ord(c) <= 0x3FF or 0x1F00 <= ord(c) <= 0x1FFF for c in s)


def has_kh(s):
    return any(is_kh(c) for c in s)


def has_brahmi(s):
    return any(0x11000 <= ord(c) <= 0x1107F for c in s)


def cut_unicode(legend):
    """Sealed rule for Unicode. Z* and P* are deleted first."""
    out = []
    join = False
    for c in legend:
        cat = unicodedata.category(c)
        if cat[0] in "ZP" or cat == "Cc":
            continue
        if not is_kh(c):
            raise SystemExit("unexpected character U+%04X in an Indic legend" % ord(c))
        if cat in ("Mn", "Mc"):
            if not out:
                raise SystemExit("combining mark with no base")
            out[-1] += c
            join = (c == VIRAMA)
        elif join:
            out[-1] += c
            join = False
        else:
            out.append(c)
    if join:
        raise SystemExit("legend ends in a virama")
    return out


def cut_latin(legend):
    """Sealed rule for a Latin-only source. Z* and P* are deleted first. Returns aksharas in lower case, NFC."""
    text = unicodedata.normalize("NFD", legend).lower()
    for w in text.split():
        base = [c for c in w if unicodedata.category(c)[0] == "L"]
        if base and base[-1] not in "aeiou":
            last = [c for c in w if unicodedata.category(c)[0] in "LM"]
            if not (base[-1] == "m" and unicodedata.category(last[-1])[0] == "M"):
                raise SystemExit("Latin word ends in a consonant: %r" % w)
    letters = []   # [base letter, marks]
    for c in text:
        cat = unicodedata.category(c)
        if cat[0] == "L":
            letters.append([c, ""])
        elif cat[0] == "M":
            if not letters:
                raise SystemExit("mark with no letter")
            letters[-1][1] += c
        elif cat[0] in "ZPC":
            continue
        else:
            raise SystemExit("unexpected character %r in a Latin legend" % c)
    out = []
    run = ""
    i = 0
    n = len(letters)
    while i < n:
        ch, marks = letters[i]
        if ch in "aeiou":
            ak = run + ch + marks
            run = ""
            i += 1
            if i < n and letters[i][0] == "m" and (letters[i][1] or i + 1 == n or letters[i + 1][0] not in "aeiou"):
                ak += "m" + letters[i][1]
                i += 1
            out.append(unicodedata.normalize("NFC", ak))
        else:
            run += ch + marks
            i += 1
    if run:
        raise SystemExit("consonant run left at the end of a Latin legend")
    return out


# ---------------------------------------------------------------- BIGR
def bigr_rows(path):
    with open(path, "rb") as f:
        raw = f.read()
    sha = hashlib.sha256(raw).hexdigest()
    if sha != BIGR_SHA256:
        raise SystemExit("A2: BIGR export hash %s is not the sealed %s" % (sha, BIGR_SHA256))
    rows = list(csv.DictReader(raw.decode("utf-8").splitlines(keepends=True)))
    stats = {"type_rows": len(rows), "greek_kharosthi": 0, "greek_brahmi": 0, "kharosthi_no_greek": 0}
    pool = {}
    order = []
    indic_legends = set()
    authorities = set()
    for r in rows:
        o, v = r["Obverse Legend"], r["Reverse Legend"]
        if has_greek(o) and not has_kh(o) and has_kh(v) and not has_greek(v):
            g, k = o, v
        elif has_greek(v) and not has_kh(v) and has_kh(o) and not has_greek(o):
            g, k = v, o
        else:
            if (has_greek(o) and has_brahmi(v)) or (has_greek(v) and has_brahmi(o)):
                stats["greek_brahmi"] += 1
            elif has_kh(o + v):
                stats["kharosthi_no_greek"] += 1
            continue
        stats["greek_kharosthi"] += 1
        auth = r["Authority"].strip() or r["Stated Authority"].strip()
        authorities.add(auth)
        people = [a for a in auth.split("||") if a.strip()]
        firsts = [re.sub(r"[^a-z]", "", a.split()[0].lower()) for a in people]
        name_id = "+".join(firsts) if firsts else "unknown"
        greek = tidy(g)
        aks = cut_unicode(k)
        same = "yes"
        if len(people) >= 2 and len(name_words(greek)) == 1:
            same = "no"
        if r["RecordId"] in NOT_A_PERSON:
            same = "no"
        indic_legends.add(tuple(aks))
        key = (name_id, greek, tuple(aks), same)
        if key not in pool:
            pool[key] = [0, r["RecordId"]]
            order.append(key)
        pool[key][0] += 1
    out = []
    for n, key in enumerate(order, 1):
        name_id, greek, aks, same = key
        out.append({"row_id": "bigr-%03d" % n, "source": "BIGR", "name_id": name_id, "greek_legend": greek,
                    "indic_form": "unicode", "indic_aksharas": " ".join(aks), "n_types": pool[key][0],
                    "same_person": same, "ref": pool[key][1]})
    stats["authority_strings"] = len(authorities)
    stats["distinct_indic_legends"] = len(indic_legends)
    stats["akshara_types"] = len({a for l in indic_legends for a in l})
    return out, stats


# ---------------------------------------------------------------- Wikipedia
def wiki_rows(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    pages = {}
    for p in d["query"]["pages"]:
        rev = p["revisions"][0]
        text = rev["slots"]["main"]["content"]
        pages[p["title"]] = (rev["revid"], hashlib.sha1(text.encode("utf-8")).hexdigest(), text)
    for title, (revid, sha1) in REVISIONS.items():
        if title not in pages:
            raise SystemExit("pinned page missing from the download: %s" % title)
        if pages[title][0] != revid or pages[title][1] != sha1:
            raise SystemExit("pinned revision of %s does not match (revid or SHA-1)" % title)
    clean = {t: re.sub(r"</?big>", "", pages[t][2]) for t in REVISIONS}
    out = []
    used_pages = set()
    for n, (name_id, greek, indic, form, same) in enumerate(PASSAGES, 1):
        hits = [t for t in sorted(REVISIONS) if greek in clean[t] and indic in clean[t]]
        if not hits:
            raise SystemExit("passage %d is not verbatim in any pinned page" % n)
        used_pages.update(hits)
        aks = cut_latin(indic) if form == "latin" else cut_unicode(indic)
        out.append({"row_id": "wiki-%03d" % n, "source": "Wikipedia", "name_id": name_id, "greek_legend": tidy(greek),
                    "indic_form": form, "indic_aksharas": " ".join(aks), "n_types": len(hits), "same_person": same,
                    "ref": "; ".join("%s oldid=%d" % (t, REVISIONS[t][0]) for t in hits)})
    return out, len(REVISIONS), sorted(used_pages)


# ---------------------------------------------------------------- output
def usable_names(rows):
    """name_ids with at least one row that names the same person and has exactly one non-title Greek word."""
    names = {}
    for r in rows:
        if r["same_person"] == "yes":
            nw = name_words(r["greek_legend"])
            if len(nw) == 1:
                names.setdefault(r["name_id"], set()).add(nw[0])
    return names


def write_csv(path, rows):
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        w.writerows(rows)


def main():
    ap = argparse.ArgumentParser(description="crossread_coins transcriber A")
    ap.add_argument("--bigr", required=True)
    ap.add_argument("--wiki", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    if os.path.exists(args.out) and os.listdir(args.out):
        raise SystemExit("--out exists and is not empty; nothing is overwritten")
    os.makedirs(args.out, exist_ok=True)

    b_rows, st = bigr_rows(args.bigr)
    b_names = usable_names(b_rows)
    b_words = {w for ws in b_names.values() for w in ws}
    w_all, n_pages, used_pages = wiki_rows(args.wiki)
    # Wikipedia is used only for names BIGR lacks.
    w_rows = [r for r in w_all if not (set(name_words(r["greek_legend"])) & b_words)]
    w_names = usable_names(w_rows)
    clash = sorted(set(b_names) & set(w_names))
    if clash:
        raise SystemExit("a name_id stands in both sources: %s" % clash)

    write_csv(os.path.join(args.out, "bigr_rows.csv"), b_rows)
    write_csv(os.path.join(args.out, "wikipedia_rows.csv"), w_rows)

    def tally(rows):
        rm = [r for r in rows if r["same_person"] == "no"]
        rm2 = [r for r in rows if r["same_person"] == "yes" and len(name_words(r["greek_legend"])) != 1]
        return rm, rm2

    b_rm, b_rm2 = tally(b_rows)
    w_rm, w_rm2 = tally(w_rows)
    L = []
    L.append("crossread_coins transcriber A: counts only (no T, no score, no comparison with B)")
    L.append("")
    L.append("BIGR export")
    L.append("  type rows: %d" % st["type_rows"])
    L.append("  rows with a Greek legend on one side and a Kharosthi legend on the other: %d" % st["greek_kharosthi"])
    L.append("  rows with a Greek legend and a Brahmi legend (not used): %d" % st["greek_brahmi"])
    L.append("  other rows with Kharosthi and no Greek side (not used): %d" % st["kharosthi_no_greek"])
    L.append("  authority strings with at least one used row: %d" % st["authority_strings"])
    L.append("  distinct Kharosthi legends (as akshara sequences): %d" % st["distinct_indic_legends"])
    L.append("  akshara types: %d" % st["akshara_types"])
    L.append("  rows in bigr_rows.csv: %d" % len(b_rows))
    L.append("  rows marked different people (for RM): %d rows, %d types" % (len(b_rm), sum(r["n_types"] for r in b_rm)))
    L.append("  rows with zero or 2+ non-title Greek words (for RM2): %d rows, %d types" % (
        len(b_rm2), sum(r["n_types"] for r in b_rm2)))
    L.append("  names with a usable pair: %d" % len(b_names))
    L.append("  Greek spellings of those names: %d" % len(b_words))
    L.append("")
    L.append("Wikipedia")
    L.append("  pinned pages read: %d" % n_pages)
    L.append("  pages that give a passage with both legends: %d" % len(used_pages))
    L.append("  passages listed: %d; kept as rows (name not in BIGR): %d" % (len(w_all), len(w_rows)))
    L.append("  rows marked different people (for RM): %d" % len(w_rm))
    L.append("  rows with zero or 2+ non-title Greek words (for RM2): %d" % len(w_rm2))
    L.append("  names with a usable pair: %d (%s)" % (len(w_names), ", ".join(sorted(w_names))))
    L.append("")
    L.append("NAMES IN A: %d (BIGR %d, Wikipedia %d)" % (len(b_names) + len(w_names), len(b_names), len(w_names)))
    L.append("The sealed gate needs 30 names to pass after the comparison with B.")
    text = "\n".join(L) + "\n"
    with open(os.path.join(args.out, "summary.txt"), "w", encoding="utf-8") as f:
        f.write(text)
    sys.stdout.write(text)
    sys.stdout.write("\nnames from BIGR: %s\n" % ", ".join(sorted(b_names)))


if __name__ == "__main__":
    main()
