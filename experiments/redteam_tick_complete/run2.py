"""Follow-up to run.py (written after seeing run.py output; exploratory checks of two weaknesses it showed).
(a) strict post-1977 site list for the ICIT replication (run.py's 'not in M77' list let in sites M77 files
    under 'Other sites' / 'West Asian finds'); (b) formula clustering: keep one ticked text per final bigram.
"""
import sys, json
from pathlib import Path
from collections import Counter
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(HERE.parents[1] / "corpus"))
import run as R, load as L  # noqa

POST1977 = {"Dholavira", "Nausharo", "Banawali", "Rakhigarhi", "Farmana", "Bhirrana", "Gola Dhoro (Bagasra)",
            "Karanpura", "Khirsara", "Kanmer", "Shikarpur", "Lakhanjo-daro", "Tarkhanewala-dera", "Naru-Waro-dharo"}
dev, ho = L.dev_heldout(version=2)
dev_freq = Counter(s for t in dev for s in t["seq"] if s not in "|#")
I = L.distinct(L.icit_texts())
home = {"Harappa", "Mohenjo-daro", "Lothal", "Kalibangan", "Chanhu-daro"}
icit_freq = Counter(s for t in I if t["site"] in home for s in t["seq"] if s not in "|#")
new = [t for t in I if t["site"] in POST1977]
R.OUT.clear()
R.block("B1_icit_post1977_single_complete", R.single_complete(new), R.TICK_W, R.PLAIN_W, icit_freq)
R.block("B1_icit_dholavira_only", R.single_complete([t for t in new if t["site"] == "Dholavira"]), R.TICK_W, R.PLAIN_W, icit_freq)
R.OUT["B1_ticked_texts"] = [(t["site"], t["id"], " ".join(t["seq"])) for t in R.single_complete(new) if set(t["seq"]) & R.TICK_W]
# (b) one ticked-fish text per final bigram (drops formula repeats), M77 held-out
H1 = R.single_complete(ho); seen, keep = set(), []
for t in H1:
    if set(t["seq"]) & R.TICK_M:
        key = tuple(t["seq"][-2:])
        if key in seen: continue
        seen.add(key)
    keep.append(t)
R.block("B2_heldout_one_per_final_bigram", keep, R.TICK_M, R.PLAIN_M, dev_freq)
json.dump(R.OUT, open(HERE / "results2.json", "w"), indent=1, default=str)
