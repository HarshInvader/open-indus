# Responding to JDMDH reviews

The paper is frozen as submitted (JDMDH, Episciences submission #20184; preprint doi:10.5281/zenodo.24371567, 2026-11-19). Change it only to answer reviewers.

## When the reviews arrive
1. Copy each review verbatim into a private response file in `docs/paper/submission/` (gitignored). Number every point R1.1, R1.2, R2.1 and so on.
2. Sort the points into three kinds:
   - **Fix:** errors and unclear text. Make the change.
   - **New analysis:** run it only if it is small and fits the paper's question. Write it up as a prereg and hash it before it runs, like every other test. Report the result whichever way it comes out.
   - **Decline:** out of scope, or it would turn the paper into a different one. Decline politely, give one sentence of reason, and offer it as future work.
3. Change `docs/paper/latex/main.tex` (anonymous) and `docs/paper/submission/main.tex` (named) together. The two may differ only in the author block and the repository line.
4. Every changed number must trace to a results file. Have an agent re-check the numbers against the results files, then get one independent pre-publication review (as with the first version).

## The response letter
- Start with one paragraph listing the main changes.
- Then go point by point: quote the reviewer's point, say what changed and where (section, and line or page in the new PDF), or why not.
- Thank the reviewers once, at the top. Don't argue tone.
- Never claim a check was done unless it was.

## Resubmitting
1. Compile both versions with `tectonic -X compile main.tex`.
2. Upload the named PDF as a **new version** of the Zenodo record (the record's "New version" button). Files of a published version can't be changed. The concept DOI 10.5281/zenodo.24371566 always points to the latest version.
3. On Episciences, open submission #20184 and use the revision request's "answer" or "new version" action. Give the new Zenodo version's identifier and attach the response letter.
4. Commit the anonymous source and PDF to the repo. Keep the named version and the letter out of git.

## Don't
- Don't extend the paper with new findings outside what reviewers asked for.
- Don't mention third-party work that is still in review.
- Don't use the word "crack", and don't claim any sign has a reading.
