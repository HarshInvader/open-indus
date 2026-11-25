# Licence note for `wikipedia_rows.csv`

- **What it is:** transcriber A's rows for names that BIGR lacks, built by `../transcriber_a.py` from the wikitext of English Wikipedia ruler pages at fixed revisions.
- **Licence:** Creative Commons Attribution-ShareAlike 4.0, https://creativecommons.org/licenses/by-sa/4.0/ . This file is offered under the same licence.
- **Attribution:** text by Wikipedia contributors. Each row names its page and revision in the column `ref`. The page history is at `https://en.wikipedia.org/w/index.php?title=<title>&action=history`, and a revision is at `https://en.wikipedia.org/w/index.php?oldid=<revision id>`.
- **Changes made:** the two legends of a passage were copied as printed, with `<big>` tags removed. The Kharosthi legend, which these pages give in Latin letters, was put in lower case and cut into aksharas, and its spaces were removed. The columns `name_id`, `n_types` and `same_person` were added.
- **Kept apart:** no row from BIGR (ODbL 1.0) is in this file. The two files are joined in memory only.

## Pinned revisions

Fetched once on 2026-11-25, in one request, with the User-Agent `open-research-site/1.0`, into a new empty directory outside the repo. The wikitext itself is not kept in the repo.

Request: `https://en.wikipedia.org/w/api.php?action=query&prop=revisions&rvprop=ids|timestamp|sha1|size|content&rvslots=main&format=json&formatversion=2&revids=<the 27 ids below, joined by |>`

SHA-256 of the answer as saved (`revisions.json`, 241,213 bytes): `8963b3bd9f2817c6f1569800c9bcd0303e304ad897465c552b78a1e140d69159`. The script checks each revision id and the SHA-1 of each wikitext.

| page | revision id | revision time (UTC) | SHA-1 of the wikitext |
|---|---|---|---|
| Abdagases I | 1381234186 | 2026-10-20T21:46:16Z | `45a3dcb3e46053f30d8ba04f8b0b6070c64f0785` |
| Arta (Kamuia) | 1358068536 | 2026-06-06T10:50:57Z | `ae273700d19b39ac9c892fbe2d69631ec903bb9a` |
| Aspavarma | 1382534177 | 2026-10-29T03:46:21Z | `ff14e4e7c41b616c822c417b3d413577fc1915ac` |
| Azes I | 1358748801 | 2026-06-10T18:11:50Z | `6dcbb9f75d5e23b175a5b651f267d280f9314e35` |
| Azes II | 1358748804 | 2026-06-10T18:11:53Z | `5e7fc59e6d6f15e171b1ab9655ab6906fb48ce69` |
| Azilises | 1358748808 | 2026-06-10T18:11:55Z | `dc49522c3f42a90634e9006fd0b041e37a7b23e3` |
| Bhumaka | 1359985380 | 2026-06-18T14:08:07Z | `d3952bdebac65ee342cbe81630251539f27c3366` |
| Chashtana | 1358751547 | 2026-06-10T18:34:50Z | `43d3dbeb355eeb66e942c36c0ee637c49896ce19` |
| Gondophares | 1383209160 | 2026-11-01T15:26:24Z | `f4ce96b8a91b57f71d0161be27f7ef1dc214b540` |
| Hagana (satrap) | 1328846766 | 2025-12-22T03:31:07Z | `a6d30ca57e298437c312446de0c6ff87c36f6591` |
| Indravarma | 1358757511 | 2026-06-10T19:20:46Z | `196ed8bb043571a60d48609427c4937e6ca82964` |
| Kharahostes | 1358759400 | 2026-06-10T19:33:05Z | `f18e077e75e8e60afe446ca4d578eb13cbb7f56c` |
| Kujula Kadphises | 1371524053 | 2026-08-26T23:53:11Z | `5962b37916ec2326e4aacc72042d08618e98b6d3` |
| Liaka Kusulaka | 1288827786 | 2025-05-04T23:28:23Z | `f3a30287201663af3fe16f76600e9dd6f30d5048` |
| Maues | 1362867327 | 2026-07-06T18:26:58Z | `15a42633dd9022a1e90d8ea4949f44b822eacb44` |
| Nahapana | 1358597747 | 2026-06-09T18:59:58Z | `d02cd968fc6c07e53664faf3a0f4b59aa6cb6694` |
| Pacores | 1356673019 | 2026-05-29T04:05:06Z | `aba30f6e82b00f5f9c7c76d4caee7bf36cf80fe5` |
| Rajuvula | 1361592437 | 2026-06-28T22:45:09Z | `e769a3ab28be85e93054573441d7f3e0840450f0` |
| Sases | 1381234523 | 2026-10-20T21:49:42Z | `a789e5c1142bb4845197e3924a6a16fb24b38443` |
| Spalagadames | 1288818538 | 2025-05-04T22:27:40Z | `4c82b9890af7a636014bf04bbb3015df9ba1a7a3` |
| Spalahores | 1358897325 | 2026-06-11T17:51:20Z | `6fa82524f0993f0f199a4e22d0bc0cb88e95a87e` |
| Spalirisos | 1288811012 | 2025-05-04T21:40:21Z | `c0ccb67ece3e3c7c50d9336c3fc841135f1eb191` |
| Vijayamitra | 1358901808 | 2026-06-11T18:29:26Z | `1f71f073a508f732823c85a10b42bf5b37eb22d0` |
| Vima Kadphises | 1381610209 | 2026-10-23T17:32:13Z | `e5ec40a3cbae5fcd3e9f5b0a1b786357cfe2b11e` |
| Vima Takto | 1371524207 | 2026-08-26T23:54:16Z | `daced5b716b7e6ba9af97581c2ae35a62362a4b9` |
| Vonones of Sakastan | 1358738489 | 2026-06-10T16:53:15Z | `96dfbe735e88e39888c1d46c1266ee27633c5bac` |
| Zeionises | 1288793306 | 2025-05-04T19:57:32Z | `e612581b883e8c06de24176baa091c49b3f9eebe` |

These are the 27 ruler pages outside BIGR that the drafter's count used. Three of its titles were redirects and are pinned under their targets (Chashtana, Indravarma, Spalirisos). "Hagana" redirected to an unrelated page and is pinned as "Hagana (satrap)". "Vonones (Indo-Scythian king)" does not exist and is pinned as "Vonones of Sakastan".

## What gives a row

A row needs a passage that prints a Greek legend and a Kharosthi legend of the same coin. Twelve of the 27 pages have one. The other pages give at most a name form in each script, which is not a legend, so they give no row.
