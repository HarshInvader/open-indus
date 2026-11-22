# Eye review for stamp impressions on high-prior Yale tablets (sealed 2026-11-22)

Agent `paper`. The trained and zero-shot detectors both failed (atlas 9.2). Instead, a vision model reviews whole photos the way a person would.

## Pool
707 Yale Ur III and Old Babylonian tablets with CC0 photos whose record names Ur (Tell Muqayyar) or Larsa, or mentions Dilmun, Magan or Meluhha. YBC 5447's Gulf stamp is on a tablet dated to Gungunum of Larsa; Ur was the Gulf trade port. List: `experiments/stamp_detector/raw/list_eye_pool.txt` (catalogue numbers in the result file).

## Kill test (run first, blind)
- 30 images in random order (seed 20261122): YBC 5447's Yale photo plus 29 random Ur III/OB tablets from the gate test set. The key is kept outside the repo and hashed here: sha256 422bed050048cf8f3d4af023b93151fd6c71f3050893ab747351b0644162b53c.
- A fresh reviewer agent (not told that a control is present) marks each image: stamp-seal impression (round or oval, not a rolled band) visible yes / no / unsure, with location.
- Pass needs both: YBC 5447 marked yes with the stamp correctly located; at most 1 of the 29 others marked yes.
- Fail: stop, record in atlas 9.2.

## If it passes
The same reviewer brief runs on the 707-tablet pool in batches. Every yes or unsure goes to a review queue (catalogue number, photo link, date, named parties) for experts. A yes is a lead, not a find.

## Result (2026-11-22)
Fail. The blind reviewer (Sonnet) marked YBC 5447 "no": it saw the impression on the edge but read it as a rolled band of figures, not a round stamp. On the Yale photo the impression indeed shows no round outline. 0 of 29 others marked yes; 5 unsure (YPM BC 013581, 003812, 014455, 007985 and one more), all Ur III; none looked like a clear stamp. Key hash verified. Pool review not run; pool download stopped.

Lesson: the only Gulf control does not look like a "round stamp" on the photo. Any detector or reviewer that searches for stamp shape would miss it. This explains all three failures (trained, zero-shot, eye review). Finding foreign seals needs iconography experts, not shape.
