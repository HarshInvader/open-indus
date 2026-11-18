"""Rebuild the Indus data on your own machine from public sources.

    python3 datasets/fetch.py list               # what exists, by tier (see catalog.csv)
    python3 datasets/fetch.py corpus             # clone the corpora at pinned commits, build data/, restore the frozen splits
    python3 datasets/fetch.py reports [--pdf]    # OCR text (and optionally PDFs) of every archive.org excavation report

Nothing fetched here is republished in this repository: the corpora state no terms that allow it, and
the report scans have an uncertain US status (LICENSING.md). Downloads go to sources/, data/ and
datasets/local/, which git ignores. One request per second; please keep it that way.
"""
import csv, hashlib, json, subprocess, sys, time, urllib.parse, urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HERE = ROOT / "datasets"
UA = {"User-Agent": "open-indus-dataset-fetch (+https://github.com/HarshInvader/open-indus)"}
REPOS = {  # folder in sources/ -> (url, commit used by every result in this repository)
    "paragorth_Indus-": ("https://github.com/paragorth/Indus-.git", "d62ec82d58642038640da25a97177d7a1fddc9d9"),
    "field-cady_indus_valley_script_corpus": ("https://github.com/field-cady/indus_valley_script_corpus.git", "30308260d8da50151a79185c9e98404db9da331a"),
    "shaunmortal_indus": ("https://github.com/shaunmortal/indus.git", "23c4884886709ed1ed5e56a1e174e089b62cd27b"),
    "joyboseroy_indus_decipher": ("https://github.com/joyboseroy/indus_decipher.git", "cd600349f6d3193a241c3eb87ff80a2a65377efc"),
}


def get(url):
    time.sleep(1.0)
    return urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=120).read()


def catalog():
    return list(csv.DictReader(open(HERE / "catalog.csv", encoding="utf-8")))


def cmd_list():
    rows = catalog()
    for tier, label in (("included", "In this repository (datasets/open/)"), ("fetch", "Public: rebuild with this script or the link"),
                        ("reference", "Not shareable: where to find it")):
        sel = [r for r in rows if r["tier"] == tier]
        print(f"\n{label}: {len(sel)}")
        for r in sel:
            print(f"  {r['id'][:48]:48}  {r['title'][:90]}")


def run(cmd, **kw):
    print("+", " ".join(cmd)); subprocess.run(cmd, check=True, **kw)


def restore_splits():
    sys.path.insert(0, str(ROOT / "corpus"))
    import load as L  # noqa
    seq_of = {}
    for t in L.m77_texts():
        seq_of.setdefault(f'{t["text_no"]}.{t["side"]}', " ".join(t["seq"]))
    for fn in ("splits_v2.json", "splits.json"):
        j = json.load(open(HERE / "splits" / fn.replace(".json", "_ids.json")))
        held = sorted(seq_of[i] for i in j.pop("heldout_ids"))
        j.pop("note", None)
        sha = hashlib.sha256("\n".join(held).encode()).hexdigest()
        if sha != j["sha256"]:
            sys.exit(f"{fn}: rebuilt split does not match (sha256 {sha[:16]} vs {j['sha256'][:16]}); "
                     "the corpus source differs from the pinned commit")
        j["heldout"] = held
        json.dump(j, open(ROOT / "data" / fn, "w"), indent=0)
        print(f"{fn}: {len(held)} held-out sequences restored, sha256 matches")


def cmd_corpus():
    src = ROOT / "sources"; src.mkdir(exist_ok=True)
    for name, (url, commit) in REPOS.items():
        d = src / name
        if not d.exists():
            run(["git", "clone", "--quiet", url, str(d)])
        run(["git", "-C", str(d), "checkout", "--quiet", commit])
    # build.py draws its own split when none is frozen (and its v1 split depends on the hash seed),
    # so build first, then overwrite both splits with the frozen ones every result used
    run([sys.executable, "-I", "corpus/build.py"], cwd=ROOT)
    restore_splits()


def cmd_reports(pdf=False):
    out = HERE / "local" / "reports"; out.mkdir(parents=True, exist_ok=True)
    for r in catalog():
        if not r["id"].startswith("archive:"):
            continue
        ident = r["id"][8:]
        d = out / ident; d.mkdir(exist_ok=True)
        try:
            meta = json.loads(get(f"https://archive.org/metadata/{urllib.parse.quote(ident)}"))
        except Exception as e:
            print("skip", ident, e); continue
        files = [f["name"] for f in meta.get("files", [])]
        want = [f for f in files if f.endswith("_djvu.txt")] + ([f for f in files if f.endswith(".pdf")][:1] if pdf else [])
        for f in want:
            p = d / Path(f).name
            if p.exists():
                continue
            try:
                p.write_bytes(get(f"https://archive.org/download/{urllib.parse.quote(ident)}/{urllib.parse.quote(f)}"))
                print("got", ident, f)
            except Exception as e:
                print("fail", ident, f, e)
        json.dump(dict(identifier=ident, title=r["title"], url=r["origin"], files=want), open(d / "SOURCE.json", "w"), indent=1)


if __name__ == "__main__":
    a = sys.argv[1:] or ["list"]
    {"list": cmd_list, "corpus": cmd_corpus, "reports": lambda: cmd_reports("--pdf" in a)}.get(a[0], cmd_list)()
