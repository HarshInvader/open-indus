# Do round seal texts share an order of their own? (sealed 2026-11-23, before any number)

Agent `paper`. This is study 3 of the Fable list dated 2026-11-23.

README #4 says round seals break Indus sign order. That leaves two readings open:
- (A) a second system with its own order rules, such as another language or a genre with its own grammar;
- (B) free strings of word signs with no order.

Round texts have only ever been scored against home models.

## Data
- The 35 texts in `experiments/round_seal_format/results.json` (`round_texts`), keeping legible Wells signs only, with length 2 or more.
- The home pool is the distinct ICIT SEAL:S texts from home sites, with length 2 or more, defined as in `round_name_shape`.

## Model and score
- **Model:** a bigram with BOS and EOS, add-k smoothing with k = 0.1, over the vocabulary of every sign in the round set plus the home pool.
- **Leave-one-out within a set:** each text is scored by a model trained on the other texts of the same set.
- **Text excess:** the mean bits per sign over 200 within-text shuffles, minus the real bits per sign.
- **Set excess:** the token-weighted mean of the text excesses.
- **p:** 1,000 draws. Each draw takes one shuffle per text and computes the set's total bits. p = (1 + number of draws with shuffled total ≤ real total) / 1,001.
- **Order found:** set excess ≥ 0.3 bits per sign and p < 0.01.

## Kill test first: power
- Take 200 random sets of home square seal texts, each matched to the round set's length distribution.
- Run the same leave-one-out procedure on each set.
- Power is the share of sets that show "order found".
- If power is under 0.8, STOP: the question is untestable at this n, and the round set is not scored.

## Then the real set, scored once
**Guard against reading weak Indus order as a second system.** For each of the 200 home sets, also score the round texts with a model trained on that home set; call the median of these the home-trained excess on round texts.

**Verdicts.**
- **(A) supported:** the round set shows "order found", AND its leave-one-out excess is greater than the home-trained excess on round texts. It is a lead for a separate order. Red team next.
- **"Order found" but not above the home-trained excess:** the order is weak Indus order, not a second system.
- **No order found at power 0.8 or more:** favours (B), free strings. Update README #4 and atlas 1.10.

## Seeds and code
- Seed 20261124.
- Code: `experiments/round_own_order/run.py`, hashed before it runs.
