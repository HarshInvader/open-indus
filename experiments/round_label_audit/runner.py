"""Re-execute another experiment's script with OLD or NEW (corrected) round-seal labels, read-only.

    .venv/bin/python -I experiments/round_label_audit/runner.py old|new experiments/context/q4_gulf.py [args...]

NEW: SEAL:R is no longer 'round' (source tuple ("SEAL:R", "SEAL:C", "SEAL:CY") -> ("SEAL:C", "SEAL:CY"),
glib.icit_register: SEAL:R -> 'seal'). Every file opened for writing is redirected to
experiments/round_label_audit/out_<variant>/<script-stem>__<basename>, so no other folder is touched.
"""
import builtins, io, os, sys, runpy, types
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ME = Path(__file__).resolve().parent
variant, script = sys.argv[1], (ROOT / sys.argv[2]).resolve()
assert variant in ("old", "new")
OUTD = ME / f"out_{variant}"; OUTD.mkdir(exist_ok=True)
_open = builtins.open


def guarded(file, mode="r", *a, **k):
    if isinstance(file, (str, os.PathLike)) and any(c in mode for c in "wax+"):
        p = Path(file).resolve()
        if ME not in p.parents:
            file = OUTD / f"{script.stem}__{p.name}"
    return _open(file, mode, *a, **k)


builtins.open = guarded; io.open = guarded
sys.path[:0] = [str(script.parent), str(ROOT), str(ROOT / "experiments/grammar")]
sys.argv = [str(script)] + sys.argv[3:]

if variant == "new":
    import glib
    old_reg = glib.icit_register

    def icit_register(tp):
        if tp == "SEAL:R":
            return "seal"
        return old_reg(tp)
    glib.icit_register = icit_register

src = _open(script).read()
if variant == "new":
    n = src.count('"SEAL:R", "SEAL:C", "SEAL:CY"')
    src = src.replace('"SEAL:R", "SEAL:C", "SEAL:CY"', '"SEAL:C", "SEAL:CY"')
    print(f"[runner] replaced {n} round tuples in {script.name}", flush=True)
# modules imported by the script that carry their own tuple (q4b imports q4_gulf constants only) are fine.
code = compile(src, str(script), "exec")
g = {"__name__": "__main__", "__file__": str(script)}
exec(code, g)
