"""Post hoc (not pre-registered): chance rate of the A2 'probable same object' match, by shifting new-set areas."""
import sys, numpy as np
sys.argv.append("--noop")
sys.path.insert(0, "experiments/reg_size")
import rs_lib as L
from corpus.build import _close
T4 = L.t4_objects(); new, _ = L.build_new_set(set(L.PRIMARY_SOURCES), t4=T4)
t4 = [(r["site"], r["log_area"], list(L.canon_seq(r["signs"]))) for r in T4[0]]
def count(shift, tol=0.03):
    n = 0; exact = 0
    for r in new:
        c = list(L.canon_seq(r["signs"]))
        for s, a, tc in t4:
            if s == r["site"] and abs(a - r["log_area"] - shift) < tol and (tc == c or _close(tc, c)):
                n += 1; exact += tc == c; break
    return n, exact
for sh in [0, 0.1, -0.1, 0.2, -0.2, 0.3]:
    print(f"shift {sh:+.1f}: matches (any, exact-canon) = {count(sh)}")
print("\nexamples (new M77 text | T4 ICIT text | new icit_ids | T4 n_obj):")
k = 0; noid = 0; tot = 0
for r in new:
    c = list(L.canon_seq(r["signs"]))
    for t in T4[0]:
        tc = list(L.canon_seq(t["signs"]))
        if t["site"] == r["site"] and abs(t["log_area"] - r["log_area"]) < 0.03 and _close(tc, c):
            tot += 1; noid += not r["icit_ids"]
            if k < 8:
                print(" ", " ".join(r["signs"]), "|", " ".join(t["signs"]), "|", r["icit_ids"], "|", t["n_obj"]); k += 1
            break
print(f"matched new texts with no ICIT link: {noid}/{tot}")
