# Checking the foreign readings against published images (board task #12, H1)

## Verdict

**Partial.** The only open source with images of the West Asian seals that I could get is Gadd 1932 ("Seals of ancient Indian style found at Ur"; archive.org item in.gov.ignca.33779, in `raw/`). Its plates are coarse halftones: they show how many signs there are and their layout, but individual sign identities cannot be read from them. Gadd's written descriptions were more useful than the plates. They correct four identities in the foreign corpus:

1. **ICIT 3887 and M77 9902 are one object: Gadd 18, BM 123059, bull mating a cow.** Gadd describes five characters: a damaged fish, two men side by side, and two others. That matches M77 (M65-M1-M1-M245-M245). It does not match the 3-sign ICIT/Laursen reading (W190-W091-W603). The object had been **counted twice**, and both copies were flagged non-Indus.
2. **M77 9842 is Gadd 12, the water-carrier "hieroglyphic" seal, not Gadd 3.** Mahadevan read the pictorial device as signs M175-M12-M182; M12 is the water-carrier sign. Gadd treats it as a picture, not an ordinary inscription. It is now excluded from the order and crib tests (row UR-10). The ICIT 3899 seal that I had merged with it is a separate object.
3. **M77 9845 is Gadd 15 (U.8685), which is Laursen no. 20.** The paragorth transcription lists Laursen no. 20 as "missing", so I had also listed it separately (UR-08). It was a duplicate and is removed.
4. **Gadd 4 conflict.** Gadd says no. 4 keeps only a "fish" sign and part of another. Mahadevan's Gadd 4 is 9834 = M75, which is a fish, so that agrees. Laursen no. 18 / ICIT 5231 also cite Gadd 4 but read a man sign plus W405. This is unresolved; neither text is in the flagged set.

There is also a count conflict on **Gadd 16 (UR-02): Gadd says four characters, ICIT has six and M77 five.**

## Effect on task #1

I re-ran the pre-registered flag with the same model and rule, after deduplication and the exclusion. **9 of 38 scorable objects now break Indus order**, against 1.9 expected (binomial p = 8.5e-5); task #1 had 10/39. The KN-bigram check gives 12. By shape: round seals and cylinders 7/23, square 2/7, other 0/8. The conclusion of #1 stands. The corrected files are `experiments/foreign_corpus/foreign_corpus.csv` and `order_flags.csv` (54 objects).

## For the crib attack (#4)

`readings_check.csv` gives a status for each flagged and borderline object and a column `use_in_crib_attack`:
- **yes, 9 objects:** UR-01, UNPROV-02 (M77 reading), SUSA-02, BAHRAIN-01, BAHRAIN-06, BAHRAIN-07, GIRSU-02, SALUT-01, UNPROV-03.
- **Run in both reading directions:** SUSA-02 and BAHRAIN-01, whose direction is disputed.
- **Sensitivity set only:** the borderline objects.
- **Exclude:** UR-10, which is pictorial.

## Not done

- **No sign-by-sign verification for any object.** The Gadd halftones are too coarse. These sources were not obtained in an open copy:
  - Amiet 1972/1973, Kjaerum 1983/1994, Al-Sindi 1999
  - Laursen 2010 (harappa.com blocks bots; Semantic Scholar returns 403)
  - Parpola 1994b
  - Frenez 2016 (Salut)

  For 6 of the 9 "yes" objects, the only image check is the earlier paragorth comparison with drawings, or none at all.
- **The four new objects were not transcribed:** Jalalabad, the Knox cylinder, Umm al-Quwain and Babylon. Only Jalalabad has a published discussion of its signs (`../foreign_corpus/raw/jalalabad_2021.pdf`), and that reading has 3-5 alternatives.
- **Reading direction is checked for none of the objects.**

What would finish this task: open scans of Parpola 1994b and of CISI vol. 3.1 (2010), which photographs the West Asian finds. Neither is on archive.org under the searches I tried.
