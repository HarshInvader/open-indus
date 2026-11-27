"""Check docs/prereg/HASHES.txt against the files in the repository.

    python3 scripts/check_prereg_hashes.py                 # report; exit 1 on a new problem
    python3 scripts/check_prereg_hashes.py --base REF      # also: HASHES.txt only grew since REF
    python3 scripts/check_prereg_hashes.py --write-known   # rewrite the known-issues list (maintainers)

Standard library only, so it runs before any install. Read-only except with --write-known.

Each line of HASHES.txt is `<sha256>  <path>  <anything>`. A file may have several lines: the last one
is the current seal, earlier ones are superseded by amendments. For every sealed file the status is:

  ok          the file matches its last line
  amended     a prereg .md whose text before the first "## Amendment" heading still matches the seal:
              the original registration is intact, the appended amendment has no hash (warning)
  unpublished the file is not in the repository and .gitignore excludes it on purpose (warning)
  earlier     the file matches an earlier line, not the last one (problem)
  mismatch    the file matches no line (problem)
  missing     the file is not in the repository and is not ignored (problem)

Problems listed in docs/prereg/HASHES_KNOWN_ISSUES.txt were present when this check was added. They are
reported but do not fail the check, so that CI fails only on a NEW broken seal. Remove a line from that
file when its seal is repaired.

--base REF fails if any line of HASHES.txt that exists at REF was removed or changed (CONTRIBUTING.md:
sealed lines are appended, never edited).
"""
import argparse, hashlib, re, subprocess, sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HASHES = ROOT / "docs" / "prereg" / "HASHES.txt"
KNOWN = ROOT / "docs" / "prereg" / "HASHES_KNOWN_ISSUES.txt"
LINE = re.compile(r"^([0-9a-f]{64})\s+(\S+)")
PROBLEMS = ("earlier", "mismatch", "missing")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def sealed():
    """path -> list of hashes, in file order."""
    out = {}
    for l in HASHES.read_text(encoding="utf-8").splitlines():
        m = LINE.match(l)
        if m:
            out.setdefault(m.group(2), []).append(m.group(1))
    return out


def resolve(path):
    """A few early lines give a bare file name; those files live in docs/prereg/."""
    p = ROOT / path
    if not p.exists() and "/" not in path and (ROOT / "docs" / "prereg" / path).exists():
        p = ROOT / "docs" / "prereg" / path
    return p


def ignored(path):
    r = subprocess.run(["git", "-C", str(ROOT), "check-ignore", "-q", path])
    return r.returncode == 0


def status(path, hashes):
    p = resolve(path)
    if not p.is_file():
        return "unpublished" if ignored(path) else "missing"
    b = p.read_bytes(); h = sha(b)
    if h == hashes[-1]:
        return "ok"
    if p.suffix == ".md":
        head = re.split(rb"\n## Amendment", b, maxsplit=1)[0]
        if len(head) < len(b) and {sha(head), sha(head + b"\n"), sha(head.rstrip(b"\n") + b"\n")} & set(hashes):
            return "amended"
    return "earlier" if h in hashes else "mismatch"


def known():
    if not KNOWN.exists():
        return {}
    out = {}
    for l in KNOWN.read_text(encoding="utf-8").splitlines():
        if l.strip() and not l.startswith("#"):
            st, path = l.split()[:2]; out[path] = st
    return out


def append_only(base):
    r = subprocess.run(["git", "-C", str(ROOT), "show", f"{base}:docs/prereg/HASHES.txt"], capture_output=True)
    if r.returncode != 0:
        print(f"append-only: cannot read HASHES.txt at {base}; skipped"); return []
    now = Counter(HASHES.read_text(encoding="utf-8").splitlines())
    gone = Counter(r.stdout.decode("utf-8").splitlines()) - now
    return [l for l in gone if l.strip()]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--base", help="git ref; fail if HASHES.txt lost or changed a line since then")
    ap.add_argument("--write-known", action="store_true", help="rewrite the known-issues list from the current state")
    a = ap.parse_args()

    res = {path: status(path, hs) for path, hs in sealed().items()}
    n = Counter(res.values())
    print(f"{len(res)} sealed files: " + ", ".join(f"{n[k]} {k}" for k in
          ("ok", "amended", "unpublished", "earlier", "mismatch", "missing") if n[k]))

    if a.write_known:
        rows = [f"{st}  {p}" for p, st in res.items() if st in PROBLEMS]
        KNOWN.write_text("# Broken seals that existed when scripts/check_prereg_hashes.py was added. They are reported,\n"
                         "# but they do not fail the check. Remove a line when its seal is repaired; never add one to\n"
                         "# hide a new problem. Format: <status>  <path>\n" + "\n".join(rows) + "\n", encoding="utf-8")
        print(f"wrote {len(rows)} lines to {KNOWN.relative_to(ROOT)}"); return 0

    kn = known(); new = []
    for p, st in res.items():
        if st == "amended":
            print(f"  warn   amended     {p}")
        elif st in PROBLEMS:
            old = p in kn
            print(f"  {'known' if old else 'NEW  '}  {st:11s} {p}")
            if not old: new.append(p)
    for p in kn:
        if res.get(p, "ok") not in PROBLEMS:
            print(f"  note   {p} is in the known-issues list but is now {res.get(p, 'not sealed')}: remove the line")

    gone = append_only(a.base) if a.base else []
    for l in gone:
        print(f"  NEW    line removed or changed since {a.base}: {l[:100]}")

    if new or gone:
        print(f"FAIL: {len(new)} new broken seal(s), {len(gone)} sealed line(s) removed or changed")
        return 1
    print("PASS: no new broken seal")
    return 0


if __name__ == "__main__":
    sys.exit(main())
