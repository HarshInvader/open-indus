"""Copy selected Dholavira catalogue crops into raw/gujarat and emit manifest rows (JSON lines).
Usage: python -I guj_dholavira_select.py seals_dir sealings_dir outdir rows.jsonl
Selections are my visual judgements: sl -> (n_signs_visible, legibility)."""
import json
import os
import re
import shutil
import sys

SEALS = {
    1: (3, "good"), 2: (4, "poor"), 4: (5, "good"), 5: (6, "fair"), 6: (4, "fair"), 8: (4, "poor"),
    9: (3, "poor"), 10: (5, "fair"), 11: (3, "fair"), 12: (4, "good"), 15: (7, "fair"), 21: (5, "poor"),
    25: (1, "poor"), 27: (3, "fair"), 28: (2, "fair"), 30: (5, "good"), 31: (3, "poor"), 32: (6, "good"),
    33: (5, "good"), 35: (3, "poor"), 36: (5, "good"), 37: (3, "poor"), 41: (3, "poor"),
    43: (5, "good"), 45: (5, "fair"), 46: (3, "poor"), 47: (3, "poor"), 50: (2, "poor"), 53: (3, "fair"),
    57: (3, "poor"), 58: (3, "fair"), 59: (3, "poor"), 60: (2, "fair"), 61: (6, "fair"), 62: (5, "good"),
    64: (2, "poor"), 65: (3, "good"), 67: (5, "good"), 68: (5, "fair"), 69: (5, "good"), 70: (1, "poor"),
    71: (5, "good"), 73: (5, "fair"), 81: (2, "good"), 82: (3, "fair"), 83: (3, "poor"), 84: (3, "poor"),
    85: (3, "poor"), 86: (4, "fair"), 87: (5, "fair"), 88: (6, "good"), 89: (2, "fair"), 91: (6, "good"),
    92: (7, "good"), 94: (4, "good"), 95: (4, "fair"), 96: (2, "poor"), 97: (3, "fair"), 98: (3, "fair"),
    99: (3, "fair"), 100: (3, "fair"), 102: (5, "fair"), 103: (3, "fair"), 106: (6, "good"),
    107: (4, "good"), 108: (3, "poor"), 109: (8, "good"), 112: (1, "fair"), 113: (2, "poor"),
    114: (2, "fair"), 118: (2, "fair"), 120: (3, "good"), 121: (7, "good"), 122: (7, "fair"),
    125: (5, "good"), 127: (4, "good"), 128: (3, "fair"), 130: (5, "good"), 133: (6, "fair"),
    134: (5, "fair"), 135: (2, "poor"), 136: (1, "poor"), 138: (3, "good"), 139: (6, "fair"),
    140: (4, "good"), 142: (3, "fair"), 143: (6, "fair"), 144: (2, "fair"), 145: (4, "good"),
    146: (8, "good"), 147: (3, "fair"), 148: (4, "fair"), 149: (4, "good"), 150: (4, "good"),
    153: (3, "poor"), 155: (1, "poor"), 156: (2, "poor"), 157: (4, "fair"), 158: (4, "poor"),
    159: (4, "good"), 160: (2, "poor"), 161: (3, "poor"), 162: (3, "poor"), 164: (3, "poor"),
    165: (4, "poor"), 167: (3, "poor"), 170: (3, "fair"), 174: (2, "poor"), 175: (3, "fair"),
    176: (3, "poor"), 177: (2, "poor"), 178: (2, "fair"), 179: (2, "fair"), 180: (3, "poor"),
    182: (2, "poor"), 183: (2, "fair"), 186: (3, "poor"), 187: (2, "poor"), 189: (4, "good"),
    190: (2, "poor"), 193: (2, "poor"), 194: (4, "fair"), 196: (4, "good"), 206: (5, "good"),
    208: (2, "fair"), 217: (4, "fair"), 219: (6, "good"), 220: (3, "poor"), 221: (5, "good"),
}
SEALINGS = {
    2: (3, "poor"), 6: (3, "fair"), 7: (3, "fair"), 19: (2, "fair"), 21: (2, "fair"), 24: (2, "poor"),
    35: (2, "poor"), 36: (3, "poor"), 39: (3, "poor"), 45: (2, "poor"), 48: (2, "fair"), 55: (2, "poor"),
    56: (2, "poor"),
}
CIT = ("Bisht, R.S. 2015. Excavations at Dholavira (1989-90 to 2004-2005). New Delhi: Archaeological "
       "Survey of India (report dated Jan/Apr 2015), section 8.2.3 'Details of individual seals' pp.260-306 / "
       "8.2.4 'Sealings' pp.308-329 (printed page numbers)")
URL = "https://archive.org/details/dholavirareportpreliminaryjan2015_860_K"

seals_dir, sealings_dir, out, rows_path = sys.argv[1:5]
rows = []
for d, sel, kind, pre in [(seals_dir, SEALS, "seal", "dhs"), (sealings_dir, SEALINGS, "sealing", "dhsl")]:
    idx = {r["sl"]: r for r in json.load(open(os.path.join(d, f"{pre}_index.json")))}
    for sl, (n, leg) in sel.items():
        r = idx[sl]
        src = os.path.join(d, r["files"][0])
        fn = f"dholavira_{'sealing_' if kind == 'sealing' else ''}acc{r['acc']}.png"
        shutil.copy(src, os.path.join(out, fn))
        text = re.sub(r"^\d+\s+", "", r["text"]).strip()
        low = text.lower()
        field = "none"
        for k in ["unicorn", "bos taurus", "buffalo", "elephant", "rhinoceros", "scorpion", "tiger",
                  "crocodile", "goat", "bull", "3 headed", "animal"]:
            if k in low:
                field = k + ("?" if "?" in low or "probabl" in low or "possibl" in low else "")
                break
        note = ("seal face (photo of seal; signs mirror-reversed)" if kind == "seal"
                else "sealing (impression; reads in normal direction); report photo shows obverse + reverse")
        if "nat" in low and "mus" in low:
            note += "; report marks object 'In Nat. Mus.' (National Museum New Delhi) - may already be published elsewhere"
        if sl == 94 and kind == "seal":
            note += "; photo in report appears identical to Sl.107 acc22100 - possible duplicate photo"
        if sl == 107 and kind == "seal":
            note += "; photo in report appears identical to Sl.94 acc21100 - possible duplicate photo"
        note += f"; report Sl.No.{sl} p.{r['page']} (pdf); remarks: {text[:300]}"
        rows.append({"file": fn, "site": "Dholavira", "object_id_in_source": f"Acc. No. {r['acc']} (Sl. {sl})",
                     "object_type": kind, "field_symbol": field, "publication_year": "2015",
                     "citation": CIT, "source_url": URL, "n_signs_visible": n, "legibility": leg,
                     "published_transcription": "", "notes": note})
with open(rows_path, "w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
print(len(rows), "rows")
