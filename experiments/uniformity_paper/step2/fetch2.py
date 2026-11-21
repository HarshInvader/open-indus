"""Where the step-2 reference data come from (not run for step 2: every file was already on disk).

Running it re-downloads the public sources into the same raw/ folders (gitignored), with the project's generic
User-Agent. No paywalled or login-only source is used.

  ORACC epsd2/admin/ur3     -> experiments/meaning_classes_seal/raw/ur3.zip        (ORACC, CC BY-SA 3.0)
  ORACC epsd2/admin/oldbab  -> experiments/onomasticon/raw/epsd2-admin-oldbab.zip  (ORACC, CC BY-SA 3.0)
  CDLI catalogue + ATF      -> experiments/short_labels/raw/cdli/                  (CDLI data repository, cdli-gh/data)
  EDH (Epigraphic Database Heidelberg) open data -> experiments/short_labels/raw/edh/ (CC BY-SA 4.0)

  .venv/bin/python -I experiments/uniformity_paper/step2/fetch2.py [ur3|oldbab|cdli]
"""
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
UA = {"User-Agent": "open-research-site/1.0"}
SOURCES = {
    "ur3": ("https://oracc.museum.upenn.edu/json/epsd2-admin-ur3.zip", ROOT / "experiments/meaning_classes_seal/raw/ur3.zip"),
    "oldbab": ("https://oracc.museum.upenn.edu/json/epsd2-admin-oldbab.zip", ROOT / "experiments/onomasticon/raw/epsd2-admin-oldbab.zip"),
    "cdli_cat": ("https://raw.githubusercontent.com/cdli-gh/data/master/cdli_cat.csv", ROOT / "experiments/short_labels/raw/cdli/cdli_cat.csv"),
    "cdli_atf": ("https://raw.githubusercontent.com/cdli-gh/data/master/cdliatf_unblocked.atf", ROOT / "experiments/short_labels/raw/cdli/cdliatf_unblocked.atf"),
}
# EDH: fetched page by page by experiments/short_labels (see that folder's fetch code); not repeated here.


def get(key):
    url, out = SOURCES[key]
    out.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r, open(out, "wb") as f:
        while True:
            b = r.read(1 << 20)
            if not b:
                break
            f.write(b)
    print(key, "->", out)


if __name__ == "__main__":
    keys = sys.argv[1:] or list(SOURCES)
    for k in keys:
        for kk in [x for x in SOURCES if x == k or x.startswith(k + "_")]:
            get(kk)
