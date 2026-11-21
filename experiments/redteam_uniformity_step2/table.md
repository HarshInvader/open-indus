# Red team of step 2: tables

Generated from `results.json` (`rt2.py report`). 50 draws per condition, seed 20261127. Median AUCs.

## A1/A2 name stripping variants vs structural within-city floors

| corpus | variant | floor split | n/side | between | within | null median | Δ | p floor | gate |
|---|---|---|---|---|---|---|---|---|---|
| ur3 | loose | U_reign | 84 | 0.657 | 0.573 | 0.496 | +0.084 | 0.020 | 94% |
| ur3 | loose | U_coll | 46 | 0.628 | 0.545 | 0.512 | +0.082 | 0.039 | 68% |
| ur3 | loose | G_reign | 67 | 0.627 | 0.711 | 0.475 | -0.084 | 1.000 | 92% |
| ur3 | loose | G_coll | 53 | 0.619 | 0.570 | 0.495 | +0.048 | 0.059 | 72% |
| ur3 | strict | U_reign | 57 | 0.614 | 0.562 | 0.492 | +0.052 | 0.078 | 80% |
| ur3 | strict | U_coll | 36 | 0.651 | 0.547 | 0.515 | +0.104 | 0.059 | 48% |
| ur3 | strict | G_reign | 42 | 0.621 | 0.682 | 0.501 | -0.061 | 0.941 | 52% |
| ur3 | strict | G_coll | 38 | 0.638 | 0.582 | 0.508 | +0.056 | 0.098 | 46% |
| ur3 | noTG | U_reign | 227 | 0.840 | 0.703 | 0.492 | +0.137 | 0.020 | 100% |
| ur3 | noTG | U_coll | 167 | 0.823 | 0.615 | 0.494 | +0.208 | 0.020 | 100% |
| ur3 | noTG | G_reign | 199 | 0.829 | 0.642 | 0.498 | +0.187 | 0.020 | 100% |
| ur3 | noTG | G_coll | 155 | 0.814 | 0.534 | 0.492 | +0.280 | 0.020 | 100% |
| ur3 | noTGtheo | U_reign | 227 | 0.781 | 0.680 | 0.510 | +0.102 | 0.020 | 100% |
| ur3 | noTGtheo | U_coll | 158 | 0.761 | 0.611 | 0.503 | +0.150 | 0.020 | 100% |
| ur3 | noTGtheo | G_reign | 203 | 0.789 | 0.626 | 0.496 | +0.163 | 0.020 | 100% |
| ur3 | noTGtheo | G_coll | 151 | 0.765 | 0.499 | 0.512 | +0.267 | 0.020 | 100% |
| ur3 | noPN | U_reign | 100 | 0.768 | 0.595 | 0.492 | +0.173 | 0.020 | 98% |
| ur3 | noPN | U_coll | 47 | 0.713 | 0.554 | 0.504 | +0.159 | 0.020 | 50% |
| ur3 | noPN | G_reign | 76 | 0.742 | 0.715 | 0.499 | +0.027 | 0.137 | 86% |
| ur3 | noPN | G_coll | 62 | 0.730 | 0.556 | 0.513 | +0.174 | 0.020 | 78% |
| cdli | loose | U_reign | 122 | 0.682 | 0.653 | 0.504 | +0.029 | 0.078 | 98% |
| cdli | loose | G_reign | 67 | 0.621 | 0.649 | 0.497 | -0.028 | 0.843 | 88% |
| cdli | strict | U_reign | 61 | 0.632 | 0.645 | 0.476 | -0.013 | 0.765 | 68% |
| cdli | strict | G_reign | 36 | 0.584 | 0.704 | 0.476 | -0.120 | 1.000 | 64% |
| cdli | noTG | U_reign | 227 | 0.834 | 0.707 | 0.491 | +0.126 | 0.020 | 100% |
| cdli | noTG | G_reign | 199 | 0.824 | 0.635 | 0.492 | +0.189 | 0.020 | 100% |
| cdli | noTGtheo | U_reign | 227 | 0.790 | 0.697 | 0.496 | +0.093 | 0.020 | 100% |
| cdli | noTGtheo | G_reign | 207 | 0.783 | 0.588 | 0.511 | +0.195 | 0.020 | 100% |
| cdli | noPN | U_reign | 100 | 0.749 | 0.626 | 0.494 | +0.123 | 0.020 | 98% |
| cdli | noPN | G_reign | 65 | 0.722 | 0.694 | 0.492 | +0.028 | 0.137 | 92% |
| ur3 | wholeAtNF | U_reign | 68 | 0.787 | 0.623 | 0.495 | +0.164 | 0.020 | 90% |
| ur3 | wholeAtNF | G_reign | 58 | 0.771 | 0.558 | 0.491 | +0.213 | 0.020 | 76% |
| lat | loose | ge_rlp_vs_bwhe | 44 | 0.658 | 0.638 | 0.490 | +0.020 | 0.255 | 70% |
| lat | loose | br_north_vs_south | 32 | 0.613 | 0.466 | 0.501 | +0.147 | 0.020 | 60% |
| lat | strict | ge_rlp_vs_bwhe | 25 | 0.638 | 0.889 | 0.489 | -0.251 | 0.902 | 20% |
| lat | strict | br_north_vs_south | 17 | 0.627 | 0.889 | 0.519 | -0.262 | 0.804 | 36% |
| lat | noUNIT | ge_rlp_vs_bwhe | 119 | 0.625 | 0.541 | 0.517 | +0.084 | 0.020 | 98% |
| lat | noUNIT | br_north_vs_south | 72 | 0.620 | 0.457 | 0.497 | +0.163 | 0.020 | 100% |
| lat | noPN | ge_rlp_vs_bwhe | 43 | 0.677 | 0.619 | 0.497 | +0.058 | 0.020 | 74% |
| lat | noPN | br_north_vs_south | 29 | 0.699 | 0.571 | 0.471 | +0.128 | 0.020 | 48% |

| family | verdict | min gated Δ |
|---|---|---|
| ur3|loose | not above floor | -0.084 |
| ur3|strict | above floor | +0.052 |
| ur3|noTG | above floor | +0.137 |
| ur3|noTGtheo | above floor | +0.102 |
| ur3|noPN | not above floor | +0.027 |
| ur3|wholeAtNF | above floor | +0.164 |
| cdli|loose | not above floor | -0.028 |
| cdli|strict | underpowered |  |
| cdli|noTG | above floor | +0.126 |
| cdli|noTGtheo | above floor | +0.093 |
| cdli|noPN | not above floor | +0.028 |
| lat|loose | underpowered |  |
| lat|strict | underpowered |  |
| lat|noPN | underpowered |  |
| lat|noUNIT | above floor | +0.084 |

## A3 planted names in Mohenjo-daro vs Harappa seals (real labels)

Share of draws with AUC − step-2 within median > observed step-2 Δ. Excluded at ≥ 95%.

| pool | form | r=0.05 | r=0.1 | r=0.2 | r=0.3 | r=0.5 | r=0.75 | r=1.0 | max consistent |
|---|---|---|---|---|---|---|---|---|---|
| m77_seal | sign | 0.551 (74%) | 0.560 (78%) | 0.591 (100%) | 0.627 (100%) | 0.718 (100%) | 0.827 (100%) | 0.915 (100%) | 0.1 |
| m77_seal | spelt | 0.559 (76%) | 0.567 (78%) | 0.606 (98%) | 0.652 (100%) | 0.755 (100%) | 0.862 (100%) | 0.946 (100%) | 0.1 |
| m77_seal | ur3emp | 0.549 (68%) | 0.556 (64%) | 0.564 (78%) | 0.595 (92%) | 0.641 (100%) | 0.710 (100%) | 0.784 (100%) | 0.3 |
| icit_seal | sign | 0.531 (52%) | 0.536 (56%) | 0.571 (98%) | 0.614 (98%) | 0.704 (100%) | 0.826 (100%) | 0.915 (100%) | 0.1 |
| icit_seal | spelt | 0.523 (46%) | 0.546 (68%) | 0.593 (94%) | 0.641 (100%) | 0.743 (100%) | 0.845 (100%) | 0.934 (100%) | 0.2 |
| icit_seal | ur3emp | 0.528 (58%) | 0.537 (58%) | 0.551 (74%) | 0.574 (92%) | 0.627 (100%) | 0.695 (100%) | 0.773 (100%) | 0.3 |
| icit_sealtype | sign | 0.553 (52%) | 0.565 (72%) | 0.613 (98%) | 0.651 (100%) | 0.733 (100%) | 0.841 (100%) | 0.937 (100%) | 0.1 |
| icit_sealtype | spelt | 0.550 (48%) | 0.574 (80%) | 0.616 (100%) | 0.674 (100%) | 0.768 (100%) | 0.870 (100%) | 0.950 (100%) | 0.1 |
| icit_sealtype | ur3emp | 0.556 (60%) | 0.547 (46%) | 0.566 (80%) | 0.597 (94%) | 0.643 (100%) | 0.726 (100%) | 0.804 (100%) | 0.3 |

Ur III reference: 99.8% of raw Umma + Girsu legends carry a personal name (1.86 per legend, 35.7% of tokens).

## A4 floor bias: step-2 Part 2 pairs under three references

| family | a | b | n | between | within | null med | Δ floor | Δ null | Δ cons | q floor | q chance | verdict floor / null / cons |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| m77_seal | Mohenjo-daro | Harappa | 200 | 0.540 | 0.535 | 0.497 | +0.005 | +0.043 | +0.005 | 0.458 | 0.245 | same / same / same |
| m77_seal | Mohenjo-daro | Lothal | 60 | 0.469 | 0.487 | 0.475 | -0.018 | -0.006 | -0.018 | 0.627 | 0.549 | underpowered / same / underpowered **flip** |
| m77_seal | Mohenjo-daro | Chanhu-daro | 42 | 0.627 | 0.516 | 0.471 | +0.111 | +0.156 | +0.111 | 0.163 | 0.245 | underpowered / underpowered / underpowered |
| m77_seal | Mohenjo-daro | Kalibangan | 38 | 0.583 | 0.481 | 0.493 | +0.102 | +0.090 | +0.090 | 0.270 | 0.245 | underpowered / underpowered / underpowered |
| m77_seal | Harappa | Lothal | 67 | 0.538 | 0.471 | 0.498 | +0.068 | +0.040 | +0.040 | 0.196 | 0.327 | underpowered / underpowered / underpowered |
| m77_seal | Harappa | Chanhu-daro | 44 | 0.631 | 0.466 | 0.513 | +0.164 | +0.117 | +0.117 | 0.098 | 0.245 | differs / underpowered / underpowered **flip** |
| m77_seal | Harappa | Kalibangan | 44 | 0.569 | 0.445 | 0.469 | +0.125 | +0.100 | +0.100 | 0.157 | 0.245 | underpowered / underpowered / underpowered |
| m77_seal | Lothal | Chanhu-daro | 34 | 0.571 | 0.330 | 0.473 | +0.241 | +0.097 | +0.097 | 0.065 | 0.245 | differs / underpowered / underpowered **flip** |
| m77_seal | Lothal | Kalibangan | 34 | 0.602 | 0.324 | 0.488 | +0.278 | +0.115 | +0.115 | 0.065 | 0.245 | differs / underpowered / underpowered **flip** |
| m77_seal | Chanhu-daro | Kalibangan | 22 | 0.605 | 0.397 | 0.470 | +0.207 | +0.135 | +0.135 | 0.065 | 0.245 | differs / underpowered / underpowered **flip** |
| icit_seal | Mohenjo-daro | Harappa | 172 | 0.525 | 0.510 | 0.510 | +0.014 | +0.014 | +0.014 | 0.447 | 0.447 | same / same / same |
| icit_seal | Mohenjo-daro | Dholavira | 41 | 0.502 | 0.512 | 0.501 | -0.010 | +0.001 | -0.010 | 0.588 | 0.510 | underpowered / underpowered / underpowered |
| icit_seal | Mohenjo-daro | Chanhu-daro | 37 | 0.612 | 0.476 | 0.487 | +0.136 | +0.125 | +0.125 | 0.235 | 0.235 | underpowered / underpowered / underpowered |
| icit_seal | Harappa | Dholavira | 47 | 0.575 | 0.527 | 0.501 | +0.049 | +0.075 | +0.049 | 0.353 | 0.265 | underpowered / underpowered / underpowered |
| icit_seal | Harappa | Chanhu-daro | 39 | 0.624 | 0.546 | 0.485 | +0.078 | +0.140 | +0.078 | 0.353 | 0.235 | underpowered / underpowered / underpowered |
| icit_seal | Dholavira | Chanhu-daro | 20 | 0.659 | 0.447 | 0.528 | +0.212 | +0.131 | +0.131 | 0.118 | 0.265 | underpowered / underpowered / underpowered |
| icit_sealtype | Mohenjo-daro | Harappa | 227 | 0.552 | 0.509 | 0.498 | +0.042 | +0.054 | +0.042 | 0.196 | 0.294 | same / underpowered / same **flip** |
| icit_sealtype | Mohenjo-daro | Dholavira | 58 | 0.534 | 0.487 | 0.483 | +0.047 | +0.051 | +0.047 | 0.404 | 0.441 | same / underpowered / same **flip** |
| icit_sealtype | Mohenjo-daro | Lothal | 49 | 0.519 | 0.490 | 0.494 | +0.029 | +0.025 | +0.025 | 0.441 | 0.561 | underpowered / underpowered / underpowered |
| icit_sealtype | Mohenjo-daro | Chanhu-daro | 38 | 0.652 | 0.499 | 0.489 | +0.153 | +0.163 | +0.153 | 0.176 | 0.294 | underpowered / underpowered / underpowered |
| icit_sealtype | Mohenjo-daro | Kalibangan | 37 | 0.487 | 0.478 | 0.481 | +0.009 | +0.006 | +0.006 | 0.520 | 0.613 | underpowered / underpowered / underpowered |
| icit_sealtype | Harappa | Dholavira | 62 | 0.592 | 0.483 | 0.490 | +0.109 | +0.103 | +0.103 | 0.210 | 0.392 | underpowered / underpowered / underpowered |
| icit_sealtype | Harappa | Lothal | 55 | 0.539 | 0.527 | 0.479 | +0.012 | +0.060 | +0.012 | 0.441 | 0.420 | underpowered / underpowered / underpowered |
| icit_sealtype | Harappa | Chanhu-daro | 40 | 0.680 | 0.493 | 0.496 | +0.187 | +0.183 | +0.183 | 0.074 | 0.294 | differs / underpowered / underpowered **flip** |
| icit_sealtype | Harappa | Kalibangan | 40 | 0.482 | 0.521 | 0.493 | -0.039 | -0.011 | -0.039 | 0.706 | 0.630 | underpowered / underpowered / underpowered |
| icit_sealtype | Dholavira | Lothal | 30 | 0.494 | 0.469 | 0.509 | +0.025 | -0.014 | -0.014 | 0.441 | 0.630 | underpowered / underpowered / underpowered |
| icit_sealtype | Dholavira | Chanhu-daro | 30 | 0.617 | 0.463 | 0.502 | +0.153 | +0.115 | +0.115 | 0.074 | 0.392 | differs / underpowered / underpowered **flip** |
| icit_sealtype | Dholavira | Kalibangan | 30 | 0.445 | 0.462 | 0.494 | -0.017 | -0.048 | -0.048 | 0.706 | 0.686 | underpowered / underpowered / underpowered |
| icit_sealtype | Lothal | Chanhu-daro | 27 | 0.611 | 0.510 | 0.474 | +0.101 | +0.136 | +0.101 | 0.074 | 0.368 | differs (gate fails) / underpowered / underpowered **flip** |
| icit_sealtype | Lothal | Kalibangan | 27 | 0.541 | 0.507 | 0.483 | +0.034 | +0.057 | +0.034 | 0.425 | 0.458 | underpowered / underpowered / underpowered |
| icit_sealtype | Chanhu-daro | Kalibangan | 19 | 0.598 | 0.433 | 0.512 | +0.164 | +0.086 | +0.086 | 0.074 | 0.559 | differs / underpowered / underpowered **flip** |
| icit_sealing | Mohenjo-daro | Harappa | 62 | 0.613 | 0.508 | 0.496 | +0.104 | +0.117 | +0.104 | 0.020 | 0.039 | differs / differs / differs |
| m77_sealing | Harappa | Mohenjo-daro | 51 | 0.608 | 0.488 | 0.478 | +0.120 | +0.130 | +0.120 | 0.020 | 0.098 | differs / differs / differs |
| icit_tablet | Harappa | Mohenjo-daro | 102 | 0.774 | 0.456 | 0.501 | +0.318 | +0.273 | +0.273 | 0.020 | 0.020 | differs / differs / differs |

Part 1 families under the three references:

- ur3|whole: d_floor above floor (+0.158); d_null above floor (+0.351); d_cons above floor (+0.158)
- cdli|whole: d_floor above floor (+0.165); d_null above floor (+0.352); d_cons above floor (+0.165)
- lat|whole: d_floor above floor (+0.123); d_null above floor (+0.165); d_cons above floor (+0.123)
- ob|whole: d_floor underpowered (); d_null underpowered (); d_cons underpowered ()
- ur3|namefree: d_floor not above floor (+0.009); d_null above floor (+0.110); d_cons not above floor (+0.009)
- cdli|namefree: d_floor underpowered (); d_null underpowered (); d_cons underpowered ()
- lat|namefree: d_floor underpowered (); d_null underpowered (); d_cons underpowered ()
- ob|namefree: d_floor underpowered (); d_null underpowered (); d_cons underpowered ()

## A5 sealings and tablets

```
{
 "strict_icit": {
  "n_side": 57,
  "between": 0.605952380952381,
  "within": 0.5150375939849624,
  "delta": 0.09091478696741861,
  "null_med": 0.4976490046665485,
  "p_floor": 0.0196078431372549,
  "p_chance": 0.0784313725490196,
  "power": 0.8,
  "q_floor": 0.0196078431372549,
  "verdict": "differs"
 },
 "cross_icit": {
  "n_side": 62,
  "X1": 0.7242420236206593,
  "X2": 0.6038505319578019,
  "X3": 0.6203134383206805,
  "X4": 0.7365726795718314,
  "d_HAsealing": 0.12039149166285734,
  "d_MDsealing": -0.11625924125115084,
  "gate_X1": 0.02,
  "gate_X3": 0.04,
  "verdict": "underpowered"
 },
 "strict_m77": {
  "n_side": 43,
  "between": 0.5612389595656754,
  "within": 0.3942346649380115,
  "delta": 0.16700429462766386,
  "null_med": 0.48948280862732685,
  "p_floor": 0.0196078431372549,
  "p_chance": 0.29411764705882354,
  "power": 1.0,
  "q_floor": 0.0196078431372549,
  "verdict": "differs"
 },
 "cross_m77": {
  "n_side": 62,
  "X1": 0.7537379949164975,
  "X2": 0.7379032258064516,
  "X3": 0.6514718843645337,
  "X4": 0.6495967741935484,
  "d_HAsealing": 0.015834769110045888,
  "d_MDsealing": 0.0018751101709852946,
  "gate_X1": 0.04,
  "gate_X3": 0.04,
  "verdict": "underpowered"
 },
 "mound_m77": {
  "n_side": 8,
  "between": 0.5334821428571428,
  "within": 0.4910714285714286,
  "delta": 0.04241071428571419,
  "p_floor": 0.43137254901960786,
  "power": 0.46
 },
 "tab_moulded": {
  "n_side": 42,
  "between": 0.6405106707317073,
  "within": 0.4901277584204413,
  "delta": 0.150382912311266,
  "p_floor": 0.0196078431372549,
  "p_chance": 0.058823529411764705,
  "power": 0.96,
  "verdict": "differs"
 },
 "tab_noncopper": {
  "n_side": 46,
  "between": 0.6078704593503748,
  "within": 0.45942028985507244,
  "delta": 0.14845016949530232,
  "p_floor": 0.0784313725490196,
  "p_chance": 0.11764705882352941,
  "power": 0.96,
  "verdict": "differs"
 },
 "dup_icit": {
  "Mohenjo-daro": {
   "raw": 134,
   "distinct": 133,
   "largest_cluster": 2,
   "top5": [
    2,
    1,
    1,
    1,
    1
   ]
  },
  "Harappa": {
   "raw": 68,
   "distinct": 64,
   "largest_cluster": 3,
   "top5": [
    3,
    2,
    2,
    1,
    1
   ]
  },
  "clean": {
   "Harappa": 63,
   "Mohenjo-daro": 131
  },
  "strict": {
   "Harappa": 57,
   "Mohenjo-daro": 123
  }
 },
 "dup_m77": {
  "Mohenjo-daro": {
   "raw": 126,
   "distinct": 75,
   "largest_cluster": 9,
   "top5": [
    9,
    8,
    7,
    6,
    3
   ]
  },
  "Harappa": {
   "raw": 367,
   "distinct": 162,
   "largest_cluster": 49,
   "top5": [
    49,
    36,
    15,
    9,
    9
   ]
  },
  "clean": {
   "Harappa": 147,
   "Mohenjo-daro": 65
  },
  "strict": {
   "Mohenjo-daro": 51,
   "Harappa": 116
  }
 }
}
```
