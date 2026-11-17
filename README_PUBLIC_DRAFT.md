# Open Indus: decipher the Indus script by 2027

**Our goal is to decipher the Indus script by 2027, in the open.**

Today we know how the script is built, but not yet what it says. No Indus sign has a proven sound or meaning, and the language is unknown.

**What "deciphered" means here.** Sound values for at least 10 signs that beat chance on our public test bench and survive an independent red team. That is the root milestone of our task board ([board/README.md](board/README.md)). If we miss it, we will publish a measured statement of exactly what evidence is still missing.

**Our honest odds of reaching it by 2027 are under 1 in 10.** Two things would raise them:

- More texts from round seals of the Gulf type. Roughly 60 to 120 are needed and about 40 are known.
- One Indus seal tied to a person whose name is written in cuneiform.

Website: [site/index.html](site/index.html), with the findings, the live tracker and the ways to help.

## Where we are: five kinds of claim

| Step | Kind of claim | Status |
|---|---|---|
| 1 | Structure: sign order, slots, direction | Done |
| 2 | Sign roles: openers, closers, numerals | Partly done |
| 3 | Topic: what a sign is about | Open |
| 4 | Meaning: one sign, one thing | Open |
| 5 | Sound: a reading | Open (the goal) |

## How the work is done

Every idea about the script is tested the same way, so that a good-looking result cannot come from trying until something works:

1. **Seal it before you look.** The prediction, the test and the pass mark go in a file in [docs/prereg/](docs/prereg/). Its SHA-256 hash is logged in `docs/prereg/HASHES.txt` before any result is seen.
2. **Test it on texts it never saw.** A quarter of the texts are held back. They are split by text family, so that no near-copy of a held-back text is used to build the idea.
3. **Find a planted answer first.** A method that claims to recover sounds, a language or a grammar must first recover a known answer from a corpus of the same size.
4. **Let someone else try to break it.** Every positive result goes to a red team that did not produce it.
5. **Publish it either way.** Failed routes are written up with the size of effect the test could have caught.

Most of the work so far was done by a small team of AI agents with a human lead, working from one shared task board under these rules. That is one more reason the rules are strict, and why every result can be rerun from code.

## What holds so far

Each of these was found on one part of the texts, confirmed on held-back texts and attacked by a second agent. Full numbers, caveats and code are in [README.md](README.md) and in each `experiments/<area>/RESULTS.md`.

- **Sign order follows rules, not just positions.** On unseen texts the real order is picked out in 40% of runs against 5.7% by chance.
- **Corner ticks move the fish sign to the end of a text.** 40 of 73 ticked fish signs close their text, against 26% expected.
- **"Six" followed by "fish" is a fixed expression.** 7 of 10 held-out cases, against a 3% base rate.
- **Round Gulf-type seals break normal sign order, wherever they were found.** This is the current main line of attack, because names on these seals may be matched with names written in cuneiform.
- **Each kind of object (seal, tablet, copper tablet, pottery) has its own vocabulary.**

## What has been ruled out

79 routes are recorded in [docs/NEGATIVE_ATLAS.md](docs/NEGATIVE_ATLAS.md), 38 of them ruled out at a stated power. Among them:

- **Published sound keys.** Five keys were tested and none beats its own values shuffled among the signs.
- **Guessing the language from statistics.** The method calls real Latin "Munda".
- **A Linear B-style sound grid.** The method finds one in made-up syllabic scripts and nothing in the Indus texts.

## Help

Read [CONTRIBUTING.md](CONTRIBUTING.md). There are ways in for:

- programmers and statisticians;
- epigraphists, archaeologists and Assyriologists;
- museums and anyone holding seal data;
- anyone with a reading to test.

Starter tasks are listed in [site/starter_tasks.json](site/starter_tasks.json) and on the contribute page. Everyone taking part follows the [code of conduct](CODE_OF_CONDUCT.md).

## Rebuild everything

```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
# clone the public sources listed in corpus/build.py into sources/, then:
.venv/bin/python -I corpus/build.py        # builds data/ from sources/
scripts/reproduce.sh                        # reruns the headline tests in a scratch copy (slow: hours)
.venv/bin/python -I site/build.py           # rebuilds the website from the results
```

The corpus files are not in this repository, because the terms of the sources they come from are not stated. `corpus/build.py` rebuilds them from public sources.

`scripts/reproduce.sh` fixes the hash seed, so its results can differ slightly from the published ones. `docs/REPRO_REPORT.md` explains why.

## Licences and credit

Code, text and pictures are under different terms; see [LICENSING.md](LICENSING.md). The texts come from:

- Iravatham Mahadevan's 1977 concordance, made available online by the Roja Muthiah Research Library;
- the Interactive Corpus of Indus Texts (ICIT) by Bryan Wells and Andreas Fuls.

Exports and tools by others are credited in [CITATION.cff](CITATION.cff). Seal photographs on the site are cropped from excavation reports published from 1931 to 1940.

To cite this work, use [CITATION.cff](CITATION.cff).
