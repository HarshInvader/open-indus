"""Tables for RESULTS.md and results.json from out/*.json."""
import json
from pathlib import Path
import numpy as np

OUT = Path(__file__).resolve().parent / "out"


def j(name):
    p = OUT / name
    return json.load(open(p)) if p.exists() else None


def f(x, d=3):
    return "-" if x is None or (isinstance(x, float) and np.isnan(x)) else (f"{x:.{d}f}" if isinstance(x, float) else str(x))


def c1():
    d = j("c1_linearb.json")
    if not d: return "", {}
    rows = ["| cond | words | tokens | lexicon | Greek acc (cons) | oracle-start acc | cognate-ID acc | Greek score/tok | best wrong (lang) | lex-shuffle | corpus-shuffle | wrong>oracle |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    key = {}
    for k, r in d.items():
        if not isinstance(r, dict): continue
        g = r["greek"]
        wr = {l: r[l]["score_tok"] for l in ("lat", "san", "fin", "sux", "tam") if l in r}
        bw = max(wr, key=wr.get) if wr else None
        rows.append(f"| {k} | {g['nwords']} | {int(g['ntok'])} | {g['nlex']} | {f(g['acc_tok'])} ({f(g['acc_cons_tok'])}) | "
                    f"{f(g['oracle_acc_tok'])} | {f(g.get('cognate_acc'))} | {f(g['score_tok'])} | "
                    f"{f(wr[bw]) if bw else '-'} ({bw}) | {f(r.get('greek_lexshuf', {}).get('score_tok'))} | "
                    f"{f(r.get('corpus_shuf', {}).get('score_tok'))} | {g['wrong_beats_oracle']} |")
        key[k] = dict(acc=g["acc_tok"], oracle_acc=g["oracle_acc_tok"], cognate_acc=g.get("cognate_acc"),
                      greek_score_tok=g["score_tok"], best_wrong=bw, best_wrong_score_tok=wr.get(bw),
                      greek_first=bool(bw is None or g["score_tok"] > wr[bw]),
                      wrong_acc=[r[l]["acc_tok"] for l in wr])
    return "\n".join(rows), key


def c2():
    cells = (j("c2_main.json") or []) + (j("c2_rest.json") or []) + (j("c2_tam40.json") or [])
    rows = ["| lang | tokens | logo | seg | units | lexicon | coverage | acc (cons) | oracle acc | wrong>oracle | score/tok | gain/tok |",
            "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    idrows = ["| lang | tokens | logo | seg | K2 rank by score (of 5) | K2 rank by gain | K1 rank by score (of 5) | K1 rank by gain | best rival (gain) | max wrong acc |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    key = []
    for c in cells:
        R = c["res"]
        for k, r in R.items():
            rows.append(f"| {c['lang']} | {c['ntok']} | {c['logo_share']:.2f} | {c['seg']} | {c['nunits']} | {k} | "
                        f"{f(r.get('lex_token_coverage'))} | {f(r.get('acc_tok'))} ({f(r.get('acc_cons_tok'))}) | "
                        f"{f(r.get('oracle_acc_tok'))} | {r.get('wrong_beats_oracle', '-')} | {f(r['score_tok'])} | {f(r.get('gain_tok'))} |")
        rivals = [k for k in R if k.startswith("W:") or k.startswith("R:")]

        def rank(k, m):
            if k not in R or m not in R[k]: return None
            return 1 + sum(1 for x in rivals if R[x].get(m, -9) > R[k][m])
        br = max(rivals, key=lambda x: R[x].get("gain_tok", -9)) if rivals else None
        mwa = max(R[x]["acc_tok"] for x in rivals) if rivals else None
        idrows.append(f"| {c['lang']} | {c['ntok']} | {c['logo_share']:.2f} | {c['seg']} | {rank('K2', 'score_tok')} | {rank('K2', 'gain_tok')} | "
                      f"{rank('K1', 'score_tok')} | {rank('K1', 'gain_tok')} | {br} ({f(R[br].get('gain_tok')) if br else '-'}) | {f(mwa)} |")
        key.append(dict(lang=c["lang"], ntok=c["ntok"], logo=c["logo_share"], seg=c["seg"],
                        acc={k: r.get("acc_tok") for k, r in R.items()},
                        oracle_acc={k: r.get("oracle_acc_tok") for k, r in R.items() if "oracle_acc_tok" in r},
                        coverage={k: r.get("lex_token_coverage") for k, r in R.items()},
                        gain={k: r.get("gain_tok") for k, r in R.items()},
                        K2_rank_score=rank("K2", "score_tok"), K2_rank_gain=rank("K2", "gain_tok"),
                        K1_rank_score=rank("K1", "score_tok"), K1_rank_gain=rank("K1", "gain_tok"), max_wrong_acc=mwa))
    return "\n".join(rows), "\n".join(idrows), key


def c3():
    d = j("c3_minimal.json") or []
    rows = ["| corpus | lexicon contains (p) | irregular edit rate e | regular change | acc (cons) | oracle acc | score/tok | shuffle/tok | wrong>oracle |",
            "|---|---|---|---|---|---|---|---|---|"]
    for r in d:
        if r["lang"] == "linb":
            rows.append(f"| Linear B 919 words | Homer10k + {r['n_injected']} cognates (p={r['p']}) | - | - | {f(r['acc_tok'])} ({f(r['acc_cons_tok'])}) | "
                        f"{f(r['oracle_acc_tok'])} | {f(r['score_tok'])} | - | {r['wrong_beats_oracle']} |")
        else:
            rows.append(f"| {r['lang']} 10k | {r['p']} | {r['e']} | {r['regfrac']} | {f(r['acc_tok'])} ({f(r['acc_cons_tok'])}) | "
                        f"{f(r['oracle_acc_tok'])} | {f(r['score_tok'])} | {f(r['shuf_score_tok'])} | {r['wrong_beats_oracle']} |")
    return "\n".join(rows), d


def c4():
    d = j("c4_bootstrap.json") or {}
    rows = ["| corpus | reference lexicon | rival | diff score/tok [95% CI] | gain-adjusted diff [95% CI] |", "|---|---|---|---|---|"]
    for case, r in d.items():
        ref = "greek_homer" if case.startswith("linb") else "K2"
        for k, v in r["vs"].items():
            rows.append(f"| {case} | {ref} | {k} | {v['diff_tok']:+.3f} [{v['ci'][0]:+.3f}, {v['ci'][1]:+.3f}] | "
                        f"{v['gain_diff_tok']:+.3f} [{v['gain_ci'][0]:+.3f}, {v['gain_ci'][1]:+.3f}] |")
    return "\n".join(rows), d


if __name__ == "__main__":
    t1, k1 = c1(); t2, t2b, k2 = c2(); t3, k3 = c3(); t4, k4 = c4()
    open(OUT / "tables.md", "w").write("## c1 Linear B\n\n" + t1 + "\n\n## c2 planted\n\n" + t2 + "\n\n### identification\n\n" + t2b +
                                       "\n\n## c3 minimal\n\n" + t3 + "\n\n## c4 bootstrap\n\n" + t4 + "\n")
    json.dump(dict(linear_b=k1, planted=k2, minimal=k3, bootstrap=k4), open(OUT / "summary.json", "w"), indent=1, default=float)
    print(open(OUT / "tables.md").read())
