"""Sign-list mapping for r_symmetry (prereg docs/prereg/r_symmetry.md, "Variants" and "Fixed before running").

Built on signlist_robustness/harness.Variant and its W2M_ALL (bridge_WM.json). Nothing here computes a statistic.

    w_to_label(V, w)      ICIT-native rows: W -> first M partner -> V.tok(); a W sign with no M partner keeps its label.
    w_to_labels_all(V, w) rows whose native code uses self_label/s2_test.icit_set(): W -> all M partners -> V.tok() each.
    m_to_label(V, m)      M77-native rows: V.tok(m).
    set_check(V, cats)    "Sign sets under a variant": every label holding a sign of a category must hold only signs of
                          that category (else the cell is NT; this also covers a contrast falling inside one label).
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "signlist_robustness"))
import harness  # noqa: E402  (Variant, W2M_ALL; harness has no import-time side effects beyond loading JSON)

Variant = harness.Variant
W2M_ALL = harness.W2M_ALL

# The 12 lists of variants.json: 9 partitions (M77 identity, parpola, 4 lumps, 3 image cuts) + 3 random splits.
# ("The 7 lists that keep M343-M345 apart from M342" = these 12 minus lump_jar_man, lump_all, img_hi/mid/lo.)
# harness.ALL also holds "ICIT", which is an edition, not a list; it is not a cell here.
LISTS = list(harness.VJ["partitions"]) + list(harness.VJ["splits"])
assert len(LISTS) == 12, LISTS
OTHER = "other_edition"
CELLS = LISTS + [OTHER]

# prereg "Families": the 3 splits are one family, the 3 image cuts another; each lump, parpola and the other edition
# are one family each. The M77 list is not named as a family in the sealed text. For M77-native rows it is the
# identity (INVARIANT); for ICIT-native rows it is a real variant (W -> first M partner). It is reported per cell but
# not counted as a family (FAMILY value None) -- flagged for review before sealing the code.
FAMILY = {"M77": None, "parpola": "parpola", "lump_fish": "lump_fish", "lump_numerals": "lump_numerals",
          "lump_jar_man": "lump_jar_man", "lump_all": "lump_all",
          "split_s1": "splits", "split_s2": "splits", "split_s3": "splits",
          "img_hi": "img", "img_mid": "img", "img_lo": "img", OTHER: OTHER}
MULTI_FAMILIES = ("splits", "img")

# frozen sign sets (M space). fr.TALL values: M86 1, M87 2, M88/M89/M92/M93/M94 3, M95 4, M96 5.
TALL_M = {"M86": 1, "M87": 2, "M88": 3, "M89": 3, "M92": 3, "M93": 3, "M94": 3, "M95": 4, "M96": 5}
TIER_M = {2: {"M87"}, 3: {"M88", "M89", "M92", "M93", "M94"}, 4: {"M95"}}   # prereg M77 tier rule (tier 3 = fr.TALL tall-three)
CUP_M = {"M328"}
SJ_M = {"M343", "M344", "M345"}


def get(name):
    """Variant object, or None for the other edition."""
    return None if name == OTHER else Variant(name)


def m_to_label(V, m):
    return V.tok(m)


def w_to_label(V, w):
    if w in ("|", "#"):
        return w
    if V.icit:
        return w
    ms = W2M_ALL.get(w)
    if not ms:
        return w                       # no M partner: keeps its own label (11% of tokens)
    return V.tok(ms[0])


def w_to_labels_all(V, w):
    """s2_test.icit_set rule (all M partners), then tok() each; a W sign with no partner keeps its label."""
    if V.icit:
        return {w}
    return {V.tok(m) for m in W2M_ALL[w]} if w in W2M_ALL else {w}


class AnyOf(frozenset):
    """A set of labels that compares equal to any member, so q1_animal.featurize's `ss[-1] == jar` test (reused
    unchanged) treats every allograph of the jar as the jar under the split lists. Used only when the jar has > 1 label."""
    def __eq__(self, other):
        if isinstance(other, str):
            return other in self
        return frozenset.__eq__(self, other)
    __hash__ = frozenset.__hash__


def labels_value(V, mvals):
    """{M sign: value} -> {label: value} under V (labels of a clean set carry their members' value)."""
    return {lab: v for m, v in mvals.items() for lab in V.labels_of([m])}


def set_check(V, cats):
    """cats: {category: set of M signs}. Returns None if clean, else an NT reason string.
    For each category, V.labels_of(set) must hold only signs of that category. Categories are disjoint, so two
    categories sharing a label (e.g. tier 2 with tier 3: the contrast inside one label) also fail here."""
    if V.icit:
        return None
    for name, S in cats.items():
        for lab in sorted(V.labels_of(S)):
            mem = V.members(lab)
            out = sorted(mem - set(S))
            if out:
                return f"label {lab} holds {name} sign(s) {sorted(mem & set(S))} and outside sign(s) {out[:4]}"
    return None


def canon(obj):
    """Relabel-invariant canonical form: label strings are renamed in order of first appearance in a deterministic
    traversal. Two inputs are identical up to a bijective renaming iff their canon() are equal. Non-label strings
    must be passed wrapped as ('#lit', s)."""
    names = {}

    def walk(x):
        if isinstance(x, tuple) and len(x) == 2 and x[0] == "#lit":
            return ("#lit", x[1])
        if isinstance(x, str):
            if x not in names:
                names[x] = f"L{len(names)}"
            return names[x]
        if isinstance(x, (list, tuple)):
            return tuple(walk(y) for y in x)
        if isinstance(x, (set, frozenset)):
            raise TypeError("pass sets as sorted tuples in a deterministic order")
        return x
    return walk(obj)
