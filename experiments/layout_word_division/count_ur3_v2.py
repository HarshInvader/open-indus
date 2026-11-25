"""Label-free count for Ur III Sumerian: Yale CC0 records with a CDLI P-number and an ATF text.
Counts objects, undamaged lines >= 3 signs, within-line gaps (excluding the last) and word
boundaries among them. Reads no image and no gap size.
Usage: python3 -I count_ur3.py <records_ur3.jsonl> <cdliatf.atf> <img_dir>"""
import json, re, sys, os, collections

rec_f, atf_f, img_dir = sys.argv[1:4]
want = {}
for line in open(rec_f):
    r = json.loads(line)
    for o in r.get("other_ids", []):
        m = re.match(r"(P\d{6}) \(CDLI number\)", o)
        if m:
            want[m.group(1)] = r.get("nat", [None])[0]
have_img = {f.split(".")[0] for f in os.listdir(img_dir)}

DAMAGE = re.compile(r"[\[\]x#?!<>]|\.\.\.")
texts, cur, keep = {}, None, False
plain = {}
for line in open(atf_f, encoding="utf8", errors="replace"):
    if line.startswith("&P"):
        cur = line[1:8]; keep = cur in want
        if keep: texts[cur] = []
        continue
    if not keep or not re.match(r"^\d+'?\.\s", line):
        continue
    body = line.split(".", 1)[1].strip()
    if DAMAGE.search(body) or "$" in body:
        continue
    words = [w for w in body.split() if w]
    counts = []; signs = []
    for wi, w in enumerate(words):
        w2 = re.sub(r"\{[^}]*\}", " {D} ", w)
        parts = [s for s in re.split(r"[-.\s+:]+", w2) if s]
        counts.append(len(parts))
        for s_ in parts:
            cls = "det" if s_ == "{D}" else ("num" if re.match(r"^\d", s_) else "syl")
            signs.append((cls, wi))
    if sum(counts) >= 3:
        texts[cur].append(counts); plain.setdefault(cur, []).append(signs)

def tally(ids):
    t = collections.Counter()
    for p in ids:
        L = texts.get(p, [])
        if not L: continue
        t["objects"] += 1; t["lines3"] += len(L)
        for c in L:
            g = sum(c) - 2
            b = len(c) - 1 - (1 if len(c) >= 2 and c[-1] == 1 else 0)
            t["gaps_excl_last"] += g; t["bound_excl_last"] += b
    for p in ids:
        for sg in plain.get(p, []):
            for i in range(len(sg) - 2):
                if sg[i][0] == "syl" and sg[i+1][0] == "syl":
                    t["gaps_plain"] += 1; t["bound_plain"] += sg[i][1] != sg[i+1][1]
    t["nonbound_excl_last"] = t["gaps_excl_last"] - t["bound_excl_last"]
    return dict(t)

print("records with P-number", len(want), "ATF found", len(texts))
print("ALL (IIIF photo available per Yale record):", tally(texts))
print("photo already on disk:", tally([p for p in texts if want[p] in have_img]))
