## Part 1: seal-type references, between vs within (median AUC, matched size)

| corpus | variant | within split | n/side | between | within | Δ | p (floor) | gate |
|---|---|---|---|---|---|---|---|---|
| ur3 | namefree | U_reign | 68 | 0.599 | 0.590 | +0.009 | 0.431 | 82% |
| ur3 | namefree | U_coll | 41 | 0.598 | 0.531 | +0.067 | 0.098 | 44% |
| ur3 | namefree | U_rand | 88 | 0.642 | 0.394 | +0.247 | 0.020 | 88% |
| ur3 | namefree | G_reign | 58 | 0.604 | 0.698 | -0.094 | 1.000 | 62% |
| ur3 | namefree | G_coll | 52 | 0.582 | 0.569 | +0.013 | 0.333 | 74% |
| ur3 | namefree | G_rand | 88 | 0.630 | 0.518 | +0.112 | 0.020 | 82% |
| cdli | namefree | U_reign | 72 | 0.651 | 0.618 | +0.033 | 0.078 | 76% |
| cdli | namefree | U_rand | 104 | 0.681 | 0.477 | +0.205 | 0.020 | 84% |
| cdli | namefree | G_reign | 48 | 0.622 | 0.696 | -0.075 | 1.000 | 64% |
| cdli | namefree | G_rand | 97 | 0.669 | 0.512 | +0.158 | 0.020 | 82% |
| ur3 | whole | U_reign | 227 | 0.876 | 0.718 | +0.158 | 0.020 | 100% |
| ur3 | whole | U_coll | 171 | 0.865 | 0.623 | +0.243 | 0.020 | 100% |
| ur3 | whole | U_rand | 227 | 0.875 | 0.470 | +0.404 | 0.020 | 100% |
| ur3 | whole | G_reign | 199 | 0.867 | 0.619 | +0.248 | 0.020 | 100% |
| ur3 | whole | G_coll | 157 | 0.856 | 0.549 | +0.307 | 0.020 | 100% |
| ur3 | whole | G_rand | 227 | 0.876 | 0.520 | +0.355 | 0.020 | 100% |
| cdli | whole | U_reign | 227 | 0.865 | 0.700 | +0.165 | 0.020 | 100% |
| cdli | whole | U_rand | 227 | 0.858 | 0.476 | +0.381 | 0.020 | 100% |
| cdli | whole | G_reign | 197 | 0.853 | 0.631 | +0.222 | 0.020 | 100% |
| cdli | whole | G_rand | 227 | 0.856 | 0.488 | +0.368 | 0.020 | 100% |
| ur3 | namefree_owner | U_reign | 30 | 0.721 | 0.517 | +0.205 | 0.020 | 22% |
| ur3 | namefree_owner | U_coll | 19 | 0.756 | 0.518 | +0.237 | 0.020 | 18% |
| ur3 | namefree_owner | U_rand | 32 | 0.701 | 0.493 | +0.208 | 0.020 | 24% |
| ur3 | namefree_owner | G_reign | 27 | 0.740 | 0.504 | +0.236 | 0.020 | 40% |
| ur3 | namefree_owner | G_coll | 23 | 0.737 | 0.519 | +0.218 | 0.020 | 38% |
| ur3 | namefree_owner | G_rand | 40 | 0.672 | 0.567 | +0.104 | 0.020 | 32% |
| cdli | namefree_owner | U_reign | 41 | 0.600 | 0.512 | +0.088 | 0.020 | 14% |
| cdli | namefree_owner | U_rand | 49 | 0.619 | 0.447 | +0.173 | 0.020 | 30% |
| cdli | namefree_owner | G_reign | 28 | 0.571 | 0.556 | +0.015 | 0.431 | 28% |
| cdli | namefree_owner | G_rand | 50 | 0.626 | 0.531 | +0.095 | 0.020 | 32% |
| ob | namefree | N_rand | 11 | 0.554 | 0.210 | +0.344 | 0.020 | 6% |
| ob | namefree | I_rand | 8 | 0.470 | 0.367 | +0.103 | 0.098 | 10% |
| lat | namefree | ge_rlp_vs_bwhe | 42 | 0.700 | 0.602 | +0.099 | 0.020 | 54% |
| lat | namefree | br_north_vs_south | 29 | 0.711 | 0.511 | +0.200 | 0.020 | 36% |
| lat | namefree | ge_random | 75 | 0.749 | 0.498 | +0.251 | 0.020 | 72% |
| lat | namefree | br_random | 50 | 0.726 | 0.482 | +0.244 | 0.020 | 78% |
| ob | whole | N_rand | 65 | 0.812 | 0.431 | +0.381 | 0.020 | 78% |
| ob | whole | I_rand | 31 | 0.789 | 0.512 | +0.277 | 0.020 | 56% |
| lat | whole | ge_rlp_vs_bwhe | 128 | 0.705 | 0.582 | +0.123 | 0.020 | 100% |
| lat | whole | br_north_vs_south | 73 | 0.659 | 0.517 | +0.143 | 0.020 | 100% |
| lat | whole | ge_random | 214 | 0.705 | 0.424 | +0.281 | 0.020 | 100% |
| lat | whole | br_random | 111 | 0.698 | 0.427 | +0.270 | 0.020 | 96% |

| within only (no between) | n/side | median | 95% |
|---|---|---|---|
| W_latstamp_namefree_ge_rlp_vs_bwhe | 19 | 0.454 | 0.366-0.537 |
| W_latstamp_namefree_ge_random | 40 | 0.543 | 0.495-0.605 |
| W_latstamp_whole_ge_rlp_vs_bwhe | 63 | 0.562 | 0.515-0.603 |
| W_latstamp_whole_ge_random | 109 | 0.464 | 0.418-0.500 |

## Part 2: Indus site pairs

| family | site a (larger) | site b | n/side | between | within (a halves) | Δ | p floor | q floor | q chance | power 10/15/20% | verdict |
|---|---|---|---|---|---|---|---|---|---|---|---|
| m77_seal | Mohenjo-daro | Harappa | 200 | 0.540 | 0.535 | +0.005 | 0.412 | 0.458 | 0.245 | 54%/98%/100% | same |
| m77_seal | Mohenjo-daro | Lothal | 60 | 0.469 | 0.487 | -0.018 | 0.627 | 0.627 | 0.549 | 54%/70%/94% | underpowered |
| m77_seal | Mohenjo-daro | Chanhu-daro | 42 | 0.627 | 0.516 | +0.111 | 0.098 | 0.163 | 0.245 | 82%/94%/100% | underpowered |
| m77_seal | Mohenjo-daro | Kalibangan | 38 | 0.583 | 0.481 | +0.102 | 0.216 | 0.270 | 0.245 | 74%/76%/98% | underpowered |
| m77_seal | Harappa | Lothal | 67 | 0.538 | 0.471 | +0.068 | 0.137 | 0.196 | 0.327 | 76%/90%/100% | underpowered |
| m77_seal | Harappa | Chanhu-daro | 44 | 0.631 | 0.466 | +0.164 | 0.039 | 0.098 | 0.245 | 98%/98%/100% | differs |
| m77_seal | Harappa | Kalibangan | 44 | 0.569 | 0.445 | +0.125 | 0.078 | 0.157 | 0.245 | 86%/96%/98% | underpowered |
| m77_seal | Lothal | Chanhu-daro | 34 | 0.571 | 0.330 | +0.241 | 0.020 | 0.065 | 0.245 | 100%/100%/100% | differs |
| m77_seal | Lothal | Kalibangan | 34 | 0.602 | 0.324 | +0.278 | 0.020 | 0.065 | 0.245 | 100%/100%/100% | differs |
| m77_seal | Chanhu-daro | Kalibangan | 22 | 0.605 | 0.397 | +0.207 | 0.020 | 0.065 | 0.245 | 88%/90%/86% | differs |
| icit_seal | Mohenjo-daro | Harappa | 172 | 0.525 | 0.510 | +0.014 | 0.373 | 0.447 | 0.447 | 64%/100%/100% | same |
| icit_seal | Mohenjo-daro | Dholavira | 41 | 0.502 | 0.512 | -0.010 | 0.588 | 0.588 | 0.510 | 32%/58%/80% | underpowered |
| icit_seal | Mohenjo-daro | Chanhu-daro | 37 | 0.612 | 0.476 | +0.136 | 0.078 | 0.235 | 0.235 | 94%/96%/92% | underpowered |
| icit_seal | Harappa | Dholavira | 47 | 0.575 | 0.527 | +0.049 | 0.235 | 0.353 | 0.265 | 54%/58%/82% | underpowered |
| icit_seal | Harappa | Chanhu-daro | 39 | 0.624 | 0.546 | +0.078 | 0.176 | 0.353 | 0.235 | 80%/82%/80% | underpowered |
| icit_seal | Dholavira | Chanhu-daro | 20 | 0.659 | 0.447 | +0.212 | 0.020 | 0.118 | 0.265 | 76%/78%/88% | underpowered |
| icit_sealtype | Mohenjo-daro | Harappa | 227 | 0.552 | 0.509 | +0.042 | 0.078 | 0.196 | 0.294 | 96%/100%/100% | same |
| icit_sealtype | Mohenjo-daro | Dholavira | 58 | 0.534 | 0.487 | +0.047 | 0.216 | 0.404 | 0.441 | 84%/90%/96% | same |
| icit_sealtype | Mohenjo-daro | Lothal | 49 | 0.519 | 0.490 | +0.029 | 0.353 | 0.441 | 0.561 | 44%/76%/90% | underpowered |
| icit_sealtype | Mohenjo-daro | Chanhu-daro | 38 | 0.652 | 0.499 | +0.153 | 0.059 | 0.176 | 0.294 | 94%/98%/96% | underpowered |
| icit_sealtype | Mohenjo-daro | Kalibangan | 37 | 0.487 | 0.478 | +0.009 | 0.451 | 0.520 | 0.613 | 44%/70%/80% | underpowered |
| icit_sealtype | Harappa | Dholavira | 62 | 0.592 | 0.483 | +0.109 | 0.098 | 0.210 | 0.392 | 92%/92%/98% | underpowered |
| icit_sealtype | Harappa | Lothal | 55 | 0.539 | 0.527 | +0.012 | 0.353 | 0.441 | 0.420 | 44%/70%/76% | underpowered |
| icit_sealtype | Harappa | Chanhu-daro | 40 | 0.680 | 0.493 | +0.187 | 0.020 | 0.074 | 0.294 | 98%/100%/96% | differs |
| icit_sealtype | Harappa | Kalibangan | 40 | 0.482 | 0.521 | -0.039 | 0.686 | 0.706 | 0.630 | 16%/48%/48% | underpowered |
| icit_sealtype | Dholavira | Lothal | 30 | 0.494 | 0.469 | +0.025 | 0.353 | 0.441 | 0.630 | 32%/54%/54% | underpowered |
| icit_sealtype | Dholavira | Chanhu-daro | 30 | 0.617 | 0.463 | +0.153 | 0.020 | 0.074 | 0.392 | 86%/88%/88% | differs |
| icit_sealtype | Dholavira | Kalibangan | 30 | 0.445 | 0.462 | -0.017 | 0.706 | 0.706 | 0.686 | 40%/34%/48% | underpowered |
| icit_sealtype | Lothal | Chanhu-daro | 27 | 0.611 | 0.510 | +0.101 | 0.020 | 0.074 | 0.368 | 72%/70%/78% | differs (gate fails) |
| icit_sealtype | Lothal | Kalibangan | 27 | 0.541 | 0.507 | +0.034 | 0.255 | 0.425 | 0.458 | 38%/28%/46% | underpowered |
| icit_sealtype | Chanhu-daro | Kalibangan | 19 | 0.598 | 0.433 | +0.164 | 0.020 | 0.074 | 0.559 | 86%/86%/92% | differs |
| icit_sealing | Mohenjo-daro | Harappa | 62 | 0.613 | 0.508 | +0.104 | 0.020 | 0.020 | 0.039 | 84%/92%/94% | differs |
| m77_sealing | Harappa | Mohenjo-daro | 51 | 0.608 | 0.488 | +0.120 | 0.020 | 0.020 | 0.098 | 88%/94%/94% | differs |
| icit_tablet | Harappa | Mohenjo-daro | 102 | 0.774 | 0.456 | +0.318 | 0.020 | 0.020 | 0.020 | 100%/100%/100% | differs |

Part 1 verdict: {'whole': 'SUPPORTED', 'namefree': 'REFUTED'} ({'whole': {'Ur III': 'above floor', 'Latin': 'above floor', 'Old Babylonian': 'underpowered'}, 'namefree': {'Ur III': 'not above floor', 'Latin': 'underpowered', 'Old Babylonian': 'underpowered'}}); Ur III kill splits: []
Part 2 question: YES: a peripheral-town pair differs while Mohenjo-daro vs Harappa does not
