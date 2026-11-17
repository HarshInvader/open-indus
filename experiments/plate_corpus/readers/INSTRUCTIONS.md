# Reading task: count and identify signs on small seal photographs

You are one of two independent readers. Work alone, from the images only.

## Material

- `P/` and `C/` each hold photographs of small stone stamp seals, or of impressions taken from them, from an ancient script. Each image is named by a random ID (e.g. `P111.png`). The two folders are separate batches; treat each image on its own.
- The sign chart is `chart_01.png` ... `chart_06.png`: 417 reference drawings, each labelled with its sign number (M1 ... M417). Signs are drawn in the orientation of an impression.
- Use only these files. Do not open any other file or folder on this computer and do not search the web. You have no other information about these objects and must not look for any.

## What to record for each image

1. `face`: does the photo look like the seal itself (signs mirror-reversed relative to the chart) or an impression (signs as in the chart)? `seal`, `impression` or `unsure`.
2. `n_lines`: number of lines of signs. Most texts are one line along the top; some have a second line (or a short second line, sometimes a single sign placed lower down).
3. `lines`: for each line, top to bottom, the signs in the order you SEE them from LEFT to RIGHT. Give each sign your best chart number ("M342"). If a sign is there but you cannot identify it, write "?" (it still counts as a sign). Count strokes that belong together as one sign the way the chart does (for example a group of short vertical strokes is one numeral sign, not several signs).
4. `conf`: per sign, 0 = guess, 1 = probable, 2 = sure.
5. `unreadable`: true only if you cannot even count the signs.
6. `notes`: one short line (e.g. damage, blur, uncertain line break).

Count only signs of the script. Ignore the animal or human figures, the object or post standing in front of an animal, edges, cracks, and any handwritten number on or near the photo.

Look at each image at full size (crop or zoom into parts of it if useful; you may use Python with Pillow via `.venv/bin/python -I` to crop or enlarge, writing only into `/tmp/pc_readers/work_<your letter>/`). Compare doubtful signs against the chart.

## Output

Write one JSON file per batch, exactly this shape:

```json
[
  {"id": "P111", "face": "impression", "unreadable": false, "n_lines": 2,
   "lines": [["M342", "?", "M99"], ["M1"]],
   "conf": [[2, 0, 1], [1]],
   "notes": "second line is one sign under the first line, right"}
]
```

Before you start each batch, run `date +%s` and record it; do the same when you finish. Put both numbers in a small file `time_<letter>_<batch>.txt` (two lines: start, end).
