# Pre-registration: redteam_size (red team of space_and_sealing T4 + reg_size)

Agent: redteam_size. Written 2026-11-14 BEFORE any statistic below was computed. Frozen with
`experiments/redteam_size/rt_size.py` (hash in `docs/prereg/HASHES.txt`, tag `redteam_size`).
`experiments/space_and_sealing/` and `experiments/reg_size/` are imported read-only, never edited.

Claim attacked: "On small seals, closers (non-jar closers, post-closers) keep their share while other classes are
dropped; the omission order (connective > title > opener > ... > jar > other closers) is stable and replicates
(rho 0.79)."

Known at registration: both RESULTS.md files, t4.log, rs_test.log, the code. Already seen (T4 log): closer-class
token counts per T4 text (any of jar/other_closer/post_closer): 0 in 186 texts, exactly 1 in 619, 2+ in 174;
other_closer presence is flat across area terciles (0.385/0.407/0.355) while length falls 5.64 -> 3.86.
Both prior tests use an area-permutation null, which destroys the length-area link itself; so any
class whose count does not fall with length gets a negative share slope under that null.

Data: T4 rows exactly as T4 (`rs_lib.t4_objects()`, 952 texts, ICIT W signs, site|period strata) and the reg_size
primary new set (`rs_lib.build_new_set(FEM+EH)`, 138 texts, M signs, site strata). Estimator = T4's (within-stratum
slope of class token share on log area, per doubling). Classes = T4's frozen 8. Protected set P = {jar,
other_closer, post_closer} ("closers"); variant P' = {other_closer, post_closer}.

## A1 Mechanical artefact (primary)
Each dataset keeps its own areas, strata and observed lengths; only the sign content is simulated (1,000 sims).
For text i with length L_i a template is drawn from the same dataset's texts of length >= max(L_i, 6), same site if
>= 10 candidates, else any site. Then:
- N1 uniform deletion: keep L_i template tokens chosen uniformly.
- N2 protected closers: keep all template tokens in P (if more than L_i, sample L_i of them), fill the rest with
  uniformly chosen non-P tokens. N2' the same with P'.
- Sensitivity: template length >= L_i (any longer-or-equal text).
Per class: observed share slope vs each null (mean, SD, two-sided p, Holm over 8 within null).
(iii) per-text presence slope and closer COUNT slope vs area, observed vs N1/N2.
Order: rho(mean N2 slopes, observed) per dataset; distribution of rho(T4 observed, new-set N2 draw) gives
the replication rho expected from mechanics alone (P(rho >= 0.79)).
Residual order: r = observed - mean N2, per class, per dataset; Spearman rho(r_T4, r_new), with exact permutation
p (8! label permutations) and a parametric p (new-set N2 draws minus N2 mean, vs r_T4).
**A1 rule.** K = a closer class (other_closer or post_closer) departs from N2 (p < 0.05, same sign) in BOTH datasets.
O = residual rho >= 0.5 with exact p < 0.05. Survives = K and O; weakened = exactly one, or closers depart from N1
but match N2 while the mechanical rho reproduces the observed order; fails = neither K nor O (the omission order
reduces to "texts carry a closer whatever their length" + uniform thinning of the rest).

## A2 Independence of the replication
- Exact one-sided permutation p of rho = 0.79 over all 8! orderings (pure 8-point reference).
- Families: T4 + new texts linked by `corpus.build._close` on rs_lib canonical tokens; connected components.
  Family-disjoint replication: drop new texts whose family contains a T4 text; rho with T4 slopes + exact p.
  Cluster bootstrap (1,000): resample families within each set; report rho median, 95% interval, P(rho >= 0.5).
- Double counting: new text vs T4 text at same site with |log area diff| < 0.03 and `_close` (or equal) canonical
  text = probable same object read twice; count and rerun without them.
- **A2 rule.** Survives if family-disjoint rho >= 0.5 (exact p < 0.05) and bootstrap P(rho >= 0.5) >= 0.8;
  fails if family-disjoint rho < 0.5 and bootstrap P < 0.5; else weakened. Same-measurer issue is stated, not testable.

## A3 Confounds
Rerun observed slopes, closer signs, N2 residuals for closers, and rho(T4 variant, new variant) with:
(a) strata + seal type (unicorn / other animal / no symbol; ICIT `symbol` Bull1* = unicorn, None = no symbol;
M77 fs80 13 = unicorn, 0 = none); (b) unicorn seals only; (c) T4 site-only strata (period removed);
(d) material: new set restricted to Mackay FEM (Mohenjo-daro; register material steatite or blank), i.e. Harappa EH
(no material recorded) dropped; T4 is steatite by construction. (A smoke run with shuffled area showed only 13 new
texts link to an ICIT steatite object, so that version is reported descriptively, not used in the rule.)
**A3 rule.** Survives if both closer classes keep negative slopes and rho >= 0.5 in every variant; fails if the
closer slopes vanish (|slope| < 1/3 of primary) or flip in (a) or (b) in both datasets; else weakened.

## Ledger
Rows `rts_*` in `docs/test_ledger.csv` (mode: redteam).
