"""C follow-up: treat every long text as ONE run (line breaks removed) and compare with nulls of the same total
length. Tests whether 'one stretched template' holds across lines or only line by line.
Usage: .venv/bin/python experiments/redteam_pnl/c2_joined.py
"""
import numpy as np
from c_long import *  # noqa
import c_long


def main():
    dev, ho, dev_g, lex, comps, G = fr.load_model()
    dev_short_lines = [lines_of(t)[0] for t in dev_g if "|" not in t["seq"] and "#" not in t["seq"] and 1 <= nsigns(t) <= 6]
    BG = Bigram(dev_short_lines)
    R = {}
    for split, texts in (("dev", dev), ("heldout", ho)):
        L = [t for t in texts if is_long(t) and "#" not in t["seq"]]
        shorts_pool = [lines_of(t)[0] for t in texts if "|" not in t["seq"] and "#" not in t["seq"] and 1 <= nsigns(t) <= 6]
        joined = [[s for s in t["seq"] if s != "|"] for t in L]
        real = np.mean([accept_lines(G, [j]) for j in joined])
        out = dict(n=len(L), real_joined_accept=float(real), lengths=sorted(len(j) for j in joined))
        for name in ("concat_exact", "bigram_short"):
            accs = []
            for d in range(300):
                a = []
                for j in joined:
                    sim = concat_fill(len(j), shorts_pool, False) if name == "concat_exact" else BG.sample(len(j), 1)[0]
                    a.append(accept_lines(G, [sim]))
                accs.append(np.mean(a))
            accs = np.array(accs)
            out[name] = dict(mean=float(accs.mean()), p_null_ge_real=float((1 + (accs >= real).sum()) / 301))
        # per-line: how many multi-line texts have every line accepted while the joined text is rejected
        ml = [t for t in L if "|" in t["seq"]]
        out["multiline_lines_ok_joined_fail"] = int(sum(G.accepts(t) and not accept_lines(G, [[s for s in t["seq"] if s != "|"]]) for t in ml))
        out["multiline_n"] = len(ml)
        R[split] = out
        print(split, out)
    dump(R, "c2_results.json")


if __name__ == "__main__":
    main()
