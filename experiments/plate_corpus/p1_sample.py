"""P1: draw the pre-registered gate sample (docs/prereg/plate_corpus.md). No images are used.
Eligible: registers.csv rows with an M77 link, both dimensions (l_in, w_in), a plate/serial reference,
M77 object_type == seal, exactly one M77 text record for that text_no, and no '#' (broken passage).
MIC rows additionally need check_depth_vs_m77 == 'agree' and, where present, seq_sim_m77_icit >= 0.5.
Stratified by source with fixed quotas (single-line / multi-line), seed 20261117.
Output: sample.csv. Run: .venv/bin/python -I experiments/plate_corpus/p1_sample.py"""
import csv, os, sys, random
D = os.path.dirname(os.path.abspath(__file__)); REPO = os.path.dirname(os.path.dirname(D))
sys.path.insert(0, REPO)
from corpus.load import m77_texts, m77_lines
SEED = 20261117
QUOTA = {  # source: (single-line, multi-line)
    "Mackay1938_FEM": (6, 2), "Vats1940_EH": (5, 1), "Mackay1943_CE": (2, 2), "Marshall1931_MIC": (2, 0)}

def eligible():
    T = {}
    for t in m77_texts():
        T.setdefault(t["text_no"], []).append(t)
    L = {}
    for l in m77_lines():
        L.setdefault(l["text_no"], []).append(l)
    out = []
    for r in csv.DictReader(open(os.path.join(REPO, "experiments/old_registers/registers.csv"))):
        if not (r["m77_text_no"] and r["l_in"] and r["w_in"] and r["plate_ref"]):
            continue
        ts = T.get(int(r["m77_text_no"]), [])
        if len(ts) != 1 or ts[0]["object_type"] != "seal" or "#" in ts[0]["seq"]:
            continue
        if r["source"] == "Marshall1931_MIC":
            if r["check_depth_vs_m77"] != "agree":
                continue
            if r["seq_sim_m77_icit"] and float(r["seq_sim_m77_icit"]) < 0.5:
                continue
        t = ts[0]
        lines = sorted(L[t["text_no"]], key=lambda l: l["line"])
        r = dict(r, m77_seq=" ".join(t["seq"]), m77_n_lines=t["n_lines"],
                 m77_signs_per_line=",".join(str(len(l["signs"])) for l in lines),
                 m77_direction=lines[0]["direction"], m77_n_signs=sum(1 for s in t["seq"] if s != "|"))
        out.append(r)
    return out

def main():
    el = eligible()
    rng = random.Random(SEED)
    pick = []
    for src, (ns, nm) in QUOTA.items():
        rs = sorted([r for r in el if r["source"] == src], key=lambda r: str(r["object_no"]).zfill(20))
        single = [r for r in rs if int(r["m77_n_lines"]) == 1]
        multi = [r for r in rs if int(r["m77_n_lines"]) > 1]
        nm2 = min(nm, len(multi))
        pick += rng.sample(multi, nm2) + rng.sample(single, ns + (nm - nm2))
        print(src, "eligible", len(rs), "single", len(single), "multi", len(multi), "-> drew", ns + nm)
    cols = ["source", "object_no", "plate_ref", "field_no", "l_in", "w_in", "m77_text_no", "cisi",
            "m77_n_lines", "m77_signs_per_line", "m77_n_signs", "m77_direction", "m77_seq"]
    with open(os.path.join(D, "sample.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore"); w.writeheader(); w.writerows(pick)
    print("n", len(pick), "eligible total", len(el))

if __name__ == "__main__":
    main()
