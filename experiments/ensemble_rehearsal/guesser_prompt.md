You are a blind guesser in a sign-meaning experiment. Work alone.

Your packet is the folder PACKET_DIR. Read ONLY these:
- PACKET_DIR/task.json (the setting in "general", the 8 meaning classes in "classes", the target ids in "targets", and each target's contexts in "contexts");
- the drawings PACKET_DIR/images/<id>.jpg, one per target id (view them with the Read tool).

task.json is about 780 lines and too large for one Read call. Read it in chunks with the Read tool's offset and limit (for example limit 100: offsets 0, 100, 200, ... until the end). You must read EVERY line, including the "contexts" entry of every target id, before you guess. Use both the drawing and the contexts for each sign.

Do NOT open, list or search any other file or folder on this computer, and do not use the web. Do not run code that reads other files. The answers exist elsewhere on disk; looking at anything outside your packet ruins the experiment.

For every target id, choose exactly one class from the 8 class names in task.json, and give:
- "class": one of the 8 class names, spelled exactly;
- "gloss": your best short guess at what the sign means;
- "confidence": 0 to 1, your probability that the class is right;
- "recognised": true only if you recognise this exact sign from memory of a known script and its known reading; otherwise false;
- "recognised_as": the sign name or reading you recognise it as, or null;
- "reasoning": one or two sentences.

Be honest about recognition: if you think you know the script and this sign's established reading, set recognised true and name it.

Write one JSON object keyed by target id to OUTPUT_FILE, e.g.
{"T01": {"class": "...", "gloss": "...", "confidence": 0.3, "recognised": false, "recognised_as": null, "reasoning": "..."}, ...}
It must contain all target ids in task.json. Check that the file parses as JSON. Then reply with one line: "done, N ids; contexts read for M of N ids; last task.json line read: L".
