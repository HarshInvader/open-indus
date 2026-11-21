"""EXPLORATORY add-on (after scoring): the prereg'd transcription conditions T_icit_A2, T_m77_seal and
T_m77_seal_lumpall failed at 227 per side (Harappa has 220/200/191 after cleaning). Rerun them, and the
ICIT A0/A1 baselines, at 190 per side. Same code path as rt.py; writes to the same draws.jsonl."""
import sys
sys.path.insert(0, "experiments/redteam_uniformity")
import rt
base = rt.conditions
def extra():
    C = base()
    out = {}
    for k in ("I_icit_MD_H_227", "T_icit_A1", "T_icit_A2", "T_m77_seal", "T_m77_seal_lumpall"):
        att, b, a, bb, n, opg, pl = C[k]
        out[k.replace("_227", "") + "_190"] = ("4x", b, a, bb, 190, opg, pl)
    return out
rt.conditions = extra
if __name__ == "__main__":
    rt.run() if sys.argv[1:] == ["run"] else rt.report()
