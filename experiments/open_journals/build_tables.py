"""Build tidy CSVs from open-access sources harvested into raw/.
Run: .venv/bin/python -I experiments/open_journals/build_tables.py
Rows are hand-transcribed from the report text (catalogue entries); every row cites source file + printed page.
Sign readings are NOT given unless clearly legible in the figure; otherwise 'needs human'."""
import csv, re, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
ICIT = os.path.join(ROOT, "sources/field-cady_indus_valley_script_corpus/inscriptions.csv")
K110 = "Lal, Joshi, Bala, Sharma & Ramachandran, Excavations at Kalibangan: The Harappans (1960-69) Part II, MASI 110 (ASI 2020); raw/asi/epub_10.pdf"
GUK = "Ali & Jan? (Ancient Pakistan 22, 2011), 'The mature Harappan occupation at Gandi Omar Khan'; raw/ancientpakistan/ap_93_85.pdf"

# (reg_no, trench, object, vessel_form/obj_form, dims, level, description, printed_page, fig)
KLB = [
    ("21626", "KLB-2", "pottery (chakla/pata)", "chakla with ring base", "dia 36 cm; th 2-3 cm", "late Period II", "Harappan inscription inside ring on bottom", 839, "14.1"),
    ("Mus.Acc.78", "surface", "pottery (chakla/pata)", "chakla with ring base", "dia 24.5 cm; basal ring 18.5 cm", "surface", "complete inscription inside ring on bottom", 841, "14.2"),
    ("21533", "KLB-2", "pottery (chakla/pata)", "chakla with ring base", "dia 15 cm", "late Period II", "Harappan inscription inside ring at bottom", 845, "14.4.1"),
    ("21625", "KLB-2", "pottery (chakla/pata)", "chakla with ring base", "dia 34 cm", "late Period II", "Harappan inscription inside ring at base", 845, "14.4.2"),
    ("21624", "KLB-1", "pottery (chakla/pata)", "chakla with ring base", "dia 34 cm", "late Period II", "inscription or incised design inside ring base", 850, "14.6.1"),
    ("21651", "KLB-2", "pottery (chakla/pata)", "chakla with ring base", "dia 24 cm", "late Period II", "fragmentary incised inscription on basal surface", 850, "14.6.2"),
    ("21623(b)", "KLB-2", "pottery (chakla/pata)", "chakla with ring base", "dia 12 cm; th 1.5 cm", "late Period II", "unidentified incised design/inscription within ring base", 850, "14.6.4"),
    ("Burial-1 urn", "KLB-8? (pot burial)", "pottery (burial urn)", "globular urn, ring base", "", "Harappan pot burial", "PREFIRING graffiti mark: several cross lines enclosed in a rectangle", 1432, ""),
    ("KLB-8 type 25 jar", "KLB-8", "pottery (burial jar)", "oval storage jar, red ware, flat base (type 25)", "", "Harappan pot burial", "inscribed with a Harappan inscription", None, "24.8"),
]
KLB_OTHER = [
    ("3011", "KLB-2", "terracotta kangan (bangle)", "triangular section", "inner dia 6.20 cm; outer 7.85 cm; th 1.65 cm", "late Period II", "inscribed with three letters of Harappan script", 916, "15.16"),
    ("14983", "KLB-1", "copper blade axe", "tapering blade axe", "L 14 cm; W 5-6 cm", "late Period II", "inscription on both sides", 768, "12.1"),
    ("16948", "KLB-2", "copper bar chisel", "bar chisel, square section", "23 x 1 cm", "late Period II", "inscribed (Fig. 12.2)", 770, "12.2"),
    ("20319", "KLB-2", "copper spearhead", "long spearhead, two rivet holes", "inscr. 3.5 x 4 cm", "mid Period II", "inscription of five vertical lines", None, ""),
    ("16113", "KLB-1", "copper dagger (lower part)", "dagger with tang", "", "middle Period II", "inscribed with four oblique lines", None, ""),
    ("18949", "KLB-1", "terracotta gamesman", "four-footed base", "", "late Period II", "incised script near knob", 1220, "21.63"),
    ("6511", "KLB-1", "terracotta gamesman", "one-footed base", "", "late Period II", "incised script", 1220, "21.63"),
    ("5329", "KLB-1", "terracotta gamesman", "three-footed base", "", "late Period II", "incised script", 1220, "21.63"),
    ("21830", "KLB-1&2", "terracotta gamesman", "five-footed base", "", "late Period II", "incised script", 1220, "21.63"),
    ("5364", "KLB-1", "terracotta gamesman", "circular base", "", "middle Period II", "incised script", 1220, "21.63"),
    ("19377", "KLB-1", "terracotta gamesman", "four-footed base", "", "late Period II", "incised script", 1220, "21.63"),
    ("1763", "KLB-1", "terracotta gamesman", "four-footed base", "", "late Period II", "incised script", 1220, "21.63"),
    ("21996", "KLB-2", "terracotta gamesman", "four-footed base", "", "late Period II", "incised script; incomplete oxidization", 1222, "21.64"),
    ("741", "KLB-1", "terracotta gamesman", "four-footed base", "", "late Period II", "incised script", 1222, "21.64"),
    ("4585", "KLB-1", "terracotta gamesman", "five-footed base", "", "late Period II", "incised script", 1222, "21.64"),
    ("17622", "KLB-1", "terracotta gamesman", "circular base", "", "late Period II", "incised script", 1222, "21.64"),
    ("1168", "KLB-1", "terracotta gamesman", "five-footed base", "", "late Period II", "incised script", 1222, "21.64"),
    ("43278", "KLB-1", "terracotta gamesman", "five-footed base", "", "late Period II", "incised script (reg. no. as printed; may be OCR/typo)", 1222, "21.64"),
    ("14712", "KLB-1", "terracotta gamesman", "five-footed base", "", "late Period II", "incised script", 1222, "21.64"),
    ("21831", "KLB-1-2", "terracotta gamesman", "six-footed base", "", "late Period II", "incised script", 1222, "21.64"),
    ("13157", "KLB-1", "terracotta gamesman", "one-footed base", "", "late Period II", "incised script", 1222, "21.64"),
    ("196", "KLB-2", "terracotta cake", "circular", "", "late Period II", "graffiti with finger impression", None, ""),
    ("21102", "KLB-2", "terracotta dog figurine", "", "", "late Period II", "graffiti on body", None, ""),
    ("18936", "KLB-1", "terracotta bull figurine", "", "", "late Period II", "graffiti on body", None, ""),
    ("19603", "KLB-1", "terracotta bull figurine", "", "", "late Period II", "graffiti on back", None, ""),
]


def icit_index():
    idx = {}
    for r in csv.DictReader(open(ICIT, encoding="utf-8")):
        if not r.get("site", "").lower().startswith("kalibangan"):
            continue
        for n in re.findall(r"\d{2,6}", r.get("excavation-idno", "")):
            idx.setdefault(n, []).append(r)
    return idx


def match(idx, reg):
    m = re.match(r"(\d+)", reg)
    if not m:
        return ""
    hits = idx.get(m.group(1), [])
    return "; ".join(f"ICIT {h['id']} ({h['cisi']}, {h['type']}, idno '{h['excavation-idno']}', text {h['text']})" for h in hits)


def main():
    idx = icit_index()
    out = {}
    # pottery_marks.csv
    cols = ["vid", "site", "period", "field_no", "object", "vessel_form", "dims", "firing", "firing_conf", "firing_basis",
            "icit_match", "seq_M", "sign_conf", "description", "source", "page", "fig", "transcription_conf"]
    rows = []
    for reg, tr, obj, form, dims, lev, desc, pg, fig in KLB:
        pre = "PREFIRING" in desc
        rows.append(dict(vid=f"KLB110-{reg}", site="Kalibangan", period=lev, field_no=f"{tr} {reg}", object=obj,
                         vessel_form=form, dims=dims, firing="pre" if pre else "unknown",
                         firing_conf="object" if pre else "", firing_basis="report says 'prefiring graffiti mark'" if pre else "not stated in report",
                         icit_match=match(idx, reg) or "no ICIT idno match (may still be in ICIT under another number)",
                         seq_M="needs human" if not pre else "n/a (non-script mark: cross lines in a rectangle)", sign_conf="",
                         description=desc, source=K110, page=pg or "", fig=fig,
                         transcription_conf="high (catalogue text)"))
    out["pottery_marks.csv"] = (cols, rows)

    # bangles.csv
    bcols = ["bid", "site", "period", "field_no", "material", "dims", "inscribed", "icit_match", "eligible_new_for_bangle_oval", "description", "source", "page"]
    b = [r for r in KLB_OTHER if "kangan" in r[2]]
    brows = []
    for reg, tr, obj, form, dims, lev, desc, pg, fig in b:
        mm = match(idx, reg)
        brows.append(dict(bid=f"KLB110-{reg}", site="Kalibangan", period=lev, field_no=f"{tr} {reg}", material="terracotta",
                          dims=dims, inscribed="yes (3 signs)", icit_match=mm, eligible_new_for_bangle_oval="no (already ICIT K-445)" if mm else "yes",
                          description=desc, source=K110, page=pg))
    out["bangles.csv"] = (bcols, brows)

    # new_texts_extra.csv (same columns as experiments/new_finds/new_texts.csv)
    ncols = ["obj_id", "file", "site", "object_type", "field_symbol", "pub_year", "citation", "status", "icit_match", "seq_M", "sign_conf", "direction", "scored", "notes"]
    nrows = []
    for reg, tr, obj, form, dims, lev, desc, pg, fig in KLB + KLB_OTHER:
        mm = match(idx, reg)
        if mm or "PREFIRING" in desc or "kangan" in obj:
            continue
        nrows.append(dict(obj_id=f"klb110_{reg}".replace(" ", "_").replace(".", ""), file="raw/asi/epub_10.pdf" + (f" Fig. {fig}" if fig else ""),
                          site="Kalibangan", object_type=obj, field_symbol="none", pub_year="2020 (MASI 110 pt II)",
                          citation=f"MASI 110 pt II p.{pg or '?'}", status="candidate new (no ICIT idno match; unverified against CISI 1/3 numbers)",
                          icit_match="none by excavation no.", seq_M="needs human", sign_conf="", direction="", scored="no",
                          notes=f"{desc}; {dims}; {lev}. Figure photo too low-res / rotated for confident sign reading"))
    nrows.append(dict(obj_id="guk_seal1", file="raw/ancientpakistan/ap_93_85.pdf p.16 Plate 12", site="Gandi Umar Khan", object_type="seal",
                      field_symbol="unicorn", pub_year="2011", citation="Ancient Pakistan 22, Plate 12", status="new (site absent from ICIT)",
                      icit_match="none (no Gomal-plain site in ICIT)", seq_M="", sign_conf="", direction="", scored="no",
                      notes="steatite unicorn seal with standard; upper edge broken off, text register lost (at most a trace at far left); no readable text"))
    out["new_texts_extra.csv"] = (ncols, nrows)

    # context.csv (all inscribed objects with object-level context, incl. ICIT-matched ones)
    ccols = ["obj", "site", "trench", "reg_no", "object", "form", "dims", "level_period", "description", "icit_match", "source", "page"]
    crows = []
    for reg, tr, obj, form, dims, lev, desc, pg, fig in KLB + KLB_OTHER:
        crows.append(dict(obj=f"KLB110-{reg}", site="Kalibangan", trench=tr, reg_no=reg, object=obj, form=form, dims=dims,
                          level_period=lev, description=desc, icit_match=match(idx, reg), source=K110, page=pg or ""))
    out["context.csv"] = (ccols, crows)

    for fn, (c, r) in out.items():
        with open(os.path.join(HERE, fn), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=c)
            w.writeheader()
            w.writerows(r)
        print(fn, len(r))


if __name__ == "__main__":
    main()
