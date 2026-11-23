"""Scorecard v1 rows (prereg docs/prereg/scorecard_v1.md). Writes rows.csv: id, group, claimant, claim, evidence.
Evidence = repo paths (and, for catalogue rows, the catalogue's own status text) that a rater reads to assign a tier.
Run: .venv/bin/python -I experiments/scorecard_v1/build_rows.py
"""
import csv
from pathlib import Path

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]

CAL = [
    ("CAL-LB-true", "calibration", "Ventris (true Linear B key)", "The true Linear B sign-to-sound key, scored as if it were an Indus claim at Indus text shape",
     "experiments/lb_certify/RESULTS.md; experiments/lb_shape_ladder/RESULTS.md"),
    ("CAL-noise-keys", "calibration", "keys fitted to random sign strings", "Keys hill-climbed to fit noise, scored the same way",
     "experiments/lb_shape_ladder/RESULTS.md; experiments/yj_ic_refute/RESULTS.md"),
]
KEYS = [
    ("KEY-yajnadevam", "phonetic key", "Yajnadevam (2024)", "Full Sanskrit sign-to-sound key; the corpus reads as Vedic Sanskrit",
     "docs/NEGATIVE_ATLAS.md section 1.1; experiments/yj_ic_refute/RESULTS.md; experiments/lb_shape_ladder/RESULTS.md"),
    ("KEY-pierson", "phonetic key", "Pierson (glossa-lab)", "Partial phonetic readings (605 readings)", "docs/NEGATIVE_ATLAS.md section 1.1; experiments/bench_pierson/ (RESULTS.md if present)"),
    ("KEY-fairservis", "phonetic key", "Fairservis (1992)", "Dravidian readings of signs as names and honorifics", "docs/NEGATIVE_ATLAS.md section 1.1; experiments/meaning_claims/CATALOGUE.csv row FAI92-honorifics"),
    ("KEY-rao", "phonetic key", "S. R. Rao", "Indo-Aryan syllabic values", "docs/NEGATIVE_ATLAS.md section 1.1"),
    ("KEY-kalyanaraman", "phonetic key", "S. Kalyanaraman", "Rebus readings (Meluhha metalwork lexicon)",
     "docs/prereg/kalyanaraman_key.md (and its addendum 1); docs/outreach/REPLIES.md (table requested, not yet received)"),
    ("KEY-adelman", "phonetic key", "Adelman (2026)", "Convergent Dravidian key, 'systemic coherence to the rarest sign'", "experiments/bench2026/RESULTS.md (Adelman section)"),
    ("FUN-kriger-hunt", "function claim", "Kriger & Hunt (2026)", "Seal texts are registration codes (uniqueness, edge pattern, numerals, near-duplicates)", "experiments/bench2026/RESULTS.md"),
    ("FUN-sigil", "function claim", "Raghavendra (2026, SIGIL)", "A sound-free emblem system reproduces the Indus statistics", "experiments/bench2026/RESULTS.md (SIGIL section); docs/NEGATIVE_ATLAS.md section 3.3"),
]
OWN = [(f"OWN-{i}", "our finding", "this project", f"README 'What we can defend' row #{i}", f"README.md table row #{i} and the folders it names") for i in range(1, 12)]


def build(catalogue_rows=None):
    """Rows as dicts. catalogue_rows: list of catalogue dicts (default: the current CATALOGUE.csv)."""
    if catalogue_rows is None:
        catalogue_rows = list(csv.DictReader(open(ROOT / "experiments/meaning_claims/CATALOGUE.csv")))
    rows = [dict(zip(("id", "group", "claimant", "claim", "evidence"), r)) for r in CAL + KEYS]
    for x in catalogue_rows:
        rows.append(dict(id="MC-" + x["id"], group="meaning claim", claimant=f"{x['author']} ({x['year']})", claim=x["claimed_meaning"],
                         evidence=f"experiments/meaning_claims/CATALOGUE.csv row {x['id']} (status: {x['status']}; {x['status_detail']})"))
    rows += [dict(zip(("id", "group", "claimant", "claim", "evidence"), r)) for r in OWN]
    return rows


def main():
    rows = build()
    with open(HERE / "rows.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["id", "group", "claimant", "claim", "evidence"]); w.writeheader(); w.writerows(rows)
    print(len(rows), "rows")


if __name__ == "__main__":
    main()
