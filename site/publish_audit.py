"""Approximate what .gitignore.proposed would publish, and flag risky content in what is kept.
Read-only; reads file names, sizes and text, writes nothing.

Usage, from the repo root:  python3 -I site/publish_audit.py . "<a name or word to search for>"
The rules below mirror .gitignore.proposed by hand; if you change one, change the other.
Once the repo is a git repository, `git status --ignored` is the exact answer."""
import os, re, sys, fnmatch
from collections import Counter

root, owner = sys.argv[1], sys.argv[2]
IMG = (".png", ".jpg", ".jpeg", ".tif", ".tiff", ".pdf")
BIN = (".pyc", ".pkl", ".npz", ".npy", ".zip", ".log", ".err")
KEEP_IMG = re.compile(r"^experiments/plate_corpus/crops/plate_[^/]*\.png$|^experiments/decipherability/phase_diagram\.png$")


def dropped(rel, is_dir):
    parts = rel.split("/")
    name = parts[-1]
    if is_dir:
        if name in (".venv", "__pycache__", ".git") and rel != ".git": return True
        if rel in ("sources", "docs/outreach", "docs/site", "experiments/iconography", "experiments/scene_text"): return True
        if len(parts) == 3 and parts[0] == "experiments" and name in ("raw", "ext", "data", "work"): return True
        return False
    if name == ".DS_Store" or name.endswith(BIN) or name.startswith("cisi_"): return True
    if rel in ("board/compute.lock", "results/top120_signs.png") or rel.startswith("board/board.db"): return True
    if fnmatch.fnmatch(rel, "experiments/fable52_plan*") or fnmatch.fnmatch(rel, "docs/fable_brief*.md"): return True
    if parts[0] == "data": return True
    if fnmatch.fnmatch(rel, "experiments/plate_corpus/crops/plate_CE_*"): return True
    if parts[0] == "experiments" and name.lower().endswith(IMG) and not KEEP_IMG.match(rel): return True
    return False


kept, total, big, by_top = [], 0, [], Counter()
for d, dirs, files in os.walk(root):
    reld = os.path.relpath(d, root)
    reld = "" if reld == "." else reld
    dirs[:] = [x for x in dirs if not dropped(f"{reld}/{x}".lstrip("/"), True)]
    for f in files:
        rel = f"{reld}/{f}".lstrip("/")
        p = os.path.join(d, f)
        try: sz = os.path.getsize(p)
        except OSError: continue
        if dropped(rel, False): continue
        kept.append((rel, sz)); total += sz; by_top[rel.split("/")[0]] += sz
        if sz > 5_000_000: big.append((rel, sz))

print(f"kept files: {len(kept)}  total: {total/1e6:.1f} MB")
for k, v in by_top.most_common(): print(f"  {k:<28}{v/1e6:8.2f} MB")
print("files over 5 MB:", *[f"{r} {s/1e6:.1f} MB" for r, s in sorted(big, key=lambda x: -x[1])], sep="\n  ")

pat = {"owner name": re.compile(re.escape(owner), re.I), "local path": re.compile(r"/Users/|/home/[a-z]"),
       "email": re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+"), "crack": re.compile(r"\bcrack", re.I)}
hits = {k: [] for k in pat}
for rel, sz in kept:
    if sz > 3_000_000 or rel.lower().endswith(IMG + (".png", ".svg", ".woff2", ".db")): continue
    try: t = open(os.path.join(root, rel), encoding="utf-8", errors="ignore").read()
    except OSError: continue
    for k, r in pat.items():
        n = len(r.findall(t))
        if n: hits[k].append((rel, n))
for k, v in hits.items():
    print(f"\n{k}: {len(v)} files")
    for rel, n in sorted(v, key=lambda x: -x[1])[:25]: print(f"  {n:5d}  {rel}")

words = re.compile(r"lemma|vocab|dict|dedr|monier|lexicon|wordlist|_lm\.", re.I)
wl = [(r, s) for r, s in kept if r.startswith("experiments/") and words.search(r.split("/")[-1]) and not r.endswith((".py", ".md"))]
print(f"\nthird-party word lists kept (by file name): {len(wl)} files, {sum(s for _, s in wl)/1e6:.1f} MB")
for r, s in sorted(wl, key=lambda x: -x[1])[:30]: print(f"  {s/1e3:8.0f} KB  {r}")
imgs = [r for r, s in kept if r.lower().endswith(IMG)]
print("\nimages kept:", len(imgs)); print("  " + "\n  ".join(sorted(imgs)))

tok = re.compile(r"\b(?:M|W)\d{1,3}\b")
whole = []
for rel, sz in kept:
    if rel.startswith("experiments/") and rel.endswith((".csv", ".json", ".jsonl", ".tsv", ".txt")) and sz < 8e6:
        n = len(tok.findall(open(os.path.join(root, rel), errors="ignore").read()))
        if n >= 2000: whole.append((n, rel, sz))
whole.sort(reverse=True)
print(f"\nresult files listing many whole texts (2,000+ sign tokens): {len(whole)} files, {sum(w[2] for w in whole)/1e6:.1f} MB")
for n, rel, sz in whole: print(f"  {n:6d} tokens  {rel}")
