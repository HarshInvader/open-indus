# local_hands count gate

Counts only (no effect statistic). Rules: `MINIMUM.txt`. Machine-readable: `count_gate.json`.

**Gate: FAIL**

- families >= 4: yes
- dev tokens >= 1600: NO
- held-out tokens >= 350: yes
- dev place-informative tokens >= 1100: NO
- dev neighbour-informative tokens >= 1500: NO
- dev sites with >= 30 tokens >= 2: yes

Families: 18 with >= 2 exclusive ICIT variants in the concordance; 6 keep >= 2 variants with >= 10 dev tokens.

| Family | Variants | Dev tokens per variant | Held-out tokens per variant | Eligible |
|---|---|---|---|---|
| M15 | W154 W156 | W154:26 W156:36 | W154:13 W156:20 | yes (W154 W156) |
| M119 | W027 W028 | W027:0 W028:0 | W027:2 W028:3 | no |
| M169 | W406 W407 | W406:10 W407:57 | W406:3 W407:17 | yes (W406 W407) |
| M180 | W297 W298 | W297:9 W298:7 | W297:6 W298:1 | no |
| M186 | W315 W317 | W315:9 W317:9 | W315:2 W317:3 | no |
| M193 | W336 W337 | W336:4 W337:5 | W336:6 W337:7 | no |
| M205 | W491 W495 | W491:12 W495:18 | W491:2 W495:10 | yes (W491 W495) |
| M210 | W501 W502 | W501:3 W502:4 | W501:0 W502:0 | no |
| M244 | W630 W632 W636 | W630:23 W632:23 W636:5 | W630:6 W632:8 W636:10 | yes (W630 W632) |
| M254 | W526 W527 | W526:5 W527:42 | W526:6 W527:18 | no |
| M261 | W625 W850 | W625:8 W850:33 | W625:3 W850:7 | no |
| M267 | W817 W861 | W817:97 W861:119 | W817:90 W861:97 | yes (W817 W861) |
| M336 | W704 W705 W706 | W704:3 W705:80 W706:49 | W704:1 W705:87 W706:33 | yes (W705 W706) |
| M341 | W711 W717 | W711:7 W717:38 | W711:1 W717:13 | no |
| M348 | W772 W773 | W772:3 W773:6 | W772:7 W773:3 | no |
| M375 | W808 W832 | W808:5 W832:32 | W808:3 W832:12 | no |
| M381 | W812 W814 | W812:5 W814:2 | W812:4 W814:0 | no |
| M397 | W370 W371 | W370:5 W371:6 | W370:2 W371:4 | no |

## dev

- tokens 550, families 6, texts 503, sites 23 (2 with >= 30 tokens)
- place-informative tokens 394, neighbour-informative tokens 482
- by site: Mohenjo-daro 262, Harappa 173, Dholavira 29, Lothal 22, Kalibangan 19, Chanhu-daro 10, Nausharo 5, Lakhanjo-daro 4, Gola Dhoro (Bagasra) 3, Rakhigarhi 3, Shikarpur 3, Allahdino 2, Banawali 2, Chandigarh 2, Desalpur 2, Nindowari-damb 2, Failaka 1, Daimabad 1, Hulas 1, Khirsara 1, Kot-Diji 1, Susa 1, Tell Umma 1
- by type: seal 354, tab_moulded 56, pot 39, tab_incised 37, sealing 24, tablet 23, other 17
- tokens with a period label 216; at sites with >= 2 period labels 212 (Dholavira 4 labels, Harappa 4 labels, Kalibangan 4 labels, Lothal 9 labels, Mohenjo-daro 9 labels, Nausharo 3 labels)

## heldout

- tokens 386, families 6, texts 352, sites 13 (2 with >= 30 tokens)
- place-informative tokens 313, neighbour-informative tokens 325
- by site: Mohenjo-daro 209, Harappa 107, Dholavira 21, Lothal 20, Chanhu-daro 12, Kalibangan 6, Nausharo 4, Allahdino 2, Bakkar Buthi 1, Rahman-deri 1, Jhukar 1, Lakhanjo-daro 1, Juna Khatiya 1
- by type: seal 293, tab_moulded 39, sealing 18, tab_incised 11, pot 10, other 8, tablet 7
- tokens with a period label 165; at sites with >= 2 period labels 157 (Harappa 4 labels, Dholavira 4 labels, Lothal 9 labels, Mohenjo-daro 9 labels)
