"""Group Vision OCR line boxes (work/vocr/*.tsv) into rows; split page into left/right halves."""
import sys
def load(path):
    out = []
    for l in open(path, encoding="utf-8"):
        a, t = l.rstrip("\n").split("\t", 1)
        x, y, w, h = map(float, a.split())
        out.append((x, 1 - y - h / 2, w, h, t))
    return out
def rows(items, tol=0.0045):
    items = sorted(items, key=lambda r: r[1]); R = []
    for it in items:
        if R and abs(it[1] - R[-1][-1][1]) < tol: R[-1].append(it)
        else: R.append([it])
    return [sorted(r) for r in R]
if __name__ == "__main__":
    for r in rows(load(sys.argv[1])):
        print(" | ".join(f"{x:.3f}:{t}" for x, y, w, h, t in r))
