#!/usr/bin/env python3
"""Build the public website in site/ from templates and the repo's own data.

Run from the repo root:   .venv/bin/python -I site/build.py

What it reads
  site/templates/*.html      page templates ({{KEY}} placeholders)
  site/starter_tasks.json    starter tasks for outside contributors
  board/board.db             live task board (read-only). If it is absent, as in a public
                             clone, the last snapshot in site/data/board_snapshot.json is used.
  docs/NEGATIVE_ATLAS.md     closed routes and red-team reversals
  docs/prereg/HASHES.txt, docs/test_ledger.csv   counts shown on the pages
  experiments/plate_corpus/crops/plate_*.png     seal photographs (excavation reports, 1931-1940)
  data/sign_images/M*.png    sign drawings (see LICENSING.md: provenance flagged)

  site/font/OpenIndus-*.ttf|woff2, OFL.txt   the typeface (made in site/font/, copied, never edited here)

What it writes
  site/index.html, findings.html, tracker.html, contribute.html, resources.html
  site/assets/img/*.jpg, site/assets/glyphs.css, site/data/board_snapshot.json
  site/assets/fonts/ (copied from site/font/), site/assets/signs/ (the sign drawings the landing page uses),
  site/assets/downloads/ (logo files offered on the Resources page)

Then it checks every internal link and #anchor in the pages it wrote and stops with an error if one is broken.

Everything is static and works from file:// and from GitHub Pages serving site/.
"""
import base64
import csv
import html
import html.parser
import io
import json
import re
import shutil
import sqlite3
import time
from pathlib import Path

from PIL import Image

# ---------------------------------------------------------------- config
NAME = "Open Indus"                                # the group's name, used everywhere
REPO_URL = "https://github.com/OWNER/REPO"         # placeholder until the repo exists
BRANCH = "main"
CONTACT_NOTE = "Open an issue on GitHub."           # the only contact route on the site
GOAL = "Decipher the Indus script by 2027"          # the mission; site/make_repo_files.py also reads it
CONDUCT_CONTACT = ""                                # private route for conduct reports; empty = not decided yet
PREVIEW = True                                      # unlisted preview: every page says noindex, nofollow. Set False at launch.
# ------------------------------------------------------------------------

SITE = Path(__file__).resolve().parent
ROOT = SITE.parent
TPL = SITE / "templates"
IMG_OUT = SITE / "assets" / "img"
E = html.escape


def blob(path):
    kind = "tree" if path.endswith("/") or "." not in path.rsplit("/", 1)[-1] else "blob"
    return f"{REPO_URL}/{kind}/{BRANCH}/{path.rstrip('/')}"


def repo_link(path, label=None):
    return f'<a class="file" href="{E(blob(path))}">{E(label or path)}</a>'


# ---------------------------------------------------------------- images
# Plate crops: scans of 1931-1940 excavation reports. The uploads were enlarged 3-6x by pixel
# replication, so real detail is far below the pixel size. We never upscale: every image is
# saved at or below its file size, and CSS shows it at no more than half its pixel width.
PLATES = {
    "EH_3":    dict(site="Harappa", what="Seal", src="Vats, Excavations at Harappa (1940), seal no. 3", mm="56 × 56 mm"),
    "EH_16":   dict(site="Harappa", what="Seal", src="Vats, Excavations at Harappa (1940), seal no. 16", mm="41 × 41 mm"),
    "EH_286":  dict(site="Harappa", what="Seal", src="Vats, Excavations at Harappa (1940), seal no. 286", mm="15 × 14 mm"),
    "FEM_273": dict(site="Mohenjo-daro", what="Seal impression", src="Mackay, Further Excavations at Mohenjo-daro (1938), no. 273", mm="41 × 15 mm", trim=0.12),
    "FEM_289": dict(site="Mohenjo-daro", what="Seal impression", src="Mackay, Further Excavations at Mohenjo-daro (1938), no. 289", mm="29 × 12 mm", trim=0.12),
    "FEM_461": dict(site="Mohenjo-daro", what="Seal impression", src="Mackay, Further Excavations at Mohenjo-daro (1938), no. 461", mm="36 × 17 mm", trim=0.06),
    "FEM_407": dict(site="Mohenjo-daro", what="Seal impression", src="Mackay, Further Excavations at Mohenjo-daro (1938), no. 407", mm="24 × 24 mm"),
    "FEM_420": dict(site="Mohenjo-daro", what="Seal impression", src="Mackay, Further Excavations at Mohenjo-daro (1938), no. 420", mm="36 × 35 mm"),
    "MIC_91":  dict(site="Mohenjo-daro", what="Seal", src="Marshall, Mohenjo-daro and the Indus Civilization (1931), seal no. 91", mm="32 × 34 mm"),
}


def plate_img(key):
    """Save a greyscale JPEG at (never above) the crop's own pixel size. Return width, height, path."""
    meta = PLATES[key]
    im = Image.open(ROOT / f"experiments/plate_corpus/crops/plate_{key}.png").convert("L")
    if meta.get("trim"):                       # cut the printed plate number off the bottom edge
        im = im.crop((0, 0, im.width, round(im.height * (1 - meta["trim"]))))
    if im.width > 900:
        im.thumbnail((900, 900))
    IMG_OUT.mkdir(parents=True, exist_ok=True)
    out = IMG_OUT / f"{key.lower()}.jpg"
    im.save(out, "JPEG", quality=82, optimize=True)
    return im.width, im.height, f"assets/img/{out.name}"


def figure(key, plate_no, alt, cls=""):
    w, h, src = plate_img(key)
    m = PLATES[key]
    show = round(w / 2)                       # never shown wider than half its pixels
    return (f'<figure class="plate {cls}" style="--w:{show}px">'
            f'<div class="plate-ground"><img src="{src}" width="{w}" height="{h}" alt="{E(alt)}" {'fetchpriority="high"' if plate_no == 1 else 'loading="lazy"'} decoding="async"></div>'
            f'<figcaption><span class="cat">Pl. {plate_no} · {E(m["site"])} · {E(m["mm"]).replace(" ", "&nbsp;")}</span>'
            f'<span>{E(m["what"])}. {E(m["src"])}.</span></figcaption></figure>')


GLYPHS = [59, 60, 65, 66, 67, 109, 342, 99, 176, 267, 391]


def glyph_css():
    rules = []
    for n in GLYPHS:
        b64 = base64.b64encode((ROOT / f"data/sign_images/M{n}.png").read_bytes()).decode()
        rules.append(f"  --g{n}: url(data:image/png;base64,{b64});")
    css = ("/* Generated by site/build.py. Sign drawings after Mahadevan 1977 (see LICENSING.md). */\n"
           ":root {\n" + "\n".join(rules) + "\n}\n")
    (SITE / "assets" / "glyphs.css").write_text(css)


SIGN_NAMES = {59: "fish", 60: "fish with four ticks", 65: "fish with a roof", 66: "roofed fish with ticks",
              67: "fish with side strokes", 109: "six strokes", 342: "jar", 99: "two strokes", 176: "comb",
              267: "diamond", 391: "oval with spokes"}


def sig(n):
    return (f'<i class="sig" style="--g:var(--g{n})" role="img" aria-label="sign M{n}, {SIGN_NAMES[n]}"></i>')


# ---------------------------------------------------------------- repo data
def board():
    """Live board, read-only. Falls back to the snapshot written by the last build."""
    snap = SITE / "data" / "board_snapshot.json"
    db = ROOT / "board" / "board.db"
    if not db.exists():
        return json.loads(snap.read_text())
    c = sqlite3.connect(f"file:{db}?mode=ro", uri=True)
    landed = {t: dict(verdict=v, path=p, summary=s) for t, v, p, s in
              c.execute("SELECT task, verdict, path, summary FROM landed ORDER BY id")}
    tasks = []
    for i, ms, title, deps, status, owner in c.execute("SELECT id, milestone, title, deps, status, owner FROM tasks ORDER BY id"):
        ids = [int(x) for x in (deps or "").split(",") if x.strip()]
        done_deps = True
        if ids:
            q = "SELECT COUNT(*) FROM tasks WHERE status='done' AND id IN (%s)" % ",".join("?" * len(ids))
            done_deps = c.execute(q, ids).fetchone()[0] == len(ids)
        state = "done" if status == "done" else "running" if status == "claimed" else "ready" if done_deps else "blocked"
        t = dict(id=i, ms=ms, title=title, state=state, owner=owner or "", waits=[] if done_deps else ids)
        t.update(landed.get(i, {}))
        tasks.append(t)
    data = dict(tasks=tasks, snapshot=time.strftime("%Y-%m-%d %H:%M"))
    snap.parent.mkdir(exist_ok=True)
    snap.write_text(json.dumps(data, indent=1))
    return data


def counts():
    hashes = (ROOT / "docs/prereg/HASHES.txt").read_text().splitlines()
    prereg_files = {l.split()[1] for l in hashes if len(l.split()) > 1 and l.split()[1].startswith("docs/prereg/")}
    with open(ROOT / "docs/test_ledger.csv", newline="") as f:
        ledger = sum(1 for _ in csv.DictReader(f))
    first = hashes[0].split()
    return dict(prereg=len(prereg_files), hash_lines=len(hashes), ledger=ledger,
                sample_hash=first[0], sample_file=first[1], sample_time=first[2] if len(first) > 2 else "")


def atlas():
    """Parse docs/NEGATIVE_ATLAS.md: sections, entry folders, summary table, red-team reversals."""
    text = (ROOT / "docs/NEGATIVE_ATLAS.md").read_text()
    sections, folders, cur = {}, {}, None
    for line in text.splitlines():
        m = re.match(r"^## (\d+b?)\. (.+)$", line)
        if m:
            sections[m.group(1)] = m.group(2).split(" (")[0]
        m = re.match(r"^### (\d+b?\.\d+) ", line)
        if m:
            cur = m.group(1)
        m = re.match(r"^- \*\*Folder\.\*\* (.+)$", line)
        if m and cur:
            folders[cur] = re.findall(r"`(experiments/[\w\-]+)`", m.group(1))
    rows = []
    table = text.split("## 12. Summary table", 1)[1]
    for line in table.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 5 and re.match(r"^\d+b?\.\d+$", cells[0]):
            num, route, verdict, power, reopen = cells
            sec = num.split(".")[0]
            rows.append(dict(num=num, sec=sec, route=route, verdict=verdict, power=power, reopen=reopen,
                             folders=folders.get(num, [])))
    rev = []
    block = text.split("## 11. Red-team reversals", 1)[1].split("## 12.", 1)[0]
    for m in re.finditer(r"^\d+\. \*\*(.+?)\*\* (.+)$", block, re.M):
        rev.append(dict(title=m.group(1).rstrip("."), text=m.group(2)))
    return sections, rows, rev


def verdict_kind(v):
    v = v.lower()
    if v.startswith("refuted"):
        return "out", "Ruled out"
    if v.startswith(("untestable", "undecidable", "underpowered")):
        return "wait", "Can't test yet"
    if v.startswith(("weakened", "reversed", "withdrawn")):
        return "weak", "Weakened"
    return "weak", "Not supported"


# ---------------------------------------------------------------- content
LEVELS = {
    "strong": ("Strong", "Held up on texts the method had not seen, survived an independent attack, and survives correction for every test the project ran."),
    "moderate": ("Moderate", "Held up on unseen texts, but rests on small numbers or weakens after correction for all tests."),
    "weak": ("Weak", "The broad pattern is real; the specific claim is barely supported."),
    "exploratory": ("Exploratory", "Found while looking at all the data. Not yet tested on unseen texts."),
    "descriptive": ("Descriptive", "A measurement, not a test of a hypothesis."),
}

FINDINGS = [
    dict(n=1, level="strong", title="Sign order follows rules, not just positions",
         plain="Knowing the signs of an unseen text, the real order can be picked out from all orderings of the same signs far more often than chance. It still works with the commonest signs removed.",
         nums="40% of 321 held-out runs vs 5.7% by chance; q ≈ 8e-72",
         folders=["experiments/structure", "experiments/redteam", "experiments/revalidation"]),
    dict(n=2, level="descriptive", title="About 400 signs: word-signs mixed with sound-signs",
         plain="The sign count and how often each sign is used look like Proto-Elamite or Sumerian, not like Linear B or an alphabet.",
         nums="≈400 signs (≈565 with unseen ones; 95% CI 508–658); 120 signs cover 90% of uses (Linear B: 63, Latin: 14)",
         folders=["experiments/structure"]),
    dict(n=3, level="moderate", title="Corner ticks move the fish sign to the end of the text",
         plain="A fish with four small ticks closes a text far more often than a plain fish: a mark inside a sign that changes where the sign goes.",
         glyphs=(59, 60),
         nums="final in 40 of 73 vs 26% expected (p = 1e-7); held-out 11 of 19 vs 7% for plain fish (p = 0.004; q = 0.03 within its family, 0.54 across all tests)",
         folders=["experiments/novel_methods", "experiments/redteam"]),
    dict(n=4, level="moderate", title="Round Gulf-type seals break normal sign order, wherever they were found",
         plain="Round seals of the Gulf type, found abroad or at home, do not follow the usual sign order. This fits Indus signs used to write another language, but plainer explanations are not ruled out.",
         nums="order excess +1.64 bits/sign on 8 home round seals (Holm p = 3e-4, rare-sign-matched null); foreign vs home round +0.11 (p = 0.66)",
         caveat="Corrected on 17 Nov 2026: a label error had hidden the home round seals. Only 3 of the 8 are confirmed round in a printed excavation report.",
         folders=["experiments/round_label_audit", "experiments/redteam_round_format", "experiments/redteam_round_order"]),
    dict(n=5, level="strong", title="Six followed by fish is a fixed expression",
         plain="The six-stroke sign followed by the fish behaves like one set phrase. The proposed 'seven stars' reading of seven plus fish has almost no support.",
         glyphs=(109, 59),
         nums="held-out 7 of 10 vs 3% base rate; q ≈ 6e-8",
         folders=["experiments/language", "experiments/redteam"]),
    dict(n=6, level="strong", title="Each kind of object has its own vocabulary",
         plain="Seals, tablets, copper tablets, rods and pottery each favour different signs, enough to tell them apart on unseen texts.",
         nums="held-out AUC: copper 0.87, tablet 0.76, pottery 0.73, seal 0.72, sealing 0.67 (chance ceiling 0.55–0.61)",
         folders=["experiments/context", "experiments/redteam"]),
    dict(n=7, level="strong", title="Texts written left to right are true reversals",
         plain="The few texts that run left to right are written backwards on purpose, not misread.",
         nums="31 of 34 copy-free lines; q = 6e-6",
         folders=["experiments/structure", "experiments/redteam"]),
    dict(n=8, level="exploratory", title="Copper tablets come in a few dozen fixed types",
         plain="Copper tablets repeat about 18 to 64 fixed text-and-picture types. A one-sign face can stand in for the picture, but the sign does not depict it.",
         nums="same legend → same sign face 8 of 8 (p = 1e-4, all data); blind matching 5 of 24 vs 3.3 by chance",
         folders=["experiments/context", "experiments/logograms"]),
    dict(n=9, level="weak", title="Texts can be parsed into a small set of roles",
         plain="An 11-role reading parses most unseen texts, far more than shuffled ones. That positional roles exist is solid; that these 11 are the right ones is not.",
         nums="parses 76% of unseen texts vs 44% for shuffles; specific roles p = 0.013, q = 0.085",
         folders=["experiments/functional_reading", "experiments/grammar"]),
    dict(n=10, level="moderate", title="The core of a seal text is one or two word-signs",
         plain="The part of a seal text between its fixed opening and closing signs is short and made of whole words, not spelled out sound by sound.",
         nums="34% of cores are one sign; recurring pairs keep one order in 91% of uses (held-out 115 of 138, p = 3e-16)",
         folders=["experiments/typology", "experiments/core_semantics"]),
    dict(n=11, level="moderate", title="The fish signs form one word class",
         plain="Six fish signs swap for each other, combine with each other and share partners. The idea that fish signs are god names is not supported.",
         nums="held-out p = 0.0002–0.0004",
         folders=["experiments/core_semantics"]),
]

CLOSED_SHORT = [
    ("Published sound keys", "Five tested, including the 185-sign key from 2026. None beats its own values shuffled."),
    ("Guessing the language from statistics", "The same method calls real Latin 'Munda'. It cannot pick a language."),
    ("Signs that picture their meaning", "No pictorial sign is tied to the matching picture on its seal (17 tests)."),
    ("Names, titles and places in the texts", "No 'son of', no place names that travel, no household signature."),
    ("A sound grid like Linear B's", "The method finds one in made-up syllabic scripts. In Indus it finds nothing."),
    ("The 2026 'registration code' reading", "Its own predictions fail on 646 seals."),
]

PLAN = [
    ("ok", "Collect every Indus-sign object found abroad", "Done", "55 objects. 41 have two or more readable signs, and only 9 of their readings are safe."),
    ("ok", "List the names their owners could have had", "Done", "7,776 names from cuneiform records, and 50 Elamite names. No list of Gulf names exists."),
    ("fail", "Prove the name-matching method on planted data", "Failed as designed", "With a long name list, the true answer scores below answers fitted to noise, even at 120 texts."),
    ("next", "Redesign it, then try it on Linear Elamite", "Running", "Short name lists, exact matches only. Linear Elamite was deciphered in 2022, so the right answer is known. If the method fails there, it stops."),
    ("", "Run it on the round seals, home and abroad", "Waiting", "If names fit the home seals as well as the foreign ones, the method is fitting the seal type, not names."),
]

DATA_ASKS = [
    ("Excavation records", "Records of inscribed objects from recent excavations at Harappa, with which seals, sealings and sherds were found together.",
     "Household and office tests, the bangle test and the potter's-mark test are all stalled on this."),
    ("Photographs of seals found abroad", "High-resolution photographs of the Indus-style seal from Ur (British Museum 120573) and of Susa tablet Sb 9382 (Louvre).",
     "Only 9 foreign readings are safe. Each checked reading matters at this sample size."),
    ("Seal impressions on cuneiform tablets", "Images of the seal impressions on tablets that name men of Meluhha.",
     "The one route to a seal tied to a person whose name is written in a readable script."),
    ("New and unpublished texts", "Inscriptions found or published since 2010, with photographs or reliable drawings.",
     "38 predictions are frozen and waiting to be scored on texts nobody here has seen."),
    ("Better scans of old plates", "Greyscale scans at 600 dpi or more of the 1930s excavation plates and of the published scene tablets.",
     "Tests on pictures stalled at about 100 dpi, where the details cannot be seen."),
]

PAPERS = [
    ("A fair test bench for Indus sound keys", "Paper and code", "ready",
     "Five published readings, including the 185-sign key from 2026, score no better than their own values shuffled. The bench and its planted checks can be released for any new claim."),
    ("Round Gulf-type seals break Indus sign order, at home and abroad", "Short paper", "needs-check",
     "Passed two independent attacks. Before publishing, the shape of 5 of the 8 home seals needs checking, and a specialist should review the readings."),
    ("Structure of the script on unseen texts", "Paper", "ready",
     "Sign order predicted on held-out texts, the ticked fish that moves to the closing slot, and six plus fish as a fixed expression."),
    ("An atlas of closed routes", "Open dataset", "ready",
     "Over 80 tested routes, each with the size of effect its test could have caught, so nobody has to repeat them."),
    ("A small agent team with a shared task board", "Tool and write-up", "later",
     "The task board, the claim and red-team rules and the compute gate, as a reusable pattern for research with AI agents."),
]

GROUPS = [
    ("code", "Programmers and statisticians",
     "Re-implement a finding from its description, write a fairer null for an old test, or make the tools easier to run. Every result in the repo can be checked from code."),
    ("specialist", "Epigraphists, archaeologists and Assyriologists",
     "Check readings against published photographs, confirm what an object is, build name lists from cuneiform sources, and tell us where our assumptions are wrong."),
    ("collections", "Museums and collection holders",
     "Photographs, excavation records and new texts unblock tests that no amount of code can. We cite every source and publish what we find, positive or negative."),
    ("readings", "Anyone with a reading to test",
     "If you have a sign-to-sound key or a proposed meaning, the bench will score it against its own shuffled values and against keys fitted to noise. The result is published either way."),
]


# ---------------------------------------------------------------- HTML pieces
def bar(label, value, maxv, shown, kind="obs"):
    pct = max(0.0, min(100.0, 100 * value / maxv))
    return (f'<div class="bar"><span class="bl">{label}</span>'
            f'<span class="track"><span class="fill {kind}" style="width:{pct:.2f}%"></span></span>'
            f'<span class="bv">{shown}</span></div>')


def chart_patterns():
    rows = [
        ("Sign order picked out on unseen texts", None, 40, "40%", 5.7, "5.7%"),
        ("Fish with ticks {a} → {b} closes the text", (59, 60), 55, "40 of 73", 26, "26%"),
        ("Six {a} is followed by fish {b}", (109, 59), 70, "7 of 10", 3, "3%"),
        ("Seals found abroad break the order", None, 24, "9 of 38", 5, "5%"),
    ]
    out = ['<div class="chart" role="group" aria-label="Observed rate compared with the rate expected by chance, 0 to 100 percent">',
           '<div class="legend"><span><i class="key obs"></i>Observed</span><span><i class="key chance"></i>Expected by chance</span></div>']
    for lab, gl, o, os_, c, cs in rows:
        if gl:
            lab = lab.format(a=sig(gl[0]), b=sig(gl[1]))
        out.append(f'<div class="pair"><div class="pl">{lab}</div>{bar("Observed", o, 100, os_)}{bar("Chance", c, 100, cs, "chance")}</div>')
    out.append('<div class="axis" aria-hidden="true"><span>0</span><span>50%</span><span>100%</span></div></div>')
    return "\n".join(out)


def chart_round():
    return ('<div class="chart" role="group" aria-label="Distance from normal sign order, bits per sign, 0 to 2">'
            '<div class="pair"><div class="pl">Distance from normal sign order, in bits per sign</div>'
            + bar("Round, found abroad", 1.75, 2, "+1.75")
            + bar("Round, Indus region", 1.64, 2, "+1.64")
            + bar("Ordinary seals", 0.0, 2, "0", "chance")
            + '</div><div class="axis" aria-hidden="true"><span>0</span><span>1</span><span>2 bits</span></div></div>')


def chart_names():
    sizes = [("2,500", 12), ("10,000", 10), ("50,000", 18), ("230,000", 22)]
    anchors = [("None", 17), ("5", 37), ("10", 47), ("20", 68)]
    a = ['<figure class="mini"><figcaption class="claim">More text barely helps</figcaption>'
         '<div class="chart" role="group" aria-label="Share of sign values recovered by text size, related language known">',
         '<div class="pair"><div class="pl">Sign values recovered, by text size in signs</div>']
    for s, v in sizes:
        a.append(bar(s + (' <em>≈ Indus</em>' if s == "10,000" else ""), v, 100, f"{v}%"))
    a.append('</div><div class="axis" aria-hidden="true"><span>0</span><span>50%</span><span>100%</span></div></div></figure>')
    b = ['<figure class="mini"><figcaption class="claim">Known names do</figcaption>'
         '<div class="chart" role="group" aria-label="Share of sign values recovered by number of sign values known from names">',
         '<div class="pair"><div class="pl">Sign values recovered, by values known from names</div>']
    for s, v in anchors:
        b.append(bar(s, v, 100, f"{v}%"))
    b.append('</div><div class="axis" aria-hidden="true"><span>0</span><span>50%</span><span>100%</span></div></div></figure>')
    return '<div class="minis">' + "".join(a) + "".join(b) + "</div>"


def ladder(caption=True):
    rungs = [("done", "Structure", "order, slots"), ("part", "Sign roles", "openers, closers"),
             ("", "Topic", "what a sign is about"), ("", "Meaning", "one sign, one thing"), ("", "Sound", "a reading")]
    cells = "".join(f'<li class="rung r{i+1} {c}"><b>{t}</b><span>{d}</span></li>' for i, (c, t, d) in enumerate(rungs))
    cap = '<figcaption class="claim">The goal is the top step</figcaption>' if caption else ""
    return (f'<figure class="ladder-fig">{cap}'
            f'<ol class="ladder" aria-label="Five kinds of claim, weakest first. Structure: done. Sign roles: partly done. Topic, meaning and sound: open.">{cells}</ol>'
            f'<div class="ladder-key" aria-hidden="true"><span><i class="key obs"></i>Done</span><span><i class="key half"></i>Partly done</span><span><i class="key open"></i>Open</span></div></figure>')



def slots(note=""):
    """Distance to root milestone R: sound values for 10 signs that pass the bench and a red team. Drawn to scale."""
    have, need = 0, 10
    cells = "".join(f'<li class="slot{" on" if i < have else ""}"></li>' for i in range(need))
    return (f'<figure class="goal-fig"><figcaption class="claim">{have} of {need} signs have a tested sound value</figcaption>'
            f'<ol class="slots" aria-label="{have} of {need} signs with a sound value that passed the bench and a red team">{cells}</ol>{note}</figure>')


def goal():
    return ladder() + slots('<p class="note">Done means 10 signs whose sound values beat chance and survive a red team. Honest odds by 2027 are under 1 in 10. '
                            '<a href="approach.html#goal">What counts as done, and why the odds are low</a></p>')


FISH_D = ['M16 3.56C9.18 9.28 8.74 16.32 16 23.14L21.05 27.88', 'M16 3.56C22.82 9.28 23.26 16.32 16 23.14L10.95 27.88', 'M11.71 17.44L8.67 19.82M20.29 17.44L23.33 19.82']


FONT_FILES = ["OpenIndus-Regular.woff2", "OpenIndus-Bold.woff2", "OpenIndus-Regular.ttf", "OpenIndus-Bold.ttf",
              "OpenIndusText-Regular.woff2", "OpenIndusText-Bold.woff2", "OpenIndusText-Regular.ttf", "OpenIndusText-Bold.ttf", "OFL.txt"]
NO_SIGN = {148}   # never shown: M148 is a swastika-like sign, too easily misread out of context


def slug():
    return re.sub(r"[^a-z0-9]+", "-", NAME.lower()).strip("-")


def copy_font():
    """Copy the typeface from site/font/ (owned by the font work) into assets/fonts/ on every build."""
    src, dst = SITE / "font", SITE / "assets" / "fonts"
    dst.mkdir(parents=True, exist_ok=True)
    for f in FONT_FILES:
        shutil.copy2(src / f, dst / f)
    info = {"files": {f: (dst / f).stat().st_size for f in FONT_FILES}, "version": "", "chars": set()}
    try:
        from fontTools.ttLib import TTFont
        t = TTFont(dst / "OpenIndus-Regular.ttf")
        info["chars"] = {chr(c) for c in t.getBestCmap()}
        info["text_chars"] = {chr(c) for c in TTFont(dst / "OpenIndusText-Regular.ttf").getBestCmap()}
        m = re.search(r"(\d+\.\d+)", t["name"].getDebugName(5) or "")
        info["version"] = m.group(1) if m else ""
    except ImportError:
        pass
    return info


def copy_logo_downloads():
    """Download copies of the mark and the wordmark: the same drawings as the header, with a plain title."""
    out = SITE / "assets" / "downloads"
    out.mkdir(parents=True, exist_ok=True)
    files = {}
    for src, kind in (("logo-mark.svg", "mark"), ("wordmark.svg", "wordmark")):
        svg = (SITE / "assets" / src).read_text()
        label = f"{NAME} {'mark: the fish sign' if kind == 'mark' else 'wordmark'}"
        svg = re.sub(r"<title>.*?</title>", f"<title>{E(label)}</title>", svg, flags=re.S)
        svg = re.sub(r'aria-label="[^"]*"', f'aria-label="{E(label)}"', svg)
        name = f"{slug()}-{kind}.svg"
        (out / name).write_text(svg)
        files[kind] = (f"assets/downloads/{name}", (out / name).stat().st_size)
    return files


SEAL_ROW = [342, 99, 267, 176, 59]   # the line of signs cut on the hero seal


def field_ids():
    return [n for n in range(1, 418) if n not in NO_SIGN][:360]


def band_ids(count=26, seed=3):
    ids = [n for n in range(1, 418) if n not in NO_SIGN]
    return [ids[((seed + k) * 37) % len(ids)] for k in range(count)]


def copy_signs():
    """The sign drawings used by the hero seal, the field behind it and the divider strip.
    Mahadevan 1977 drawings: licence still open (PUBLISHING_CHECKLIST.md); to be redrawn or cleared before publishing."""
    out = SITE / "assets" / "signs"
    out.mkdir(parents=True, exist_ok=True)
    for n in set(SEAL_ROW) | set(field_ids()) | set(band_ids()):
        assert n not in NO_SIGN
        dst = out / f"M{n}.png"
        if not dst.exists():
            shutil.copy2(ROOT / "data" / "sign_images" / f"M{n}.png", dst)


FISH_PATHS = ('<path d="M16 3.56C9.18 9.28 8.74 16.32 16 23.14L21.05 27.88"/><path d="M16 3.56C22.82 9.28 23.26 16.32 16 23.14L10.95 27.88"/>'
              '<path d="M11.71 17.44L8.67 19.82M20.29 17.44L23.33 19.82"/>')


def seal_object():
    """Hero object: a carved steatite seal. The face is an SVG height map (white = polished face, black = cuts) lit with
    feDiffuseLighting and feSpecularLighting; the thickness is a stack of slices of the same rounded square, so the
    sides meet the face exactly at every tilt. site.js turns it with the pointer and swings the light.
    RENDER SLOT: the element with data-slot="hero-object" can be replaced by a rendered image later.
    It is an illustration, captioned as one: no catalogue number, no findspot."""
    depth, n = 34, 15
    slices = "".join(f'<i class="sl" style="--z:{depth * (k + 1) / n:.2f}px;--a:{0.04 + 0.16 * k / (n - 1):.3f}"></i>' for k in range(n))
    field = "".join(f'<image href="assets/signs/M{m}.png" x="{(k % 20) * 36}" y="{(k // 20) * 36}" width="32" height="32"/>'
                    for k, m in enumerate(field_ids()))
    row = "".join(f'<image href="assets/signs/M{m}.png" x="{x}" y="26" width="78" height="78"/>' for m, x in zip(SEAL_ROW, (28, 96, 160, 226, 294)))
    return f'''<div class="stage">
<div class="field" aria-hidden="true"><svg viewBox="0 0 720 640" preserveAspectRatio="xMidYMid slice"><defs><filter id="emb" color-interpolation-filters="sRGB"><feOffset in="SourceAlpha" dx=".9" dy=".9" result="o"/><feComposite in="o" in2="SourceAlpha" operator="out" result="e"/><feFlood flood-color="#000" flood-opacity=".22"/><feComposite in2="e" operator="in" result="lo"/><feOffset in="SourceAlpha" dx="-.9" dy="-.9" result="o2"/><feComposite in="o2" in2="SourceAlpha" operator="out" result="e2"/><feFlood flood-color="#fff" flood-opacity=".5"/><feComposite in2="e2" operator="in" result="hi"/><feMerge><feMergeNode in="lo"/><feMergeNode in="hi"/></feMerge></filter></defs><g filter="url(#emb)">{field}</g></svg></div>
<figure class="seal-fig">
<!-- RENDER SLOT: replace .scene with a rendered steatite seal (transparent PNG about 1200 px square, light from the top left). -->
<div class="scene" data-slot="hero-object" role="img" aria-label="Illustration of a square stone seal: a line of Indus signs above the fish sign, cut into its face">
<i class="contact"></i>
<div class="seal" id="seal">{slices}
<div class="face"><svg viewBox="0 0 400 400" aria-hidden="true" focusable="false"><defs><filter id="carve" x="0" y="0" width="100%" height="100%" color-interpolation-filters="sRGB">
<feColorMatrix in="SourceGraphic" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  1 0 0 0 0" result="h0"/>
<feGaussianBlur in="h0" stdDeviation="2.4" result="hb"/>
<feTurbulence type="fractalNoise" baseFrequency=".75" numOctaves="3" seed="4" result="grain"/>
<feColorMatrix in="grain" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  0 0 0 .07 0" result="ga"/>
<feComposite in="hb" in2="ga" operator="arithmetic" k2="1" k3="1" result="h"/>
<feDiffuseLighting in="h" surfaceScale="8" diffuseConstant="1" lighting-color="#fff6ea" result="dif"><feDistantLight id="L1" azimuth="225" elevation="40"/></feDiffuseLighting>
<feSpecularLighting in="h" surfaceScale="8" specularConstant=".6" specularExponent="26" lighting-color="#fff4e6" result="spec"><feDistantLight id="L2" azimuth="225" elevation="48"/></feSpecularLighting>
<feTurbulence type="fractalNoise" baseFrequency=".012" numOctaves="2" seed="11" result="mot"/>
<feColorMatrix in="mot" type="matrix" values="0 0 0 0 .93  0 0 0 0 .88  0 0 0 0 .80  0 0 0 0 1" result="base0"/>
<feColorMatrix in="mot" type="matrix" values="0 0 0 0 0  0 0 0 0 0  0 0 0 0 0  -.35 0 0 0 .22" result="motA"/>
<feFlood flood-color="#b99a7c" result="patina"/><feComposite in="patina" in2="motA" operator="in" result="pat"/>
<feMerge result="base"><feMergeNode in="base0"/><feMergeNode in="pat"/></feMerge>
<feComponentTransfer in="hb" result="floor"><feFuncA type="table" tableValues=".7 1"/></feComponentTransfer>
<feComposite in="base" in2="dif" operator="arithmetic" k1=".95" k2=".22" result="lit"/>
<feComposite in="lit" in2="floor" operator="in" result="lit2"/>
<feFlood flood-color="#8a6e55" result="dark"/>
<feMerge result="lit3"><feMergeNode in="dark"/><feMergeNode in="lit2"/></feMerge>
<feComposite in="spec" in2="lit3" operator="arithmetic" k2=".4" k3="1" result="out"/>
<feComposite in="out" in2="SourceAlpha" operator="in"/>
</filter></defs>
<g filter="url(#carve)"><rect x="-20" y="-20" width="440" height="440" fill="#fff"/><g style="filter:brightness(0)">{row}</g>
<g transform="translate(200 254) scale(7.6) translate(-16 -15.7)" fill="none" stroke="#000" stroke-width="2.7" stroke-linecap="round" stroke-linejoin="round">{FISH_PATHS}</g></g></svg></div>
<i class="rim"></i>
</div>
</div>
<figcaption class="seal-note">Illustration, not a real seal</figcaption>
</figure>
</div>'''


def sign_band():
    """Section divider: a recessed band with a running line of signs pressed into it."""
    # The line is drawn four times, so sliding it left by a quarter of its width loops with no seam on screens up to about 4000px wide (site.css .band-in svg).
    ids = band_ids()
    imgs, x = [], 5
    for n in ids * 4:
        imgs.append(f'<image href="assets/signs/M{n}.png" x="{x}" y="9" width="46" height="46"/>')
        x += 56
    return (f'<div class="band" aria-hidden="true"><div class="band-in"><svg viewBox="0 0 {56 * 4 * len(ids)} 64" preserveAspectRatio="xMinYMid meet">'
            '<defs><filter id="press" color-interpolation-filters="sRGB"><feOffset in="SourceAlpha" dx="1" dy="1" result="o"/>'
            '<feComposite in="o" in2="SourceAlpha" operator="out" result="e"/><feFlood flood-color="#fff" flood-opacity=".6"/>'
            '<feComposite in2="e" operator="in" result="hi"/><feFlood flood-color="#000" flood-opacity=".3"/>'
            '<feComposite in2="SourceAlpha" operator="in" result="body"/><feMerge><feMergeNode in="body"/><feMergeNode in="hi"/></feMerge></filter></defs>'
            f'<g filter="url(#press)">{"".join(imgs)}</g></svg></div></div>')


def plan_steps():
    out = ['<ol class="flow">']
    for i, (cls, t, st, d) in enumerate(PLAN, 1):
        out.append(f'<li class="step {cls}"><span class="dot" aria-hidden="true">{i}</span><div><div class="sh">{E(t)} <span class="tag {cls}">{E(st)}</span></div><p>{E(d)}</p></div></li>')
    out.append("</ol>")
    return "".join(out)


def findings_list(full):
    out = ['<ol class="findings">']
    for f in FINDINGS:
        lab, _ = LEVELS[f["level"]]
        title = E(f["title"])
        if f.get("glyphs"):
            title += " " + " ".join(sig(g) for g in f["glyphs"])
        links = " ".join(repo_link(p + "/", p.split("/")[-1]) for p in f["folders"])
        cav = f'<p class="caveat">{E(f["caveat"])}</p>' if f.get("caveat") else ""
        if full:
            out.append(f'<li class="finding" id="f{f["n"]}"><details><summary><span class="num">{f["n"]:02d}</span>'
                       f'<span class="ft">{title}</span><span class="lvl {f["level"]}">{lab}</span></summary>'
                       f'<div class="fbody"><p>{E(f["plain"])}</p><p class="nums">{E(f["nums"])}</p>{cav}<p class="where">Code and results: {links}</p></div></details></li>')
        else:
            out.append(f'<li class="finding"><span class="num">{f["n"]:02d}</span><span class="ft">{title}</span><span class="lvl {f["level"]}">{lab}</span></li>')
    out.append("</ol>")
    return "".join(out)


def level_key():
    return '<dl class="levels">' + "".join(
        f'<div><dt><span class="lvl {k}">{E(l)}</span></dt><dd>{E(d)}</dd></div>' for k, (l, d) in LEVELS.items()) + "</dl>"


def closed_routes(sections, rows):
    out = []
    for sec, name in sections.items():
        rs = [r for r in rows if r["sec"] == sec]
        if not rs:
            continue
        n_out = sum(1 for r in rs if verdict_kind(r["verdict"])[0] == "out")
        items = []
        for r in rs:
            kind, lab = verdict_kind(r["verdict"])
            folder = " ".join(repo_link(p + "/", p.split("/")[-1]) for p in r["folders"])
            reopen = r["reopen"] if r["reopen"] not in ("None", "n/a") else "Nothing in sight"
            items.append(f'<li class="route"><div class="rt"><span class="rn">{E(r["num"])}</span>{E(r["route"])}</div>'
                         f'<span class="tag {kind}" title="{E(r["verdict"])}">{lab}</span>'
                         f'<div class="rd"><span>Verdict: {E(r["verdict"])}. Test power: {E(r["power"])}.</span>'
                         f'<span>Would reopen with: {E(reopen)}.</span>{"<span>" + folder + "</span>" if folder else ""}</div></li>')
        out.append(f'<details class="group"><summary><span class="gt">{E(name)}</span>'
                   f'<span class="gc">{len(rs)} routes · {n_out} ruled out</span></summary><ul class="routes">{"".join(items)}</ul></details>')
    return "".join(out)


def reversals(rev):
    return '<ol class="rev">' + "".join(f'<li><b>{E(r["title"])}.</b> {E(r["text"])}</li>' for r in rev) + "</ol>"


def papers():
    lab = {"ready": "Ready to write", "needs-check": "Needs one check", "later": "Later"}
    return '<ul class="plainlist">' + "".join(
        f'<li><div class="pt">{E(t)} <span class="tag {"good" if s == "ready" else "weak" if s == "needs-check" else ""}">{lab[s]}</span></div>'
        f'<p>{E(k)}. {E(d)}</p></li>' for t, k, s, d in PAPERS) + "</ul>"


def asks():
    return '<ul class="plainlist asks">' + "".join(
        f'<li><div class="pt">{E(t)}</div><p>{E(w)}</p><p class="why">{E(y)}</p></li>' for t, w, y in DATA_ASKS) + "</ul>"


def closed_short():
    return '<dl class="closed">' + "".join(f'<div><dt>{E(a)}</dt><dd>{E(b)}</dd></div>' for a, b in CLOSED_SHORT) + "</dl>"


def groups_short():
    return '<dl class="groups">' + "".join(
        f'<div><dt><a href="contribute.html#{k}">{E(t)}</a></dt><dd>{E(d)}</dd></div>' for k, t, d in GROUPS) + "</dl>"


def starter_list(tasks, group=None, limit=None):
    ts = [t for t in tasks if group is None or group in t["who"]]
    if limit:
        ts = ts[:limit]
    who = {"code": "Programmers", "stats": "Statisticians", "specialist": "Specialists", "anyone": "Anyone careful", "collections": "Collections"}
    out = ['<ul class="starters">']
    for t in ts:
        start = " ".join(repo_link(p) for p in t["start"])
        out.append(f'<li class="starter" id="{t["id"]}"><details><summary><span class="sid">{t["id"]}</span><span class="st">{E(t["title"])}</span>'
                   f'<span class="sw">{" · ".join(who[w] for w in t["who"])}</span></summary>'
                   f'<div class="sb"><p><b>Why:</b> {E(t["why"])}</p><p><b>Done when:</b> {E(t["done_when"])}</p>'
                   f'<p class="where"><b>Start from:</b> {start}</p></div></details></li>')
    out.append("</ul>")
    return "".join(out)


def board_open(b):
    ms = {"M1": "Names on seals found abroad", "M2": "Test the 2026 published readings", "M3": "South Indian graffiti beside early Tamil",
          "M4": "Sign meaning classes", "M5": "Research sweep", "M6": "Red team"}
    lab = {"running": "Being worked on", "ready": "Open", "blocked": "Waiting"}
    rows = [t for t in b["tasks"] if t["state"] != "done"]
    out = ['<ul class="starters">']
    for t in sorted(rows, key=lambda t: t["id"], reverse=True):
        waits = f' Waits for task {", ".join("#" + str(w) for w in t["waits"])}.' if t["waits"] else ""
        out.append(f'<li class="starter"><div class="row"><span class="sid">#{t["id"]}</span><span class="st">{E(t["title"])}</span>'
                   f'<span class="tag {"run" if t["state"] == "running" else ""}">{lab[t["state"]]}</span></div>'
                   f'<p class="sub">{E(ms.get(t["ms"], t["ms"]))}.{E(waits)}</p></li>')
    out.append("</ul>")
    return "".join(out)


# ---------------------------------------------------------------- pages
def inline_mark():
    svg = (SITE / "assets/logo-mark.svg").read_text()
    svg = re.sub(r"<title>.*?</title>\n?", "", svg)
    svg = re.sub(r' role="img" aria-label="[^"]*"', "", svg)
    return svg.replace("<svg ", '<svg class="mark" aria-hidden="true" focusable="false" ', 1).strip()


def inline_wordmark():
    """The hand-drawn 'Open Indus' lettering (subtle study) for the header."""
    svg = (SITE / "assets/wordmark.svg").read_text()
    svg = re.sub(r"<title>.*?</title>\n?", "", svg)
    svg = re.sub(r' role="img" aria-label="[^"]*"', "", svg)
    return svg.replace("<svg ", '<svg class="wordmark" aria-hidden="true" focusable="false" ', 1).strip()


def smart(page):
    """Curly quotes and apostrophes in visible text; leaves tags, scripts, styles and code alone."""
    parts = re.split(r"(<script.*?</script>|<style.*?</style>|<code.*?</code>|<[^>]+>)", page, flags=re.S)
    def fix(t):
        t = t.replace("&#x27;", "'").replace("&#39;", "'").replace("&quot;", '"')
        t = re.sub(r"(?<=\w)'", "\u2019", t)
        t = re.sub(r"'(?=\w)", "\u2018", t)
        t = re.sub(r'"(?=\w)', "\u201c", t)
        t = re.sub(r'(?<=[\w.,)])"', "\u201d", t)
        return t
    return "".join(p if p.startswith("<") else fix(p) for p in parts)


PAGES = (("index.html", "Overview"), ("approach.html", "Approach"), ("findings.html", "Findings"), ("tracker.html", "Tracker"),
         ("contribute.html", "Contribute"), ("resources.html", "Resources"))
ARROW = ('<svg class="ext-ic" viewBox="0 0 12 12" width="11" height="11" aria-hidden="true" focusable="false" fill="none" '
         'stroke="currentColor" stroke-width="1.5" stroke-linecap="round"><path d="M3.5 8.5L8.5 3.5M4.5 3.5H8.5V7.5"/></svg>')


def nav_items(current):
    out = []
    for href, lab in PAGES:
        cur = ' aria-current="page"' if href == current else ""
        out.append(f'<li><a href="{href}"{cur}>{lab}</a></li>')
    out.append(f'<li><a href="{E(REPO_URL)}" class="ext">GitHub{ARROW}<span class="vh"> (code repository)</span></a></li>')
    return "".join(out)


def foot_pages(current):
    cur = ' aria-current="page"'
    return "".join(f'<a href="{href}"{cur if href == current else ""}>{lab}</a>' for href, lab in PAGES)


def render(name, title, desc, current, fills, body_class=""):
    layout = (TPL / "layout.html").read_text()
    body = (TPL / f"{name}.html").read_text()
    for k, v in fills.items():
        body = body.replace("{{" + k + "}}", str(v))
    page = layout
    for k, v in dict(TITLE=E(title), DESC=E(desc), NAV=nav_items(current), FOOT_PAGES=foot_pages(current), BODY_CLASS=body_class,
                     MAIN=body, NAME=E(NAME), ROBOTS='\n<meta name="robots" content="noindex, nofollow">' if PREVIEW else "", REPO=E(REPO_URL), MARK=inline_mark(), WORDMARK=inline_wordmark(),
                     CONTACT=E(CONTACT_NOTE), BUILT=time.strftime("%d %b %Y").lstrip("0").replace(" ", "\u00a0")).items():
        page = page.replace("{{" + k + "}}", v)
    page = page.replace("{{NAME}}", E(NAME)).replace("{{REPO}}", E(REPO_URL))
    page = smart(page)
    left = re.findall(r"\{\{[A-Z_]+\}\}", page)
    assert not left, f"{name}: unfilled {left}"
    (SITE / f"{name}.html").write_text(page)
    return SITE / f"{name}.html"


# ---------------------------------------------------------------- checks
class _Links(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.refs, self.stack, self.text = set(), [], [], []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        for k in ("href", "src"):
            if a.get(k):
                self.refs.append((tag, a[k]))
        if tag in ("script", "style", "code", "pre", "title", "svg"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "code", "pre", "title", "svg"):
            self.skip = max(0, self.skip - 1)

    def handle_data(self, data):
        if not self.skip:
            self.text.append(data)


def parse(path):
    p = _Links()
    p.feed(path.read_text())
    return p


def check_links(pages):
    """Fail the build if any internal href/src or #anchor in the written pages does not resolve."""
    parsed = {p.name: parse(p) for p in pages}
    bad = []
    for name, p in parsed.items():
        for tag, ref in p.refs:
            if ref.startswith(REPO_URL) or re.match(r"^(https?:|mailto:|data:)", ref):
                continue
            path, _, frag = ref.partition("#")
            path = path.split("?")[0]
            target = name if path == "" else path
            if not (SITE / target).is_file():
                bad.append(f"{name}: {ref} (no file {target})")
                continue
            if frag:
                ids = parsed[target].ids if target in parsed else parse(SITE / target).ids
                if frag not in ids:
                    bad.append(f"{name}: {ref} (no id #{frag} in {target})")
    if bad:
        raise SystemExit("Broken internal links:\n  " + "\n  ".join(bad))
    n = sum(len(p.refs) for p in parsed.values())
    print(f"links: {n} href/src checked across {len(parsed)} pages, none broken")


def font_gaps(page, chars):
    """Characters in a page's visible text that Open Indus Display lacks (they would fall back to another font)."""
    if not chars:
        return {}
    text = "".join(parse(page).text)
    miss = {}
    for ch in text:
        if ch not in chars and not ch.isspace():
            miss[ch] = miss.get(ch, 0) + 1
    return miss


def size_kb(n):
    return f"{max(1, round(n / 1024))} KB"


DIST_ASSETS = ["site.css", "site.js", "glyphs.css", "favicon.svg", "favicon-32.png", "apple-touch-icon.png",
               "logo-mark.svg", "wordmark.svg", "seal-illustration.svg", "fonts", "img", "signs", "downloads"]


def make_dist(built):
    """Write the upload set for a static host into site/dist/: the built pages and only the assets they use.
    Rebuilt from scratch each time. Nothing else from site/ (templates, scripts, font sources, explore/, repo_files) goes in."""
    dist = SITE / "dist"
    if dist.exists():
        shutil.rmtree(dist)
    (dist / "assets").mkdir(parents=True)
    for p in built:
        shutil.copy2(p, dist / p.name)
    src = SITE / "assets"
    used = {m for p in built for m in re.findall(r'assets/img/([^"#?]+)', p.read_text())}
    for name in DIST_ASSETS:
        s = src / name
        if name == "img":   # only the seal crops a page actually shows
            (dist / "assets" / "img").mkdir()
            for f in sorted(used):
                shutil.copy2(s / f, dist / "assets" / "img" / f)
        elif s.is_dir():
            shutil.copytree(s, dist / "assets" / name)
        elif s.exists():
            shutil.copy2(s, dist / "assets" / name)
    # every local href/src in the pages must resolve inside dist/
    missing = set()
    for p in built:
        for ref in re.findall(r'(?:href|src)="([^"#?]+)', p.read_text()):
            if ref.startswith(("http", "mailto:", "data:")) or ref.startswith(REPO_URL):
                continue
            if not (dist / ref).exists():
                missing.add(ref)
    css = (src / "site.css").read_text() + (src / "glyphs.css").read_text()
    for ref in re.findall(r'url\("?((?!data:)[^")]+)"?\)', css):
        if not (dist / "assets" / ref).exists():
            missing.add("assets/" + ref)
    if missing:
        raise SystemExit("dist/ is missing: " + ", ".join(sorted(missing)))
    files = [f for f in dist.rglob("*") if f.is_file()]
    print(f"dist: {len(files)} files, {sum(f.stat().st_size for f in files) // 1024} KB in site/dist/ (upload this folder)")


def main():
    glyph_css()
    font = copy_font()
    copy_signs()
    logo = copy_logo_downloads()
    c = counts()
    b = board()
    sections, rows, rev = atlas()
    starters = json.loads((SITE / "starter_tasks.json").read_text())["tasks"]
    n_out = sum(1 for r in rows if verdict_kind(r["verdict"])[0] == "out")
    common = dict(N_ROUTES=len(rows), N_OUT=n_out, N_REV=len(rev), N_PREREG=c["prereg"], N_LEDGER=f'{c["ledger"]:,}',
                  HASH=c["sample_hash"][:16], HASH_FILE=E(c["sample_file"].split("/")[-1]), HASH_TIME=E(c["sample_time"][:10]),
                  SIG59=sig(59), SIG60=sig(60), SIG342=sig(342), SIG109=sig(109))
    built = []
    built.append(render("index", f"{NAME}: decipher the Indus script by 2027",
                        "An open research group working to decipher the Indus script by 2027. Nothing is deciphered yet, and every test of a reading is published.",
                        "index.html", dict(common,
                            HERO=seal_object(), BAND=sign_band(),
                            LADDER=ladder(caption=False),
                            FIG_TEXT=figure("EH_3", 1, "Square stamp seal from Harappa: a line of Indus signs above a one-horned bull standing before a feeding trough")),
                        body_class="oi-page"))
    built.append(render("approach", f"Approach · {NAME} · Decipher the Indus script by 2027",
                        "What counts as deciphering the Indus script, the rules every test follows, the agent team, the route through names and the honest odds.",
                        "approach.html", dict(common, SLOTS=slots(), CHART_ROUND=chart_round(), CHART_NAMES=chart_names(), PLAN=plan_steps())))
    built.append(render("findings", f"Findings · {NAME} · Decipher the Indus script by 2027",
                        "Ranked findings about the Indus script with their evidence, and every route the project has tested and closed.",
                        "findings.html", dict(common, LEVELS=level_key(), FINDINGS=findings_list(True),
                            ROUTES=closed_routes(sections, rows), REVERSALS=reversals(rev), PAPERS=papers(),
                            FIG_A=figure("MIC_91", 4, "Square seal: signs along the top, a striped animal below"),
                            FIG_B=figure("FEM_461", 5, "Impression of a one-line seal text"))))
    built.append(render("tracker", f"Tracker · {NAME} · Decipher the Indus script by 2027", "How far the project is from its goal of deciphering the Indus script by 2027, and the live task board of the agent team.",
                        "tracker.html", dict(common, GOAL=goal(), DATA=json.dumps(b).replace("</", "<\\/"), SNAP=E(b.get("snapshot", "")))))
    built.append(render("contribute", f"Contribute · {NAME} · Help decipher the Indus script",
                        "Help decipher the Indus script by 2027. Point a strong AI agent at an open task, share data or photographs, check readings, or break one of our results.",
                        "contribute.html", dict(common,
                            ST_CODE=starter_list(starters, "code") , ST_STATS=starter_list([t for t in starters if "stats" in t["who"] and "code" not in t["who"]]),
                            ST_SPEC=starter_list(starters, "specialist"), ST_ANY=starter_list([t for t in starters if t["who"] == ["anyone"]]),
                            BOARD_OPEN=board_open(b), ASKS=asks(),
                            FIG_C=figure("EH_286", 6, "Very small square seal carrying three large signs, one of them the jar"))))
    fs = font["files"]
    built.append(render("resources", f"Resources · {NAME} · Decipher the Indus script by 2027",
                        f"Free downloads from {NAME}: the Open Indus Display typeface (SIL Open Font License) and the fish-sign logo, plus the research files that open with the repository.",
                        "resources.html", dict(common,
                            FONT_VERSION=E(font["version"] or "0.x"), FONT_NCHARS=len(font["chars"]) or "about 80",
                            SZ_REG_WOFF2=size_kb(fs["OpenIndus-Regular.woff2"]), SZ_BOLD_WOFF2=size_kb(fs["OpenIndus-Bold.woff2"]),
                            SZ_REG_TTF=size_kb(fs["OpenIndus-Regular.ttf"]), SZ_BOLD_TTF=size_kb(fs["OpenIndus-Bold.ttf"]),
                            SZ_TREG_WOFF2=size_kb(fs["OpenIndusText-Regular.woff2"]), SZ_TBOLD_WOFF2=size_kb(fs["OpenIndusText-Bold.woff2"]),
                            SZ_TREG_TTF=size_kb(fs["OpenIndusText-Regular.ttf"]), SZ_TBOLD_TTF=size_kb(fs["OpenIndusText-Bold.ttf"]),
                            SZ_OFL=size_kb(fs["OFL.txt"]), MARK_BIG=inline_mark().replace('class="mark"', 'class="mark-big"'),
                            WORDMARK_BIG=inline_wordmark().replace('class="wordmark"', 'class="wordmark-big"'),
                            MARK_FILE=logo["mark"][0], MARK_NAME=logo["mark"][0].split("/")[-1], SZ_MARK=size_kb(logo["mark"][1]),
                            WORD_FILE=logo["wordmark"][0], WORD_NAME=logo["wordmark"][0].split("/")[-1], SZ_WORD=size_kb(logo["wordmark"][1]))))
    for p in built:
        print("wrote", p.relative_to(ROOT), f"{p.stat().st_size // 1024} KB")
    print(f"font: Open Indus Display v{font['version']}, {len(font['chars'])} characters, copied to site/assets/fonts/")
    for p in built:   # every page's text is set in Open Indus Text; Display only in capitals
        gaps = font_gaps(p, font.get("text_chars") or font["chars"])
        if gaps:
            print(f"{p.name}: characters Open Indus Text lacks:", " ".join(f"{c!r}x{n}" for c, n in sorted(gaps.items())))
    check_links(built)
    make_dist(built)


if __name__ == "__main__":
    main()
