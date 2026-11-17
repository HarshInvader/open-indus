"""Control (b): planted Sanskrit / Tamil name corpora at Indus size, deciphered by word-level matching.

Planting (as in experiments/decipherability, but word boundaries kept): real Rigveda name/epithet chunks
(Sanskrit) or synthetic Tamil [title] name(+case) templates, written with one sign per CV/C/V value
(101 values, random sign ids); the most frequent word types become logograms until the target share.

Candidate words for matching:
  gold  = true word segments (optimistic; Indus has no dividers)
  text  = whole texts as one unit (pessimistic, undersegmented)
Lexicons (all capped at NLEX entries, 1-8 syllables):
  K1inj_p  true-language lexicon that contains a fraction p of the corpus's syllabic word types
           (rest filled with other true-language types)  -> how much exact coverage is needed
  K1       true-language lexicon, natural (frequency-ranked wiki types / random headwords)
  K2       related language, natural (Pali+Prakrit for Sanskrit, Malayalam for Tamil)
  W:x      wrong languages (Latin, Finnish, Sumerian, and the other Indian family)
  K2shuf   K2 with values permuted across entries
  corpus_shuf  K2 against a sign-shuffled corpus
"""
import json, sys, time, random
from collections import Counter
import numpy as np
import common as C
import wm

OUT = C.HERE / "out"; OUT.mkdir(exist_ok=True)
NLEX = 5000
LD = C.LD


def plant(lang, ntok, logo, rep):
    rng = random.Random(1000 * rep + (17 if lang == "san" else 29))
    pool = LD.name_texts(lang, C.L(), max(ntok // 2, 1500) + 500, rng)
    rng.shuffle(pool)
    wc = Counter(w for t in pool for w in t)
    tot = sum(wc.values()); logos, acc = set(), 0
    for w, c in wc.most_common():
        if acc >= logo * tot - 1e-9 or len(logos) >= 320: break
        logos.add(w); acc += c
    vals = list(range(wm.NV)); rng.shuffle(vals)
    sid = {v: i for i, v in enumerate(vals)}
    lid = {w: wm.NV + i for i, w in enumerate(sorted(logos))}
    texts, words, tok = [], [], 0
    for t in pool:
        if tok >= ntok: break
        enc = [(w, (lid[w],) if w in logos else tuple(sid[LD.VIDX[x]] for x in LD.syllabify(w))) for w in t]
        texts.append([e for _, e in enc]); words += enc
        tok += sum(len(e) for _, e in enc)
    used = sorted({s for t in texts for e in t for s in e})
    m = {s: i for i, s in enumerate(used)}
    true = np.full(len(used), -1)
    for v, i in sid.items():
        if i in m: true[m[i]] = v
    for w, i in lid.items():
        if i in m: true[m[i]] = wm.NV
    texts = [[tuple(m[s] for s in e) for e in t] for t in texts]
    word_forms = {}
    for w, e in words: word_forms[tuple(m[s] for s in e)] = w
    return texts, true, word_forms, logos, acc / tot


def units(texts, mode):
    c = Counter()
    for t in texts:
        if mode == "gold":
            for e in t: c[e] += 1
        else:
            c[tuple(s for e in t for s in e)] += 1
    W = sorted(c); return W, [c[w] for w in W]


def k1_types(lang):
    d = C.L()[lang]
    if lang == "san":
        mw = [t[0] for t in d["K1"] if len(t) == 1]          # MW headwords
        wiki = Counter(w for t in d["K1"] if len(t) > 1 for w in t)
        return [w for w, _ in wiki.most_common()], mw
    wiki = Counter(w for t in d["K1"] for w in t)
    return [w for w, _ in wiki.most_common()], []


def build_lex(kind, lang, corpus_types, rng):
    r = np.random.default_rng(rng.randint(0, 10**9))
    if kind.startswith("K1inj"):
        p = float(kind.split("_")[1])
        ct = list(corpus_types); rng.shuffle(ct)
        inj = ct[:int(round(p * len(ct)))]
        inj_v = C.wm_lex(inj)
        freq, hw = k1_types(lang)
        fill = [w for w in freq + hw if w not in set(corpus_types)]
        rest = C.wm_lex(fill[:4 * NLEX])
        k = max(NLEX - len(inj_v), 0)
        idx = r.choice(len(rest), min(k, len(rest)), replace=False)
        return inj_v + [rest[i] for i in idx]
    if kind == "K1":
        freq, hw = k1_types(lang)
        if hw:   # Sanskrit: half wiki-frequent, half random MW headwords
            a = C.wm_lex(freq)[:NLEX // 2]
            b = C.sample_lex(hw, NLEX - len(a), r)
            return a + b
        return C.wm_lex(freq)[:NLEX]
    if kind == "K2" or kind.startswith("R:"):
        lg = lang if kind == "K2" else kind[2:]
        d = C.L()[lg]["K2"]
        single = [t[0] for t in d if len(t) == 1]           # dictionary headwords
        multi = Counter(w for t in d if len(t) > 1 for w in t)
        a = C.wm_lex(single)
        if len(a) >= NLEX:
            return [a[i] for i in sorted(r.choice(len(a), NLEX, replace=False))]
        b = [v for v in C.wm_lex([w for w, _ in multi.most_common()]) if v not in a]
        return a + b[:NLEX - len(a)]
    if kind.startswith("W:"):
        lg = kind[2:]
        if lg == "sux":
            return C.sample_lex([t[0] for t in C.L()["sux"]["K1"]], NLEX, r)
        wiki = Counter(w for t in C.L()[lg]["K1"] for w in t)
        return C.wm_lex([w for w, _ in wiki.most_common()])[:NLEX]
    raise ValueError(kind)


def coverage(lex, corpus_forms):
    S = {tuple(v) for v in lex}
    cv = [tuple(LD.VIDX[x] for x in LD.syllabify(w)) for w in corpus_forms]
    return float(np.mean([c in S for c in cv])) if cv else 0.0


def run_cell(lang, ntok, logo, rep, seg, kinds, restarts, log):
    texts, true, wforms, logos, share = plant(lang, ntok, logo, rep)
    W, wc = units(texts, seg)
    S = len(true)
    syl_forms = sorted({w for w in wforms.values() if w not in logos})
    tok_forms = [wforms[e] for t in texts for e in t if wforms[e] not in logos]
    rng = random.Random(rep * 101 + ntok)
    cell = dict(lang=lang, ntok=sum(len(e) for t in texts for e in t), ntexts=len(texts), logo=logo,
                logo_share=share, seg=seg, rep=rep, nunits=len(W), S=S, res={})
    t0 = time.time()
    for kind in kinds:
        if kind == "corpus_shuf":
            lex = build_lex("K2", lang, syl_forms, random.Random(rep))
            Wsh = C.shuffle_words(W, np.random.default_rng(rep))
            r = C.search(Wsh, wc, lex, S, restarts=restarts, seed=rep, oracle=False)
            cov = None
        elif kind == "K2shuf":
            lex = C.shuffle_lex(build_lex("K2", lang, syl_forms, random.Random(rep)), np.random.default_rng(rep))
            r = C.search(W, wc, lex, S, true=true, restarts=restarts, seed=rep, oracle=False); cov = None
        else:
            lex = build_lex(kind, lang, syl_forms, random.Random(rep) if kind == "K2" else rng)
            orc = kind in ("K1", "K2") or kind.startswith("K1inj")
            r = C.search(W, wc, lex, S, true=true, restarts=restarts, seed=rep, oracle=orc)
            cov = coverage(lex, tok_forms)
        rr = C.strip(r); rr["lex_token_coverage"] = cov
        if kind not in ("corpus_shuf", "K2shuf"):
            Wsh = C.shuffle_words(W, np.random.default_rng(rep + 5))
            rs = C.search(Wsh, wc, lex, S, restarts=max(restarts // 2, 4), seed=rep + 5, oracle=False)
            rr["shuf_score_tok"] = rs["score_tok"]
            rr["gain_tok"] = r["score_tok"] - rs["score_tok"]
        cell["res"][kind] = rr
        log(f"[{lang} {cell['ntok']}tok logo={logo:.1f}({share:.2f}) {seg} rep{rep} units={len(W)}] {kind:10s} "
            f"score/tok={r['score_tok']:.3f} acc={r.get('acc_tok', float('nan')):.3f} "
            f"cons={r.get('acc_cons_tok', float('nan')):.3f} cov={cov} gain={rr.get('gain_tok', float('nan')):.3f} "
            + (f"oracle/tok={r['oracle_score'] / r['ntok']:.3f} oracc={r['oracle_acc_tok']:.3f} wrong>or={r['wrong_beats_oracle']}"
               if 'oracle_score' in r else "") + f" t={time.time() - t0:.0f}s")
    return cell


KINDS = {"san": ["K1inj_1.0", "K1inj_0.5", "K1inj_0.2", "K1", "K2", "W:lat", "W:fin", "W:sux", "R:tam", "K2shuf"],
         "tam": ["K1inj_1.0", "K1inj_0.5", "K1inj_0.2", "K1", "K2", "W:lat", "W:fin", "W:sux", "R:san", "K2shuf"]}


def main():
    plan = sys.argv[1] if len(sys.argv) > 1 else "main"
    restarts = int(sys.argv[2]) if len(sys.argv) > 2 else 16
    logf = open(OUT / f"c2_{plan}.log", "a")

    def log(s):
        print(s, flush=True); logf.write(s + "\n"); logf.flush()
    cells = []
    if plan == "main":
        grid = [(lang, 10000, logo, 0, "gold") for lang in ("san", "tam") for logo in (0.0, 0.2)]
        grid += [(lang, 2500, 0.0, 0, "gold") for lang in ("san", "tam")]
        grid += [(lang, 10000, 0.0, 1, "gold") for lang in ("san", "tam")]
        grid += [(lang, 10000, 0.0, 0, "text") for lang in ("san", "tam")]
        grid += [(lang, 40000, 0.0, 0, "gold") for lang in ("san", "tam")]
    elif plan == "rest":
        grid = [("tam", 10000, 0.0, 0, "gold"), ("tam", 10000, 0.2, 0, "gold"),
                ("san", 2500, 0.0, 0, "gold"), ("tam", 2500, 0.0, 0, "gold"),
                ("san", 10000, 0.0, 0, "text"), ("san", 40000, 0.0, 0, "gold"), ("tam", 40000, 0.0, 0, "gold")]
    elif plan == "tam40":
        grid = [("tam", 40000, 0.0, 0, "gold")]
    else:
        grid = [("san", 2500, 0.0, 0, "gold")]
    for lang, ntok, logo, rep, seg in grid:
        if ntok == 40000 and (logo > 0 or rep > 0): continue
        kinds = KINDS[lang]
        if ntok == 40000 or seg == "text":
            kinds = [k for k in kinds if k not in ("K1inj_1.0", "K1inj_0.5", "K2shuf")]
        cells.append(run_cell(lang, ntok, logo, rep, seg, kinds, restarts, log))
        json.dump(cells, open(OUT / f"c2_{plan}.json", "w"), indent=1, default=float)


if __name__ == "__main__":
    main()
