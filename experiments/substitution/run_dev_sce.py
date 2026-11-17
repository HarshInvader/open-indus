"""Dev system-consistent equations (SCE) from the saved dev L-tier run (indus_dev.L.sig):
q<0.05 and no spelling sign is X or a 1<->1 paradigm partner of X. Same for ICIT (native).
Writes results.json key dev_sce.
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import load_icit, load_m77, paradigm_partners, save_results, sce_filter, sce_system  # noqa: E402

res = json.load(open(HERE / "results.json"))
D, H = load_m77()
out = {}
for name, T, sig in (("m77_dev", D, res["indus_dev"]["L"]["sig"]), ("icit_all", load_icit(), res["icit_all"]["sig"])):
    part = paradigm_partners(T)
    s = sce_filter(sig, part)
    n_shared, n_in, shared = sce_system(s)
    out[name] = dict(n_sig=len(sig), n_sce=len(s), sce_shared=n_shared, sce_in_sys=n_in,
                     shared={k: sorted(v) for k, v in shared.items()}, sce=s)
    print(name, "sig", len(sig), "SCE", len(s), "shared signs", {k: sorted(v) for k, v in shared.items()})
    for r in s:
        print("   %s = %s k=%d q=%.3g" % (r["X"], r["Y"], r["k"], r["q"]))
out["sce"] = out["m77_dev"]["sce"]
save_results("dev_sce", out)
