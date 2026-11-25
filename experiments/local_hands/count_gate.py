"""local_hands step 3: count gate (MINIMUM.txt section 9). Counts only.

Counts eligible variant families and occurrences with their site, type and period coverage,
the dev / held-out split, and the tokens that can inform each test (strata structure only).
It computes no effect statistic: no G, no mutual information, no permutation p, and no
cross-tabulation of form against site, period or neighbour.

Run: .venv/bin/python -I experiments/local_hands/count_gate.py -> count_gate.json, count_gate.md
"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "experiments" / "split_witness"))
import lh_lib as L  # noqa: E402
import sw_lib  # noqa: E402

# Gate thresholds: copied from MINIMUM.txt section 9 (frozen there).
MIN_FAMILIES = 4
MIN_DEV_TOKENS = 1600
MIN_HELDOUT_TOKENS = 350
MIN_PL_INFORMATIVE = 1100
MIN_NB_INFORMATIVE = 1500
MIN_SITES_30 = 2

FROZEN = ["experiments/local_hands/lh_lib.py", "experiments/local_hands/power.py",
          "experiments/local_hands/power_F4.json", "experiments/local_hands/power_F8.json",
          "experiments/split_witness/sw_lib.py", "corpus/load.py", "corpus/build.py",
          "data/icit_texts.jsonl", "experiments/consensus_corpus/out/concordance.json"]


def sha(p):
    return hashlib.sha256(open(ROOT / p, "rb").read()).hexdigest()


def main():
    fams_all = L.load_families()
    text_fam = sw_lib.families()
    occ0 = L.occurrences(fams_all, text_fam)
    occ, keep = L.apply_floor(occ0)
    dev = [o for o in occ if not o["holdout"]]
    ho = [o for o in occ if o["holdout"]]

    fam_rows = []
    for f in sorted(fams_all, key=lambda m: int(m[1:])):
        d0 = Counter(o["form"] for o in occ0 if o["family"] == f and not o["holdout"])
        h0 = Counter(o["form"] for o in occ0 if o["family"] == f and o["holdout"])
        fam_rows.append(dict(family=f, variants=fams_all[f],
                             dev_tokens_per_variant={w: d0.get(w, 0) for w in fams_all[f]},
                             heldout_tokens_per_variant={w: h0.get(w, 0) for w in fams_all[f]},
                             eligible=f in keep, kept_variants=sorted(keep.get(f, []))))

    def coverage(rows):
        site = Counter(o["site"] for o in rows)
        typ = Counter(o["type"] for o in rows)
        per = [o for o in rows if o["period"]]
        per_sites = defaultdict(set)
        for o in per:
            per_sites[o["site"]].add(o["period"])
        multi = {s: sorted(v) for s, v in per_sites.items() if len(v) >= 2}
        return dict(tokens=len(rows), families=len({o["family"] for o in rows}),
                    texts=len({o["rec_id"] for o in rows}),
                    sites=len(site), by_site=dict(site.most_common()),
                    sites_with_30=sum(1 for c in site.values() if c >= 30),
                    by_type=dict(typ.most_common()),
                    tokens_with_period=len(per),
                    period_tokens_at_multi_period_sites=sum(1 for o in per if o["site"] in multi),
                    multi_period_sites={s: len(v) for s, v in multi.items()})

    out = dict(frozen={p: sha(p) for p in FROZEN},
               families_before_floor=len(fams_all), families_after_floor=len(keep),
               occurrences_before_floor=len(occ0), family_table=fam_rows,
               dev=coverage(dev), heldout=coverage(ho))
    out["dev"].update(L.informative_counts(L.arrays(dev)) if dev else {})
    out["heldout"].update(L.informative_counts(L.arrays(ho)) if ho else {})

    checks = {
        "families >= %d" % MIN_FAMILIES: len(keep) >= MIN_FAMILIES,
        "dev tokens >= %d" % MIN_DEV_TOKENS: out["dev"]["tokens"] >= MIN_DEV_TOKENS,
        "held-out tokens >= %d" % MIN_HELDOUT_TOKENS: out["heldout"]["tokens"] >= MIN_HELDOUT_TOKENS,
        "dev place-informative tokens >= %d" % MIN_PL_INFORMATIVE:
            out["dev"].get("pl_informative", 0) >= MIN_PL_INFORMATIVE,
        "dev neighbour-informative tokens >= %d" % MIN_NB_INFORMATIVE:
            out["dev"].get("nb_informative", 0) >= MIN_NB_INFORMATIVE,
        "dev sites with >= 30 tokens >= %d" % MIN_SITES_30: out["dev"]["sites_with_30"] >= MIN_SITES_30,
    }
    out["checks"] = checks
    out["gate"] = "PASS" if all(checks.values()) else "FAIL"
    json.dump(out, open(HERE / "count_gate.json", "w"), indent=1)

    md = ["# local_hands count gate", "",
          "Counts only (no effect statistic). Rules: `MINIMUM.txt`. Machine-readable: `count_gate.json`.", "",
          f"**Gate: {out['gate']}**", ""]
    md += [f"- {k}: {'yes' if v else 'NO'}" for k, v in checks.items()]
    md += ["", f"Families: {len(fams_all)} with >= 2 exclusive ICIT variants in the concordance; "
           f"{len(keep)} keep >= 2 variants with >= {L.MIN_VARIANT_TOKENS} dev tokens.", "",
           "| Family | Variants | Dev tokens per variant | Held-out tokens per variant | Eligible |",
           "|---|---|---|---|---|"]
    for r in fam_rows:
        md.append("| {} | {} | {} | {} | {} |".format(
            r["family"], " ".join(r["variants"]),
            " ".join(f"{w}:{c}" for w, c in r["dev_tokens_per_variant"].items()),
            " ".join(f"{w}:{c}" for w, c in r["heldout_tokens_per_variant"].items()),
            "yes (" + " ".join(r["kept_variants"]) + ")" if r["eligible"] else "no"))
    for part in ("dev", "heldout"):
        c = out[part]
        md += ["", f"## {part}", "",
               f"- tokens {c['tokens']}, families {c['families']}, texts {c['texts']}, sites {c['sites']} "
               f"({c['sites_with_30']} with >= 30 tokens)",
               f"- place-informative tokens {c.get('pl_informative')}, neighbour-informative tokens {c.get('nb_informative')}",
               f"- by site: " + ", ".join(f"{s} {n}" for s, n in c["by_site"].items()),
               f"- by type: " + ", ".join(f"{s} {n}" for s, n in c["by_type"].items()),
               f"- tokens with a period label {c['tokens_with_period']}; at sites with >= 2 period labels "
               f"{c['period_tokens_at_multi_period_sites']} ({', '.join(f'{s} {n} labels' for s, n in c['multi_period_sites'].items()) or 'none'})"]
    open(HERE / "count_gate.md", "w").write("\n".join(md) + "\n")
    print("\n".join(md))


if __name__ == "__main__":
    main()
