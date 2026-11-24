"""meaning_calibration v2 (prereg docs/prereg/meaning_calibration_v2.md): resolution gate, pair planting, verdict2.
fcore (v1) is imported unchanged."""
import math
import fcore as F

SEED0 = 20261125
MIN_NULL_DEV, MIN_NULL_HELD = 99, 19


def verdict2(dev, held, head, main, sq, power_by_bin):
    """S / R / U / U-resolution for one claim on one draw."""
    if not (dev.n(head) >= F.MIN_DEV and held.n(head) >= F.MIN_HELD): return "U", None
    rd = F.f_test(dev, head, main, sq); rh = F.f_test(held, head, main, sq)
    if rd is None or rh is None or rd["n_null"] < MIN_NULL_DEV or rh["n_null"] < MIN_NULL_HELD: return "U-resolution", (rd, rh)
    if rd["obs"] >= F.SHARE and rd["p"] <= 0.01 and rh["p"] <= 0.05: return "S", (rd, rh)
    if rd["obs"] <= rd["median"] and power_by_bin.get(F.bin_of(rd["n"]), 0) >= 0.8: return "R", (rd, rh)
    return "U", (rd, rh)


def plant_set(texts, head, P, rng):
    """Set ceil(0.4 n) of head's next-positions to members of P = [main, *sq] (existing P tokens count towards it):
    half (rounded up) of the needed total to main, the rest at random over sq. Returns (texts, ok)."""
    Ps = set(P)
    pos, n, have = [], 0, 0
    for ti, t in enumerate(texts):
        for i, s in enumerate(t):
            if s != head: continue
            if i == len(t) - 1: n += 1; continue
            r = t[i + 1]
            if r == "#": continue
            n += 1
            if r in Ps: have += 1
            else: pos.append((ti, i + 1))
    need = math.ceil(F.SHARE * n) - have
    if need <= 0: return texts, True
    if need > len(pos): return texts, False
    out = [list(t) for t in texts]
    chosen = rng.sample(range(len(pos)), need)
    n_main = math.ceil(need / 2) if len(P) > 1 else need
    for j, c in enumerate(chosen):
        ti, i = pos[c]
        out[ti][i] = P[0] if j < n_main else rng.choice(P[1:])
    return out, True
