"""v2 label-free count for S1 (Neo-Assyrian). Excludes lines with any ORACC break/uncertainty mark.
Also reports Dencker box coverage, line-annotation coverage, and the possible gold consecutive pairs.
Reads no gap size. Usage: python3 -I count_na2.py <oracc_dir> <ds_dir>"""
import csv, json, sys, zipfile, glob, collections, os, statistics as st

oracc_dir, ds_dir = sys.argv[1], sys.argv[2]
BAD_KEYS = ("break", "flags", "queried", "uflag1", "uflag2", "uflag3", "uflag4", "collated")

def leaves(g, acc):
    for x in g:
        if not isinstance(x, dict):
            continue
        if "seq" in x:
            leaves(x["seq"], acc)
        elif "group" in x:
            leaves(x["group"], acc)
        elif any(k in x for k in ("v", "s", "n", "x", "q")) or x.get("type") == "x":
            bad = any(k in x for k in BAD_KEYS) or "o" in x or "c" in x or "ho" in x or "hc" in x \
                or x.get("x") is not None or str(x.get("v", "")).startswith("x")
            cls = "num" if "n" in x else ("det" if "det" in x else ("logo" if x.get("role") == "logo" else "syl"))
            acc.append((bad, cls))
    return acc

def walk(node, out):
    if isinstance(node, dict):
        if node.get("node") == "d" and node.get("type") == "line-start":
            out.append([])
        elif node.get("node") == "l":
            f = node.get("f", {})
            s = leaves(f.get("gdl", []), []) if f else []
            if out and s:
                out[-1].append(s)
        elif node.get("node") == "d" and node.get("type") in ("nonx", "nonw") and out:
            out[-1].append([(True, "x")])
        for v in node.get("cdl", []) if isinstance(node.get("cdl"), list) else []:
            walk(v, out)
    elif isinstance(node, list):
        for v in node:
            walk(v, out)

lines_by_p, mus2p = {}, {}
for z in sorted(glob.glob(os.path.join(oracc_dir, "*.zip"))):
    zf = zipfile.ZipFile(z)
    for nm in zf.namelist():
        if "/corpusjson/" in nm and nm.endswith(".json"):
            raw = zf.read(nm)
            if not raw.strip():
                continue
            d = json.loads(raw)
            out = []
            walk(d.get("cdl", []), out)
            lines_by_p[d["textid"]] = out
        if nm.endswith("/catalogue.json"):
            for p, m in json.loads(zf.read(nm)).get("members", {}).items():
                for k in ("museum_no", "accession_no"):
                    if m.get(k):
                        mus2p[m[k].replace(" ", "").replace(",", "").upper()] = p

def to_p(t):
    if t.startswith("P") and t[1:].isdigit():
        return t
    key = t.replace(" ", "").upper()
    k2 = key[:-2] if key.endswith(("VS", "RS")) else key
    for c in (key, k2, k2.replace("K0", "K", 1), k2.replace("ND0", "ND", 1), k2.replace("BM0", "BM", 1)):
        if c in mus2p:
            return mus2p[c]

boxes = collections.Counter(); face_boxes = collections.Counter()
for f in glob.glob(os.path.join(ds_dir, "bbox_annotations_*_full.csv")):
    for r in csv.DictReader(open(f)):
        if r["train_label"] != "0":
            boxes[r["tablet_CDLI"]] += 1; face_boxes[(r["tablet_CDLI"], r["segm_idx"])] += 1
# transliterated signs per face (Dencker transliteration files)
face_tl = collections.Counter(); tl_line = collections.defaultdict(list)
for f in glob.glob(os.path.join(ds_dir, "transliterations_*.csv")):
    for r in csv.DictReader(open(f)):
        if r["train_label"] != "0" or r["mzl_label"] != "0":
            face_tl[(r["tablet_CDLI"], r["segm_idx"])] += 1
la = set()
for f in glob.glob(os.path.join(ds_dir, "line_annotations_*.csv")):
    for r in csv.DictReader(open(f)):
        la.add(r["tablet_CDLI"])
cov = [face_boxes[k] / face_tl[k] for k in face_boxes if face_tl.get(k)]
print("faces with boxes and Dencker TL:", len(cov), "median box/TL coverage %.2f" % st.median(cov) if cov else "")
print("tablets with boxes:", len(boxes), "with line annotations:", len(la & set(boxes)))

tot = collections.Counter(); matched = []
for t in boxes:
    p = to_p(t)
    if not p or p not in lines_by_p:
        continue
    matched.append(t)
    for ln in lines_by_p[p]:
        n = sum(len(w) for w in ln)
        if n < 3:
            continue
        tot["lines3_all"] += 1
        if any(b for w in ln for b, _ in w):
            continue
        tot["lines3_clean"] += 1
        wl = [len(w) for w in ln]
        tot["gaps"] += n - 2
        b = len(wl) - 1 - (1 if len(wl) >= 2 and wl[-1] == 1 else 0)
        tot["bound"] += b
        # gaps (excl last) where neither neighbour is num/det/logo
        signs = [(c, wi) for wi, w in enumerate(ln) for _, c in w]
        for i in range(len(signs) - 2):
            if signs[i][0] == "syl" and signs[i + 1][0] == "syl":
                tot["gaps_plain"] += 1
                tot["bound_plain"] += signs[i][1] != signs[i + 1][1]
tot["nonbound"] = tot["gaps"] - tot["bound"]; tot["nonbound_plain"] = tot["gaps_plain"] - tot["bound_plain"]
tot["tablets"] = len(matched)
tot["tablets_with_line_ann"] = len(set(matched) & la)
print(json.dumps(tot, indent=1))
