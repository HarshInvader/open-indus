"""Scott (Dunn) key values -> sets of consonant-class skeletons (prereg docs/prereg/scott_ic_refute.md).
Reads .local/scott_lis/key.csv and overrides.csv at run time. Never writes sign-level values anywhere.

Classes (SLP1 after yj_common.iast_to_slp): k kh g gh C j jh T th dh N p ph B bh m y R S h.
"""
import csv, re, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / "experiments/language"))
from yj_common import iast_to_slp  # noqa: E402

LOCAL = ROOT / ".local/scott_lis"
CLS = {"k": "k", "K": "kh", "g": "g", "G": "gh", "c": "C", "C": "C", "j": "j", "J": "jh",
       "t": "T", "d": "T", "w": "T", "q": "T", "T": "th", "W": "th", "D": "dh", "Q": "dh",
       "n": "N", "R": "N", "Y": "N", "N": "N", "p": "p", "P": "ph", "b": "B", "v": "B", "B": "bh",
       "m": "m", "y": "y", "r": "R", "l": "R", "f": "R", "F": "R", "x": "R",
       "S": "S", "z": "S", "s": "S", "h": "h", "H": "h"}
VOW = set("aAiIuUeEoO")
NONSKT = set("fqxzw")          # letters that do not occur in plain/IAST Sanskrit spelling of the key
MAXALT = 4


def skel_slp(slp, anusvara="N"):
    out = []
    for ch in slp:
        if ch in VOW: continue
        if ch == "M": out.append(anusvara); continue
        if ch in CLS: out.append(CLS[ch]); continue
        return None
    return tuple(out)


def key_skel(alt):
    a = alt.lower().replace("sh", "ś")
    return skel_slp(iast_to_slp(a))


def _alts(v):
    v = re.sub(r"\([^)]*\)", " ", v)
    v = re.split(r"[–;]", v)[0]
    v = v.replace("?", "")
    out = [""]
    # brackets: single-letter alternatives -> one alternative per letter; otherwise dropped (understood part)
    parts = re.split(r"(\[[^\]]*\])", v)
    for p in parts:
        if p.startswith("["):
            inner = p[1:-1]
            if re.fullmatch(r"\w(/\w)+", inner):
                out = [o + "\x00" + l for o in out for l in inner.split("/")]
            continue
        out = [o + p for o in out]
    alts = []
    for o in out:
        for a in re.split(r"/|,| or ", o):
            a = a.replace("\x00", "")
            if "…" in a: continue
            a = a.replace("-", "").strip()
            a = re.sub(r"\s+", "", a)
            if a == "" and not o.strip(): continue
            alts.append(a)
    return [a for a in alts if a != "" or len(alts) == 1]


def flag(raw_alt):
    return bool(set(raw_alt.lower()) & NONSKT) or any(c in raw_alt for c in '".+“”') or len(raw_alt.split()) >= 3


def load(blank_uncertain=False, blank_overrides=False):
    """Returns (key: sign -> list of skeleton tuples | None for blank, report dict with aggregates only)."""
    rows = list(csv.DictReader(open(LOCAL / "key.csv", encoding="utf-8")))
    ov = {}
    if (LOCAL / "overrides.csv").exists():
        for r in csv.DictReader(open(LOCAL / "overrides.csv", encoding="utf-8")):
            ov[r["M"]] = r["value"]
    key, flagged, nalt = {}, [], {}
    for r in rows:
        m = r["M"]
        if r["status"] == "blank" or (blank_uncertain and r["status"] == "uncertain"):
            key[m] = None; continue
        if m in ov:
            if blank_overrides: key[m] = None; continue
            v = ov[m]
            if v == "":
                key[m] = None; continue
            assert all(t.lower() in r["value"].lower() for t in re.split(r"[/ ]", v) if t), f"override {m} not printed text"
        else:
            v = r["value"]
        raw = re.sub(r"\([^)]*\)", " ", v); raw = re.split(r"[–;]", raw)[0]
        if m not in ov and any(flag(a) for a in re.split(r"/|,| or ", raw)):
            flagged.append(m); continue
        alts = _alts(v)
        sk = []
        for a in alts:
            s = key_skel(a)
            if s is None:
                if m not in ov: flagged.append(m)
                break
            if s not in sk: sk.append(s)
        else:
            if len(sk) > MAXALT and m not in ov:
                flagged.append(m); continue
            key[m] = sk if sk else None
    return key, dict(flagged=sorted(set(flagged), key=lambda x: int(x[1:])), n_override=len(ov))


if __name__ == "__main__":
    # local diagnostic: prints flagged entries (terminal only; never redirect into the repo)
    key, rep = load()
    rows = {r["M"]: r["value"] for r in csv.DictReader(open(LOCAL / "key.csv", encoding="utf-8"))}
    print("flagged", len(rep["flagged"]))
    for m in rep["flagged"]: print(m, "|", rows[m][:160])
