"""Scorecard staleness check. Flags rows to re-rate; never changes a tier.
For each row, the evidence it names is compared between the commit that holds its current rating and the working tree:
  - meaning-claim rows: that row of CATALOGUE.csv (status, status detail, claim);
  - 'docs/NEGATIVE_ATLAS.md section X': the text of that section;
  - 'README.md table row #i': that row of the "What we can defend" table;
  - any other repo path: the whole file (a folder: its RESULTS.md).
A row is flagged if any of its evidence units changed. A second pass flags catalogue rows still marked 'testable'
whose id is cited in some experiment's RESULTS.md or a prereg (a test may have been run and the catalogue not updated).
Run: .venv/bin/python -I experiments/scorecard_v1/staleness.py   -> staleness.json
"""
import csv, io, json, re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
import build_rows  # noqa: E402

PATH_RE = re.compile(r"((?:experiments|docs)/[\w./-]*[\w/]|README\.md)")
CAT = "experiments/meaning_claims/CATALOGUE.csv"


def git(*a):
    return subprocess.run(["git", "-C", str(ROOT), *a], capture_output=True, text=True).stdout


def at(commit, path):
    """File text at a commit (None if absent); commit None = working tree."""
    if commit is None:
        p = ROOT / path
        return p.read_text(errors="ignore") if p.is_file() else None
    out = subprocess.run(["git", "-C", str(ROOT), "show", f"{commit}:{path}"], capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


def atlas_section(text, sec):
    if text is None:
        return None
    m = re.search(rf"^###? {re.escape(sec)}\b.*?(?=^###? |\Z)", text, re.S | re.M)
    return m.group(0) if m else None


def readme_row(text, i):
    if text is None:
        return None
    m = re.search(rf"^\| {i} \|.*$", text, re.M)
    return m.group(0) if m else None


def catalogue_row(text, cid):
    if text is None:
        return None
    for x in csv.DictReader(io.StringIO(text)):
        if x["id"] == cid:
            return (x["claimed_meaning"], x["status"], x["status_detail"])
    return None


def units(row):
    """(label, extractor(commit)) for each evidence unit of a row."""
    ev = row["evidence"]; out = []
    if row["id"].startswith("MC-"):
        cid = row["id"][3:]
        out.append((f"{CAT} row {cid}", lambda c, cid=cid: catalogue_row(at(c, CAT), cid)))
        return out
    for sec in re.findall(r"NEGATIVE_ATLAS\.md section ([\d.]+)", ev):
        out.append((f"NEGATIVE_ATLAS section {sec}", lambda c, s=sec: atlas_section(at(c, "docs/NEGATIVE_ATLAS.md"), s)))
    m = re.search(r"README\.md table row #(\d+)", ev)
    if m:
        out.append((f"README row #{m.group(1)}", lambda c, i=m.group(1): readme_row(at(c, "README.md"), i)))
    for p in sorted(set(PATH_RE.findall(ev))):
        if p in ("docs/NEGATIVE_ATLAS.md", "README.md", CAT):
            continue
        q = p.rstrip("/") + "/RESULTS.md" if (ROOT / p).is_dir() else p
        out.append((q, lambda c, q=q: at(c, q)))
    return out


UNTRACKED_CACHE = set()


def rating_commits():
    """id -> commit holding the row's current rating (addendum raters override v1.0 raters)."""
    rc = {}
    for f in ("rater_A.json", "rater_B.json", "rater_C.json", "rater_D.json", "rater_E.json", "rater_F.json"):
        path = f"experiments/scorecard_v1/{f}"
        h = git("log", "-1", "--format=%H", "--", path).strip()
        if not h:
            continue
        for x in json.loads(at(h, path)):
            if f in ("rater_D.json", "rater_E.json", "rater_F.json") or x["id"] not in rc:
                rc[x["id"]] = h
    return rc


def main():
    rows = build_rows.build()
    final = {r["id"]: r for r in json.load(open(HERE / "final.json"))["rows"]}
    rc = rating_commits()
    flags = []
    for r in rows:
        i = r["id"]
        if i not in rc:
            flags.append(dict(id=i, tier=None, why="row not rated", changed=[])); continue
        changed = []
        t_rated = int(git("show", "-s", "--format=%ct", rc[i]).strip())
        for lab, f in units(r):
            if lab in UNTRACKED_CACHE or not git("ls-files", lab.split(" ")[0]).strip() and (ROOT / lab).is_file():
                # local-only file (gitignored): no history, so compare modification time with the rating commit
                UNTRACKED_CACHE.add(lab)
                if (ROOT / lab).stat().st_mtime > t_rated:
                    changed.append(lab + " (local file, modified after rating)")
            elif f(rc[i]) != f(None):
                changed.append(lab)
        if changed:
            flags.append(dict(id=i, tier=final.get(i, {}).get("tier"), why="evidence changed after rating", changed=changed, rated_at=rc[i][:7]))
    docs = list((ROOT / "experiments").glob("*/RESULTS.md")) + list((ROOT / "docs/prereg").glob("*.md"))
    text = {d: d.read_text(errors="ignore") for d in docs}
    for x in csv.DictReader(open(ROOT / CAT)):
        if not x["status"].startswith("testable"):
            continue
        hits = [str(d.relative_to(ROOT)) for d, t in text.items()
                if re.search(rf"(?<![\w-]){re.escape(x['id'])}(?![\w-])", t) and "meaning_claims" not in str(d) and "scorecard" not in str(d)]
        if hits:
            flags.append(dict(id="MC-" + x["id"], tier=final.get("MC-" + x["id"], {}).get("tier"),
                              why="catalogue says testable but a result or prereg cites it", changed=hits))
    json.dump(flags, open(HERE / "staleness.json", "w"), indent=1)
    print(f"{len(rows)} rows checked, {len(flags)} flags")
    for f in flags:
        print(f["id"], f["tier"], "|", f["why"], "|", ", ".join(f["changed"])[:220])


if __name__ == "__main__":
    main()
