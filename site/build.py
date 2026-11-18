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

from PIL import Image, ImageFilter, ImageOps, ImageEnhance

# ---------------------------------------------------------------- config
NAME = "Open Indus"                                # the group's name, used everywhere
REPO_URL = "https://github.com/HarshInvader/open-indus"   # public repository, branch main
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


def block_size(im):
    """Width of the replicated pixel blocks in an enlarged scan (1 if none): the period of sharp column-to-column jumps."""
    import numpy as np
    d = np.abs(np.diff(np.asarray(im, float), axis=1)).mean(0)
    score = {p: max(d[i::p].mean() for i in range(p)) / d.mean() for p in range(2, 9)}
    top = max(score.values())
    if top < 1.8:
        return 1
    return min(p for p, v in score.items() if v >= 0.9 * top)


def plate_img(key):
    """Save a greyscale JPEG at (never above) the crop's own pixel size. Return width, height, path."""
    meta = PLATES[key]
    im = Image.open(ROOT / f"experiments/plate_corpus/crops/plate_{key}.png").convert("L")
    if meta.get("trim"):                       # cut the printed plate number off the bottom edge
        im = im.crop((0, 0, im.width, round(im.height * (1 - meta["trim"]))))
    # Classical cleanup only, at the scan's own size (nothing generative, nothing enlarged): soften the print grain
    # and JPEG blocks, stretch the contrast, then sharpen gently.
    blk = block_size(im)                      # the scans are pixel-replicated enlargements: undo the blocks first
    if blk > 1:
        w, h = im.width // blk * blk, im.height // blk * blk
        im = im.crop((0, 0, w, h)).resize((w // blk, h // blk), Image.BOX).resize((w, h), Image.LANCZOS)
    im = im.filter(ImageFilter.GaussianBlur(0.8)).filter(ImageFilter.MedianFilter(3))
    im = ImageEnhance.Contrast(ImageOps.autocontrast(im, cutoff=(0.5, 0.5))).enhance(1.08)
    im = im.filter(ImageFilter.UnsharpMask(radius=2, percent=55, threshold=4))
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
    "strong": ("Strong", "Held up on texts we never looked at while building the idea, and survived a second team trying to break it."),
    "moderate": ("Moderate", "Held up on unseen texts, but the numbers are small, so it could still be luck."),
    "weak": ("Weak", "The general pattern is real. The details are barely supported."),
    "exploratory": ("Exploratory", "Spotted in the data, but not yet checked on unseen texts."),
    "descriptive": ("Descriptive", "A count or measurement, not a test of an idea."),
}

FINDINGS = [
    dict(n=1, level="strong", novelty='known', prior="Known since Mahadevan's 1977 concordance and measured by Rao et al. (2009) and Yadav et al. (2010). New here: a test on texts held back from the model.",
         head='The signs follow rules about order', gist='Shuffle the signs of a text and we can usually tell which order is the real one. That only works if the order follows rules, like words in a sentence.',
         title="Sign order is fixed, not just positional",
         plain="Knowing the signs of an unseen text, the real order can be picked out from all orderings of the same signs far more often than chance. It still works with the commonest signs removed. Codes such as weather reports and chess openings pass this test too, so it shows a fixed format, not necessarily a grammar. It still holds with half the texts read backwards.",
         nums="40% of 321 held-out runs vs 5.7% by chance; q ≈ 8e-72",
         folders=["experiments/structure", "experiments/redteam", "experiments/revalidation"]),
    dict(n=2, level="descriptive", novelty='known', prior='Mahadevan (1977) listed 417 signs and Parpola (1994) about 386. Both called the script mostly word-signs with some sound-signs.',
         head='About 400 signs: too many for an alphabet', gist='An alphabet needs around 30 signs and a syllable script around 90. With about 400, most signs probably stand for whole words, as in early Chinese or Sumerian writing.',
         title="About 400 signs: if this is writing, mostly word-signs, perhaps with sound-signs",
         plain="The sign count and how often each sign is used look like Proto-Elamite or Sumerian, not like Linear B or an alphabet.",
         nums="≈400 signs (≈565 with unseen ones; 95% CI 508–658); 120 signs cover 90% of uses (Linear B: 63, Latin: 14)",
         folders=["experiments/structure"]),
    dict(n=3, level="moderate", novelty='new', prior='We know of no earlier report that the ticks change where the fish sign goes.',
         head='Four small ticks move the fish sign to the end', gist='A plain fish sign can sit anywhere in a text. Add four small ticks and it usually comes last, so the ticks change how the sign is used, a bit like a word ending.',
         title="Corner ticks move the fish sign to the end of the text",
         plain="A fish with four small ticks closes a text far more often than a plain fish: a mark inside a sign that changes where the sign goes. It holds on complete single-line texts too (9 of 16 vs 2%).",
         glyphs=(59, 60),
         nums="final in 40 of 73 vs 26% expected (p = 1e-7); held-out 11 of 19 vs 7% for plain fish (p = 0.004; q = 0.03 within its family, 0.54 across all tests)",
         folders=["experiments/novel_methods", "experiments/redteam"]),
    dict(n=4, level="moderate", novelty='partly', prior='Parpola and others suggested that Gulf seals carry unusual sign sequences, perhaps in another language. New here: round seals found in Indus cities break the order too.',
         head='Round seals from the Gulf break the usual rules', gist='Small round seals in a Gulf style were used by traders around Bahrain. Their signs come in an order Indus writers rarely used, wherever the seal was found. It could be another language, a special kind of seal, or imitation writing.',
         title="Round Gulf-type seals break normal sign order, wherever they were found",
         plain="Round seals of the Gulf type, found abroad or at home, do not follow the usual sign order. This fits three readings our data cannot separate: another language, a round-seal genre in the Indus language, or pseudo-writing.",
         nums="order excess +1.64 bits/sign on 8 home round seals (Holm p = 3e-4, rare-sign-matched null); foreign vs home round +0.11 (p = 0.66)",
         caveat="Corrected on 17 Nov 2026: a label error had hidden the home round seals. Only 3 of the 8 are confirmed round in a printed excavation report.",
         folders=["experiments/round_label_audit", "experiments/redteam_round_format", "experiments/redteam_round_order"]),
    dict(n=5, level="strong", novelty='tests', prior='Parpola read six + fish as “six stars”, the Pleiades, and seven + fish as “seven stars”. The pair is confirmed as a unit; the “seven stars” reading is not supported.',
         head='“Six” followed by “fish” is a set phrase', gist='The six-stroke sign and the fish sign appear together far more than chance, like “New York”. A popular idea that “seven + fish” means “seven stars” has almost no support.',
         title="Six followed by fish is a fixed expression",
         plain="The six-stroke sign followed by the fish behaves like one set phrase. The proposed 'seven stars' reading of seven plus fish has almost no support.",
         glyphs=(109, 59),
         nums="held-out 7 of 10 vs 3% base rate; q ≈ 6e-8",
         folders=["experiments/language", "experiments/redteam"]),
    dict(n=6, level="strong", novelty='partly', prior='Differences between seals and tablets were noted before in general terms. New here: a measured test on unseen texts, across five kinds of object.',
         head='Seals, tablets and pots each use different signs', gist='From the signs alone we can often tell what kind of object a text was on, the way you can tell a shop sign from a letter.',
         title="Each kind of object has its own vocabulary",
         plain="Seals, tablets, copper tablets, rods and pottery each favour different signs, enough to tell them apart on unseen texts.",
         nums="held-out AUC: copper 0.87, tablet 0.76, pottery 0.73, seal 0.72, sealing 0.67 (chance ceiling 0.55–0.61)",
         folders=["experiments/context", "experiments/redteam"]),
    dict(n=7, level="strong", novelty='known', prior='Right-to-left reading was shown by Lal (1966), and the left-to-right exceptions were listed by Mahadevan (1977). New here: a check that they are true reversals.',
         head='Texts that run left to right were written that way on purpose', gist='Indus texts normally read from right to left. The few that run the other way are deliberate reversals, not mistakes by modern readers.',
         title="Texts written left to right are true reversals",
         plain="The few texts that run left to right are written backwards on purpose, not misread. This depends on each text's direction label being right; with 1 in 10 flipped, the result misses its bar.",
         nums="31 of 34 copy-free lines; q = 6e-6",
         folders=["experiments/structure", "experiments/redteam"]),
    dict(n=8, level="exploratory", novelty='known', prior='Copper tablets with repeated texts and matching animals were described by Parpola and others. Our type count is new but not yet tested.',
         head='Copper tablets repeat a few dozen fixed messages', gist='Small copper tablets carry the same text-and-picture pairs again and again, like a set of standard tokens. We spotted this in the data but have not yet tested it on unseen texts.',
         title="Copper tablets come in a few dozen fixed types",
         plain="Copper tablets repeat about 18 to 64 fixed text-and-picture types. A one-sign face can stand in for the picture, but the sign does not depict it.",
         nums="same legend → same sign face 8 of 8 (p = 1e-4, all data); blind matching 5 of 24 vs 3.3 by chance",
         folders=["experiments/context", "experiments/logograms"]),
    dict(n=9, level="weak", novelty='known', prior='Splitting texts into recurring parts goes back to Koskenniemi (1981), Parpola and Mahadevan. Our specific set of slots is new and weakly supported.',
         head='Texts seem to have slots, like a sentence', gist='Most texts fit a pattern of a few positions, such as an opening, a middle and a closing part. That positions exist is solid. Our exact list of them is not.',
         title="Texts can be parsed into a small set of roles",
         plain="An 11-role reading parses most unseen texts, far more than shuffled ones. That positional roles exist is solid; that these 11 are the right ones is not. Role names such as 'title' and 'noun' are labels for positions, not tested meanings.",
         nums="parses 76% of unseen texts vs 44% for shuffles; specific roles p = 0.013, q = 0.085",
         folders=["experiments/functional_reading", "experiments/grammar"]),
    dict(n=10, level="moderate", novelty='partly', prior='Fixed opening and closing signs were known (Mahadevan 1977). New here: showing the part between them is usually one or two word-signs.',
         head='The middle of a seal text is just one or two signs', gist='Many seal texts have a fixed opening and closing. The part in between is usually one or two word-signs, not a name spelled out sound by sound.',
         title="The core of a seal text is one or two signs, not a spelled-out name",
         plain="The part of a seal text between its fixed opening and closing signs is short and made of whole words, not spelled out sound by sound. Nothing shows these cores are names.",
         nums="34% of cores are one sign; recurring pairs keep one order in 91% of uses (held-out 115 of 138, p = 3e-16)",
         folders=["experiments/typology", "experiments/core_semantics"]),
    dict(n=11, level="moderate", novelty='tests', prior='Parpola grouped the fish signs and read them as star or god names. Our test supports the grouping but not the god-name reading.',
         head='The fish signs are variants of one sign', gist='Six fish-like signs replace each other in the same places and pair with the same neighbours. They behave like forms of one word, not like names of six different gods.',
         title="The fish signs form one class that substitute for each other",
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
    ("fail", "Redesign it, then try it on Linear Elamite", "Failed, stopped", "Linear Elamite was read in 2022, so the right answer is known. Short lists and exact matches recovered none of its values: too few of its words carry a known name. As promised, the method stops here."),
    ("fail", "Run it on the round seals, home and abroad", "Not run", "There is no point running a method that failed its known-answer check."),
    ("next", "Wait for outside evidence, with the tests frozen", "Now", "Requests are out for seal impressions on tablets that name men of Meluhha, museum images and excavation records. What each one could show is fixed in advance."),
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
    """Distance to root milestone R: sound values for 10 signs with an outside anchor that passed a red team. Drawn to scale."""
    have, need = 0, 10
    cells = "".join(f'<li class="slot{" on" if i < have else ""}"></li>' for i in range(need))
    return (f'<figure class="goal-fig"><figcaption class="claim">{have} of {need} signs have a tested sound value</figcaption>'
            f'<ol class="slots" aria-label="{have} of {need} signs with a sound value with an outside anchor that passed a red team">{cells}</ol>{note}</figure>')


def goal():
    return ladder() + slots('<p class="note">Done means 10 signs whose sound values have an outside anchor, predict unseen texts and survive a red team. '
                            '<a href="approach.html#goal">What counts as done, and why it is hard</a></p>')


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
    # one zip of every font file plus the licence, for the "download all" link (fixed timestamps: same bytes each build)
    import zipfile
    z = dst / "open-indus-fonts.zip"
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED) as zf:
        for f in FONT_FILES:
            zi = zipfile.ZipInfo(f"open-indus-fonts/{f}", date_time=(2026, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(zi, (dst / f).read_bytes())
    info["files"]["open-indus-fonts.zip"] = z.stat().st_size
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


def data_figure():
    """Open-data section: an archive desk with four kinds of source. The register rows are real
    (Mackay 1938 seal register, datasets/open/register_mackay1938_seals.csv); the rest is illustration."""
    def sign(m, x, y, s, cls="dv-sign"):
        return f'<image class="{cls}" href="assets/signs/M{m}.png" x="{x}" y="{y}" width="{s}" height="{s}"/>'

    def proj(lon, lat):  # map card: lon 45-79, lat 18-34 -> 204 x 128
        return 12 + (lon - 45) / 34 * 204, 12 + (34 - lat) / 16 * 128

    def path(pts):
        return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in (proj(*p) for p in pts))

    # report page: title, text lines and a plate of two seal impressions
    lines = "".join(f'<rect x="22" y="{y}" width="{w}" height="3.2" rx="1.6" class="dv-line"/>'
                    for y, w in ((66, 150), (75, 162), (84, 138), (93, 156)))
    plate = ""
    for k, signs in enumerate(((342, 99, 267), (176, 293, 59))):
        x = 26 + k * 78
        plate += f'<rect x="{x}" y="110" width="68" height="68" rx="7" class="dv-imp"/>'
        plate += "".join(sign(m, x + 6 + j * 19, 116, 18) for j, m in enumerate(signs))
        bx, by = x + 10, 140   # a small bull facing right: body, legs, neck, head, one horn
        plate += (f'<g class="dv-animal" transform="translate({bx} {by})">'
                  '<path d="M4 14 C4 6 12 4 24 5 C32 5 38 6 40 10 C41 16 36 19 26 19 C16 19 6 19 4 14 Z"/>'
                  '<path d="M38 8 L44 3 C47 2 49 4 48 6 L44 10 Z"/>'
                  '<path d="M45 3 C46 0 48 -2 51 -3" class="dv-horn"/>'
                  '<path d="M9 18 L9 26 M15 19 L15 26 M30 19 L31 26 M36 17 L37 25 M4 13 C1 15 0 19 1 22" class="dv-legs"/></g>')
    report = f'''<g transform="translate(18 34) rotate(-5)">
<rect width="200" height="250" rx="6" class="dv-card" filter="url(#dvsh)"/>
<text x="22" y="34" class="dv-cap">EXCAVATIONS AT HARAPPA</text>
<text x="22" y="50" class="dv-small">Vats, 1940</text>
{lines}{plate}
<text x="26" y="194" class="dv-small">Fig. 1, 2 · seal impressions</text>
<rect x="22" y="208" width="156" height="3.2" rx="1.6" class="dv-line"/>
<rect x="22" y="217" width="132" height="3.2" rx="1.6" class="dv-line"/>
</g>'''

    rows = (("127", "9 / VIII / 10", "−6.7", "1.01"), ("269", "9 / XI / 75", "−9.3", "1.20"),
            ("387", "9 / VI / 78", "−12.2", "0.98"), ("645", "12 / V / 95", "−20.2", "1.24"),
            ("85", "14 / II / 8", "−5.9", "1.25"))
    body = ""
    for i, (no, spot, depth, size) in enumerate(rows):
        y = 70 + i * 22
        if i == 1:
            body += f'<rect x="10" y="{y - 14}" width="236" height="20" rx="4" class="dv-hl"/>'
        body += (f'<text x="18" y="{y}" class="dv-mono">{no}</text><text x="52" y="{y}" class="dv-mono">{spot}</text>'
                 f'<text x="196" y="{y}" text-anchor="end" class="dv-mono">{depth}</text><text x="238" y="{y}" text-anchor="end" class="dv-mono">{size}</text>')
    register = f'''<g transform="translate(196 84) rotate(3)">
<rect width="256" height="186" rx="6" class="dv-card" filter="url(#dvsh)"/>
<text x="18" y="28" class="dv-cap">SEAL REGISTER</text>
<text x="238" y="28" text-anchor="end" class="dv-small">Mohenjo-daro, 1938</text>
<line x1="10" y1="40" x2="246" y2="40" class="dv-rule"/>
<text x="18" y="54" class="dv-head">NO.</text><text x="52" y="54" class="dv-head">FINDSPOT</text>
<text x="196" y="54" text-anchor="end" class="dv-head">DEPTH FT</text><text x="238" y="54" text-anchor="end" class="dv-head">IN</text>
{body}
</g>'''

    coast = path([(47.6, 30.4), (50.3, 29.2), (51.4, 27.9), (54.5, 26.6), (56.4, 27.1), (57.3, 25.8), (61.6, 25.2),
                  (66.6, 25.4), (67.4, 24.4), (68.4, 23.6), (69.6, 22.9), (70.3, 22.7), (69.1, 22.4), (70.0, 21.0),
                  (72.6, 21.2), (72.5, 22.3), (73.0, 19.6)])
    arabia = path([(47.6, 30.4), (48.5, 28.6), (50.1, 26.6), (51.4, 24.6), (54.6, 24.2), (56.1, 26.2), (56.6, 24.2),
                   (58.7, 23.5), (59.8, 22.4)])
    river = path([(73.6, 33.6), (72.1, 31.6), (71.0, 29.4), (69.4, 28.2), (68.2, 26.6), (68.3, 25.2), (67.9, 24.4)])
    sites = (("Harappa", 72.86, 30.63, 1), ("Mohenjo-daro", 68.14, 27.33, 1), ("Dholavira", 70.21, 23.89, 0),
             ("Lothal", 72.25, 22.52, 0), ("Kalibangan", 74.13, 29.47, 0), ("Ur", 46.1, 30.96, 0), ("Dilmun", 50.55, 26.1, 0))
    place = {"Harappa": (-6, -2, "end"), "Mohenjo-daro": (6, 3, "start"), "Dholavira": (-5, 11, "end"),
             "Ur": (5, -3, "start"), "Dilmun": (-2, 13, "middle")}
    dots = ""
    for name, lon, lat, big in sites:
        x, y = proj(lon, lat)
        dots += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{3.4 if big else 2.6}" class="dv-dot"/>'
        if name in place:
            dx, dy, anchor = place[name]
            dots += f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{anchor}" class="dv-small dv-label">{name}</text>'
    trade = path([(67.6, 24.6), (64.0, 24.4), (58.6, 24.6), (54.0, 25.6), (51.2, 26.2)])
    mapc = f'''<g transform="translate(286 300) rotate(-2)">
<rect width="228" height="152" rx="6" class="dv-card" filter="url(#dvsh)"/>
<path d="{coast}" class="dv-coast"/><path d="{arabia}" class="dv-coast"/>
<path d="{river}" class="dv-river"/><path d="{trade}" class="dv-trade"/>
{dots}
<text x="14" y="142" class="dv-cap dv-capsm">FIND SITES</text>
</g>'''

    sherd = f'''<g transform="translate(64 318) rotate(-8)">
<path d="M8 22 C30 4 92 0 132 10 C150 16 156 40 148 66 C140 92 120 108 84 112 C54 116 26 104 12 84 C2 66 0 38 8 22 Z" class="dv-sherd" filter="url(#dvsh)"/>
<path d="M20 30 C44 16 96 14 128 22" class="dv-sherd-rim"/>
{sign(342, 50, 30, 56, "dv-scratch")}
<text x="22" y="132" class="dv-cap dv-capsm">POTTERY MARKS</text>
</g>'''
    return (f'<figure class="data-fig"><svg viewBox="0 0 540 470" role="img" aria-label="Illustration of the kinds of data we gather: '
            f'an excavation report with seal impressions, a seal register, a marked potsherd and a map of sites from the Indus to the Gulf">'
            f'<defs><filter id="dvsh" x="-10%" y="-10%" width="130%" height="135%"><feDropShadow dx="0" dy="6" stdDeviation="7" style="flood-color:var(--dv-shadow)"/></filter></defs>'
            f'{report}{register}{sherd}{mapc}</svg>'
            f'</figure>')


def _sign_img(m, x, y, s, cls="ag-sign"):
    return f'<image class="{cls}" href="assets/signs/M{m}.png" x="{x}" y="{y}" width="{s}" height="{s}"/>'


def fig_signs():
    """Findings 01: 48 of Mahadevan's sign drawings as a grid."""
    ids = field_ids()[:48]
    cells = "".join(_sign_img(m, 6 + (k % 8) * 36, 6 + (k // 8) * 36, 28) for k, m in enumerate(ids))
    return (f'<figure class="art-fig"><svg viewBox="0 0 300 228" role="img" aria-label="A grid of 48 Indus signs as drawn by Mahadevan">'
            f'<rect x="0.5" y="0.5" width="299" height="227" rx="8" class="ag-card"/>{cells}</svg>'
            f'<figcaption>48 of about 400 signs, as drawn in Mahadevan 1977.</figcaption></figure>')


def fig_mirror():
    """Findings 01: a seal is cut in mirror image; its impression reads right to left."""
    row = SEAL_ROW[:4]
    S, Y, IX, SX, W = 26, 40, 162, 6, 132           # sign size, row y, impression and seal square x, square width
    imp_u = [W - 12 - S - k * 29 for k in range(len(row))]       # reading order starts at the right
    imp = "".join(_sign_img(m, IX + u, Y, S) for m, u in zip(row, imp_u))
    seal = "".join(f'<g transform="translate({SX + (W - u - S) + S} 0) scale(-1 1)">{_sign_img(m, 0, Y, S)}</g>'
                   for m, u in zip(row, imp_u))
    bull = ('<path d="M4 14 C4 6 12 4 24 5 C32 5 38 6 40 10 C41 16 36 19 26 19 C16 19 6 19 4 14 Z" class="ag-animal"/>'
            '<path d="M38 8 L44 3 C47 2 49 4 48 6 L44 10 Z" class="ag-animal"/>'
            '<path d="M45 3 C46 0 48 -2 51 -3 M9 18 L9 26 M15 19 L15 26 M30 19 L31 26 M36 17 L37 25 M4 13 C1 15 0 19 1 22" class="ag-legs"/>')
    return (f'<figure class="art-fig"><svg viewBox="0 0 300 200" role="img" aria-label="Diagram: the seal is carved in mirror image; pressed into clay, the impression reads from right to left">'
            f'<rect x="{SX}" y="20" width="{W}" height="{W}" rx="10" class="ag-seal"/>{seal}'
            f'<g transform="translate({SX + W - 26} 84) scale(-1.6 1.6)">{bull}</g>'
            f'<rect x="{IX}" y="20" width="{W}" height="{W}" rx="10" class="ag-imp"/>{imp}'
            f'<g transform="translate({IX + 26} 84) scale(1.6)">{bull}</g>'
            f'<path d="M142 86 L158 86" class="ag-arrow"/><path d="M153 81 L159 86 L153 91" class="ag-arrow"/>'
            f'<path d="M282 166 L176 166" class="ag-read"/><path d="M183 161 L176 166 L183 171" class="ag-read"/>'
            f'<text x="{SX + W / 2:.0f}" y="170" text-anchor="middle" class="ag-lab">SEAL</text>'
            f'<text x="{SX + W / 2:.0f}" y="184" text-anchor="middle" class="ag-small">cut in reverse</text>'
            f'<text x="{IX + W / 2:.0f}" y="186" text-anchor="middle" class="ag-lab">IMPRESSION</text>'
            f'<text x="{IX + W / 2:.0f}" y="198" text-anchor="middle" class="ag-small">read right to left</text></svg>'
            f'<figcaption>Seals were cut in mirror image, so the impression reads the right way round.</figcaption></figure>')


def fig_map():
    """Findings 01: the Indus cities, the Gulf and Mesopotamia, with the sea route."""
    def proj(lon, lat):
        return 10 + (lon - 43) / 36 * 300, 12 + (36 - lat) / 18 * 200

    def path(pts):
        return "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in (proj(*p) for p in pts))
    coast = path([(47.9, 30.0), (50.3, 29.2), (51.4, 27.9), (54.5, 26.6), (56.4, 27.1), (57.3, 25.8), (61.6, 25.2),
                  (66.6, 25.4), (67.4, 24.4), (68.4, 23.6), (69.6, 22.9), (70.3, 22.7), (69.1, 22.4), (70.0, 21.0),
                  (72.6, 21.2), (72.5, 22.3), (73.0, 19.6), (73.5, 18.2)])
    arabia = path([(47.9, 30.0), (48.5, 28.6), (50.1, 26.6), (51.4, 24.6), (54.6, 24.2), (56.1, 26.2), (56.6, 24.2),
                   (58.7, 23.5), (59.8, 22.4), (59.0, 20.6), (57.8, 19.0)])
    indus = path([(73.6, 34.6), (72.1, 31.6), (71.0, 29.4), (69.4, 28.2), (68.2, 26.6), (68.3, 25.2), (67.9, 24.4)])
    tigris = path([(44.0, 35.6), (45.5, 33.0), (46.6, 31.6), (47.6, 30.6), (47.9, 30.0)])
    route = path([(67.6, 24.6), (63.0, 24.3), (58.6, 24.8), (55.0, 25.9), (51.3, 26.3), (49.4, 28.4), (47.9, 29.9)])
    sites = (("Harappa", 72.86, 30.63, 6, -3, "start"), ("Mohenjo-daro", 68.14, 27.33, -7, 4, "end"),
             ("Dholavira", 70.21, 23.89, -6, 12, "end"), ("Lothal", 72.25, 22.52, 6, 4, "start"),
             ("Ur", 46.1, 30.96, -5, -4, "end"), ("Susa", 48.25, 32.19, 6, -2, "start"),
             ("Dilmun", 50.55, 26.1, -4, 13, "end"), ("Magan", 57.0, 23.0, 0, 14, "middle"))
    dots = ""
    for name, lon, lat, dx, dy, an in sites:
        x, y = proj(lon, lat)
        dots += (f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3" class="ag-dot"/>'
                 f'<text x="{x + dx:.1f}" y="{y + dy:.1f}" text-anchor="{an}" class="ag-small ag-halo">{name}</text>')
    mx, my = proj(68.6, 31.6)
    return (f'<figure class="art-fig"><svg viewBox="0 0 320 224" role="img" aria-label="Map: Indus cities, the Persian Gulf and Mesopotamia, linked by a sea route">'
            f'<rect x="0.5" y="0.5" width="319" height="223" rx="8" class="ag-card"/>'
            f'<path d="{coast}" class="ag-coast"/><path d="{arabia}" class="ag-coast"/>'
            f'<path d="{indus}" class="ag-river"/><path d="{tigris}" class="ag-river"/><path d="{route}" class="ag-route"/>'
            f'<text x="{mx:.1f}" y="{my:.1f}" text-anchor="middle" class="ag-region">MELUHHA?</text>{dots}</svg>'
            f'<figcaption>Sea trade linked the Indus cities with the Gulf (Dilmun, Magan) and Mesopotamia.</figcaption></figure>')


def fig_routes(sections, rows):
    """Findings 05: one tile per closed route, by area, coloured by verdict."""
    lines = []
    tot = {"out": 0, "wait": 0, "weak": 0}
    for sec, name in sections.items():
        rs = [r for r in rows if r["sec"] == sec]
        if not rs:
            continue
        tiles = ""
        for r in rs:
            k = verdict_kind(r["verdict"])[0]
            tot[k] += 1
            tiles += f'<i class="rt-{k}" title="{E(r["route"])}"></i>'
        lines.append(f'<div class="rmap-row"><span class="rmap-lab">{E(name)}</span><span class="rmap-tiles">{tiles}</span></div>')
    legend = (f'<div class="rmap-key"><span><i class="rt-out"></i>Ruled out {tot["out"]}</span>'
              f'<span><i class="rt-wait"></i>Can’t test yet {tot["wait"]}</span><span><i class="rt-weak"></i>Weakened or not supported {tot["weak"]}</span></div>')
    return f'<figure class="rmap" aria-label="Each closed route as a tile, grouped by area">{"".join(lines)}{legend}</figure>'


def fig_pipeline():
    """Approach: the path every claim takes, as a row of steps with small drawn icons."""
    icons = {
        "seal": '<rect x="5" y="10" width="14" height="10" rx="2"/><path d="M8 10 V7 a4 4 0 0 1 8 0 V10"/>',
        "split": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M15.5 5 V19"/>',
        "test": '<circle cx="11" cy="11" r="6"/><path d="M15.5 15.5 L20 20"/>',
        "chance": '<rect x="4" y="4" width="16" height="16" rx="3"/><circle cx="9" cy="9" r="1.2"/><circle cx="15" cy="15" r="1.2"/><circle cx="15" cy="9" r="1.2"/><circle cx="9" cy="15" r="1.2"/>',
        "red": '<path d="M12 3 L19 6 V11 C19 16 16 19 12 21 C8 19 5 16 5 11 V6 Z"/><path d="M9 12 L11 14 L15 10"/>',
        "pub": '<path d="M6 3 H14 L18 7 V21 H6 Z"/><path d="M14 3 V7 H18 M9 12 H15 M9 16 H15"/>',
    }
    steps = (("seal", "Seal the plan", "Written down and fingerprinted first"),
             ("split", "Build on ¾", "A quarter of the texts kept aside"),
             ("test", "Test once on ¼", "No tuning on the kept texts"),
             ("chance", "Beat chance", "Against shuffles, every test counted"),
             ("red", "Red team", "A second team tries to break it"),
             ("pub", "Publish", "Whether it holds or fails"))
    items = "".join(f'<li><svg viewBox="0 0 24 24" aria-hidden="true">{icons[k]}</svg><b>{E(t)}</b><span>{E(d)}</span></li>'
                    for k, t, d in steps)
    return f'<ol class="pipe" aria-label="The path every claim takes">{items}</ol>'


def fig_how():
    """Homepage 04: how a lost script gets read, in four drawn steps, plus the missing piece."""
    S = 22
    def signs(ms, x0, y, mark=None):
        out = ""
        for k, m in enumerate(ms):
            x = x0 + k * (S + 6)
            out += _sign_img(m, x, y, S)
            if k == mark:
                out += f'<rect x="{x-3}" y="{y-3}" width="{S+6}" height="{S+6}" rx="4" class="hw-mark"/>'
        return out
    card = lambda x, y, w, h, cls="hw-card": f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" class="{cls}"/>'
    lines = lambda x, y: "".join(f'<path d="M{x+6} {y+8+i*6} H{x+24-(i%2)*6}" class="hw-ln"/>' for i in range(2))
    pics = [
        # 1. patterns: a text with one sign that keeps turning up at the end
        signs(SEAL_ROW[:4], 8, 22, mark=0) + '<path d="M11 56 Q14 64 22 64 H40" class="hw-arrow"/><text x="44" y="67" class="hw-t">often ends a text</text>',
        # 2. a guess: sign -> sound, with a question mark
        _sign_img(59, 14, 16, 30) + '<path d="M54 31 H78" class="hw-arrow"/><path d="M73 26 L78 31 L73 36" class="hw-arrow"/>'
        '<text x="86" y="37" class="hw-guess">mīn?</text><text x="8" y="67" class="hw-t">fish sign = “fish”?</text>',
        # 3. hidden texts: three open cards, one locked
        "".join(card(8 + i * 34, 14, 28, 36) + lines(8 + i * 34, 20) for i in range(3)) +
        card(110, 14, 28, 36, "hw-card hw-lock") + '<rect x="118" y="30" width="12" height="9" rx="1.5" class="hw-lk"/><path d="M120.5 30 v-3 a3.5 3.5 0 0 1 7 0 v3" class="hw-lk2"/>'
        '<text x="8" y="67" class="hw-t">a quarter kept unseen</text>',
        # 4. attack: a claim card with a shield
        card(10, 14, 52, 36) + lines(14, 20) + '<path d="M96 12 L114 18 V30 C114 41 106 47 96 51 C86 47 78 41 78 30 V18 Z" class="hw-shield"/>'
        '<path d="M89 31 L94 36 L104 26" class="hw-ok"/><path d="M66 32 H74" class="hw-arrow"/><text x="8" y="67" class="hw-t">a second team attacks</text>',
    ]
    steps = (("Find the patterns", "Which signs start texts, end them, or travel together."),
             ("Make a guess", "Suggest what a sign might mean or sound like."),
             ("Check it fairly", "Test the guess on texts we never looked at while building it."),
             ("Try to break it", "If it survives, we publish. If it fails, we publish that too."))
    items = "".join(f'<li><svg viewBox="0 0 150 74" aria-hidden="true">{p}</svg><b>{E(t)}</b><span>{E(d)}</span></li>'
                    for p, (t, d) in zip(pics, steps))
    key = ('<div class="how-key"><svg viewBox="0 0 92 40" aria-hidden="true">' + _sign_img(342, 6, 8, 24) +
           '<path d="M36 20 H52" class="hw-arrow"/><text x="58" y="26" class="hw-guess">“…”</text></svg>'
           '<p><b>The missing piece.</b> Most lost scripts were finally read through an outside clue, such as a name '
           'written in a script we can already read. None has been found for the Indus script yet, so we are looking for one.</p></div>')
    return f'<figure class="how-fig"><ol class="how" aria-label="How we try to read the script">{items}</ol>{key}</figure>'


def plan_steps():
    out = ['<ol class="flow">']
    for i, (cls, t, st, d) in enumerate(PLAN, 1):
        out.append(f'<li class="step {cls}"><span class="dot" aria-hidden="true">{i}</span><div><div class="sh">{E(t)} <span class="tag {cls}">{E(st)}</span></div><p>{E(d)}</p></div></li>')
    out.append("</ol>")
    return "".join(out)


NOVELTY = {"new": ("New", "We know of no earlier report of this."),
           "partly": ("Partly new", "The general idea was known; part of the result is new."),
           "tests": ("Tests an old idea", "Checks a reading or claim made by earlier scholars."),
           "known": ("Known, rechecked", "Already known; we re-tested it more strictly.")}


def nov_tag(k):
    return f'<span class="nov {k}">{E(NOVELTY[k][0])}</span>'


STRENGTH = [("strong", "Solid", 3), ("moderate", "Likely", 2), ("weak", "Shaky", 1),
            ("exploratory", "Not yet tested", 0), ("descriptive", "A measurement", -1)]


def meter(level):
    _, word, n = next(x for x in STRENGTH if x[0] == level)
    pips = "" if n < 0 else "".join(f'<i class="{"on" if k < n else ""}"></i>' for k in range(3))
    return f'<span class="meter {level}"><span class="pips" aria-hidden="true">{pips}</span>{E(word)}</span>'


def finding_fig(n):
    """A small drawing for each finding (viewBox 200x96)."""
    S = 22
    def row(ms, x0, y, gap=6, s=S):
        return "".join(_sign_img(m, x0 + k * (s + gap), y, s) for k, m in enumerate(ms))
    T = lambda x, y, t, c="hw-t", a="start": f'<text x="{x}" y="{y}" class="{c}" text-anchor="{a}">{E(t)}</text>'
    box = lambda x, y, w, h, c="hw-card": f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" class="{c}"/>'
    ok = lambda x, y: f'<path d="M{x} {y} l4 4 l8 -8" class="hw-ok"/>'
    no = lambda x, y: f'<path d="M{x} {y} l9 9 M{x+9} {y} l-9 9" class="hw-no"/>'
    d = {
        1: row([342, 99, 267, 176], 14, 10) + ok(134, 21) + T(156, 26, "real") +
           row([267, 342, 176, 99], 14, 52) + no(135, 59) + T(156, 68, "shuffled"),
        2: "".join(T(8, y + 11, l) + f'<rect x="64" y="{y}" width="{w}" height="14" rx="3" class="{c}"/>' + T(70 + w, y + 11, v)
                   for y, l, w, v, c in ((10, "alphabet", 8, "~26", "hw-bar"), (36, "syllables", 26, "~90", "hw-bar"), (62, "Indus", 104, "~400", "hw-bar hi"))),
        3: T(100, 10, "← read this way", a="middle") + row([342, 59, 267, 176], 44, 18) + T(4, 33, "plain") +
           row([60, 99, 267, 176], 44, 58) + f'<rect x="41" y="55" width="28" height="28" rx="4" class="hw-mark"/>' + T(4, 73, "ticks") + T(160, 73, "← end"),
        4: '<circle cx="48" cy="48" r="36" class="hw-card"/>' + row([267, 59, 99], 18, 37, 0, 20) +
           box(118, 14, 68, 68) + row([99, 267, 342], 124, 37, 0, 20) + T(48, 94, "Gulf round seal", a="middle") + T(152, 94, "usual square seal", a="middle"),
        5: f'<rect x="40" y="18" width="80" height="44" rx="22" class="hw-pill"/>' + row([109, 59], 52, 25, 12, 30) +
           T(136, 45, "always") + T(136, 58, "together") + T(80, 84, "like “New York”", a="middle"),
        6: box(8, 18, 44, 44) + _sign_img(342, 19, 29, S) + T(30, 80, "seal", a="middle") +
           box(70, 26, 60, 28) + row([99, 176], 76, 29, 4) + T(100, 80, "tablet", a="middle") +
           '<path d="M152 18 h28 l-4 8 c10 8 10 26 0 36 h-20 c-10 -10 -10 -28 0 -36 z" class="hw-card"/>' + _sign_img(267, 155, 32, 22) + T(166, 80, "pot", a="middle"),
        7: T(8, 24, "most") + row([342, 99, 267], 52, 8) + '<path d="M150 20 H190" class="hw-arrow"/><path d="M155 15 L150 20 L155 25" class="hw-arrow"/>' +
           T(8, 66, "a few") + row([267, 99, 342], 52, 50) + '<path d="M150 62 H190" class="hw-arrow hi"/><path d="M185 57 L190 62 L185 67" class="hw-arrow hi"/>',
        8: "".join(box(10 + i * 62, 14 - i * 0, 52, 56) + f'<circle cx="{36 + i * 62}" cy="32" r="10" class="hw-pic"/>' + _sign_img(176, 26 + i * 62, 46, 18) for i in range(3)) +
           T(100, 88, "same text + picture, repeated", a="middle"),
        9: "".join(box(x, 20, w, 40, "hw-slot") + T(x + w / 2, 78, l, a="middle") for x, w, l in ((8, 52, "opening"), (66, 70, "middle"), (142, 52, "closing"))) +
           row([342], 23, 29) + row([267, 176], 75, 29, 4) + row([99], 157, 29),
        10: box(8, 22, 40, 40, "hw-slot") + box(54, 22, 92, 40, "hw-slot hi") + box(152, 22, 40, 40, "hw-slot") +
            row([342], 17, 31) + row([59, 267], 74, 31, 8) + row([99], 161, 31) + T(100, 82, "core: one or two word-signs", a="middle"),
        11: row([59, 60, 65, 66, 67], 10, 22, 16, 22) + "".join(f'<path d="M{36 + k * 38} 33 h10" class="hw-arrow"/>' for k in range(4)) +
            f'<rect x="4" y="14" width="192" height="38" rx="19" class="hw-pill"/>' + T(100, 76, "they swap in for each other", a="middle"),
    }
    return f'<svg class="ffig" viewBox="0 0 200 96" aria-hidden="true">{d[n]}</svg>'


def findings_list(full):
    out = []
    for level, word, _ in STRENGTH:
        fs = [f for f in FINDINGS if f["level"] == level]
        if not fs:
            continue
        out.append(f'<h3 class="fgroup">{meter(level)}<span class="fgn">{len(fs)}</span></h3><ol class="findings">')
        for f in fs:
            head = E(f["head"])
            links = " ".join(repo_link(p + "/", p.split("/")[-1]) for p in f["folders"])
            cav = f'<p class="caveat">{E(f["caveat"])}</p>' if f.get("caveat") else ""
            out.append(f'<li class="finding fcard" id="f{f["n"]}">{finding_fig(f["n"])}<div class="fh"><h4 class="ft">{head}</h4>{nov_tag(f["novelty"])}'
                       f'<p class="fg">{E(f["gist"])}</p><details class="tech"><summary>Technical version</summary>'
                       f'<div class="fbody"><p class="ftech">{E(f["title"])}</p><p>{E(f["plain"])}</p><p class="prior"><b>Earlier work:</b> {E(f["prior"])}</p>'
                       f'<p class="nums">{E(f["nums"])}</p>{cav}<p class="where">Code and results: {links}</p></div></details></div></li>')
        out.append("</ol>")
    return "".join(out)


def level_key():
    return ('<dl class="levels">' + "".join(
        f'<div><dt>{meter(k)}</dt><dd>{E(LEVELS[k][1])}</dd></div>' for k, _, _ in STRENGTH) + "</dl>"
        '<h3 class="key-h">Is it new?</h3><dl class="levels">' + "".join(
        f'<div><dt>{nov_tag(k)}</dt><dd>{E(d)}</dd></div>' for k, (_, d) in NOVELTY.items()) + "</dl>")


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


DIST_ASSETS = ["site.css", "site.js", "glyphs.css", "favicon.svg", "favicon-32.png", "apple-touch-icon.png", "email-logo.png",
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
    stale = [str(f.relative_to(dist)) for f in files if f.suffix in (".html", ".css", ".js", ".txt", ".svg")
             and "OWNER/REPO" in f.read_text(errors="ignore")]
    assert not stale, f"dist still has the OWNER/REPO placeholder in: {stale}"
    print("dist: no OWNER/REPO placeholder left")
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
                            HERO=seal_object(), BAND=sign_band(), DATA_FIG=data_figure(), HOW_FIG=fig_how(),
                            LADDER=ladder(caption=False),
                            FIG_TEXT=figure("EH_3", 1, "Square stamp seal from Harappa: a line of Indus signs above a one-horned bull standing before a feeding trough")),
                        body_class="oi-page"))
    built.append(render("approach", f"Approach · {NAME} · Decipher the Indus script by 2027",
                        "What counts as deciphering the Indus script, the rules every test follows, the agent team, the routes to sound values and the directions still open.",
                        "approach.html", dict(common, SLOTS=slots(), CHART_ROUND=chart_round(), CHART_NAMES=chart_names(), PLAN=plan_steps(), FIG_PIPE=fig_pipeline())))
    built.append(render("findings", f"Findings · {NAME} · Decipher the Indus script by 2027",
                        "Ranked findings about the Indus script with their evidence, and every route the project has tested and closed.",
                        "findings.html", dict(common, LEVELS=level_key(), FINDINGS=findings_list(True),
                            ROUTES=closed_routes(sections, rows), FIG_ROUTES=fig_routes(sections, rows), FIG_SIGNS=fig_signs(), FIG_MIRROR=fig_mirror(), FIG_MAP=fig_map(), FIG_SEALS=figure("EH_16", 2, "Square stamp seal from Harappa with a line of signs above an animal") + figure("FEM_273", 3, "Long clay impression of a one-line seal text"), REVERSALS=reversals(rev), PAPERS=papers(),
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
                            SZ_OFL=size_kb(fs["OFL.txt"]), SZ_ZIP=size_kb(fs["open-indus-fonts.zip"]), MARK_BIG=inline_mark().replace('class="mark"', 'class="mark-big"'),
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
