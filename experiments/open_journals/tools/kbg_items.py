"""Pull inscribed-object entries from MASI 110 vol II (Kalibangan, Harappans) text (pdftotext flow mode).
Input: work/kbg/masi110_flow.txt (from raw/asi/epub_10.pdf). Output: work/kbg/kbg_inscribed_items.json"""
import re, json, sys
src = sys.argv[1] if len(sys.argv) > 1 else "experiments/open_journals/work/kbg/masi110_flow.txt"
t = open(src, encoding="utf-8", errors="replace").read()
t = re.sub(r"-\n(?=[a-z])", "", t)
flat = re.sub(r"\s+", " ", t)
items = []
for m in re.finditer(r"(?i)(inscri\w*|incised script|harappan script|graffiti)", flat):
    # item start: last 'N. ' with capital word before match, within 500 chars
    pre = flat[max(0, m.start() - 500): m.start()]
    st = [x for x in re.finditer(r"(?:^|\s)(\d{1,2})\.\s+(?=[A-Z])", pre)]
    start = m.start() - 500 + st[-1].start() if st else m.start() - 200
    post = flat[m.start(): m.start() + 500]
    e = re.search(r"\)", post)
    reg = re.search(r"\(([^()]*?(?:Reg|Acc)[^()]*)\)", flat[start: m.start() + 500])
    end = m.start() + (e.end() if e else 200)
    txt = flat[max(0, start): end].strip()
    items.append({"pos": m.start(), "text": txt, "reg": reg.group(1) if reg else ""})
# dedupe by reg/text
seen, out = set(), []
for it in items:
    k = it["reg"] or it["text"][:80]
    if k in seen: continue
    seen.add(k); out.append(it)
json.dump(out, open("experiments/open_journals/work/kbg/kbg_inscribed_items.json", "w"), indent=1)
for it in out: print(it["reg"], "|", it["text"][:260])
