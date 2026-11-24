"""One table for r_symmetry: row (and sub-test) by cell, power first and then the result.
Reads shape.json, then power.json and test.json if present. Writes table.md.
Run: .venv/bin/python -I experiments/r_symmetry/summarise.py
"""
import json, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from maps import CELLS, FAMILY  # noqa: E402

# kept in step with run.py (not imported: run.py loads the corpora and the tested modules at import)
ROWS = [("MC-MUK23-cup-vessel-fee", ["Q1", "Q2", "Q3"]), ("MC-MUK23-licence-pairing", ["T3"]),
        ("MC-KM-tablets-tokens", ["T1", "T3"]), ("MC-MUK23-emblem-organisation", ["EMB"]),
        ("MC-MUK19-stroked-jar-MET", ["SJ"]), ("MC-LAU10-other-language", ["RND"])]
OUT_OF_SCOPE = [
    ("FUN-kriger-hunt", "out of scope: kh_tests.planted() covers K4 only, so K1 and K3 have no plant and no cell can be gated"),
    ("KEY-pierson", "out of scope: its key is defined per Mahadevan sign, so no other list applies, and its R rests on "
                    "its own failed power gate, not on a list-dependent statistic"),
]
SHORT = {"other_edition": "other ed."}
STAT = dict(Q1="rho", Q2="rho", Q3="chi2", T1="G", T3="S", EMB="auc", SJ="ratio", RND="excess")


def load(name):
    p = HERE / name
    return json.load(open(p)) if p.exists() else None


def cell_text(sub, cell, sh, pw, te):
    c = (te or pw or sh)["cells"][sub][cell]
    st = c.get("status")
    if st in ("NT", "NOT_RUN") and "power" not in c:
        return "NOT RUN" if st == "NOT_RUN" else "NT"
    if st == "INVARIANT":
        return "INV"
    if "power" not in c:
        return "cand."
    s = f"pw {c['power']:.2f}"
    if st == "NT":
        return s + " NT"
    r = c.get("result")
    if r is None:
        return s
    p = r.get("p", r.get("p_enrich"))
    tag = "SURVIVE" if c.get("survive") else ("kill" if c.get("kill") else "no kill")
    return f"{s}; {STAT[sub]} {r[STAT[sub]]:.3g}" + (f" p {p:.3g}" if p is not None else "") + f" {tag}"


def main():
    sh, pw, te = load("shape.json"), load("power.json"), load("test.json")
    if sh is None:
        sys.exit("run `run.py shape` first")
    head = ["row", "test"] + [SHORT.get(c, c) + ("" if FAMILY[c] else " (no family)") for c in CELLS] + ["verdict"]
    lines = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
    for row, subs in ROWS:
        for i, sub in enumerate(subs):
            if pw and row in pw.get("rows_unchecked", []):
                cells = ["UNCHECKED (reproduce mismatch)"] * len(CELLS)
            else:
                cells = [cell_text(sub, c, sh, pw, te) for c in CELLS]
            v = ""
            if i == len(subs) - 1 and te:
                vv = te["verdicts"][row]; v = f"**{vv['verdict']}** ({vv['reason']})"
            lines.append("| " + " | ".join([row if i == 0 else "", sub] + cells + [v]) + " |")
    for row, why in OUT_OF_SCOPE:
        lines.append("| " + " | ".join([row, "-"] + ["-"] * len(CELLS) + [f"**out of scope** ({why.split(': ', 1)[1]})"]) + " |")
    notes = ["", "INV = test inputs identical to native (not testable, not a family); NT = not testable (by construction, "
             "a label mixing a frozen sign set with outside signs, or power < 0.8); pw = planted power; "
             "kill / no kill / SURVIVE = the row's own kill condition and the claim's survive bar."]
    if pw:
        rep = pw["reproduce"]
        notes.append("Reproduce first: " + "; ".join(f"{s} {r['statistic']} {r['reproduced']:.4g} "
                                                      f"({'ok' if r['match'] else 'MISMATCH'})" for s, r in rep.items()
                                                      if isinstance(r, dict) and "statistic" in r))
    txt = "\n".join(lines + notes) + "\n"
    open(HERE / "table.md", "w").write(txt)
    print(txt)


if __name__ == "__main__":
    main()
