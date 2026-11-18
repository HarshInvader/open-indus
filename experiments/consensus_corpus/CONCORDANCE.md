# Corrected Mahadevan (M77) <-> Wells (ICIT) sign concordance

**Use this instead of the fish pairing hard-coded in `experiments/signlist_robustness/harness.py`** whenever you map a single sign between the two lists.

Files:
- `corrected_concordance.csv`: one row per M sign, with columns primary partners, provisional extras, harness original, rule applied and positional evidence.
- `out/concordance.json`: keys `primary`, `provisional`, `doubles_primary`, `doubles_provisional`, `harness_original`, `changes`.

How to load:
```python
import json
C = json.load(open("experiments/consensus_corpus/out/concordance.json"))
M2W = C["primary"]                # {"M65": ["W235"], ...}
DOUBLE = C["doubles_primary"]     # {"M245": ["W617"], ...}: M77 writes the sign twice, Wells has one sign
```

## Evidence used

- The start point is the harness ICIT mapping: `bridge_WM.json` plus harness.py's font-verified overrides.
- The main evidence is **mapping-free**. It comes from the 469 objects that the 1930s excavation registers link to both an M77 text and an ICIT record (audit_followups #29; the link uses serial and field numbers, never signs). On the 395 of them whose two readings have the same number of signs, `cooc.py` counts which Wells sign stands at the same position as each Mahadevan sign. No bridge is involved.
- Mahadevan's drawings (`data/sign_images/M*.png`) were checked for every change. No Wells drawings are in the repo, so the Wells side rests on co-occurrence and Wells' numbering order.

## Changes (primary tier, used by every analysis here)

| M77 | was | now | rule | positional evidence (same-position count) | drawing check |
|---|---|---|---|---|---|
| M65 | W231 | **W235** | R1 re-pair | W235 22 of 23; W231 0 | roofed fish (chevron over fish) |
| M67 | W233 | **W240** | R1 re-pair | W240 37 of 38; W233 0 | cross-headed fish |
| M70 | W235 | **W231** | R1 re-pair | W231 9 of 9 | fish with an inner stroke |
| M72 | W240 | **W233** | R1 re-pair | W233 20 of 23 (W220 plain fish 2) | fish with a slash |
| M66 | W232 | **W236** | R1 re-pair (3 of 3) | W236 3 of 3 | ticked roofed fish |
| M68 | W234 | **W241** | R5 analogy (+1 positional, +2 aligned) | W241 1 of 1 | ticked cross-headed fish |
| M71 | W236 | **W232** | R5 analogy (no matched data) | none | ticked fish with an inner stroke |
| M73 | W241 | **W234** | R5 analogy (no matched data) | none | ticked slashed fish |
| M389 | none | **W806** | R2 add | W806 14 of 18 (W803 3) | leaf-in-oval with a side branch; M387 is the upright-branch variant = W803 |
| M387 | W803, W806 | **W803** | R4 narrow | W803 9 of 9; W806 belongs to M389 | as above |
| M162 | W390, W405 | **W390** | R4 narrow | W390 32 of 32; W405 co-occurs with M169 (9) | |
| M216 | W550, W798 | **W550** | R4 narrow | W550 6 of 6; W798 co-occurs with M53 (16) | |
| M175 | W350 | W350, **W353** | R3 alternate | W350 5, W353 3 | Wells splits the sign |
| M205 | W491 | W491, **W495** | R3 alternate | W495 3, W491 2 | Wells splits the sign |
| M210 | W501 | W501, **W502** | R3 alternate | W502 3, W501 1 | Wells splits the sign |
| M245 M245 | (two signs) | **W617** (one sign) | R6 doubled sign | 4 aligned cases + 1 more in a 3-sign run | Mahadevan writes the sign twice; Wells has a single "double" sign |
| M176 M176 | | **W401** | R6 | 2 | |
| M375 M375 | | **W792** | R6 | 2 | |

The **fish pattern**: Wells numbers each fish variant, then its ticked form right after it:
- W220 plain, W226 ticked;
- W231 inner stroke, W232 ticked;
- W233 slash, W234 ticked;
- W235 roof, W236 ticked;
- W240 cross-head, W241 ticked.

The harness zip paired the M list (59, 65, 67, 70, 72) with the W list in numerical order, but the two lists order the variants differently. Set-level tests (ticked vs plain; the fish class) are unaffected, because both sets keep the same members.

## Provisional tier (2 observations; reported in the disagreement rate only, not used in tests)

- Added where M77 had no bridge entry: M113=W048, M163=W391, M188=W330, M212=W521, M217=W552, M258=W605, M371=W786.
- Alternates: M130+W436, M155+W072, M230+W463, M284+W824, M294+W927, M345+W746, M379+W829.
- Doubled signs (1 case each): M391+M391=W821, M194+M194=W586, M162+M162=W389, M293+M293=W919, M59+M59=W219, M1+M1=W091.

## Not changed, deliberately

- **M328 = W700 and M89 = W033** stay as they are (37 of 43 and 40 of 47 positional). The 5 crossings each way are adjacent order swaps: M77 reads "M89 M328" where ICIT reads "W700 W033". That is a real reading difference, not a mapping error. The drawings (a U against three strokes) cannot be confused.
- **M104 -> W034** (3 of 10) is not added, because W034's main Mahadevan partner is M95 (5 co-occurrences). Treat it as a stroke-count reading difference.
- **Order around M328.** 9 of the 12 adjacent order swaps on matched texts involve M328, all on Harappa objects (texts 4357-4579). There M77 puts M328 after a stroke or fish sign, and ICIT puts it before. This is a systematic editorial difference about where M328 sits in the reading order, not random error.
- About 5% of M77 tokens on matched texts (105 of 2,036) still have no Wells partner at all.
