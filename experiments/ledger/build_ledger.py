"""Project-wide test ledger and multiple-testing correction.

Run from the repo root (after v2_reruns.py):  .venv/bin/python -I experiments/ledger/build_ledger.py
Writes docs/test_ledger.csv and experiments/ledger/results.json.

Every row is one hypothesis test reported in an experiments/*/RESULTS.md (or recomputed here, area=ledger).
Numbers are transcribed from the RESULTS.md files; where only counts were reported, the p-value is computed
here from those counts (p_source = 'ledger-computed'). z-scores are converted one-sided.

Columns
  mode: confirmatory = hypothesis fixed before the data used to test it were seen (pre-registered, frozen
        prediction, held-out test of a dev-derived claim, or an independent re-test of an already-stated
        claim). Everything else (all-data tests, dev tests, screens) = exploratory.
  split: v1 leaky | v1 copies removed (red team dropped held-out texts with an edit-1 dev neighbour) | v2 |
         ICIT (same objects re-transcribed) | ICIT new sites (objects absent from M77) | none
  family / family_size: the correction family the test belongs to and how many tests the team said it ran in
        that family (listed or not). Unlisted tests are padded with p = 1 in the corrections (conservative).
Corrections (q < 0.05)
  q_global: BH over every confirmatory test project-wide (with padding).
  q_area:   BH within the area (team folder) over its confirmatory tests (with padding) = "per-area correction".
  q_hier:   two-level: Simes p per family -> BH across families -> within selected families BH at level
            0.05*R/F (Benjamini & Bogomolov 2014); reported as the within-family BH q scaled by F/R.
  q_all:    sensitivity: BH over ALL tests (confirmatory + exploratory + every unlisted screening test at p=1),
            about 13,900 tests.
"""
import csv, json, math, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
from scipy import stats

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
V2 = json.load(open(HERE / "v2_reruns.json"))

def zp(z): return float(stats.norm.sf(z))
def binom(k, n, p0): return float(stats.binomtest(k, n, p0, alternative="greater").pvalue)
def t7(z): return float(stats.t.sf(z, 7))

ROWS = []
def R(id, claim, area, file, stat, p, n, dist, split, mode, fam, famsize, repl, readme="", ci="", note="", psrc="reported"):
    ROWS.append(dict(id=id, claim=claim, area=area, file=file, statistic=stat,
                     p_value=("" if p is None else float(p)), p_source=("" if p is None else psrc), ci=ci, n=n,
                     distinct_text_unit=dist, split=split, mode=mode, family=fam, family_size=famsize,
                     replicated_independently=repl, readme_claim=readme, note=note))

C, E = "confirmatory", "exploratory"
Y, N_ = "yes", "no"
S = "experiments/structure/RESULTS.md"
# ------------------------------------------------------------------ structure
R("st_dir1", "L-R lines read as labelled are more probable under an R-L bigram (M77)", "structure", S, "134/150 oriented", 1e-24, "150 lines", Y, "none", E, "structure:direction", 8, Y, "7", note="77% of these lines are copies of R-L lines (redteam)")
R("st_dir2", "same, ICIT", "structure", S, "120/134", 2e-22, "134 lines", Y, "ICIT", C, "structure:direction", 8, N_, "7")
R("st_dir3", "same, jar removed from train and test (M77)", "structure", S, "86/102", 5e-13, "102 lines", Y, "none", E, "structure:direction", 8, N_, "7")
R("st_dir4", "jar M342 last rather than first in L-R lines (M77)", "structure", S, "33 last vs 3 first", 1e-7, "150 lines", Y, "none", E, "structure:direction", 8, N_, "7", note="copy-free lines: 5 vs 0, p=0.03 (ledger E)")
R("st_dir5", "same, ICIT", "structure", S, "36 vs 2", 3e-9, "134 lines", Y, "ICIT", C, "structure:direction", 8, N_, "7")
R("st_dir6", "line order of multi-line texts recoverable from grammar", "structure", S, "61/112", 0.20, "112 texts", Y, "none", E, "structure:direction", 8, N_)
R("st_inv1", "inventory ~400 signs, Chao2 565 incl. unseen", "structure", S, "Chao2 estimate", None, "10,005 tokens", Y, "none", E, "structure:inventory", 6, N_, "2", ci="508-658", note="estimate, not a test")
R("st_inv2", "frequency profile sits with Proto-Elamite/Sumerian, not Linear B/alphabet (120 signs for 90%)", "structure", S, "matched-size comparison", None, "10k tokens", Y, "none", E, "structure:inventory", 6, N_, "2", note="descriptive; no null or CI on the comparison")
R("st_allo1", "held-out perplexity validates allograph merges", "structure", S, "z=-3.6 vs random merges", 0.005, "9 merges", Y, "v1 leaky", C, "structure:allograph", 2, N_, note="but non-look-alike context-matched merges do as well (st_allo2): test refuted as validation")
R("st_allo2", "context-matched non-look-alike merges do worse than look-alike merges", "structure", S, "4.937 vs 4.947", 0.67, "", Y, "v1 leaky", C, "structure:allograph", 2, N_)
R("st_pos_screen", "signs have positional preferences (screen, 124 signs; 82 at q<0.05)", "structure", S, "82/124 at BH q<0.05", None, "124 signs", Y, "none", E, "structure:positional_screen", 124, Y, note="ICIT 85/133; family summary row")
R("st_pos_ho", "K=3 positional classes from dev hold on held-out (nearest-centroid agreement)", "structure", S, "70/80 vs 0.47", binom(70, 80, 0.47), "80 signs", Y, "v1 leaky", C, "structure:positional", 3, Y, psrc="ledger-computed", note="v2 re-run: 78.2% vs 41.7%, p<1e-4 (ledger C)")
R("st_pos_k10", "short-stroke numerals form a class (K=10)", "structure", S, "hypergeometric", 0.002, "", Y, "none", E, "structure:positional", 9, N_, note="best of 9 K, unstable ARI 0.24")
R("st_seg1", "DP and PMI segmentations agree beyond chance (held-out)", "structure", S, "F1 0.49 vs 0.35, z=25", zp(25), "held-out", Y, "v1 leaky", C, "structure:segmentation", 8, N_)
R("st_seg2", "same, Dholavira-only ICIT", "structure", S, "F1 0.66 vs 0.52, z=38", zp(38), "Dholavira", Y, "ICIT new sites", C, "structure:segmentation", 8, N_)
R("st_seg3", "segment lexicon beats sign unigram and shuffled lexicon on held-out", "structure", S, "6.19 vs 6.84/6.94 bits", None, "held-out", Y, "v1 leaky", C, "structure:segmentation", 8, N_, note="no p or CI")
R("st_seg4", "segment lexicon beats sign bigram on held-out", "structure", S, "6.19 vs 5.83 bits", None, "held-out", Y, "v1 leaky", C, "structure:segmentation", 8, N_, note="refuted")
R("st_seg5", "MD vs Harappa segment inventories differ (seals)", "structure", S, "z=+0.2", zp(-0.2), "", Y, "none", E, "structure:segmentation", 8, N_)
R("st_seg6", "MD vs Harappa segment inventories differ (all objects)", "structure", S, "z=-4.9", zp(4.9), "", Y, "none", E, "structure:segmentation", 8, N_, note="driven by Harappa tablets")
R("st_seg7", "MD vs Harappa segment inventories differ (ICIT seals)", "structure", S, "z=-1.9", zp(1.9), "", Y, "ICIT", E, "structure:segmentation", 8, N_)
R("st_ord_tmpl", "texts fit O* K C* template more than shuffles", "structure", S, "66.8% vs 24.8+-0.7%", zp(60), "1,758", Y, "none", E, "structure:order", 9, N_, "", note="circular (redteam): classes defined by the positions the shuffle destroys")
R("st_ord_pairs", "sign pairs keep one order", "structure", S, "0.75 vs 0.20", zp(55), "346 pairs", Y, "none", E, "structure:order", 9, N_)
R("st_ord_ho", "real order beats all permutations on held-out", "structure", S, "63% of 415 vs 5.5%", binom(261, 415, 0.055), "415 texts", Y, "v1 leaky", C, "structure:order", 9, Y, "1", psrc="ledger-computed", note="magnitude inflated by copies; v2 40% vs 5.7%")
R("st_ord_dhol1", "same, Dholavira-only, ICIT model", "structure", S, "46% of 61 vs 5.7%", binom(28, 61, 0.057), "61", Y, "ICIT new sites", C, "structure:order", 9, Y, "1", psrc="ledger-computed")
R("st_ord_dhol2", "same, M77 model on bridged Dholavira-only", "structure", S, "54% of 54 vs 8.2%", binom(29, 54, 0.082), "54", Y, "ICIT new sites", C, "structure:order", 9, Y, "1", psrc="ledger-computed")
R("st_ord_ms", "recurring multisets have one order", "structure", S, "1.03 vs 3.08 orders", None, "139 multisets", N_, "none", E, "structure:order", 9, N_, note="counts objects (copies); redteam restated on distinct texts: 8 of 1,505 multisets in two orders")
R("st_ord_rep", "3-5-sign formulae exceed bigram (length-5 repeats)", "structure", S, "81 vs 17+-4", zp(16), "", Y, "none", E, "structure:order", 9, N_)
R("st_dhol", "Dholavira pairings less predictable (regional lexicon)", "structure", S, "bigram gain 0.71 vs 1.19", None, "89 runs", Y, "ICIT new sites", E, "structure:dholavira", 1, N_, note="broken by redteam site-held-out control")
# ------------------------------------------------------------------ novel_methods
S = "experiments/novel_methods/RESULTS.md"
R("nm_e1_null", "near-duplicate density / variation position exceed bigram (12 metrics x 2 nulls)", "novel_methods", S, "all at bigram level", None, "1,685 dev", Y, "v1 leaky", E, "novel:exp1", 26, N_, note="family summary: refuted")
R("nm_e1_pairs", "single substitution pairs beyond bigram", "novel_methods", S, "smallest empirical p", 0.048, "", Y, "v1 leaky", E, "novel:exp1", 26, N_)
R("nm_e1_ho1", "dev substitution edges predict held-out swaps", "novel_methods", S, "91 vs 35.8+-5.2", 0.002, "293 swaps", Y, "v1 leaky", C, "novel:exp1", 26, N_)
R("nm_e1_ho2", "dev substitution classes predict held-out swaps", "novel_methods", S, "82 vs 50.2+-6.3", 0.002, "293 swaps", Y, "v1 leaky", C, "novel:exp1", 26, N_)
R("nm_e2_tmpl", "slot template beats bigram on held-out", "novel_methods", S, "5.40 vs 4.87 bits", None, "554", Y, "v1 leaky", C, "novel:exp2", 48, N_, note="refuted; descriptive comparisons")
R("nm_e2_share", "Indus more position-bound than bigram process", "novel_methods", S, "template share 0.57 vs 0.42", None, "", Y, "v1 leaky", E, "novel:exp2", 48, N_, note="single split, no CI")
R("nm_e3_encl", "enclosure shifts signs to final (dev, all families)", "novel_methods", S, "10 up / 2 down", 0.039, "12 pairs", Y, "v1 leaky", E, "novel:exp3_dev", 25, N_)
R("nm_e3_enclcos", "enclosed signs share contexts with bases", "novel_methods", S, "Fisher", 0.009, "12 pairs", Y, "v1 leaky", E, "novel:exp3_dev", 25, N_)
R("nm_e3_roofcos", "roof signs share contexts", "novel_methods", S, "Fisher", 0.034, "3 pairs", Y, "v1 leaky", E, "novel:exp3_dev", 25, N_)
R("nm_e3_roofoff", "roof is a consistent analogy offset (dev)", "novel_methods", S, "0.31 vs 0.13", 0.024, "3 pairs", Y, "v1 leaky", E, "novel:exp3_dev", 25, N_)
R("nm_e3_roofte", "roof offset (test)", "novel_methods", S, "", 0.05, "2-3 pairs", Y, "v1 leaky", C, "novel:exp3_dev", 25, N_)
R("nm_e3_jar", "jar+strokes M343-345 are allographs of M342 (context similarity)", "novel_methods", S, "cosine at null", 0.55, "5 pairs", Y, "v1 leaky", E, "novel:exp3_dev", 25, N_, note="refuted as allographs")
R("nm_e3_fish", "fish marks share contexts with M59", "novel_methods", S, "Fisher", 0.004, "3 pairs", Y, "v1 leaky", E, "novel:exp3_dev", 25, N_)
R("nm_e3_cup", "cup->jar shares contexts", "novel_methods", S, "", 0.50, "1 pair", Y, "v1 leaky", E, "novel:exp3_dev", 25, N_)
R("nm_t6_dev", "ticked/enclosed fish are text-final (dev)", "novel_methods", S, "0.595 (42) vs 0.163", 0.005, "42 tokens", Y, "v1 leaky", E, "novel:T6", 6, Y, "3")
R("nm_t6_devo", "other enclosed signs are text-final (dev)", "novel_methods", S, "0.213 vs 0.180", 0.30, "47 tokens", Y, "v1 leaky", E, "novel:T6", 6, N_)
R("nm_t6_te", "ticked fish are text-final (held-out + external)", "novel_methods", S, "0.526 (19) vs 0.153", 0.032, "19 tokens", Y, "v1 leaky", C, "novel:T6", 6, Y, "3", note="came out of a dev screen (forking path)")
R("nm_t6_teo", "other enclosed signs text-final (test)", "novel_methods", S, "0.308 vs 0.174", 0.13, "13 tokens", Y, "v1 leaky", C, "novel:T6", 6, N_)
# ------------------------------------------------------------------ redteam
S = "experiments/redteam/RESULTS.md"
R("rt_tf1", "ticked fish final (native ICIT, within-text shuffle)", "redteam", S, "40/73 vs 0.26", 1.1e-7, "73 tokens", Y, "ICIT", C, "redteam:ticked_fish", 10, Y, "3")
R("rt_tf2", "ticked fish final (frequency-matched null)", "redteam", S, "0.55 vs 0.19", 0.018, "73", Y, "ICIT", C, "redteam:ticked_fish", 10, Y, "3")
for i, (pair, st, p) in enumerate([("W220->W226", "18/31 vs 19/265", 5e-11), ("W231->W232", "3/8 vs 3/66", 0.015),
                                   ("W233->W234", "3/5 vs 8/141", 0.003), ("W235->W236", "7/18 vs 5/158", 2e-5),
                                   ("W240->W241", "9/11 vs 10/213", 1e-9)]):
    R(f"rt_tf_pair{i+1}", f"ticked form more often final than base, {pair}", "redteam", S, st, p, "", Y, "ICIT", C, "redteam:ticked_fish", 10, Y, "3")
R("rt_tf_noW226", "ticked fish final without W226", "redteam", S, "22/42", 1.2e-4, "42", Y, "ICIT", C, "redteam:ticked_fish", 10, Y, "3")
R("rt_tf_jar", "texts with ticked fish avoid the jar (closer slot)", "redteam", S, "13.7% vs 48.1%", 5e-4, "", Y, "ICIT", C, "redteam:ticked_fish", 10, N_, "3")
R("rt_tf_new", "ticked fish final at sites absent from M77", "redteam", S, "5/10", 0.07, "10 tokens", Y, "ICIT new sites", C, "redteam:ticked_fish", 10, N_, "3")
R("rt_6f1", "M109 followed by M59 (M77)", "redteam", S, "12/25 vs 0.06", 9e-9, "25 tokens", Y, "none", C, "redteam:sixfish", 5, Y, "5", note="10 families, 3 sites")
R("rt_6f2", "W016 followed by W220 (ICIT native)", "redteam", S, "13/33", 4e-9, "33 tokens", Y, "ICIT", C, "redteam:sixfish", 5, Y, "5", note="11 families incl. Nausharo")
R("rt_7f1", "7+fish depleted (all objects)", "redteam", S, "1/60 vs 0.096", 0.017, "60", Y, "none", C, "redteam:sixfish", 5, N_)
R("rt_7f2", "7+fish depleted (seals)", "redteam", S, "1/50", 0.07, "50", Y, "none", C, "redteam:sixfish", 5, N_)
R("rt_7f3", "7+fish depleted (ICIT seals)", "redteam", S, "1/45", 0.07, "45", Y, "ICIT", C, "redteam:sixfish", 5, N_)
for i, (cl, st, p, sp, rd) in enumerate([("M99 enriched on seals (families)", "392/364", 0.07, "none", ""),
                                         ("W002 enriched on seals (ICIT families)", "449/434", 0.23, "ICIT", ""),
                                         ("M99 depleted on copper", "2/9.3", 0.005, "none", "6"),
                                         ("W002 depleted on ICIT tablets", "39/52", 0.04, "ICIT", "6"),
                                         ("M342-M176 on rods", "6/0.34 families", 1e-6, "none", "6"),
                                         ("W740-W400 on rods (ICIT)", "4/0.5", 0.001, "ICIT", "6"),
                                         ("W740-W400 on ICIT tablets", "27/10.4", 1e-5, "ICIT", "6"),
                                         ("W407 on copper (ICIT)", "14/1.5", 1e-9, "ICIT", "6")]):
    R(f"rt_reg{i+1}", cl, "redteam", S, st, p, "families", Y, sp, C, "redteam:registers", 8, N_, rd, note="family-level, site x length strata")
R("rt_reg_cv", "object type predictable from text (grouped CV)", "redteam", S, "AUC 0.62-0.89", None, "", Y, "none", C, "redteam:registers", 8, Y, "6", note="no p")
R("rt_gulf", "Gulf round seals: order percentile below every Indus site (site held out)", "redteam", S, "0.53 vs 5th pct >=0.75", None, "12 texts", Y, "none", C, "redteam:gulf", 1, Y, "4", note="no exact p; ledger F gives p=5e-4")
for i, (cl, k, n, p0, rd) in enumerate([("order best of permutations, all held-out", 294, 520, 0.115, "1"),
                                        ("same, held-out without edit-1 dev neighbour", 126, 303, 0.034, "1"),
                                        ("same, jar/M176/M267/M391/M99 deleted", 125, 300, 0.086, "1"),
                                        ("same, 11 most positional signs deleted", 124, 295, 0.111, "1"),
                                        ("same, texts with none of the 5 fixed signs", 29, 87, 0.084, "1"),
                                        ("same, interior only", 134, 268, 0.148, "1"),
                                        ("position-only model beats permutations", 14, 303, 0.034, "")]):
    R(f"rt_ord{i+1}", cl, "redteam", S, f"{k}/{n} vs {p0}", binom(k, n, p0), str(n), Y,
      "v1 leaky" if i == 0 else "v1 copies removed", C, "redteam:order", 7, Y if rd else N_, rd, psrc="ledger-computed")
R("rt_cu", "copper legend copies share one picture (legend level)", "redteam", S, "0.90 vs 0.39", 2e-4, "18 legends", Y, "none", C, "redteam:copper", 1, Y, "8")
R("rt_dhol", "Dholavira less predictable than other peripheral sites (site-held-out)", "redteam", S, "0.84 vs Kalibangan 0.83", None, "48", Y, "ICIT new sites", C, "redteam:dholavira", 1, Y, "R-h", note="refutes st_dhol")
R("rt_dir1", "L-R copy-free lines oriented as labelled (M77)", "redteam", S, "31/34", 4e-7, "34", Y, "none", C, "redteam:direction", 4, Y, "7")
R("rt_dir2", "same, top-20 positional signs + jar removed", "redteam", S, "25/33", 0.002, "33", Y, "none", C, "redteam:direction", 4, Y, "7")
R("rt_dir3", "same, ICIT", "redteam", S, "18/23", 0.005, "23", Y, "ICIT", C, "redteam:direction", 4, N_, "7")
R("rt_dir4", "same, ICIT, positional removed", "redteam", S, "15/22", 0.07, "22", Y, "ICIT", C, "redteam:direction", 4, N_, "7")
# ------------------------------------------------------------------ revalidation (v2)
S = "experiments/revalidation/RESULTS.md"
R("rv_order", "order beats permutations (v2 held-out)", "revalidation", S, "129/321 vs 0.057", binom(129, 321, 0.0568), "321 runs", Y, "v2", C, "revalidation", 8, Y, "1", psrc="ledger-computed")
R("rv_tf", "ticked fish final (v2 held-out)", "revalidation", S, "11/19 vs null 0.19", 0.004, "19 tokens", Y, "v2", C, "revalidation", 8, Y, "3")
R("rv_6f", "M109 followed by M59 (v2 held-out)", "revalidation", S, "7/10 vs 0.031", 2.8e-9, "10 tokens", Y, "v2", C, "revalidation", 8, Y, "5")
for k, v in V2["G_registers_exact"].items():
    R(f"rv_reg_{k.split()[0]}", f"text predicts object type: {k} (v2 held-out AUC)", "revalidation", S, f"AUC {v['auc']}", v["p"], f"{v['n']} of 556", Y, "v2", C, "revalidation", 8, Y, "6", psrc="ledger-computed (Mann-Whitney from AUC)")
# ------------------------------------------------------------------ context
S = "experiments/context/RESULTS.md"
R("cx_q1a", "whole text predicts seal animal (M77 CV, balanced acc.)", "context", S, "0.192 vs 0.123", 0.005, "1,149", Y, "none", E, "context:Q1", 40, N_, "R-e")
R("cx_q1b", "same, macro AUC", "context", S, "0.615 vs 0.493", 0.005, "1,149", Y, "none", E, "context:Q1", 40, N_, "R-e")
R("cx_q1c", "same, length + classes only", "context", S, "0.219 vs 0.124", 0.005, "1,149", Y, "none", E, "context:Q1", 40, N_, "R-e")
R("cx_q1d", "unicorn vs other AUC (M77)", "context", S, "0.516", 0.39, "1,149", Y, "none", E, "context:Q1", 40, N_, "R-e")
R("cx_q1e", "seal animal from text, held-out", "context", S, "bal. acc 0.240 vs 0.124", 0.035, "275", Y, "v1 leaky", C, "context:Q1", 40, N_, "R-e", note="v2 re-run: 0.194 vs 0.145, p=0.093 (ledger D)")
R("cx_q1f", "unicorn AUC held-out", "context", S, "0.517", 0.38, "275", Y, "v1 leaky", C, "context:Q1", 40, N_, "R-e")
R("cx_q1g", "seal animal from text, ICIT CV", "context", S, "0.177 vs 0.134", 0.045, "1,409", Y, "ICIT", E, "context:Q1", 40, N_, "R-e")
R("cx_q1h", "unicorn AUC ICIT", "context", S, "0.523", 0.18, "1,409", Y, "ICIT", E, "context:Q1", 40, N_, "R-e")
R("cx_q1i", "unicorn AUC cross-site (train MD+Harappa)", "context", S, "0.505", 0.44, "250", Y, "ICIT new sites", C, "context:Q1", 40, N_, "R-e")
R("cx_q1j", "goat-antelope legends short (ICIT)", "context", S, "2.31 vs ~4.5", 0.003, "13", Y, "ICIT", E, "context:Q1", 40, N_, note="q=0.024 within 8")
R("cx_q1k", "goat-antelope legends short (M77)", "context", S, "3.60", 0.062, "10", Y, "none", E, "context:Q1", 40, N_)
R("cx_q1l", "zebu legends short (ICIT)", "context", S, "3.96", 0.045, "52", Y, "ICIT", E, "context:Q1", 40, N_)
R("cx_q1m", "same-emblem texts share signs (16 tests; best rhino ICIT)", "context", S, "1.45x", 0.054, "", Y, "none", E, "context:Q1", 40, N_, "R-e", note="best of 16, q=0.43")
R("cx_q2_screen", "register enrichment screen (unigrams+bigrams x types; 25/22/33 survivors)", "context", S, "BH q<0.05", None, "11,232 tests", Y, "none", E, "context:Q2screen", 11232, N_, "6", note="family summary row")
for i, (r) in enumerate(json.load(open(ROOT / "experiments/context/results.json"))["q2_registers"]["icit_replication"]):
    R(f"cx_q2rep{i+1}", f"M77 register marker replicates on ICIT: {r['m_feat']}->{r['w_feat']} on {r['type']}", "context", S,
      f"{r['icit_obs']} vs {r['icit_exp']:.1f}", r["p_one"], "distinct texts", Y, "ICIT", C, "context:Q2replication", 17, N_, "6")
R("cx_q2_clf", "object type predictable from text (15 classifiers, all p<=0.01)", "context", S, "AUC 0.66-0.91", 0.01, "", Y, "none", E, "context:Q2classifier", 15, Y, "6", note="permutation floor, 100 perms")
R("cx_cu1", "copper tablets with identical text share the picture", "context", S, "0.62 vs 0.06", 2e-4, "272 pairs", N_, "none", E, "context:Q2b", 4, Y, "8", note="pairs, 82% from 3 legends")
R("cx_cu2", "copper: legends sharing signs share picture (nearest neighbour)", "context", S, "0.03 vs 0.06", 0.81, "20 families", Y, "none", E, "context:Q2b", 4, N_)
R("cx_cu3", "copper: bigram-sharing legends share picture", "context", S, "0.11 vs 0.05", 0.078, "20 families", Y, "none", E, "context:Q2b", 4, N_)
R("cx_q3a", "sealing texts travel more than seal texts", "context", S, "13 vs 10.0", 0.17, "66", Y, "ICIT", E, "context:Q3", 835, N_)
R("cx_q3b", "jar texts recur at more sites (M77)", "context", S, "55 vs 31.0, q=5e-5", None, "", Y, "none", E, "context:Q3", 835, N_, note="screen survivor, q only")
R("cx_q3c", "jar texts recur at more sites (ICIT)", "context", S, "48 vs 27.4, q=0.0013", None, "", Y, "ICIT", E, "context:Q3", 835, N_, note="screen survivor, q only")
for i, (cl, st, p, rd) in enumerate([("all foreign texts anomalous under native bigram", "+1.35 bits", 1e-4, "4"),
                                     ("foreign round/cylinder seals anomalous", "+2.17 [1.63, 2.70]", 1e-4, "4"),
                                     ("same, pseudo-script removed", "+2.44", 1e-4, "4"),
                                     ("foreign round vs home round seals", "+2.09", 1e-4, "4"),
                                     ("foreign square seals anomalous", "+0.44", 0.19, "4"),
                                     ("foreign other objects anomalous", "+0.28", 0.31, ""),
                                     ("unknown-provenance texts anomalous", "+0.56", 0.018, ""),
                                     ("home round vs home square", "+0.17", 0.011, ""),
                                     ("Dholavira anomalous", "+0.52", 1e-4, ""),
                                     ("M77 West Asian finds anomalous", "+1.96", 1e-4, "4")]):
    R(f"cx_q4_{i+1}", cl, "context", S, st, p, "", Y, "none", E, "context:Q4", 15, Y if rd == "4" and i in (1, 3) else N_, rd,
      note="splices across breaks; native CV leaks copies (redteam)" if i < 4 else "")
R("cx_q5a", "feature x site chronological trends (55)", "context", S, "best rho +0.13", 0.008, "", Y, "none", E, "context:Q5", 161, N_, "R-i", note="q=0.15")
R("cx_q5b", "early vs late classifier, MD", "context", S, "AUC 0.569", 0.02, "750", Y, "none", E, "context:Q5", 161, N_, "R-i")
R("cx_q5c", "early vs late classifier, Kalibangan", "context", S, "AUC 0.650", 0.03, "97", Y, "none", E, "context:Q5", 161, N_, "R-i")
R("cx_q5d", "sign innovation/obsolescence (102 signs)", "context", S, "best W690", 0.002, "", Y, "none", E, "context:Q5", 161, N_, "R-i", note="q=0.20")
R("cx_q6a", "short-stroke 8 is a trough (not binary series)", "context", S, "E=-0.84", None, "", Y, "none", E, "context:Q6", 6, N_, "R-g", ci="[-1.87, 0.06]")
R("cx_q6b", "tall-stroke 4 is a trough", "context", S, "E=-1.68", None, "", Y, "none", E, "context:Q6", 6, N_, "R-g", ci="[-2.41, -1.15]")
R("cx_q6c", "short-stroke 7 is a spike", "context", S, "E=+1.43", None, "", Y, "none", E, "context:Q6", 6, N_, "R-g", ci="[1.03, 2.03]")
R("cx_q6d", "numeral pair ratios are powers of two above chance", "context", S, "0.19 vs 0.22", None, "140", Y, "none", E, "context:Q6", 6, N_, "R-g")
# ------------------------------------------------------------------ language
S = "experiments/language/RESULTS.md"
R("lg_a1a", "Yajnadevam key beats its own permutations (generous)", "language", S, "z=1.0", 0.15, "2,962 runs", Y, "none", C, "language:A1", 4, Y, "R-a")
R("lg_a1b", "same, strict matching", "language", S, "z=1.45", 0.040, "2,962 runs", Y, "none", C, "language:A1", 4, N_, "R-a")
R("lg_p1a", "6+fish enriched (frozen prediction)", "language", S, "12/28 vs 13%", 1e-4, "28", Y, "none", C, "language:A2", 22, Y, "5")
R("lg_p1a_ho", "6+fish enriched, held-out", "language", S, "4/7", 0.002, "7", Y, "v1 leaky", C, "language:A2", 22, Y, "5")
R("lg_p1b", "7+fish enriched (frozen prediction)", "language", S, "1/60", 0.99, "60", Y, "none", C, "language:A2", 22, N_, "5", note="prediction failed; p for enrichment approximated as 0.99")
R("lg_p1b_d", "7+fish depleted (post hoc direction)", "language", S, "1/60", 0.0025, "60", Y, "none", E, "language:A2", 22, N_, note="redteam: base-rate/object effect")
R("lg_p1c", "3+fish enriched", "language", S, "16/93 vs 8.6%", 0.005, "93", Y, "none", C, "language:A2", 22, N_)
R("lg_p1c_ho", "3+fish enriched, held-out", "language", S, "2/22", binom(2, 22, 0.086), "22", Y, "v1 leaky", C, "language:A2", 22, N_, psrc="ledger-computed")
R("lg_p1j1", "P1 joint, fish family", "language", S, "+0.04", 0.18, "", Y, "none", C, "language:A2", 22, N_)
R("lg_p1j2", "P1 joint, plain fish", "language", S, "+0.11", 0.002, "", Y, "none", C, "language:A2", 22, N_, note="carried by 6 alone")
R("lg_p2", "marked fish share M59's slot (10 signs, percentiles)", "language", S, "88-100th pct", None, "10 signs", Y, "none", C, "language:A2", 22, N_, note="no p per sign")
R("lg_p3a", "plain and marked fish adjacent more than chance (dev)", "language", S, "48 vs 31.1", 0.002, "", Y, "v1 leaky", E, "language:A2", 22, N_)
R("lg_p3b", "same, held-out", "language", S, "6 vs 6.2", None, "", Y, "v1 leaky", C, "language:A2", 22, N_, note="null")
R("lg_p4", "numerals precede marked fish less often than plain fish", "language", S, "2.9% vs 13%", 1e-4, "982", Y, "none", C, "language:A2", 22, Y, "9")
R("lg_p4_ho", "same, held-out", "language", S, "1.9% vs 12.1%", 0.003, "", Y, "v1 leaky", C, "language:A2", 22, Y, "9", note="v2: 4.7% vs 14.9%, p=0.012 (ledger B)")
R("lg_p5a", "jar M342 is final", "language", S, "72.6% vs 22.6%", None, "", Y, "none", C, "language:A2", 22, N_, note="no p; not diagnostic")
R("lg_p5b", "jar is left-diverse", "language", S, "94th pct", 0.06, "", Y, "none", C, "language:A2", 22, N_)
R("lg_b3", "typology classifier identifies language on real controls", "language", S, "Latin -> MUN 8/10", None, "", N_, "none", C, "language:B3", 14, N_, "R-d", note="external validity fails")
# ------------------------------------------------------------------ phonetic_grid
S = "experiments/phonetic_grid/RESULTS.md"
for i, (cl, z, sp, md) in enumerate([("end alternation vs block null (dev)", 5.1, "v1 leaky", E), ("start alternation vs block null (dev)", 6.6, "v1 leaky", E),
                                     ("end alternation (held-out)", 4.7, "v1 leaky", C), ("start alternation (held-out)", 7.0, "v1 leaky", C),
                                     ("end alternation (ICIT)", 4.9, "ICIT", C), ("start alternation (ICIT)", 5.0, "ICIT", C),
                                     ("end modularity vs block (dev)", -0.04, "v1 leaky", E), ("start modularity (dev)", 0.1, "v1 leaky", E),
                                     ("end modularity (held-out)", 0.8, "v1 leaky", C), ("start modularity (held-out)", 0.5, "v1 leaky", C),
                                     ("end modularity (ICIT)", -0.5, "ICIT", C), ("start modularity (ICIT)", 3.1, "ICIT", C),
                                     ("end alternation vs bigram (dev)", -0.7, "v1 leaky", E), ("start alternation vs bigram (dev)", 5.6, "v1 leaky", E),
                                     ("end vs bigram (held-out)", -0.8, "v1 leaky", C), ("start vs bigram (held-out)", 2.8, "v1 leaky", C),
                                     ("end vs bigram (ICIT)", -1.3, "ICIT", C), ("start vs bigram (ICIT)", 5.9, "ICIT", C)]):
    R(f"pg_alt{i+1}", cl, "phonetic_grid", S, f"z={z}", zp(z), "", Y, sp, md, "grid:alternation", 48, N_, "R-c" if "modularity" in cl else "")
R("pg_st1", "Harappa vs MD grid partitions agree", "phonetic_grid", S, "ARI 0.058 vs 0.033", 0.35, "", Y, "none", E, "grid:stability", 8, N_, "R-c")
R("pg_st2", "dev grid replicates on held-out", "phonetic_grid", S, "ARI 0.138", 0.16, "", Y, "v1 leaky", C, "grid:stability", 8, N_, "R-c")
R("pg_m99", "M99 never dropped (held-out)", "phonetic_grid", S, "0/115 vs 5.5%", 0.002, "115", Y, "v1 leaky", C, "grid:connectives", 4, N_, "9")
R("pg_m176", "M176 optional (droppable) above peers (held-out)", "phonetic_grid", S, "9/39 = 23% vs 5.5%", binom(9, 39, 0.055), "39", Y, "v1 leaky", C, "grid:connectives", 4, N_, "9", psrc="ledger-computed")
R("pg_m176d", "M176 optional (dev)", "phonetic_grid", S, "z=+4.6", zp(4.6), "", Y, "v1 leaky", E, "grid:connectives", 4, N_, "9")
# ------------------------------------------------------------------ logograms
S = "experiments/logograms/RESULTS.md"
R("lo_t3", "each copper legend takes one sign face", "logograms", S, "8/8 legends vs null 0.9", 1e-4, "8 legends", Y, "none", E, "logograms:L2", 7, N_, "8", note="batch copies; ICIT overlaps M77 objects")
R("lo_t3m", "same, M77 only", "logograms", S, "4/4", 3e-4, "4", Y, "none", E, "logograms:L2", 7, N_, "8")
R("lo_t3i", "same, ICIT only", "logograms", S, "7/7", 1e-4, "7", Y, "ICIT", E, "logograms:L2", 7, N_, "8")
R("lo_t4", "sign-face legends more often pictured", "logograms", S, "5/8 vs 15/21", 0.82, "", Y, "none", E, "logograms:L2", 7, N_)
R("lo_t6", "substituting signs are 'horned head'", "logograms", S, "3/3 vs 0.79", 0.49, "", Y, "none", E, "logograms:L2", 7, N_)
R("lo_l3", "pictorial signs echo the seal picture (17 pre-registered; min p shown)", "logograms", S, "all q=1", 0.26, "1,538 / 2,124", Y, "none", C, "logograms:L3prereg", 17, N_, "R-f", note="16 unlisted tests p>=0.26")
R("lo_l3x", "exploratory sign x picture scan (835; best M242)", "logograms", S, "q=0.21", None, "", Y, "none", E, "logograms:L3explore", 835, N_, "R-f")
R("lo_l4a", "picture/sign minimal pairs recur (ICIT)", "logograms", S, "9 vs 10.4", 0.85, "114", Y, "ICIT", E, "logograms:L4", 2, N_)
R("lo_l4b", "same, M77", "logograms", S, "10 vs 11.1", 0.83, "109", Y, "none", E, "logograms:L4", 2, N_)
R("lo_l5a", "candidate logograms text-initial (M77)", "logograms", S, "4/7 vs 1.23", 0.02, "7", Y, "none", E, "logograms:L5", 2, N_)
R("lo_l5b", "same, ICIT", "logograms", S, "3/4 vs 1.10", 0.05, "4", Y, "ICIT", E, "logograms:L5", 2, N_)
# ------------------------------------------------------------------ functional_reading
S = "experiments/functional_reading/RESULTS.md"
R("fr_cov_ho", "role grammar parses held-out texts above within-text shuffles", "functional_reading", S, "0.760 vs 0.334, z=27.5", zp(27.5), "525", Y, "v1 leaky", C, "fr:coverage", 11, Y, "9", note="v2 re-run: 0.762 vs 0.438, z=20.3 (ledger A)")
R("fr_cov_new", "same, ICIT sites absent from M77", "functional_reading", S, "0.772 vs 0.371, z=13.8", zp(13.8), "189", Y, "ICIT new sites", C, "fr:coverage", 11, Y, "9")
R("fr_cov_dhol", "same, Dholavira", "functional_reading", S, "0.775 vs 0.382, z=9.0", zp(9.0), "80", Y, "ICIT new sites", C, "fr:coverage", 11, Y, "9")
R("fr_cov_pot", "same, pottery", "functional_reading", S, "z=1.8", zp(1.8), "17", Y, "v1 leaky", C, "fr:coverage", 11, N_)
R("fr_lexnull", "evidence-based lexicon beats permuted role sets", "functional_reading", S, "0.760 vs 0.510+-0.131", 0.01, "525", Y, "v1 leaky", C, "fr:coverage", 11, N_, "9", note="permutation floor; v2 p=0.013 (ledger A)")
R("fr_obj_roles", "abstract roles alone predict object type", "functional_reading", S, "AUC 0.672 vs null 95th 0.577", 0.05, "551", Y, "v1 leaky", C, "fr:objecttype", 15, N_, "9", psrc="upper bound (obs > null 95th pct)")
R("fr_obj_bag", "parse predicts object type better than a sign bag", "functional_reading", S, "delta -0.073 [-0.114,-0.037]", None, "551", Y, "v1 leaky", C, "fr:objecttype", 15, N_, note="refuted")
R("fr_mask", "grammar adds to bigram on masked signs", "functional_reading", S, "MRR 0.476 vs 0.506", None, "2,197", Y, "v1 leaky", C, "fr:masked", 8, N_, note="refuted")
for i, (cl, p, sp) in enumerate([("Gulf round seals fail to parse more (parse failure)", 0.009, "ICIT"), ("Gulf round seals: grammar bits", 0.002, "ICIT"),
                                 ("Gulf round seals: bigram bits", 0.0005, "ICIT"), ("all foreign: parse failure", 0.11, "ICIT"),
                                 ("all foreign: grammar bits", 0.004, "ICIT"), ("all foreign: bigram bits", 0.001, "ICIT"),
                                 ("M77 West Asian: parse failure", 0.24, "v1 leaky"), ("M77 West Asian: grammar bits", 0.19, "v1 leaky"),
                                 ("M77 West Asian: bigram bits", 0.03, "v1 leaky")]):
    R(f"fr_for{i+1}", cl, "functional_reading", S, "AUC", p, "", Y, sp, C, "fr:foreign", 15, Y if i in (0, 1, 2) else N_, "4" if i < 3 else "")
# ------------------------------------------------------------------ iconography (v2)
S = "experiments/iconography/RESULTS.md"
R("ic_bl1", "copper substitution signs resemble the pictures they replace (blind)", "iconography", S, "5/24 vs 3.27", 0.22, "24 ratings", N_, "none", C, "icono:blind", 2, N_)
R("ic_bl2", "same, top-2 choices", "iconography", S, "8 vs 6.55", 0.32, "24", N_, "none", C, "icono:blind", 2, N_)
for i, (cl, p, sp, md) in enumerate([("referent class predicts lexicon role (incl. numerals)", 1e-4, "none", E),
                                     ("referent class predicts positional class", 0.20, "none", E),
                                     ("closers are vessels", 0.42, "none", E), ("openers are abstract", 0.14, "none", E),
                                     ("referent predicts role excl. numerals", 0.39, "none", E),
                                     ("frequency differs by class (dev)", 0.31, "v2", E), ("frequency differs by class (held-out)", 0.23, "v2", C),
                                     ("promiscuity differs by class (dev)", 0.08, "v2", E), ("promiscuity differs by class (held-out)", 0.26, "v2", C),
                                     ("pictorial signs more promiscuous (dev)", 0.61, "v2", E), ("pictorial signs more promiscuous (held-out)", 0.45, "v2", C)]):
    R(f"ic_sem{i+1}", cl, "iconography", S, "", p, "120 signs", Y, sp, md, "icono:semantics", 36, N_, note="circular (numerals)" if i == 0 else "")
# ------------------------------------------------------------------ administration (v2, pre-registered)
S = "experiments/administration/RESULTS.md"
for pid, cl, st, p, sp, fam, fs in [("P1", "line 2 / side 2 attested elsewhere", "2/28 vs 0.118", 0.88, "v2", "admin:prereg", 14),
                                    ("P2", "line 2 attested at same site", "1/2 vs 1.67", 0.99, "v2", "admin:prereg", 14),
                                    ("P3", "one-line texts are compounds of two texts", "5/279 vs 0.024", 0.68, "v2", "admin:prereg", 14),
                                    ("P4", "compound halves at same site", "2/5 vs 2.16", 0.71, "v2", "admin:prereg", 14),
                                    ("P5", "M336-M89 enriched on Harappa AB (ICIT)", "7 vs 4.8", 0.53, "ICIT", "admin:prereg", 14),
                                    ("P6", "final M211 enriched on Harappa F", "", 0.50, "v2", "admin:prereg", 14),
                                    ("P7", "any feature x area (best of 12, BH)", "best M176 on MD SD", 0.011, "v2", "admin:P7", 12),
                                    ("P8", "copies of a text share a locus", "1 vs 2.43", 0.96, "v2", "admin:prereg", 14),
                                    ("P9", "M267 vs M293 citadel contrast (min of 4)", "", 0.40, "v2", "admin:P9", 4),
                                    ("P10", "ICIT feature x area (best of 26)", "", 0.05, "ICIT", "admin:P10", 26),
                                    ("P11", "side-2 N fixed per identity", "2/7 vs 2.16", 0.70, "v2", "admin:prereg", 14),
                                    ("P12", "short values capped by tall (bundling)", "+0.54", 0.85, "v2", "admin:prereg", 14),
                                    ("P13", "sign predicts Lothal back type (best of 12)", "W740", 0.008, "none", "admin:P13", 12),
                                    ("P14", "same text -> same back (elephant seal excluded)", "5 vs 6.0", 0.70, "none", "admin:prereg", 14)]:
    R(f"ad_{pid}", cl, "administration", S, st, p, "distinct", Y, sp, C, fam, fs, N_)
R("ad_d1", "one-line compounds above bigram (dev)", "administration", S, "0.052 vs 0.025", 0.005, "1,009", Y, "v2", E, "admin:dev", 26, N_, note="vanished on held-out (P3)")
R("ad_d2", "repeated seal texts share MD locus (naive dev)", "administration", S, "47 vs 29", 0.003, "", Y, "v2", E, "admin:dev", 26, N_, note="artefact of double-counted sides")
# ------------------------------------------------------------------ decipherability (real Indus run)
S = "experiments/decipherability/RESULTS.md"
for lang, z in [("Tamil", 0.76), ("Malayalam", 1.05), ("Sanskrit", 0.25), ("Sumerian", 0.54), ("Latin", 0.4), ("Finnish/Estonian", 2.3)]:
    R(f"dc_{lang[:4].lower()}", f"{lang} model fits real Indus better than it fits wrong-language planted corpora (max z)", "decipherability", S,
      f"calibrated z={z}", t7(z), "10,005 tokens", Y, "none", C, "decipher:indus", 22, N_, "",
      psrc="ledger-computed (t, 7 df)", note="max over 2 logogram shares")
# ------------------------------------------------------------------ internal_phonetics (v2, pre-registered)
S = "experiments/internal_phonetics/RESULTS.md"
R("ip_dev_screen", "dev screens: T1 143 host tests, T2 69 pairs, T3 76 triples, T4 6 classes", "internal_phonetics", S, "BH within family; 2 T2 pairs q<0.05", None, "1,675 dev", Y, "v2", E, "iphon:dev", 294, N_, note="family summary row")
R("ip_h1", "phonetic complements: >=3 host-specific optional signs (held-out, 14 tested)", "internal_phonetics", S, "0/14 significant", None, "564", Y, "v2", C, "iphon:prereg", 6, N_, note="count rule, no single p; power 40%")
R("ip_h2a", "M65|M72 alternate across frames (held-out)", "internal_phonetics", S, "k=1", 0.225, "31 frames", Y, "v2", C, "iphon:prereg", 6, N_)
R("ip_h2b", "M99|M402 alternate across frames (held-out)", "internal_phonetics", S, "k=0", 1.0, "31 frames", Y, "v2", C, "iphon:prereg", 6, N_)
R("ip_h3", "M12 = M342 M176 ligature recurs (held-out)", "internal_phonetics", S, "0 events", 1.0, "46 events", Y, "v2", C, "iphon:prereg", 6, N_)
R("ip_h4", "fish internal marks dropped more than chance (held-out)", "internal_phonetics", S, "2 vs 0.25", 0.026, "", Y, "v2", C, "iphon:prereg", 6, N_, note="prereg required dev to pass too; dev p=0.21")
# ------------------------------------------------------------------ typology (v2, pre-registered)
S = "experiments/typology/RESULTS.md"
for tid, cl, st, ok in [("H1a", "core signs not fixed-position", "H_rel 0.96 [0.91,1.01]", "pass"),
                        ("H1b", "cores freer than Ur III / Linear B names", "lower 0.91 > 0.71", "pass"),
                        ("H2", "cores are whole-word signs (standalone)", "len-1 0.34, standalone 0.80 [0.73,0.85]", "pass"),
                        ("H3", "core signs have fixed partners", "partner_rel upper 0.933 vs 0.93", "fail"),
                        ("H4", "productivity between Linear B and Ur III", "[0.27,0.29]", "pass")]:
    R(f"ty_{tid}", cl, "typology", S, st, None, "423 cores", Y, "v2", C, "typology:Q1", 5, N_, ci=ok, note="interval criterion, no p; registered verdict inconclusive")
for gid, cl, p in [("G1", "Gulf residue uses a smaller sign set", 0.81), ("G2", "Gulf texts repeat a sign", 0.010),
                   ("G3", "Gulf adjacent reduplication", 0.004), ("G4", "Gulf texts share signs", 0.94)]:
    R(f"ty_{gid}", cl, "typology", S, "", p, "20 residues", Y, "none", C, "typology:Q2", 20, N_,
      note="reduplication = two texts doubling the jar W740" if gid in ("G2", "G3") else "")
# ------------------------------------------------------------------ ledger re-runs (v2, own code)
S = "experiments/ledger/RESULTS.md"
A = V2["A_functional_reading"]
R("lr_fr_cov", "role grammar parses v2 held-out above shuffles", "ledger", S, f"{A['v2']['coverage']} vs {A['v2']['shuffled_mean']}, z={A['v2']['z']}", A["v2"]["p_normal"], str(A["v2"]["n"]), Y, "v2", C, "ledger:v2", 8, Y, "9")
R("lr_fr_lex", "lexicon beats permuted role sets (v2)", "ledger", S, f"{A['v2']['coverage']} vs {A['v2']['lexicon_null_mean']}+-{A['v2']['lexicon_null_sd']}", A["v2"]["lexicon_null_p"], str(A["v2"]["n"]), Y, "v2", C, "ledger:v2", 8, N_, "9")
R("lr_fr_dhol", "role grammar parses Dholavira (v2 lexicon)", "ledger", S, f"{A['dholavira_v2lex']['coverage']} vs {A['dholavira_v2lex']['shuffled_mean']}", A["dholavira_v2lex"]["p_normal"], str(A["dholavira_v2lex"]["n"]), Y, "ICIT new sites", C, "ledger:v2", 8, Y, "9")
B = V2["B_language_P4"]["v2_heldout"]
R("lr_p4", "numerals precede marked fish less (v2 held-out)", "ledger", S, f"{B['marked_rate']} vs {B['plain_rate']}", B["p"], f"{B['plain'][1]}+{B['marked'][1]}", Y, "v2", C, "ledger:v2", 8, Y, "9")
Cc = V2["C_positional_classes"]
R("lr_pos", "K=3 positional classes hold on v2 held-out", "ledger", S, f"{Cc['agreement']} vs {Cc['chance_mean']}", Cc["p"], f"{Cc['n_test_signs']} signs", Y, "v2", C, "ledger:v2", 8, Y, "", note="permutation floor 1e-4")
D = V2["D_animal_heldout"]
R("lr_animal", "seal animal predictable from text (v2 held-out)", "ledger", S, f"bal. acc {D['bal_acc']} vs {D['null_mean']}", D["p"], str(D["n_test"]), Y, "v2", C, "ledger:v2", 8, N_, "R-e")
Ej = V2["E_jar_LR_copyfree"]
R("lr_jar", "jar M342 last rather than first in copy-free L-R lines", "ledger", S, f"{Ej['jar_last']} vs {Ej['jar_first']} of {Ej['lr_copyfree']} lines", Ej["p_binom_last_vs_first"], str(Ej["lr_copyfree"]), Y, "none", C, "ledger:v2", 8, N_, "7")
F = V2["F_gulf_round"]
R("lr_gulf", "Gulf round seals: perm-percentile below length-matched peripheral seals (site held out)", "ledger", S, f"{F['foreign_mean_pct']} vs {F['native_matched_mean']}", F["p"], str(F["n_foreign"]), Y, "none", C, "ledger:v2", 8, Y, "4", note=f"{F.get('n_draws', 20000):,} matched draws" + (f"; MC 95% {F['p_mc95'][0]:.2g}-{F['p_mc95'][1]:.2g}" if "p_mc95" in F else ""))

# ===================================================================== corrections
def bh(p):
    p = np.asarray(p, float); m = len(p); o = np.argsort(p)
    q = p[o] * m / np.arange(1, m + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    out = np.empty(m); out[o] = np.minimum(q, 1); return out

def padded(rows, key_fn):
    """Return list of (row_index or None, p) with unlisted family members padded at p=1."""
    items = [(i, r["p_value"]) for i, r in rows if r["p_value"] != ""]
    listed = defaultdict(int); fsize = {}
    for i, r in rows:
        listed[r["family"]] += 1; fsize[r["family"]] = max(fsize.get(r["family"], 0), int(r["family_size"]))
    for f, n in listed.items():
        items += [(None, 1.0)] * max(0, fsize[f] - n)
    return items

ix = list(enumerate(ROWS))
conf = [(i, r) for i, r in ix if r["mode"] == C]
for r in ROWS: r.update(q_global="", q_area="", q_hier="", q_all="")
# global
it = padded(conf, None); q = bh([p for _, p in it])
for (i, _), qq in zip(it, q):
    if i is not None: ROWS[i]["q_global"] = qq
M_GLOBAL = len(it)
# per area
for area in sorted({r["area"] for _, r in conf}):
    sub = [(i, r) for i, r in conf if r["area"] == area]
    it = padded(sub, None); q = bh([p for _, p in it])
    for (i, _), qq in zip(it, q):
        if i is not None: ROWS[i]["q_area"] = qq
# hierarchical (families of confirmatory tests)
fams = defaultdict(list)
for i, r in conf: fams[r["family"]].append((i, r))
fam_simes, fam_within = {}, {}
for f, sub in fams.items():
    if all(r["p_value"] == "" for _, r in sub): continue  # interval-only family: no p to combine
    it = padded(sub, None)
    ps = np.array([p for _, p in it]); m = len(ps)
    fam_simes[f] = float(min(1.0, np.min(np.sort(ps) * m / np.arange(1, m + 1))))
    fam_within[f] = list(zip([i for i, _ in it], bh(ps)))
fl = sorted(fam_simes); fq = bh([fam_simes[f] for f in fl]); Fn = len(fl)
sel = [f for f, qq in zip(fl, fq) if qq <= 0.05]; Rn = len(sel)
for f, qq in zip(fl, fq):
    for i, qw in fam_within[f]:
        if i is None: continue
        ROWS[i]["q_hier"] = min(1.0, qw * Fn / max(Rn, 1)) if f in sel else 1.0
# everything (sensitivity)
it = padded(ix, None); q = bh([p for _, p in it]); M_ALL = len(it)
for (i, _), qq in zip(it, q):
    if i is not None: ROWS[i]["q_all"] = qq

# ===================================================================== write
cols = ["id", "claim", "area", "file", "statistic", "p_value", "p_source", "ci", "n", "distinct_text_unit", "split", "mode",
        "family", "family_size", "replicated_independently", "readme_claim", "q_global", "q_area", "q_hier", "q_all", "note"]
def fmt(v):
    return f"{v:.3g}" if isinstance(v, float) else v
with open(ROOT / "docs" / "test_ledger.csv", "w", newline="") as fh:
    w = csv.DictWriter(fh, fieldnames=cols); w.writeheader()
    for r in ROWS: w.writerow({k: fmt(r[k]) for k in cols})

summary = dict(n_rows=len(ROWS), n_confirmatory=len(conf), n_with_p=sum(r["p_value"] != "" for r in ROWS),
               m_global_padded=M_GLOBAL, m_all_padded=M_ALL, n_families_conf=Fn, n_families_selected=Rn,
               family_simes={f: round(fam_simes[f], 6) for f in fl}, families_selected=sel,
               by_split={s: sum(r["split"] == s for r in ROWS) for s in sorted({r["split"] for r in ROWS})},
               by_mode={m: sum(r["mode"] == m for r in ROWS) for m in (C, E)})
def sig(r, k): return r[k] != "" and r[k] < 0.05
summary["survive_global"] = [r["id"] for r in ROWS if sig(r, "q_global")]
summary["survive_area_not_global"] = [r["id"] for r in ROWS if sig(r, "q_area") and not sig(r, "q_global")]
summary["survive_global_not_hier"] = [r["id"] for r in ROWS if sig(r, "q_global") and not sig(r, "q_hier")]
summary["survive_hier_not_global"] = [r["id"] for r in ROWS if sig(r, "q_hier") and not sig(r, "q_global")]
summary["survive_all"] = [r["id"] for r in ROWS if sig(r, "q_all")]
json.dump(dict(summary=summary, v2_reruns=V2), open(HERE / "results.json", "w"), indent=1, default=float)
print(json.dumps(summary, indent=1))
