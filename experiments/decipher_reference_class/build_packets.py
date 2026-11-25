"""Decipherment reference class: fetch the fixed accounts and build the two coder packets.

Sealed prereg: docs/prereg/decipher_reference_class.md (v2). Nothing here changes it.

Run: python3 -I experiments/decipher_reference_class/build_packets.py OUT_DIR
  OUT_DIR must not exist, or must be an empty directory, and must lie outside the repo.
  The account texts are CC BY-SA and stay out of the repo; only their hashes go in.

Fetches (User-Agent open-research-site/1.0, at most one request per second):
  - each row's Wikipedia page at its fixed revision (api.php action=parse&oldid=...),
  - the revision timestamp and title of each revision (api.php action=query&revids=...),
  - the Mnamon page where the frozen list gives an id.
Writes to OUT_DIR:
  raw/<name>.html          the HTML as fetched
  texts/<name>.txt         each account as plain text
  packet_coder1.md         rows shuffled with seed 20261125
  packet_coder2.md         rows shuffled with seed 20261126
Writes to the repo:
  experiments/decipher_reference_class/packets.sha256

Exit: 0 = packets written, 1 = a fetch failed (nothing is written to the repo; the prereg
says the study stops), 2 = prereg hash mismatch or bad OUT_DIR.
Standard library only.
"""
import hashlib
import html
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from html.parser import HTMLParser

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
PREREG_REL = "docs/prereg/decipher_reference_class.md"
HASHES_REL = "docs/prereg/HASHES.txt"
SHA_REL = "experiments/decipher_reference_class/packets.sha256"

UA = "open-research-site/1.0"
MIN_GAP = 2.5  # seconds between request starts (the limit is one request per second)
WP_API = "https://en.wikipedia.org/w/api.php"
MNAMON = "https://mnamon.sns.it/index.php?page=Scrittura&id=%d&lang=en"
SEEDS = (("coder1", 20261125), ("coder2", 20261126))

# ---- the frozen script list, copied from the prereg -------------------------------------
# (set, number in its table, script name, T as the prereg gives it or None, pages, Mnamon id)
# pages = [(Wikipedia page, revision id), ...]; the first is the script's own page.
# T is None for U, the target row and C: the packet then gives the account date.
_RAW_ROWS = [
    ("D1", 1, "Palmyrene", "1754", [("Palmyrene_alphabet", 1376618079)], None),
    ("D1", 2, "Phoenician", "1758", [("Phoenician_alphabet", 1387525641)], 23),
    ("D1", 3, "Pahlavi", "1791", [("Pahlavi_scripts", 1385710803)], None),
    ("D1", 4, "Demotic", "1816", [("Demotic_Egyptian_script", 1387003548)], 6),
    ("D1", 5, "Lycian", "1821", [("Lycian_alphabet", 1336944040)], 55),
    ("D1", 6, "Egyptian hieroglyphs", "1822",
     [("Egyptian_hieroglyphs", 1387646159),
      ("Decipherment_of_ancient_Egyptian_scripts", 1383048866)], 32),
    ("D1", 7, "Old Persian cuneiform", "1823",
     [("Old_Persian_cuneiform", 1383878573), ("Decipherment_of_cuneiform", 1377477828)], None),
    ("D1", 8, "Brahmi", "1837", [("Brahmi_script", 1385416860)], None),
    ("D1", 9, "Kharosthi", "1837", [("Kharosthi", 1379847884)], None),
    ("D1", 10, "Nabataean", "1840", [("Nabataean_script", 1376893068)], None),
    ("D1", 11, "Libyco-Berber", "1843", [("Libyco-Berber_alphabet", 1382352877)], 47),
    ("D1", 12, "Mesopotamian cuneiform", "1857", [("Cuneiform", 1387668614)], 39),
    ("D1", 13, "Cypriot syllabary", "1871", [("Cypriot_syllabary", 1383916676)], 4),
    ("D1", 14, "Old Turkic", "1893", [("Old_Turkic", 1383724847)], None),
    ("D1", 15, "Oracle bone script", "1899", [("Oracle_bone_script", 1387651602)], None),
    ("D1", 16, "Safaitic", "1901", [("Safaitic", 1385643189)], 66),
    ("D1", 17, "Meroitic", "1909", [("Meroitic_script", 1373940996)], 69),
    ("D1", 18, "Hittite cuneiform", "1915", [("Hittite_cuneiform", 1341776131)], 16),
    ("D1", 19, "Northeastern Iberian", "1922", [("Northeastern_Iberian_script", 1359640333)], 13),
    ("D1", 20, "Ugaritic", "1930", [("Ugaritic_alphabet", 1382309044)], 30),
    ("D1", 21, "Tangut", "1930s", [("Tangut_script", 1369050224)], None),
    ("D1", 22, "Linear B", "1952", [("Linear_B", 1381263317)], 20),
    ("D1", 23, "Maya", "1950s", [("Maya_script", 1387537194)], None),
    ("D1", 24, "Carian", "1980s", [("Carian_language", 1371669903)], 56),
    ("D1", 25, "Caucasian Albanian", "2001", [("Caucasian_Albanian_script", 1375555724)], None),
    ("D1", 26, "Linear Elamite", "2022", [("Linear_Elamite", 1379887485)], 67),
    ("U", 1, "Proto-Elamite", None, [("Proto-Elamite_script", 1377337083)], 9),
    ("U", 2, "Linear A", None, [("Linear_A", 1383661467)], 19),
    ("U", 3, "Cretan hieroglyphs", None, [("Cretan_hieroglyphs", 1386486383)], 35),
    ("U", 4, "Cypro-Minoan", None, [("Cypro-Minoan_script", 1361395878)], 34),
    ("U", 5, "Byblos syllabary", None, [("Byblos_syllabary", 1382993728)], 3),
    ("U", 6, "Rongorongo", None,
     [("Rongorongo", 1386878024), ("Decipherment_of_rongorongo", 1377140952)], None),
    ("U", 7, "Isthmian", None, [("Isthmian_script", 1364788667)], None),
    ("U", 8, "Zapotec", None, [("Zapotec_script", 1364302696)], None),
    ("U", 9, "Khitan large script", None, [("Khitan_large_script", 1384399817)], None),
    ("U", 10, "Khitan small script", None, [("Khitan_small_script", 1375659721)], None),
    ("U", 11, "Southwest Paleohispanic", None,
     [("Southwest_Paleohispanic_script", 1253389624)], None),
    ("U", 12, "Ba–Shu", None, [("Ba–Shu_scripts", 1374117805)], None),
    ("U", 13, "Shankhalipi", None, [("Shankhalipi", 1380173053)], None),
    ("U", 14, "Phaistos Disc", None, [("Phaistos_Disc", 1373685216)], 22),
    ("TARGET", 1, "Indus", None, [("Indus_script", 1383975240)], None),
    ("C", 1, "Proto-Sinaitic", None, [("Proto-Sinaitic_script", 1387678777)], 25),
    ("C", 2, "Kushan script", None, [("Kushan_script", 1375969649)], None),
    ("D2", 1, "Anatolian hieroglyphs", "1973", [("Anatolian_hieroglyphs", 1384294051)], 46),
    ("D2", 2, "Ancient South Arabian", "1841", [("Ancient_South_Arabian_script", 1386224373)], 27),
    ("D2", 3, "Lydian", "1916", [("Lydian_alphabet", 1364001919)], 18),
    ("D2", 4, "Sidetic", "2002", [("Sidetic_language", 1387353954)], None),
]


def _build_rows():
    # Row ids must not show a row's set, so they follow the alphabetical order of the script
    # names, not the order of the prereg tables.
    order = sorted(_RAW_ROWS, key=lambda r: r[2].casefold())
    rows = []
    for i, (st, num, script, t, pages, mn) in enumerate(order, 1):
        rows.append({"row_id": "R%02d" % i, "set": st, "num": num, "script": script, "T": t,
                     "pages": list(pages), "mnamon": mn})
    return rows


ROWS = _build_rows()
ROW_BY_ID = {r["row_id"]: r for r in ROWS}
assert len(ROWS) == 47
assert sum(r["set"] == "D1" for r in ROWS) == 26 and sum(r["set"] == "U" for r in ROWS) == 14

FEATURES = ["LANG_PRIOR", "LANG_HIND", "ANCHOR", "VALUES", "WORDDIV", "CORPUS"]
CSV_COLUMNS = (["row_id", "script"] + FEATURES + [f + "_quote" for f in FEATURES] + ["notes"])


def text_names(row):
    """File stems of a row's saved accounts, Wikipedia first."""
    names = ["%s__wp_%d" % (row["row_id"], rev) for _, rev in row["pages"]]
    if row["mnamon"] is not None:
        names.append("%s__mnamon_%d" % (row["row_id"], row["mnamon"]))
    return names


# ---- fetching ---------------------------------------------------------------------------
_last = [0.0]


def fetch(url):
    """One GET. A 429 or 5xx is a busy server, not a missing page: wait and try again."""
    last_err = None
    for attempt in range(6):
        wait = MIN_GAP - (time.monotonic() - _last[0])
        if wait > 0:
            time.sleep(wait)
        _last[0] = time.monotonic()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as resp:
                if resp.status != 200:
                    raise urllib.error.URLError("HTTP %s" % resp.status)
                return resp.read()
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code != 429 and e.code < 500:
                break
            try:
                pause = float(e.headers.get("Retry-After") or 0)
            except ValueError:
                pause = 0.0
            time.sleep(min(max(pause, 20.0 * (attempt + 1)), 180.0))
        except (urllib.error.URLError, OSError, ValueError) as e:
            last_err = e
            time.sleep(5.0 * (attempt + 1))
    raise RuntimeError("fetch failed: %s" % last_err)


# ---- HTML to plain text -----------------------------------------------------------------
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source",
        "track", "wbr"}
BLOCK = {"p", "div", "h1", "h2", "h3", "h4", "h5", "h6", "li", "ul", "ol", "dl", "dt", "dd",
         "tr", "table", "blockquote", "pre", "section", "figure", "figcaption", "caption",
         "br", "hr"}
DROP_TAGS = {"script", "style", "noscript", "nav", "form", "select", "button"}
# PREREG-AMBIGUITY: the prereg says "the saved text" of a page and does not say which parts of
# the rendered page count. Kept: all prose, tables, infoboxes, notes and reference lists.
# Dropped: navigation boxes and site chrome (they are link lists, not the account), the
# bracketed footnote markers (they would break a quoted sentence in two) and edit links.
WP_DROP = {"navbox", "navbox-styles", "navbar", "mw-editsection", "reference",
           "mw-cite-backlink", "shortdescription", "mw-empty-elt", "Z3988", "side-box",
           "sistersitebox", "catlinks", "printfooter"}
MN_DROP = {"header", "footer", "breadcrumb", "vertical_menu", "logo"}


class Plain(HTMLParser):
    def __init__(self, drop_classes):
        super().__init__(convert_charrefs=True)
        self.drop = drop_classes
        self.stack = []
        self.skip_at = None
        self.out = []

    def handle_starttag(self, tag, attrs):
        if tag in BLOCK and self.skip_at is None:
            self.out.append("\n")
        if tag in VOID:
            return
        self.stack.append(tag)
        if self.skip_at is None:
            classes = set((dict(attrs).get("class") or "").split())
            if tag in DROP_TAGS or classes & self.drop:
                self.skip_at = len(self.stack)

    def handle_endtag(self, tag):
        if tag in VOID or tag not in self.stack:
            return
        while self.stack:
            top = self.stack.pop()
            if self.skip_at is not None and len(self.stack) < self.skip_at:
                self.skip_at = None
            if top == tag:
                break
        if self.skip_at is None:
            if tag in ("td", "th"):
                self.out.append(" | ")
            elif tag in BLOCK:
                self.out.append("\n")

    def handle_data(self, data):
        if self.skip_at is None:
            self.out.append(data)


def to_text(markup, drop_classes):
    p = Plain(drop_classes)
    p.feed(markup)
    p.close()
    text = html.unescape("".join(p.out)).replace(" ", " ")
    lines = []
    for line in text.split("\n"):
        line = re.sub(r"[ \t\r\f\v]+", " ", line).strip()
        line = re.sub(r"^(\| )+|( \|)+$", "", line).strip()
        if line and line != "|":
            lines.append(line)
    return "\n".join(lines) + "\n"


def sha(data):
    return hashlib.sha256(data).hexdigest()


# ---- the packet -------------------------------------------------------------------------
def codebook_text():
    with open(os.path.join(ROOT, PREREG_REL), "rb") as f:
        raw = f.read()
    digest = sha(raw)
    sealed = None
    with open(os.path.join(ROOT, HASHES_REL), encoding="utf-8") as f:
        for line in f:
            parts = line.split()
            if len(parts) >= 2 and parts[1] == PREREG_REL:
                sealed = parts[0]
    if sealed != digest:
        print("prereg hash mismatch: file %s, sealed %s" % (digest, sealed))
        sys.exit(2)
    text = raw.decode("utf-8")
    start = text.index("## Codebook (frozen)")
    # The "Indus profile" subsection sits under the codebook heading but is the project's own
    # coding of the target row. The protocol says a coder is not told the target, so the
    # codebook given to a coder ends where that subsection begins.
    end = text.index("### Indus profile, stated now")
    book = text[start:end].rstrip() + "\n"
    assert "Indus" not in book
    return book


RETURN_INSTRUCTIONS = """## How to return your codes

Return one CSV file with a header line and exactly one line per row of this packet.
Quote every field that contains a comma, a double quote or a line break, in the usual CSV
way (wrap it in double quotes and double any double quote inside it).

Columns, in this order:

{cols}

- `row_id` and `script`: copied from the row heading.
- `LANG_PRIOR`: `0`, `1` or `NS`.
- `LANG_HIND`: `0`, `1` or `NS`. Write `NA` where the row says `LANG_HIND: NA`.
- `ANCHOR`, `VALUES`, `WORDDIV`: `0`, `1`, `2` or `NS`.
- `CORPUS`: `A`, `B`, `C`, `D` or `NS`.
- Each `..._quote` column: the one sentence that supports that code, copied character for
  character from an account text of the same row. Do not shorten it, join two passages or
  add an ellipsis. Leave it empty only where the code is `NS` or `NA`.
- `notes`: optional. Use it where the codebook asks you to say something, such as a conflict
  between two accounts or a corpus size you got by multiplying.

Code every row. Use only this packet.
"""


def build_packet(order, book, texts, when):
    parts = ["# Coding packet\n",
             "This packet holds a codebook, the format for your answer, and %d rows. Each row is "
             "a script with one or more account texts.\n" % len(order),
             book,
             RETURN_INSTRUCTIONS.format(cols="`" + ", ".join(CSV_COLUMNS) + "`"),
             "## Rows\n"]
    for rid in order:
        row = ROW_BY_ID[rid]
        head = ["=" * 78, "ROW %s" % rid, "Script: %s" % row["script"]]
        if row["T"] is not None:
            head.append("T: %s" % row["T"])
        else:
            # PREREG-AMBIGUITY: for rows off the timeline the prereg gives T as "the account
            # date" and does not define it. Used here: the date of the Wikipedia revision of
            # the script's own page.
            head.append("T: %s (the account date)" % when[row["pages"][0][1]])
            head.append("LANG_HIND: NA")
        parts.append("\n".join(head) + "\n")
        n_wp = len(row["pages"])
        for i, (page, rev) in enumerate(row["pages"]):
            label = "Wikipedia account" if n_wp == 1 else "Wikipedia account, page %d of %d" % (i + 1, n_wp)
            parts.append("--- %s: \"%s\" ---\n%s" % (
                label, page.replace("_", " "), texts["%s__wp_%d" % (rid, rev)]))
        if row["mnamon"] is not None:
            parts.append("--- Mnamon account ---\n%s" % texts["%s__mnamon_%d" % (rid, row["mnamon"])])
        parts.append("END OF ROW %s\n" % rid)
    return "\n".join(parts)


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    out = os.path.abspath(sys.argv[1])
    if os.path.commonpath([out, ROOT]) == ROOT:
        print("OUT_DIR must be outside the repo")
        sys.exit(2)
    if os.path.exists(out) and (not os.path.isdir(out) or os.listdir(out)):
        print("OUT_DIR must be new or empty")
        sys.exit(2)
    book = codebook_text()
    os.makedirs(os.path.join(out, "raw"))
    os.makedirs(os.path.join(out, "texts"))

    failures = []
    texts = {}
    meta = {}  # stem -> label for packets.sha256

    # 1. revision titles and dates
    revs = [(page, rev) for r in ROWS for page, rev in r["pages"]]
    when = {}
    for i in range(0, len(revs), 40):
        chunk = revs[i:i + 40]
        url = WP_API + "?" + urllib.parse.urlencode({
            "action": "query", "prop": "revisions", "rvprop": "ids|timestamp",
            "revids": "|".join(str(rev) for _, rev in chunk), "format": "json",
            "formatversion": "2"})
        try:
            data = json.loads(fetch(url))
            for pg in data["query"].get("pages", []):
                for rv in pg.get("revisions", []):
                    when[rv["revid"]] = (rv["timestamp"][:10], pg["title"])
        except Exception as e:  # noqa: BLE001
            failures.append("revision lookup: %s" % e)
    for page, rev in revs:
        if rev not in when:
            failures.append("revision %d (%s): not found" % (rev, page))
        elif when[rev][1] != page.replace("_", " "):
            failures.append("revision %d: title is %r, the list says %r" % (rev, when[rev][1], page))
    dates = {rev: v[0] for rev, v in when.items()}

    # 2. the accounts
    for row in ROWS:
        rid = row["row_id"]
        for page, rev in row["pages"]:
            stem = "%s__wp_%d" % (rid, rev)
            url = WP_API + "?" + urllib.parse.urlencode({
                "action": "parse", "oldid": str(rev), "prop": "text", "format": "json",
                "formatversion": "2", "disableeditsection": "1", "disabletoc": "1"})
            try:
                data = json.loads(fetch(url))
                markup = data["parse"]["text"]
                if data["parse"].get("revid", rev) != rev:
                    raise RuntimeError("API returned revision %s" % data["parse"].get("revid"))
                text = to_text(markup, WP_DROP)
                if len(text) < 1500:
                    raise RuntimeError("converted text is only %d characters" % len(text))
            except Exception as e:  # noqa: BLE001
                failures.append("%s %s oldid=%d: %s" % (rid, page, rev, e))
                continue
            with open(os.path.join(out, "raw", stem + ".html"), "w", encoding="utf-8") as f:
                f.write(markup)
            texts[stem] = text
            meta[stem] = "wikipedia rev=%d page=%s rev_date=%s" % (rev, page, dates.get(rev, "?"))
            print("ok %s %s (%d chars)" % (stem, page, len(text)), flush=True)
        if row["mnamon"] is not None:
            stem = "%s__mnamon_%d" % (rid, row["mnamon"])
            try:
                rawb = fetch(MNAMON % row["mnamon"])
                markup = rawb.decode("utf-8", errors="replace")
                text = to_text(markup, MN_DROP)
                if len(text) < 300:
                    raise RuntimeError("converted text is only %d characters" % len(text))
            except Exception as e:  # noqa: BLE001
                failures.append("%s mnamon id=%d: %s" % (rid, row["mnamon"], e))
                continue
            with open(os.path.join(out, "raw", stem + ".html"), "wb") as f:
                f.write(rawb)
            texts[stem] = text
            meta[stem] = "mnamon id=%d unversioned fetched=%s" % (
                row["mnamon"], time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
            print("ok %s (%d chars)" % (stem, len(text)), flush=True)

    if failures:
        print("\nFETCH FAILURES (%d). No packet written; the prereg says the study stops." % len(failures))
        for f_ in failures:
            print("  " + f_)
        sys.exit(1)

    lines = []
    for row in ROWS:
        for stem in text_names(row):
            data = texts[stem].encode("utf-8")
            with open(os.path.join(out, "texts", stem + ".txt"), "wb") as f:
                f.write(data)
            lines.append("%s  texts/%s.txt  %s" % (sha(data), stem, meta[stem]))
    canonical = [r["row_id"] for r in ROWS]
    for name, seed in SEEDS:
        order = list(canonical)
        random.Random(seed).shuffle(order)
        data = build_packet(order, book, texts, dates).encode("utf-8")
        fname = "packet_%s.md" % name
        with open(os.path.join(out, fname), "wb") as f:
            f.write(data)
        lines.append("%s  %s  packet seed=%d rows=%d bytes=%d" % (sha(data), fname, seed, len(order), len(data)))
        print("packet %s: %d rows, %d bytes" % (fname, len(order), len(data)))
    with open(os.path.join(ROOT, SHA_REL), "w", encoding="utf-8") as f:
        f.write("# sha256  file (relative to the packet directory, which is outside the repo)  source\n")
        f.write("\n".join(lines) + "\n")
    print("wrote %s (%d texts, %d packets)" % (SHA_REL, len(texts), len(SEEDS)))


if __name__ == "__main__":
    main()
