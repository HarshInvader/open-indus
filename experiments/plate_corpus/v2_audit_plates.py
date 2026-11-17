"""v2 step 1b: measure seal-plate pages (located by eye on thumbnails) in every greyscale upload and in
some bitonal ones. Appends to work/v2_scan_audit_plates.csv. Run: .venv/bin/python -I v2_audit_plates.py"""
import csv, os, sys
D = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, D)
from v2_audit import audit_page, probe

PLATES = [  # (volume, item, page index of a seal plate)
    ("Mackay1938_FEM", "in.gov.ignca.9954", 189), ("Mackay1938_FEM", "in.gov.ignca.9954", 201),
    ("Mackay1938_FEM", "furtherexcavationsatmohenjodaro192731vol2ejhmackay_191_N", 189),
    ("Mackay1938_FEM", "in.ernet.dli.2015.57013", 189), ("Mackay1938_FEM", "in.ernet.dli.2015.440862", 106),
    ("Vats1940_EH", "dli.ministry.25730", 97), ("Vats1940_EH", "dli.ministry.25730", 100),
    ("Vats1940_EH", "excavationsatharappamadhosarupvatsvol2alt_435_p", 145),
    ("Vats1940_EH", "excavationsatharappamadhosarupvatsvol2alt_435_p", 146),
    ("Vats1940_EH", "excavationsatharappamadhosarupvatsvol2alt1_617_R", 184),
    ("Mackay1943_CE", "dli.ministry.25495", 402), ("Mackay1943_CE", "dli.ministry.25495", 403),
    ("Mackay1943_CE", "nufj-chanhu-daro-excavations-1935-36-by-ernest-j-h-mack", 419),
    ("Mackay1943_CE", "nufj-chanhu-daro-excavations-1935-36-by-ernest-j-h-mack", 420),
    ("Mackay1943_CE", "chanhudaroexcavations193536emackay_184_y", 416),
    ("Marshall1931_MIC", "in.gov.ignca.48270", 187), ("Marshall1931_MIC", "in.gov.ignca.48270", 201),
    ("Marshall1931_MIC", "xSFp_mohenjodaro-and-the-indus-civilization-by-john-marshall-edited-by-sir-john-marsh", 152),
    ("Marshall1931_MIC", "xSFp_mohenjodaro-and-the-indus-civilization-by-john-marshall-edited-by-sir-john-marsh", 155),
]
rows = []
for vol, item, i in PLATES:
    try:
        r = audit_page(vol, item, i, probe(item).get("ppi"))
    except Exception as e:
        print("fail", item, i, e); continue
    rows.append(r)
    print(vol, item[:30].ljust(30), i, r["mode"], r["W"], "mid", r["tile_midtone"], "grid", r["grid_ratio"], r["grid_period"],
          "eff", r["eff_factor"], "real_ppi", r["real_ppi"], r["loss"])
with open(os.path.join(D, "work", "v2_scan_audit_plates.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
