"""v2: collect the scan audit and the v1 re-measurement into results_v2.json.
Run after v2_audit.py, v2_audit_plates.py, v2_crop.py:  .venv/bin/python -I experiments/plate_corpus/v2_summary.py"""
import csv, json, os, statistics as st
D = os.path.dirname(os.path.abspath(__file__))

rem = list(csv.DictReader(open(os.path.join(D, "crops_v2", "v1_remeasure.csv"))))
plates = list(csv.DictReader(open(os.path.join(D, "work", "v2_scan_audit_plates.csv"))))

# best upload per volume: greyscale/colour only (v1 prereg rule), TRUE seal px/mm.
# Uploads without a measured seal crop get an upper bound from page geometry relative to the v1 upload
# (same physical page, so seal px/mm scales with page width in px), divided by the round-trip factor.
BEST = {
    "Mackay1938_FEM": dict(
        greyscale=[("in.gov.ignca.9954", "6x enlargement (block period 6)", 3.32),
                   ("furtherexcavationsatmohenjodaro192731vol2ejhmackay_191_N", "same file as 9954: 6x enlargement", 3.32)],
        bitonal=["in.ernet.dli.2015.57013 (same master scan as 9954, page geometry identical, 1-bit)",
                 "in.ernet.dli.2015.440862 (300 ppi, 1-bit)", "dli.jZY9...TVA_BOK_0009130 (1-bit)", "dli.ernet.426189 (1-bit)"]),
    "Vats1940_EH": dict(
        greyscale=[("dli.ministry.25730", "4x enlargement (block period 4)", 3.86)],
        bitonal=["excavationsatharappamadhosarupvatsvol2alt_435_p", "excavationsatharappamadhosarupvatsvol2alt1_617_R",
                 "in.ernet.dli.2015.106332", "in.ernet.dli.2015.210462", "in.ernet.dli.2015.358921",
                 "in.ernet.dli.2015.358923", "in.ernet.dli.2015.426170", "in.ernet.dli.2015.537391"]),
    "Mackay1943_CE": dict(
        greyscale=[("dli.ministry.25495", "4x enlargement (block period 4)", 5.52),
                   ("nufj-chanhu-daro-excavations-1935-36-by-ernest-j-h-mack",
                    "no enlargement found; page 2051 px wide vs 4507 for 25495 -> nominal ~10.1, true 6.7-10.1 (upper bound)", 10.1),
                   ("in.gov.ignca.27263", "6x enlargement (block period 6), ~100 ppi real", None)],
        bitonal=["chanhudaroexcavations193536emackay_184_y", "in.ernet.dli.2015.105167",
                 "BK001064... (72 ppi stated)"]),
    "Marshall1931_MIC": dict(
        greyscale=[("in.gov.ignca.48270", "3-4x enlargement", 3.09),
                   ("xSFp_... (1973 reprint)", "page 1362 px wide vs 2677 for 48270 -> nominal ~5.4 (upper bound)", 5.4),
                   ("mohenjodaroandtheinduscivilizationvol3jmarshalled1931_292_u", "150 ppi stated, ~75 ppi real", None),
                   ("dli.ministry.25759", "150 ppi stated", None)],
        bitonal=["in.ernet.dli.2015.96024", "in.ernet.dli.2015.441817 (v1: vol. I text)"]),
}


def med(xs):
    return round(st.median(xs), 2) if xs else None


by_vol = {}
for v in BEST:
    x = [r for r in rem if r["source"] == v]
    by_vol[v] = dict(n_v1_seals=len(x), nominal_median=med([float(r["nominal_px_per_mm"]) for r in x]),
                     factors=sorted({float(r["true_factor"]) for r in x}),
                     true_median_v1_upload=med([float(r["true_px_per_mm"]) for r in x]),
                     best_greyscale_true_px_per_mm_upper=max(b[2] for b in BEST[v]["greyscale"] if b[2] is not None),
                     passes_12=False, uploads=BEST[v])
c = [r for r in rem if r.get("cisi_true_px_per_mm")]
out = dict(
    date="2026-11-17", gate="plate_corpus v2 (re-check of scan detail)",
    verdict="FAIL at step 1: no greyscale/colour archive.org upload of any of the four volumes has >= 12 px/mm of real detail; no second gate was run",
    v1_correction=dict(nominal_median_px_per_mm=18.5,
                       true_median_px_per_mm=med([float(r["true_px_per_mm"]) for r in rem]),
                       true_range=[min(float(r["true_px_per_mm"]) for r in rem), max(float(r["true_px_per_mm"]) for r in rem)],
                       cause="the source uploads are low-resolution images enlarged 3-6x (pixel replication, visible block grid); cropping did no resampling",
                       paired_cisi_true_median_lower_bound=med([float(r["cisi_true_px_per_mm"]) for r in c]),
                       paired_plate_true_median=med([float(r["true_px_per_mm"]) for r in c]),
                       cisi_pair_error="FEM 288: the CISI crop shows a different seal (square unicorn seal, longer text) from the plate (5-sign bar seal)"),
    method=dict(test="v2_effres.py: block-grid period + grid-aligned and smooth round-trip loss; THRESH 0.17",
                controls="sharp CISI crop -> 2 (floor 1.5-2); x3 nearest -> 3; x3 bicubic -> 4; x6 nearest -> 6; x6 bicubic -> 6",
                bitonal_rule="1-bit uploads excluded as in v1 prereg (greyscale or colour only)"),
    by_volume=by_vol,
    bitonal_fem_check=dict(item="in.ernet.dli.2015.57013", note="same master as IGNCA 9954 at full resolution but thresholded to 1 bit; "
                           "158 specks <= 4 px on FEM 273 vs 2 in a thresholded 6x enlargement, so it was made before the downsampling; "
                           "relief shading is lost (shadows fill black)",
                           midtone_frac=[float(r["dli_bitonal_midtone"]) for r in rem if r.get("dli_bitonal_midtone")]),
    readers_run=0, prereg_written=False,
)
json.dump(out, open(os.path.join(D, "results_v2.json"), "w"), indent=1)
print(json.dumps({k: out[k] for k in ("verdict", "v1_correction")}, indent=1))
for v, b in by_vol.items():
    print(v, b["nominal_median"], b["factors"], b["true_median_v1_upload"], b["best_greyscale_true_px_per_mm_upper"])
