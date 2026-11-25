"""Build the primary lexicon of certify_size_curve from the SAAo open-data archive.

Label-free: reads one glossary, writes consonant skeletons. No text is read and nothing is scored.

Usage:  python3 -I build_lexicon.py PATH_TO/saao.zip

The archive (66 MB) is not kept in the repo. Its SHA-256 is checked before anything is read.
Output: raw/saao/neoass_skeletons.tsv beside this script (UTF-8, LF line ends, sorted).
Rule (docs/prereg/certify_size_curve.md, "Lexicon"): the skeleton of every normalised form (`norms`) of every
headword of the Neo-Assyrian glossary; name classes and numerals left out; long vowels shortened; voiced,
voiceless and emphatic stops merged to 11 letters; y, j and the glottal stop dropped; a doubled consonant
written once.
"""
import hashlib
import json
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

ZIP_SHA256 = "29bcf61b55ef291a97180f836ca620e13a1bcab802dad7ff64e2baf2e9d7a17f"
MEMBER = "saao/gloss-akk-x-neoass.json"
OUT = Path(__file__).resolve().parent / "raw" / "saao" / "neoass_skeletons.tsv"

VOWELS = set("aeiu")
MERGE = {"b": "P", "p": "P", "d": "T", "t": "T", "ṭ": "T", "g": "K", "k": "K", "q": "K",
         "s": "S", "ṣ": "S", "z": "S", "š": "Š", "m": "M", "n": "N", "l": "L", "r": "R",
         "h": "H", "ḫ": "H", "w": "W"}
DROP = set("yj'ʾʿ-")
LONG = str.maketrans("āēīūâêîûáéíúàèìù", "aeiuaeiuaeiuaeiu")
DIGITS = set("0123456789₀₁₂₃₄₅₆₇₈₉ₓ")
NAME_POS = {"PN", "DN", "GN", "RN", "TN", "WN", "SN", "ON", "MN", "EN", "CN", "LN", "QN", "AN", "FN", "YN", "NU"}
EXPECT_SKELETONS = 3632
EXPECT_BY_LENGTH = {4: 1612, 5: 896, 6: 259, 7: 48}


def skeleton(form):
    """Consonant skeleton of one normalised form, or None if it holds a letter outside the alphabet."""
    out, prev = [], None
    for ch in form.lower().translate(LONG):
        if ch in DIGITS:
            continue
        if ch in VOWELS:
            prev = None
            continue
        if ch in DROP:
            continue
        if ch not in MERGE:
            return None
        letter = MERGE[ch]
        if letter == prev:          # doubled consonant with no vowel between: written once
            continue
        out.append(letter)
        prev = letter
    return "".join(out)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    zpath = Path(sys.argv[1])
    h = hashlib.sha256()
    with open(zpath, "rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    if h.hexdigest() != ZIP_SHA256:
        sys.exit("saao.zip SHA-256 mismatch: got %s" % h.hexdigest())
    with zipfile.ZipFile(zpath) as z:
        entries = json.loads(z.read(MEMBER))["entries"]
    forms, heads = defaultdict(set), defaultdict(set)
    kept = 0
    for i, e in enumerate(entries):
        if e.get("pos") in NAME_POS:
            continue
        kept += 1
        for no in e.get("norms", []):
            sk = skeleton(no.get("n", ""))
            if sk:
                forms[sk].add(no.get("n", ""))
                heads[sk].add(i)
    by_len = defaultdict(int)
    for sk in forms:
        by_len[len(sk)] += 1
    if len(forms) != EXPECT_SKELETONS or any(by_len[k] != v for k, v in EXPECT_BY_LENGTH.items()):
        sys.exit("skeleton counts differ from the prereg: %d, %s" % (len(forms), dict(sorted(by_len.items()))))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = ["skeleton\tconsonants\tnormalised_forms\theadwords"]
    for sk in sorted(forms):
        rows.append("%s\t%d\t%d\t%d" % (sk, len(sk), len(forms[sk]), len(heads[sk])))
    data = ("\n".join(rows) + "\n").encode("utf-8")
    OUT.write_bytes(data)
    print("entries %d, entries kept %d, skeletons %d, of 4 to 7 consonants %d"
          % (len(entries), kept, len(forms), sum(EXPECT_BY_LENGTH.values())))
    print("wrote raw/saao/%s, %d bytes, SHA-256 %s" % (OUT.name, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
