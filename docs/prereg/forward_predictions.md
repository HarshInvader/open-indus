# Prereg: forward predictions for the leads that survived 2026-11-18 (board #44)

Agent forward_predictions, 2026-11-18. Written and hashed before any sign sequence of the held-out site was read and before any statistic below was computed. Scorer: `experiments/forward_predictions/fp.py` (hashed with this file).

## Why

Every lead that survived the 2026-11-18 red teams gets a sharp prediction about material we do not yet have: CISI vol 3, the HARP inscribed-object / sherd spreadsheet (Kenoyer, due ~2027-01), and new excavation reports. Each is stated so that a future agent can score it mechanically with `fp.py --mode forward` on rows added to `experiments/new_finds/new_texts.csv` (M numbers), and each is compared with a trigram or frequency baseline. A dry run on one site held out now shows the scoring works.

Leads covered (source in brackets): round-seal closer deficit [redteam_round_seal_format C1]; round-seal order excess after format matching [round_seal_format, R41 C2]; jar sign M342 rarer on pottery than on seals [self_label finding 3, firing_stage]; cup sign M328 takes only tall-stroke values 2/3/4 [m328_measure, tablet_archives]; M328 on offering-scene tablets [scene_text H1, untestable so far]; plain fish M67 = M70 = M72 behave as one sign [signlist_shape, R40]. Not covered, already frozen: ticked fish final (P3), M109+M59 (P4), M373 on bangles (BO-H1-4), painted vessels M342 <5% (A4b). Not covered, did not survive: M342 on broken seals (R37, corrected p 0.06), numeral-opening round seals (#39), the full shape-only list L_strict (fails ICIT replication; only the fish merge carries its gain).

## Common definitions

- Units: distinct texts, de-duplicated by (site, sign sequence); `|` removed; `#` marks a break. "Signs" are tokens starting with M (M77, forward) or W (ICIT).
- Sign codes (M / Wells): jar M342 / W740; cup M328 / W700; tall strokes M86=1, M87=2, M88/M89/M92/M93/M94=3, M95=4, M96=5 / W031..W037 = 1..7 (from `sources/shaunmortal_indus/data/stroke_signs.json` and `m328_measure`). Closer set C = signs with `final_class == closer` in `experiments/grammar/sign_classes.csv` (M column; Wells column split on `[;\s]+`, the R41-corrected set).
- Round seal: ICIT type SEAL:C or SEAL:CY; for new finds, object_type contains "round", "circular", "button" or "cylinder" and is a seal. Square seal: any other SEAL type from a home (non-FOREIGN, non-Unknown) site.
- Baselines. Trigram: interpolated trigram over signs, weights 0.5/0.3/0.15/0.05 on trigram/bigram/unigram/uniform (vocab = training signs + UNK), with BOS/EOS. End-trigram (for "what is the last sign"): closer share among training texts whose last-but-one two signs match, backing off to last-but-one sign (if ≥3 texts) then to the global final closer share, add-1 smoothed. Frequency: per-token unigram rate over all training texts.
- Log score: per unit, log2 probability the forecast gave the observed outcome. Gain = lead minus baseline, bits per unit. Positive = the lead forecasts better.

## Predictions (frozen numbers)

**F1 Round seals rarely end in a closer.** Eligible: round seals, ≥2 signs, last sign legible. Statistic: share whose last sign is in C. Lead forecast p = 0.20 per text; baseline = end-trigram trained on all training seal texts. Pass: share ≤ 0.25 and one-sided binomial p < 0.05 against p0 = closer-final share of training home square seals. Fail: share ≥ 0.40. Min n 8.

**F2 Round seals break square-seal order.** Statistic: mean bits/sign of round-seal texts under a trigram trained on training home square seals, minus the same for square seals scored in the same batch (forward: the new square seals; if fewer than 8, the leave-one-out mean of training home square seals). Lead: excess ≥ +0.5 bits/sign; baseline forecast: excess 0. Pass: excess ≥ 0.5 and label-shuffle permutation p < 0.05 (2,000 shuffles, one-sided). Fail: excess < 0. Min n 8 round texts. Gain reported as observed excess (bits/sign) minus 0.25 (the midpoint between the two forecasts); positive = nearer the lead.

**F3 The jar sign is rarer on pottery than its seal rate predicts.** Eligible: post-firing pottery graffiti (ICIT POT:T:g; M77 / new finds "pottery graffito", not painted or stamped), ≥1 sign. Expected count E = Σ 1−(1−f_seal)^L over texts, f_seal = jar token share on training seal texts. Statistic RR = observed texts with jar / E. Lead forecast per text: 0.6·(1−(1−f_seal)^L). Baseline per text: 1−(1−f_all)^L, f_all = jar token share over all training texts. Pass: RR ≤ 0.70 and one-sided Poisson p < 0.05 (observed vs E). Fail: RR ≥ 1.0. Min E ≥ 8.

**F3b Jar sign is not a vessel self-label (needs vessel forms; HARP).** Where vessel form is recorded, RR of jar-bearing texts on storage jars vs other forms. Pass: RR < 1.5. Fail: RR ≥ 2 with Fisher p < 0.05. Min 5 jar-bearing texts with form. Not scored in the dry run (no forms).

**F4 The cup sign takes tall-stroke values 2, 3 or 4 only.** Eligible: each cup token immediately preceded by a tall stroke, on distinct texts. Statistic: share with N ∈ {2,3,4}; share with N ≥ 5. Lead forecast: training distribution of N before the cup (+0.5 per value 1..7). Baseline: training distribution of tall-stroke values before any other sign (+0.5). Pass: share ≥ 0.90 and Wilson lower ≥ 0.80 and N≥5 share ≤ 0.05. Fail: share < 0.80 or N≥5 share > 0.05. Min n 10.

**F4b Cup sign on offering-scene tablets (needs CISI vol 3 / hi-res photos).** Among moulded tablet types whose scene shows a figure with a vessel (blind-coded), cup sign present with odds ratio ≥ 3 vs other moulded tablet types. Pass: OR ≥ 3 and Fisher p < 0.05. Fail: OR < 1.5 with ≥ 10 offering-scene types. Min 5 offering-scene types. Not scored in the dry run.

**F5 The three plain fish are one sign.** Eligible: texts in M numbers. Statistic: log-likelihood gain (nats per scored token; tokens = signs seen in training plus EOS, per break-free run) of a class trigram with {M67, M70, M72} as one class, emission P(sign | class) from training counts (+0.5), over the same trigram on the plain M77 list. Bootstrap by text, 2,000 draws. Pass: gain > 0 and CI lower > 0. Fail: CI upper < 0. Min 30 tokens of M67/M70/M72 in the scored texts. Gain is its own baseline comparison.

## Dry run (known answer): held-out site = Kalibangan

Chosen from object counts only (no texts read): the one non-core site present in both editions (M77 111 texts, ICIT 212 objects) with a large post-firing graffito set (89 POT:T:g) and a seal set (50+), so F3 and F5 can reach min n. Expected not evaluable there: F1, F2 (few or no round seals), F4 (few or no cup tablets), F3b, F4b.

Procedure: training = every text not from Kalibangan (ICIT for F1-F4 in Wells codes, M77 for F5). All frozen parameters (p0, f_seal, f_all, N distributions, trigram counts) are recomputed by `fp.py --mode dryrun` from training only, then scored on Kalibangan. Caveat stated in advance: the leads were found on corpora that include Kalibangan, so the dry run tests that the scoring works and that the leads transfer to one site; it is not a clean confirmation.

Kill (from board #44): if the summed gain over the evaluable predictions is ≤ 0 on Kalibangan, the forward-prediction set has no gain over baseline and is reported as killed; individual predictions with negative gain are flagged. If none is evaluable, the dry run is reported as uninformative, not as a pass.

Forward scoring trigger: any of (a) CISI vol 3 in hand, (b) HARP spreadsheet received, (c) ≥ 20 newly published scorable texts in new_texts.csv, (d) ≥ 8 new round seals. Training for forward mode = all current M77 texts. Each prediction is scored once per trigger, all reported, no re-tuning.

## Amendment A1 (2026-11-18, after the Kalibangan dry run, before any forward scoring)

The dry run printed the training distribution for F4 on distinct texts: N = {1: 4, 2: 8, 3: 18, 4: 7, 6: 2} (39 tokens). Its {2,3,4} share is 0.85 and N≥5 share 0.05, so the current corpus itself fails the F4 bar as frozen. The bar was set by mistake from m328_measure's object-level counts (300 identities, mould copies kept), not from distinct texts. The dry-run verdicts above are unchanged by this amendment (F4 was not evaluable there). For forward scoring only, F4 is replaced by **F4-A1**: share of N = 5 ≤ 0.02 and mean log-score gain over the frequency baseline > 0 = pass; N = 5 share > 0.05 or gain < 0 = fail; min n 10 cup tokens on distinct texts. Reason: the m328_measure claim that survived is "a fixed set of formula values, 5 absent", which a count model (zero-truncated Poisson, ~9% fives) contradicts. The original F4 bar is still reported alongside.

F3 is kept frozen but reported as retired: in the exploratory leave-one-site-out check (x_f3_sites.py, run after the dry run) RR is 0.92-1.17 at Harappa, Mohenjo-daro and Kalibangan, so the length-aware depletion it predicts is absent everywhere we have data.
