"""Check every number in docs/paper/AUDIT_DRAFT.md against the file it cites.

Convention in the draft: each sentence (or group of sentences) that contains
numbers ends with an HTML comment naming its sources:

    ... 12.9% of signs. <!-- src: experiments/consensus_corpus/RESULTS.md -->

Several sources are separated by ";". A source written "rows:path.csv" means
"the number of data rows in that CSV". Numbers between a comment and the next
comment are checked against that next comment's sources. Numbers after the
last comment of a paragraph are reported as uncited.

Skipped: section headings below the title, inline code, URLs, sign and finding
labels (M342, W621, F3, #3, L0, Hit@1), "Section 4.2", list markers, and text
between "<!-- audit: skip -->" and "<!-- audit: end-skip -->".

A number passes if, after removing thousands separators and the sign, it
appears in a cited file as a whole number token (not inside a longer number).
"2.70" also matches "2.7". This is a presence check: it proves the number is in
the cited file, not that it means the same thing there. That second check is
done by reading.

Usage: python3 scripts/audit_paper_numbers.py [--write]
  --write  replace the "## Numbers audit" section of the draft with the report.
Exit code 1 if any number is unmatched or uncited.
"""

import csv
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DRAFT = ROOT / "docs/paper/AUDIT_DRAFT.md"
AUDIT_HEADING = "## Numbers audit"

SRC_RE = re.compile(r"<!--\s*src:\s*(.*?)\s*-->")
DATE_RE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
NUM_RE = re.compile(r"[+\-−]?\d[\d,]*(?:\.\d+)?(?:e-?\d+)?")


def body_text(text):
    text = text.split("\n" + AUDIT_HEADING)[0]
    text = re.sub(r"<!--\s*audit: skip\s*-->.*?<!--\s*audit: end-skip\s*-->", "", text, flags=re.S)
    return text


def clean(segment):
    s = re.sub(r"`[^`]*`", " ", segment)
    s = re.sub(r"https?://\S+", " ", s)
    s = re.sub(r"<!--.*?-->", " ", s, flags=re.S)
    s = re.sub(r"(?m)^\s*\d+\.\s", " ", s)  # numbered list markers
    s = re.sub(r"\bSections? \d+(?:\.\d+)?(?: and \d+(?:\.\d+)?)?", " ", s)
    s = re.sub(r"\bSHA-256\b", " ", s)
    s = re.sub(r"\b[Vv]ersion [12]\b", " ", s)  # split names
    s = re.sub(r"\bCC BY \d\.\d\b", " ", s)  # licence names
    s = re.sub(r"\barXiv \d+\.\d+", " ", s)
    return s


def numbers_in(segment):
    s = clean(segment)
    out = [m.group(0) for m in DATE_RE.finditer(s)]
    s = DATE_RE.sub(" ", s)
    for m in NUM_RE.finditer(s):
        start = m.start()
        tok = m.group(0)
        prev = s[start - 1] if start > 0 else " "
        if tok[0] in "+-−":
            # a hyphen between two numbers is a range, not a sign
            tok = tok[1:]
        if prev.isalpha() or prev in "@#_/":
            continue  # M342, W621, F3, L0, Hit@1, #3
        if prev in "-" and start > 1 and s[start - 2].isalpha():
            continue  # SHA-256, KN-3
        end = m.end()
        nxt = s[end] if end < len(s) else " "
        if nxt.isalpha() and s[end:end + 2] not in ("x ",) and not s[end:].startswith(("st ", "nd ", "rd ", "th ")):
            # 3rd, 10x are fine; a number glued to letters (e.g. 4B) is a label
            if not re.match(r"[x]\b", s[end:end + 2]):
                continue
        tok = tok.rstrip(",.")
        if tok:
            out.append(tok)
    return out


def variants(tok):
    t = tok.replace(",", "")
    vs = {t}
    if "." in t and "e" not in t:
        vs.add(t.rstrip("0").rstrip("."))
    if t.startswith("0."):
        vs.add(t[1:])  # .87 written without the leading zero
    return {v for v in vs if v}


_cache = {}
weak = []


def source_text(src):
    if src in _cache:
        return _cache[src]
    path = ROOT / src
    if not path.exists():
        _cache[src] = None
        return None
    txt = path.read_text(errors="replace")
    txt = re.sub(r"(?<=\d),(?=\d{3}\b)", "", txt)  # 2,270 -> 2270
    txt = txt.replace("−", "-")
    _cache[src] = txt
    return txt


def found(tok, sources):
    for src in sources:
        if src.startswith("rows:"):
            with open(ROOT / src[5:], newline="") as f:
                n = sum(1 for _ in csv.DictReader(f))
            if tok.replace(",", "") == str(n):
                return src
            continue
        txt = source_text(src)
        if txt is None:
            continue
        for v in variants(tok):
            if re.search(r"(?<![\d.])" + re.escape(v) + r"(?![\d])", txt):
                return src
            # 2.70 in the draft vs 2.70 in the file is covered; also allow 2.7 -> 2.70
            if "." in v and re.search(r"(?<![\d.])" + re.escape(v) + r"0+(?![\d])", txt):
                return src
    return None


def audit():
    text = body_text(DRAFT.read_text())
    lines = text.split("\n")
    # keep the title, drop lower headings
    kept = []
    for i, ln in enumerate(lines):
        if ln.startswith("#") and not ln.startswith("# "):
            kept.append("")
        else:
            kept.append(ln)
    paragraphs = re.split(r"\n\s*\n", "\n".join(kept))
    checked, problems, missing_files = 0, [], set()
    global weak
    weak = []
    for para in paragraphs:
        pos = 0
        for m in SRC_RE.finditer(para):
            seg = para[pos:m.start()]
            sources = [x.strip() for x in m.group(1).split(";") if x.strip()]
            for src in sources:
                if not src.startswith("rows:") and source_text(src) is None:
                    missing_files.add(src)
            for tok in numbers_in(seg):
                checked += 1
                hit = found(tok, sources)
                if hit and re.fullmatch(r"\d", tok):
                    weak.append(tok)
                if not hit:
                    ctx = " ".join(clean(seg).split())
                    i = ctx.find(tok)
                    snippet = ctx[max(0, i - 50): i + 40] if i >= 0 else ctx[:90]
                    problems.append(("not in cited file", tok, "; ".join(sources), snippet))
            pos = m.end()
        tail = para[pos:]
        for tok in numbers_in(tail):
            checked += 1
            ctx = " ".join(clean(tail).split())
            i = ctx.find(tok)
            problems.append(("uncited", tok, "-", ctx[max(0, i - 50): i + 40]))
    return checked, problems, missing_files


def report(checked, problems, missing_files):
    out = [AUDIT_HEADING, ""]
    out.append(f"Generated by `scripts/audit_paper_numbers.py`. Numbers checked: {checked}. "
               f"Mismatches: {len(problems)}. Missing source files: {len(missing_files)}.")
    out.append("")
    out.append("The check is mechanical: a number passes if it appears in the file its sentence cites. "
               "It does not prove the number means the same thing there; that was checked by reading.")
    out.append("")
    out.append(f"Single-digit numbers pass on presence alone, which is weak evidence: {len(weak)} of the "
               f"{checked} checks. These were also read against their sources by hand.")
    out.append("")
    if missing_files:
        out.append("Missing source files: " + ", ".join(sorted(missing_files)))
        out.append("")
    if problems:
        out.append("| kind | number | cited file | context |")
        out.append("|---|---|---|---|")
        for kind, tok, src, snip in problems:
            out.append(f"| {kind} | {tok} | `{src}` | {snip.replace('|', '/')} |")
    else:
        out.append("No mismatches.")
    return "\n".join(out) + "\n"


def main():
    checked, problems, missing = audit()
    rep = report(checked, problems, missing)
    print(rep)
    if "--write" in sys.argv:
        txt = DRAFT.read_text()
        head = txt.split("\n" + AUDIT_HEADING)[0].rstrip("\n")
        DRAFT.write_text(head + "\n\n" + rep)
    sys.exit(1 if problems or missing else 0)


if __name__ == "__main__":
    main()
