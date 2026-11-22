"""Build the anonymised reproducibility archive for reviewers of the uniformity paper.

    .venv/bin/python -I docs/paper/uniformity/review_package/build_package.py

What goes in (all of it tracked in git, so nothing gitignored for licence reasons can slip in):
  - the experiment folders the paper uses (code, results.json, draws*.jsonl, ledger_rows.csv, RESULTS.md);
  - every local module they import, found by following imports and sys.path inserts from those folders;
  - the derived, tracked data files they read from other experiments (DERIVED below);
  - the corpus build script, the pool builders and fetch scripts, board/run.sh;
  - the pre-registrations for these runs and docs/prereg/HASHES.txt;
  - the figure scripts and the published figures;
  - REPRODUCE.md, SOURCES.md, README.md from this folder, and an environment lock written now.
Third-party corpora (Indus corpora, ORACC, CDLI, EDH, DAMOS, ...) are never copied: they are untracked.

Anonymisation: text files are rewritten with SUBST, then the tree is searched for FORBIDDEN and the build fails
on any hit. The zip is deterministic (sorted names, fixed timestamps), so the same tree gives the same bytes.
Outputs: MANIFEST.tsv (committed) and uniformity_review_archive.zip (gitignored), both in this folder.
"""
import ast
import hashlib
import re
import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
STAGE = HERE / "build" / "review_archive"
ZIP = HERE / "uniformity_review_archive.zip"

EXPERIMENTS = [
    "experiments/uniformity_benchmark",
    "experiments/redteam_uniformity",
    "experiments/uniformity_paper",  # step1, step2, revision
    "experiments/redteam_uniformity_step1",
    "experiments/redteam_uniformity_step2",
    "experiments/chanhudaro_followup",
    "experiments/recchia_rerun",
    "experiments/uniformity_referee_checks",
]
PREREG = [
    "docs/prereg/HASHES.txt",
    "docs/prereg/site_signal.md",  # the frozen scoring pipeline (experiments/site_signal/lib.py)
    "docs/prereg/uniformity_benchmark.md",
    "docs/prereg/redteam_uniformity.md",
    "docs/prereg/uniformity_paper_step1.md",
    "docs/prereg/redteam_uniformity_step1.md",
    "docs/prereg/uniformity_paper_step2.md",
    "docs/prereg/redteam_uniformity_step2.md",
    "docs/prereg/chanhudaro_followup.md",
    "docs/prereg/recchia_rerun.md",
    "docs/prereg/uniformity_paper_revision.md",
    "docs/prereg/uniformity_paper_contrast.md",
    "docs/prereg/uniformity_referee_checks.md",
]
# Tracked files of our own that the code reads from other experiments (derived tables, no third-party text).
DERIVED = [
    "experiments/audit_followups/out/b_editor_agreement.json",
    "experiments/consensus_corpus/out/seq_links.json",
    "experiments/numeral_grammar/inventory.csv",
    "experiments/old_registers/registers.csv",
    "experiments/protocuneiform/pc_lines.json",
    "experiments/reg_harappa/findspots.csv",
    "experiments/signlist_robustness/variants.json",
]
OTHER = [
    "board/run.sh",
    "corpus/__init__.py",
    "corpus/build.py",
    "corpus/load.py",
    "docs/paper/uniformity/figures/_style.py",
    "docs/paper/uniformity/figures/make_fig1_between_within.py",
    "docs/paper/uniformity/figures/make_fig3_power.py",
    "docs/paper/uniformity/figures/make_fig4_sites.py",
    "docs/paper/uniformity/latex/figures/fig1_between_within.pdf",
    "docs/paper/uniformity/latex/figures/fig1_between_within.png",
    "docs/paper/uniformity/latex/figures/fig2_gap.pdf",
    "docs/paper/uniformity/latex/figures/fig2_gap.png",
    "docs/paper/uniformity/latex/figures/fig3_power.pdf",
    "docs/paper/uniformity/latex/figures/fig3_power.png",
    "docs/paper/uniformity/latex/figures/fig4_sites.pdf",
    "docs/paper/uniformity/latex/figures/fig4_sites.png",
]
PACKAGE_DOCS = ["README.md", "REPRODUCE.md", "SOURCES.md"]

# Literal substitutions applied to every text file in the archive (order matters: longest first).
SUBST = [
    ("open-citizen-science/.local/", "<shared-lock-dir>/"),
    ("open-citizen-science", "<parent-dir>"),
    ("Open Citizen Science", "<parent project>"),
]
# Generic patterns live here. Names of people, accounts and projects are kept out of the public repository: they
# are read from forbidden_terms.txt next to this script (gitignored, one term per line), and the build refuses to
# run without it.
GENERIC = [r"/Users/", r"pages\.dev", r"[@]g" + "mail", r"indus-decipher"]
TERMS_FILE = HERE / "forbidden_terms.txt"
TEXT_EXT = {".py", ".sh", ".md", ".txt", ".json", ".jsonl", ".csv", ".tsv", ""}


def git_files(*paths):
    out = subprocess.check_output(["git", "-C", str(ROOT), "ls-files", "-z", "--", *paths])
    return [p for p in out.decode().split("\0") if p]


def local_imports(files):
    """Follow imports from the given .py files to local modules (repo root, the file's folder, sys.path inserts)."""
    # Search order: the paper's own folders first (they are on sys.path when its scripts run), then the
    # repository root, then other experiment folders in sorted order (for helpers inserted by name).
    own = [ROOT / e for e in EXPERIMENTS] + [ROOT / "experiments/uniformity_paper" / s
                                            for s in ("step1", "step2", "revision")]
    dirs = own + [ROOT] + sorted(p for p in (ROOT / "experiments").iterdir() if p.is_dir() and p not in own)
    todo, seen = [f for f in files if f.endswith(".py")], set()
    while todo:
        f = todo.pop()
        if f in seen:
            continue
        seen.add(f)
        src = (ROOT / f).read_text(encoding="utf-8")
        mods = set()
        for n in ast.walk(ast.parse(src)):
            if isinstance(n, ast.Import):
                mods |= {a.name for a in n.names}
            elif isinstance(n, ast.ImportFrom) and n.module and n.level == 0:
                mods.add(n.module)
        for m in mods:
            path = m.replace(".", "/")
            cands = [c for d in [(ROOT / f).parent] + dirs
                     for c in (d / (path + ".py"), d / path / "__init__.py") if c.exists()]
            if cands:  # first match wins, as on sys.path
                todo.append(str(cands[0].relative_to(ROOT)))
                if m.startswith("corpus."):
                    todo.append("corpus/__init__.py")
    return seen


def forbidden():
    if not TERMS_FILE.exists():
        sys.exit(f"missing {TERMS_FILE.name}: list the names, accounts and project names to keep out, one per line")
    terms = [t.strip() for t in TERMS_FILE.read_text().splitlines() if t.strip() and not t.startswith("#")]
    return re.compile("|".join(GENERIC + [re.escape(t) for t in terms]), re.I)


def main():
    FORBIDDEN = forbidden()
    files = set(git_files(*EXPERIMENTS)) | set(PREREG) | set(DERIVED) | set(OTHER)
    files |= local_imports(sorted(files))
    tracked = set(git_files())
    missing = sorted(f for f in files if f not in tracked)
    if missing:
        sys.exit("not tracked in git (refusing to package): " + ", ".join(missing))

    if STAGE.parent.exists():
        shutil.rmtree(STAGE.parent)
    STAGE.mkdir(parents=True)
    changed = []
    for rel in sorted(files):
        src, dst = ROOT / rel, STAGE / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        if src.suffix in TEXT_EXT:
            text = data.decode("utf-8")
            new = text
            for a, b in SUBST:
                new = new.replace(a, b)
            if new != text:
                changed.append((rel, hashlib.sha256(data).hexdigest()))
            data = new.encode("utf-8")
        dst.write_bytes(data)
        if src.stat().st_mode & 0o111:
            dst.chmod(0o755)
    for name in PACKAGE_DOCS:
        shutil.copy(HERE / name, STAGE / name)

    env = STAGE / "environment"
    env.mkdir()
    py = ROOT / ".venv/bin/python"
    freeze = subprocess.check_output([str(py), "-I", "-m", "pip", "freeze"]).decode()
    (env / "requirements.lock.txt").write_text(freeze)
    ver = subprocess.check_output([str(py), "-I", "-c",
                                   "import sys, platform; print(sys.version); print(platform.machine())"]).decode()
    (env / "python_version.txt").write_text(ver)
    (env / "ANONYMISED_FILES.txt").write_text(
        "Files whose text was edited for anonymity. Only local folder names in notes about the compute lock were\n"
        "replaced (<parent-dir>, <shared-lock-dir>); no code path, number or result changed. Because the bytes\n"
        "changed, files listed here that are also in docs/prereg/HASHES.txt will not match their hash in this copy.\n"
        "The SHA-256 of each original file is given so it can be checked against the public repository later.\n\n"
        + "".join(f"{h}  {r}\n" for r, h in changed))

    figs = STAGE / "docs/paper/uniformity/latex/figures"
    (figs / "SHA256SUMS").write_text("".join(
        f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.name}\n" for p in sorted(figs.iterdir()) if p.is_file()))

    hits = []
    for p in sorted(STAGE.rglob("*")):
        if p.is_file():
            try:
                t = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                t = p.read_bytes().decode("latin-1")
            for i, line in enumerate(t.splitlines(), 1):
                if FORBIDDEN.search(line) or FORBIDDEN.search(str(p.relative_to(STAGE))):
                    hits.append(f"{p.relative_to(STAGE)}:{i}: {line[:120]}")
    if hits:
        sys.exit("identifying strings left in the archive:\n" + "\n".join(hits[:50]))

    rows = []
    for p in sorted(STAGE.rglob("*")):
        if p.is_file():
            b = p.read_bytes()
            rows.append((str(p.relative_to(STAGE)), len(b), hashlib.sha256(b).hexdigest()))
    (HERE / "MANIFEST.tsv").write_text("path\tbytes\tsha256\n" + "".join(f"{a}\t{b}\t{c}\n" for a, b, c in rows))

    if ZIP.exists():
        ZIP.unlink()
    with zipfile.ZipFile(ZIP, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for rel, _, _ in rows:
            zi = zipfile.ZipInfo("review_archive/" + rel, date_time=(2026, 1, 1, 0, 0, 0))
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = ((0o755 if (STAGE / rel).stat().st_mode & 0o111 else 0o644) << 16)
            z.writestr(zi, (STAGE / rel).read_bytes())
    total = sum(r[1] for r in rows)
    print(f"{len(rows)} files, {total / 1e6:.1f} MB unpacked, zip {ZIP.stat().st_size / 1e6:.1f} MB -> {ZIP.name}")
    print(f"{len(changed)} files anonymised:", ", ".join(r for r, _ in changed))


if __name__ == "__main__":
    main()
