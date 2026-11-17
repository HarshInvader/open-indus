"""Build registers.csv from the parsed report catalogues and link each row to M77 and ICIT.

Links
  M77:  Mahadevan text_no = 1000 + MIC serial, 2000 + FEM serial, 4000 + EH serial (Mahadevan 1977 App. V,
        confirmed in shaunmortal STATE.md); Chanhu-daro 6000 + 100*k + plate no. (k = 1,2,3 for CE pl. LI, LII,
        LIII; tested here against ICIT sign sequences).
  ICIT: (a) report field no. == field no. in the CISI 'Basic data' table -> CISI no. -> ICIT `cisi`;
        (b) CISI second column (Koskenniemi-Parpola no.) -> M77 text_no (MD: identical; Harappa: KP 3xxx = M77 4xxx).
  Every link is checked: depth vs M77 level (integer ft) and, where both texts exist, sign-sequence similarity of
  the M77 and ICIT texts through the Wells<->Mahadevan bridge (sources/shaunmortal_indus/data/bridge_WM.json).
Run: .venv/bin/python -I experiments/old_registers/link.py
"""
import csv, json, os, re, random
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
rd = lambda f: list(csv.DictReader(open(os.path.join(HERE, f))))

# ---------- reference data
M77 = {}
for l in open(os.path.join(REPO, "data/m77_lines.jsonl")):
    x = json.loads(l)
    o = M77.setdefault(x["text_no"], dict(site=x["site"], object_type=x["object_type"], level=x["level"], locus=x["locus"], signs=[]))
    o["signs"] += [s for s in x["signs"]]
ICIT = defaultdict(list)
for l in open(os.path.join(REPO, "data/icit_texts.jsonl")):
    x = json.loads(l)
    if x["cisi"] not in ("-", ""):
        ICIT[x["cisi"]].append(x)
BR = json.load(open(os.path.join(REPO, "sources/shaunmortal_indus/data/bridge_WM.json")))
W2M = {f"W{int(k):03d}": {f"M{m}" for m in v["M"]} for k, v in BR.items()}


def seqsim(msigns, wseq):
    """LCS of M77 signs vs ICIT signs, a W matching an M if the bridge maps it there; / max length."""
    a = [s for s in msigns if s.startswith("M")]
    b = [s for s in wseq if s.startswith("W")]
    if not a or not b:
        return None
    D = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a)):
        for j in range(len(b)):
            D[i + 1][j + 1] = D[i][j] + 1 if a[i] in W2M.get(b[j], ()) else max(D[i][j + 1], D[i + 1][j])
    return D[-1][-1] / max(len(a), len(b))


def best_sim(tn, cisi):
    if tn not in M77 or cisi not in ICIT:
        return None
    sims = [seqsim(M77[tn]["signs"], i["seq"]) for i in ICIT[cisi]]
    sims = [s for s in sims if s is not None]
    return max(sims) if sims else None


def fkey(s):
    """normalise a field number to prefix-less digits+suffix (e.g. 'DK 11212' -> '11212', 'DK-i 441' -> 'i441')."""
    s = (s or "").strip()
    m = re.search(r"(DK-?[A-Gi]|DK|VS|HR|SD|DM|L|C|E|F|D|B|A)?\s*[-.]?\s*(\d{2,6}[a-z]?)\s*$", s)
    if not m:
        return ""
    pre = (m.group(1) or "")
    sub = pre[-1].lower() if pre.startswith("DK-") else ""
    return sub + m.group(2)


CISI = rd("cisi_basic.csv")
cisi_by_field = defaultdict(list)
for c in CISI:
    site = c["cisi"].split("-")[0]
    rest = c["rest"]
    if site == "M":
        k = fkey(c["field_no"])
    elif site in ("H", "C"):
        m = re.match(r"^\s*(?:CH[. ]*)?([A-Za-z]{0,3}[\s-]?\d{2,6}[a-z]?)", rest)
        k = re.sub(r"\W", "", m.group(1)).upper() if m else ""
    else:
        k = ""
    if k:
        cisi_by_field[(site, k)].append(c)
KP2M77 = {}
for c in CISI:
    if not c["num4"].isdigit():
        continue
    n, site = int(c["num4"]), c["cisi"].split("-")[0]
    if site == "M" and 1000 < n < 3000:
        KP2M77[c["cisi"].split("(")[0]] = n
    elif site == "H" and 3000 < n < 4000:
        KP2M77[c["cisi"].split("(")[0]] = n + 1000

# ---------- register rows
rows = []
for r in rd("fem_seals.csv"):
    s = r["serial"]
    rows.append(dict(source="Mackay1938_FEM", object_no=s, site="Mohenjo-daro", findspot=(("DK/SD area: " + r["findspot"]) if r["findspot"] else ""),
                     block=r["block"], house=r["house"], room=r["room"], depth_ft=r["level_ft"].replace("surface", "0.0"), depth_ref="below datum (Mackay)",
                     l_in=r["l_in"], w_in=r["w_in"], t_in=r["t_in"], material=r["material_n"], description=f"type {r['type']}".strip(),
                     plate_ref=f"FEM tab. seal {s}", field_no=r["field_no"], ocr_repaired=r["serial_repaired"],
                     m77_guess=2000 + int(s) if s.isdigit() else ""))
for r in rd("eh_seals.csv"):
    s = r["serial"]
    rows.append(dict(source="Vats1940_EH", object_no=s, site="Harappa", findspot=f"Mound/Area {r['mound']}" if r["mound"] else "",
                     block="", house="", room="", depth_ft=r["depth_ft"].replace("surface", "0.0").replace("spoil", ""), depth_ref="below surface (Vats)",
                     l_in=r["l_in"], w_in=r["w_in"], t_in="", material="", description=f"type {r['type']}; colour {r['colour']}",
                     plate_ref=f"EH pl. seal {s}", field_no=r["find_no"], ocr_repaired=r["serial_repaired"],
                     m77_guess=4000 + int(s) if s.isdigit() else ""))
for r in rd("ce_seals.csv"):
    k = {"LI": 1, "LII": 2, "LIII": 3}.get(r["plate"])
    rows.append(dict(source="Mackay1943_CE", object_no=r["plate_ref"], site="Chanhu-daro", findspot=r["findspot"], block="", house="", room="",
                     depth_ft=r["level_ft"], depth_ref="relative to datum (Mackay)", l_in=r["l_in"], w_in=r["w_in"], t_in=r["t_in"],
                     material=r["material"], description=r["description"][:200], plate_ref=r["plate_ref"], field_no="CH " + r["field_no"],
                     ocr_repaired="", m77_guess=6000 + 100 * k + int(r["plate_no"]) if k and r["plate_no"].isdigit() else ""))
for r in rd("mic_seals.csv"):
    if not r["field_no"] or not r["serial"].isdigit():
        continue
    s = r["serial"]
    rows.append(dict(source="Marshall1931_MIC", object_no=s, site="Mohenjo-daro", findspot=f"Area {r['field_no'].split()[0]}", block="", house="", room="",
                     depth_ft=r["level_ft"].replace("surface", "0.0"), depth_ref="below surface (Marshall)", l_in=r["l_in"], w_in=r["w_in"], t_in="",
                     material="", description="", plate_ref=f"MIC tab. seal {s}", field_no=r["field_no"], ocr_repaired=r["serial_repaired"],
                     m77_guess=1000 + int(s)))

# drop exact duplicate rows (double-scanned pages)
seen, R = set(), []
for r in rows:
    k = (r["source"], r["object_no"], r["field_no"])
    if k in seen:
        continue
    seen.add(k); R.append(r)
rows = R

# ---------- link
for r in rows:
    site = {"Mohenjo-daro": "M", "Harappa": "H", "Chanhu-daro": "C"}[r["site"]]
    if site == "M":
        fk = fkey(r["field_no"])
    else:
        fk = re.sub(r"\W", "", r["field_no"].replace("CH ", "")).upper()
    cands = cisi_by_field.get((site, fk), []) if fk else []
    r["cisi"] = ";".join(sorted({c["cisi"].split("(")[0] for c in cands}))
    r["cisi_kp_no"] = ";".join(sorted({c["num4"] for c in cands if c["num4"]}))
    tn = r["m77_guess"]
    r["m77_text_no"] = tn if tn in M77 else ""
    # depth check vs M77 integer level
    chk = ""
    if r["m77_text_no"] and r["depth_ft"] and M77[tn]["level"] not in ("", "0"):
        try:
            chk = "agree" if abs(abs(float(r["depth_ft"])) - abs(int(M77[tn]["level"]))) <= 1.01 else "disagree"
        except ValueError:
            pass
    r["check_depth_vs_m77"] = chk
    # KP number from CISI agrees with serial-based M77 number?
    kp = [KP2M77.get(c) for c in r["cisi"].split(";") if c]
    r["check_kp"] = ("agree" if tn in kp else "disagree") if any(kp) and tn else ""
    sims = [best_sim(tn, c) for c in r["cisi"].split(";") if c and tn]
    sims = [s for s in sims if s is not None]
    r["seq_sim_m77_icit"] = f"{max(sims):.2f}" if sims else ""
    ic = [i for c in r["cisi"].split(";") if c for i in ICIT.get(c, [])]
    r["icit_ids"] = ";".join(sorted({i["id"] for i in ic}))
    r["icit_dims_mm"] = ";".join(sorted({f"{i['width_mm']}x{i['height_mm']}" for i in ic}))
    r["icit_material"] = ";".join(sorted({i["material"] for i in ic}))
    # ---- what is new beyond our corpus files
    m = M77.get(r["m77_text_no"]) if r["m77_text_no"] else None
    linked = bool(m) or bool(ic)
    r["linked"] = "yes" if linked else "no"
    has_dims = bool(r["l_in"])
    icit_has_dims = any(float(i["width_mm"] or 0) > 0 for i in ic)
    r["new_dims"] = "yes" if linked and has_dims and not icit_has_dims else ""
    r["new_depth"] = ""
    if linked and r["depth_ft"] not in ("", None):
        if not m or m["level"] in ("", "0"):
            r["new_depth"] = "yes (absent in M77)"
        elif re.search(r"\.\d*[1-9]", str(r["depth_ft"])):
            r["new_depth"] = "precision (M77 integer ft)"
    fine = r["source"] == "Mackay1938_FEM" and (r["room"] or r["house"] or "St" in r["findspot"] or "Bet" in r["findspot"]) or \
        r["source"] == "Mackay1943_CE" and "loc." in r["findspot"]
    r["new_findspot"] = "yes (room/locus; M77 has area code only)" if linked and fine else ""
    r["new_field_no"] = "yes" if linked and r["field_no"] else ""

# ---------- quality checks: is the serial->M77 rule right? sequence similarity of linked vs random pairs
random.seed(0)
real = [float(r["seq_sim_m77_icit"]) for r in rows if r["seq_sim_m77_icit"]]
pool_m = [t for t in M77 if M77[t]["signs"]]
pool_i = [c for c in ICIT]
rand = []
for _ in range(2000):
    s = best_sim(random.choice(pool_m), random.choice(pool_i))
    if s is not None:
        rand.append(s)
# CE plate-number rule test with alternative k for each plate
ce_tests = {}
for r in rows:
    if r["source"] != "Mackay1943_CE" or not r["cisi"]:
        continue
    pl, no = r["plate_ref"].split("pl. ")[1].split(", ")
    for k in (1, 2, 3, 4, 5):
        tn = 6000 + 100 * k + int(no) if no.isdigit() else None
        for c in r["cisi"].split(";"):
            s = best_sim(tn, c)
            if s is not None:
                ce_tests.setdefault((pl, k), []).append(s)

cols = ["source", "object_no", "site", "findspot", "block", "house", "room", "depth_ft", "depth_ref", "l_in", "w_in", "t_in",
        "material", "description", "plate_ref", "field_no", "ocr_repaired", "m77_text_no", "cisi", "cisi_kp_no", "icit_ids",
        "icit_dims_mm", "icit_material", "check_depth_vs_m77", "check_kp", "seq_sim_m77_icit", "linked",
        "new_depth", "new_dims", "new_findspot", "new_field_no"]
with open(os.path.join(HERE, "registers.csv"), "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(rows)

# ---------- summary
S = {}
for src in sorted({r["source"] for r in rows}):
    X = [r for r in rows if r["source"] == src]
    d = Counter(r["check_depth_vs_m77"] for r in X)
    k = Counter(r["check_kp"] for r in X)
    sims = [float(r["seq_sim_m77_icit"]) for r in X if r["seq_sim_m77_icit"]]
    S[src] = dict(rows=len(X), with_depth=sum(1 for r in X if r["depth_ft"] not in ("", None)), with_dims=sum(1 for r in X if r["l_in"]),
                  with_field_no=sum(1 for r in X if r["field_no"]),
                  linked_m77=sum(1 for r in X if r["m77_text_no"]), linked_cisi=sum(1 for r in X if r["cisi"]),
                  linked_icit=sum(1 for r in X if r["icit_ids"]), linked_any=sum(1 for r in X if r["linked"] == "yes"),
                  depth_vs_m77=dict(d), kp_check=dict(k),
                  seqsim_n=len(sims), seqsim_ge_0_5=sum(1 for s in sims if s >= 0.5),
                  new_depth_absent=sum(1 for r in X if r["new_depth"].startswith("yes")),
                  new_depth_precision=sum(1 for r in X if r["new_depth"].startswith("precision")),
                  new_dims=sum(1 for r in X if r["new_dims"]), new_findspot=sum(1 for r in X if r["new_findspot"]),
                  new_field_no=sum(1 for r in X if r["new_field_no"]),
                  new_any_of_depth_dims_findspot=sum(1 for r in X if r["new_depth"] or r["new_dims"] or r["new_findspot"]))
S["_seqsim_real_mean"] = sum(real) / len(real) if real else None
S["_seqsim_real_ge_0_5"] = f"{sum(1 for s in real if s >= .5)}/{len(real)}"
S["_seqsim_random_mean"] = sum(rand) / len(rand)
S["_seqsim_random_ge_0_5"] = f"{sum(1 for s in rand if s >= .5)}/{len(rand)}"
S["_ce_plate_rule"] = {f"{pl} k={k}": f"mean {sum(v)/len(v):.2f} n={len(v)}" for (pl, k), v in sorted(ce_tests.items())}
json.dump(S, open(os.path.join(HERE, "link_summary.json"), "w"), indent=1)
print(json.dumps(S, indent=1))
