"""Data for core_semantics: Indus name cores with context, and reference name corpora.

Indus cores follow the frozen typology definition (experiments/typology/corpora.py, functional-reading parse):
maximal runs of N/F tokens outside opener/closer/title/numeral/register constituents, not crossing line breaks
or '#'.  Here each core occurrence also keeps its left and right context sign (or '^'/'$') and whether it
is adjacent to a numeral (number-name), so 'standalone' can exclude number+X compounds.

Reference corpora (two-element personal names; unit = distinct name type):
  sanskrit  Monier-Williams 2020 XML (Cologne), compounds glossed 'N. of a man / king / Brahman ...', key2
            segmentation with exactly two members.  Known head-final (Deva-datta, Agni-sarman).
  ur3       CDLI Ur III seal-legend personal names (codelib/ur3_legends), name slot (first word or after
            dumu/dam), split into elements at hyphens with {d}DN kept whole.  Known head-initial (ur-DN,
            lu2-DN, lugal-X).  Syllabic noise (a-kal etc.) is left in on purpose.
  chinese   Chinese two-character given names (typology/data).  No agreed head direction (control).
Run from repo root.
"""
import json, re, sys
from pathlib import Path
from collections import Counter, defaultdict
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "typology"))
from corpus.load import dev_heldout  # noqa
import corpora as TY  # noqa  (typology core definition, read-only reuse)

FR = ROOT / "experiments" / "functional_reading"
NUMROLES = ("S", "T")
FISH = ["M59", "M65", "M67", "M70", "M72", "M75", "M62", "M61", "M63", "M74", "M64", "M69",
        "M60", "M66", "M68", "M71", "M73"]  # plain + bracketed fish family (lexicon fish-class)


def indus_occurrences(split="dev"):
    """List of dicts per core occurrence in distinct texts of the split:
    core (tuple), left, right (context signs, '^' '$' '|' for edges), left_role, right_role, num_adj (bool),
    text (tuple seq), object_type, site."""
    d = pd.read_csv(FR / "readings.csv")
    d = d.drop_duplicates("signs")
    by = {tuple(r.signs.split()): r for _, r in d.iterrows() if isinstance(r.parse_roles, str)}
    dev, ho = dev_heldout(version=2)
    texts = {"dev": dev, "heldout": ho, "all": dev + ho}[split]
    out = []
    for t in texts:
        key = tuple(t["seq"])
        if key not in by:
            continue
        r = by[key]
        signs = list(key)
        toks = [x for x in r.parse_roles.split() if "/" in x]
        roles = [x.split("/")[1] for x in toks]
        labs = []
        for lab, sg in TY._constituents(r.reading):
            labs += [lab] * len(sg)
        if len(labs) != len(toks):
            labs = ["?"] * len(toks)
        # token stream with role, keep separators
        stream = []
        k = 0
        for s in signs:
            if s in ("|", "#"):
                stream.append((s, s, s, False))
                continue
            ok = roles[k] in ("N", "F") and labs[k] not in TY.STRIP_CONST
            if ok and s in TY.LEX.index:
                prim = str(TY.LEX.loc[s, "roles"]).split(";")[0].rsplit(" ", 1)[0]
                if prim not in ("NOUN", "FISH-CLASS NOUN"):
                    ok = False
                if str(TY.LEX.loc[s, "meaning_category"]).startswith(TY.NONNAME_MEANING):
                    ok = False
            stream.append((s, roles[k], labs[k], ok))
            k += 1
        i, n = 0, len(stream)
        while i < n:
            if not stream[i][3]:
                i += 1
                continue
            j = i
            while j < n and stream[j][3]:
                j += 1
            lft = stream[i - 1] if i > 0 else ("^", "^", "^", False)
            rgt = stream[j] if j < n else ("$", "$", "$", False)
            if lft[0] != "#" and rgt[0] != "#":
                out.append(dict(core=tuple(x[0] for x in stream[i:j]), left=lft[0], right=rgt[0],
                                left_role=lft[1], right_role=rgt[1],
                                num_adj=(lft[1] in NUMROLES) or (rgt[1] in NUMROLES),
                                text=key, object_type=t.get("object_type", r.object_type), site=r.site))
            i = j
    return out


def indus_types(split="dev"):
    """core type -> number of distinct texts; plus standalone counts per sign (1-sign cores not next to a numeral)."""
    occ = indus_occurrences(split)
    inc = Counter()
    seen = set()
    for o in occ:
        k = (o["text"], o["core"])
        if k in seen:
            continue
        seen.add(k)
        inc[o["core"]] += 1
    return dict(inc), occ


# ---------------------------------------------------------------- Sanskrit (Monier-Williams)
MW = HERE / "data" / "mw" / "xml" / "mw.xml"
_PERS = re.compile(r"<ab>N\.</ab> of (a man|men|various men|a Brāhman|a king|a prince|a Ṛishi|a ṛishi|"
                   r"a teacher|a poet|an author|a Muni|a minister|a merchant|a son of|a pupil)")
_ENT = re.compile(r"<(H\d[A-Z]?)><h><key1>([^<]*)</key1><key2>(.*?)</key2>.*?<body>(.*?)</body>")


def _mw_members(k2):
    k = re.sub(r"<[^>]+>", "", k2)
    k = re.sub(r"[/\^\\'~]", "", k)
    return [re.sub("[^A-Za-z]", "", p) for p in k.split("—") if re.sub("[^A-Za-z]", "", p)]


def sanskrit_names():
    """-> (two-member name types {(a,b):1}, single-member name set)."""
    two, single = Counter(), set()
    for line in open(MW, encoding="utf-8"):
        m = _ENT.search(line)
        if not m or not _PERS.search(m.group(4)[:200]):
            continue
        mem = _mw_members(m.group(3))
        if len(mem) == 2:
            two[tuple(mem)] = 1
        elif len(mem) == 1:
            single.add(mem[0])
    return dict(two), single


SKT_DEITY = set("""deva indra agni soma vizRu viSRu Siva rudra brahma brahman sUrya varuRa yama kfzRa rAma
hari hara skanda kumAra nArAyaRa vAsudeva lakzmI durgA gOrI gaurI Bava SaMkara Sankara ISvara mahADeva maheSvara
ravi candra Banu BAnu Aditya vasu prajApati bfhaspati guha kAma gaReSa gaRapati vinAyaka bala balaBadra
kArttikeya umA pArvatI caRqI kAlI sarasvatI SrI vAyu marut pUzan tvazwf aSvin gaRga gaNgA nanda
kubera varAha nfsiMha mAdhava keSava govinda janArdana dAmodara trivikrama vAmana Sakra mahendra surendra
sura tri""".split()) - {"tri", "sura", "bala"}


# ---------------------------------------------------------------- Ur III personal names
UR = ROOT / "sources" / "paragorth_Indus-" / "data" / "codelib" / "ur3_legends.jsonl"


def ur3_elements(w):
    w = w.strip("_").replace("#", "").replace("!", "").replace("?", "")
    if "x" in w.split("-") or not w:
        return None
    m = re.match(r"^(.*?)-?(\{d\}.*)$", w)
    if m and m.group(1):
        return tuple(m.group(1).split("-") + [m.group(2)])
    if m:
        return (m.group(2),)
    return tuple(w.split("-"))


def ur3_names():
    """-> (two-element name types, single-element name set). Name slot as in typology/corpora.ur3_names."""
    two, single = Counter(), set()
    for l in open(UR):
        seq = [w.strip("_") for w in json.loads(l)["seq"]]
        for i, w in enumerate(seq):
            if not (i == 0 or seq[i - 1] in ("dumu", "dam", "dumu-munus")):
                continue
            if w in TY.UR_TITLES or "{ki}" in w:
                continue
            el = ur3_elements(w)
            if not el:
                continue
            if len(el) == 2:
                two[el] = 1
            elif len(el) == 1:
                single.add(el[0])
    return dict(two), single


def is_deity_ur(e):
    return e.startswith("{d}")


# ---------------------------------------------------------------- Chinese given names
def chinese_given():
    d = TY.chinese_names(given_only=True)
    two = {c: 1 for c in d if len(c) == 2}
    single = {c[0] for c in d if len(c) == 1}
    return two, single


if __name__ == "__main__":
    for sp in ("dev", "heldout"):
        inc, occ = indus_types(sp)
        L = Counter(len(c) for c in inc)
        print(sp, "core types", len(inc), dict(sorted(L.items())), "occurrences", len(occ),
              "num-adjacent 1-sign", sum(1 for o in occ if len(o["core"]) == 1 and o["num_adj"]))
    s2, s1 = sanskrit_names(); print("sanskrit 2-member", len(s2), "single", len(s1))
    u2, u1 = ur3_names(); print("ur3 2-element", len(u2), "single", len(u1), list(u2)[:10])
    c2, c1 = chinese_given(); print("chinese given 2-char", len(c2), "single", len(c1))
