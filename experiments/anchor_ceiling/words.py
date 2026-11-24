"""Write truth/words.txt: the union of eligible words over the 5 draws (alphabetical, no counts).
Checks draw_docs against fcore.draw first. Reads no anchor."""
import sys; from pathlib import Path; sys.path.insert(0, str(Path(__file__).resolve().parent))
import core as K
from pathlib import Path
U, per, scored = set(), [], []
for k in range(K.NDRAW):
    dev, held = K.draw_docs(k)
    fd, fh = K.F.draw(k)
    assert [d["seq"] for d in dev] == fd and [d["seq"] for d in held] == fh, f"draw {k} mismatch"
    el, sc, _ = K.eligible(dev, held)
    per.append(set(el)); scored.append(len(sc)); U |= set(el)
inter = set.intersection(*per)
print("eligible per draw", [len(p) for p in per], "union", len(U), "in all five", len(inter), "scored per draw", scored)
Path(__file__).resolve().parent.joinpath("truth/words.txt").write_text("\n".join(sorted(U)) + "\n")
