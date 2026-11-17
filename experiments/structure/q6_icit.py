"""Q6. Replication on ICIT (Wells signs) as an independent transcription, with Dholavira-only texts as an
out-of-sample site. Direction/inventory/positional replications live in q1-q3 (ICIT sections); here:
segmentation + grammar on ICIT, and M77-trained models scored on bridged ICIT/Dholavira texts.
"""
import json
import random
from collections import Counter, defaultdict

import numpy as np

from common import (Bigram, distinct, icit_texts, is_clean, load_bridge, m77_split, m77_texts, runs, save_json, signs)
from q4_segment import (DPSeg, analyse_corpus, bigram_bits, site_stability, unigram_bits, word_model_bits)
from q5_grammar import perm_test, run_all

random.seed(5)
I = distinct(icit_texts())
for t in I:
    t["site_n"] = t["site"]
non_dh = [t for t in I if t["site"] != "Dholavira"]
dh = [t for t in I if t["site"] == "Dholavira"]
other_seqs = {" ".join(t["seq"]) for t in non_dh}
dh_only = [t for t in dh if " ".join(t["seq"]) not in other_seqs]
res = {"ICIT_distinct": len(I), "Dholavira_distinct": len(dh), "Dholavira_only": len(dh_only)}

# --- segmentation: train on non-Dholavira ICIT, test on Dholavira-only ---
tr = [r for t in non_dh for r in runs(t["seq"])]
te = [r for t in dh_only for r in runs(t["seq"])]
seg = analyse_corpus(tr, te, "ICIT nonDholavira -> Dholavira-only", iters=120)
seg.pop("_lex"); seg.pop("_boundaries")
res["segment_ICIT_to_Dholavira"] = seg
# ICIT site stability (seals only: SEAL:S square seals)
by = defaultdict(list)
for t in I:
    if t["type"].startswith("SEAL"):
        s = {"Mohenjo-daro": "Mohenjodaro"}.get(t["site"], t["site"])
        by[s] += runs(t["seq"])
res["segment_site_stability_ICIT_seals"] = {k: v for k, v in site_stability(by, reps=8).items()}

# --- grammar on ICIT with ICIT positional classes; perm test trained on non-Dholavira, tested on Dholavira-only ---
from q5_grammar import cls_map
cm = cls_map("ICIT")
texts = [t["seq"] for t in I]
clean = [signs(t["seq"]) for t in I if is_clean(t)]
dho_texts = [signs(t["seq"]) for t in dh_only if "#" not in t["seq"] and "|" not in t["seq"]]
gr = run_all("ICIT", texts, clean, "W740", cm, tr, dho_texts, None)
res["grammar_ICIT_perm_on_Dholavira_only"] = gr
# Dholavira-only templates under ICIT classes
from q5_grammar import template
tm = Counter(template(s, cm, "W740") for s in dho_texts)
res["Dholavira_only_templates"] = tm.most_common(12)

# --- cross-transcription: M77 model scored on bridged ICIT texts ---
br = load_bridge()
dev, ho = m77_split()
m77_runs = [r for t in dev for r in runs(t["seq"])]
def bridged(ts):
    out = []
    for t in ts:
        for r in runs(t["seq"]):
            if all(s in br for s in r):
                out.append([br[s] for s in r])
    return out
ho_runs = [r for t in ho for r in runs(t["seq"])]
b_all = bridged(non_dh); b_dh = bridged(dh_only)
cross = {}
for name, test in (("M77_heldout", ho_runs), ("ICIT_nonDholavira_bridged", b_all), ("Dholavira_only_bridged", b_dh)):
    sh = [random.sample(r, len(r)) for r in test]
    cross[name] = {"runs": len(test), "tokens": sum(map(len, test)),
                   "unigram_bits": unigram_bits(m77_runs, test), "bigram_bits": bigram_bits(m77_runs, test),
                   "bigram_bits_shuffled": bigram_bits(m77_runs, sh)}
# perm test of order with the M77 model on bridged Dholavira-only texts
cross["perm_test_M77_model_on_Dholavira_bridged"] = perm_test(m77_runs, [r for r in b_dh if len(r) >= 3])
res["cross_transcription_M77_model"] = cross
res["bridge_coverage_Dholavira_only_runs"] = (len(b_dh), sum(len(runs(t["seq"])) for t in dh_only))
save_json("q6_icit", res)
print(json.dumps({k: (v if k not in ("grammar_ICIT_perm_on_Dholavira_only", "segment_ICIT_to_Dholavira", "segment_site_stability_ICIT_seals") else "...") for k, v in res.items()}, indent=1, default=str))
for k in ("dp_chain_boundary_F1", "agreement_F1", "heldout_bits_per_sign", "mean_segment_len_DP"):
    print(k, seg[k])
ss = res["segment_site_stability_ICIT_seals"]; print({k: ss[k] for k in ("jaccard_MD_vs_HA", "null_mean", "null_sd", "z")})
for k in ("templates_top", "share_conforming_O*_K_C*", "conform_null_mean", "class_precedence", "sign_pair_order", "heldout_perm_test", "repeated_substrings_by_len", "null_bigram_repeated_by_len", "n_families_len_ge6", "n_families_len_ge6_not_near_duplicates(edit>2)"):
    print(k, gr[k])

# --- length-matched comparison: bigram gain over unigram (bits/sign) by run length ---
def gain_by_len(test):
    out = {}
    for L in (2, 3, 4):
        sub = [r for r in test if (len(r) == L if L < 4 else len(r) >= 4)]
        if len(sub) >= 10:
            out[L if L < 4 else "4+"] = {"runs": len(sub), "gain_bits": unigram_bits(m77_runs, sub) - bigram_bits(m77_runs, sub)}
    return out
res["bigram_gain_by_len"] = {"M77_heldout": gain_by_len(ho_runs), "ICIT_nonDholavira_bridged": gain_by_len(b_all),
                             "Dholavira_only_bridged": gain_by_len(b_dh)}
# square seals only for site stability
by2 = defaultdict(list)
for t in I:
    if t["type"] == "SEAL:S":
        by2[{"Mohenjo-daro": "Mohenjodaro"}.get(t["site"], t["site"])] += runs(t["seq"])
ss2 = site_stability(by2, reps=8)
res["segment_site_stability_ICIT_square_seals"] = ss2
save_json("q6_icit", res)
print(res["bigram_gain_by_len"]); print({k: ss2[k] for k in ("jaccard_MD_vs_HA", "null_mean", "null_sd", "z")})
