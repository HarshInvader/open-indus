# Pre-registration: detached signs and non-textual covariates (2026-11-14)

Area: `experiments/detached_signs/`. Hashed in `docs/prereg/HASHES.txt` (tag `detached_signs`) together with `ds_lib.py`, `d1_detach.py`, `d1_detach.json`, `d2_covariates.py` and `d3_inline.py` BEFORE `d2_covariates.py` or `d3_inline.py` was run. Any later edit gets a logged amendment below.

## Background and what was already seen
- line_breaks noted that several signs sit alone on a line apart from the main text (M242, M374, M393, M93).
- Earlier leads that touched these signs and covariates (so they are NOT independent of this test):
  - scene_text: W621 = M242 on 5 Mohenjo-daro scene-seal types (M-295, M-296, M-306, M-310, M-1186), q = 0.20. Its catalogue coded 408 CISI objects (`experiments/scene_text/scene_codes_objects.csv`).
  - logograms: M242 on M77 scene seals (fs80 600-810), 4 vs 0.24, q = 0.21. That scan used all of M77.
  - self_label / bangle_oval: oval W790 (bridge: M261/M373/M374) on 6/41 ICIT bangle texts. Every ICIT `BNGL` row was in the discovery set.
- The analyst knows these results. Before freezing I ran only the layout step (d1) and counted covariate levels (scene / animal / object type / material / sized seals) in the confirmatory sets without any class-sign split.

## Step 1 (done, layout only): the class
- Unit: distinct M77 texts (`distinct(m77_texts())`), split `dev_heldout(version=2)`.
- Detached token: the only sign on a line with no `#`, in a text with >= 2 non-empty lines.
- Global null: hypergeometric over all tokens of the split (share of tokens in solo lines = 39/7,626 on dev). Conditional null: same within multi-line texts only (39/512).
- Rule (frozen before held-out was looked at, applied on dev): detached if BH q_global < 0.05 over the 112 tested signs AND p_cond < 0.05.
- Result on dev: **C = {M242, M374, M93, M326, M393}**. Held-out layout replication: M374 2/2, M393 2/2, M242 1/4 detached; M93 0/2, M326 0/6; pooled 5/17 vs 0.09 expected (p = 8e-9). ICIT-only texts (no match to any M77 text): W621 2/7 detached (p = 3e-4); W790 1/20 (p = 0.07; W790 also contains diamond M261); W384 (= M326) 0/12.
- ICIT image of C via the bridge: **CW = {W621, W790, W384}**. M93 and M393 have no bridge entry and are absent from ICIT tests.
- Secondary "core" class (replicated in layout): {M242, M374, M393} / {W621, W790}.

## Step 2 (confirmatory): covariates
Unit: distinct text (M77: distinct seq, object side; ICIT: distinct (site, seq) with no match to any M77 text = "ICIT-only"). Carrier = text containing >= 1 class token anywhere (inline or detached).

**Confirmatory sets, with the overlap removed:**
- `m77_heldout_conf`: M77 held-out families (571 texts), minus held-out texts that would be logograms hits (M242 on a seal/sealing with field category Scenes).
- `icit_only_conf`: ICIT-only texts, minus every `BNGL` object, every object in the scene_text coded catalogue (408 CISI numbers), and the 5 scene_text W621 hits. Consequence stated plainly: **bangles cannot be tested confirmatorily (all bangles are discovery data)**, and only 8 (M77 held-out) / 5 (ICIT-only) scene seals remain, so H1 has little power.

**Statistic.** All comparisons are stratified by site x text length bin (1,2,3,4,5,6-7,8+ signs) x multi-line flag, so that "long text on a big multi-line seal" does not count as an effect. "Beyond frequency" is enforced by a control null: 2,000 sets of non-class signs, each matched one-to-one on token count in the analysis set (within 0.7n-1 .. 1.3n+1, else 10 nearest), statistic recomputed; p_ctrl = (1 + #controls >= observed) / 2001, one-sided.

**Hypotheses (family of 6, Holm):**
- H1 iconography (one-sided): on seals and sealings with a scene or animal field, carriers have a scene/anthropomorphic field more than stratum mates. Mantel-Haenszel-type z. Sets: M77 held-out (scene = fs_category Scenes or Anthropomorphic forms; animal = Animals); ICIT-only (scene = symbol Scene/Anth; animal = animal codes listed in the script).
- H2 object type (omnibus): carriers' distribution over object types differs from stratum expectation, G = sum (O-E)^2/E. Sets: M77 held-out (M77 object_type); ICIT-only (SEAL, TAG, POT, TAB:B, TAB:I, TAB:C, ROD, IMPL, OTHER).
- H3 material (omnibus): ICIT-only (steatite, clay/terracotta/ceramic, faience, copper, stoneware, ivory/bone, other; unrecorded dropped).
- H4 seal size (one-sided, larger): mean residual log(width x height) of carriers vs stratum mean, ICIT-only square seals with both dimensions > 5 mm.

**Decision.** A hypothesis passes if Holm-adjusted p_ctrl < 0.05 in every set where it is tested (H1, H2 need both sets). Verdict: SUPPORTED if >= 2 of H1-H4 pass; PARTIAL if 1; otherwise REFUTED where power (planted OR 3 for H1/H2/H3, about +0.5 SD for H4, 300 reps, reported per test) is >= 0.8, and INCONCLUSIVE where it is lower.
- Secondary (not in Holm family): same tests on the core class.
- Exploratory: same tests with the overlap objects kept; on dev; on all distinct ICIT (bangles included). These describe, they do not confirm.

## Step 3 (exploratory, pre-declared): inline use and co-occurrence
- For each sign in C: tokens in single-line break-free texts and their slot (alone, first, medial, last) vs 20 frequency-matched non-class signs.
- In multi-line texts: detached (which line) vs inline in a multi-sign line (slot).
- Co-occurrence: texts holding >= 2 different class signs vs a token-shuffle null (text lengths and sign frequencies kept, 2,000 shuffles).

## What would falsify the "class apart from the text" idea
- Class signs often inline in ordinary slots at the rate of matched signs (step 3), AND no covariate beyond frequency (step 2) with adequate power.
- Even a pass shows only association with object/scene class; it does not say what the signs mean, and a workshop or carver habit on large seals explains it as well as a determinative.

## Amendments
(none)
