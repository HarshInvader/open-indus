"""R9 (review 2): how many Mohenjo-daro and Harappa seal objects the M77 and ICIT editions share.
Descriptive count from the existing link tables, no scoring:
  register links  experiments/audit_followups/out/b_editor_agreement.json via consensus_corpus/cooc.matched_pairs
                  (1930s excavation registers; never signs; MD, Harappa, Chanhu-daro only)
  sign links      experiments/consensus_corpus/out/seq_links.json (best same-site ICIT record, distance <= 0.5;
                  biased toward agreement, so a lower bound on true overlap)
Also lists the two suspect Chanhu-daro links named in the paper (M77 6203, 6204). Writes overlap.json."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "experiments" / "consensus_corpus"))
sys.path.insert(0, str(ROOT / "experiments" / "audit_followups"))
from cooc import matched_pairs  # noqa: E402
from corpus.load import m77_texts, icit_texts  # noqa: E402

SITE = {"Mohenjodaro": "Mohenjo-daro", "Chanhudaro": "Chanhu-daro"}
SITES = ("Mohenjo-daro", "Harappa", "Chanhu-daro")


def main():
    m77 = {(t["text_no"], t["side"]): t for t in m77_texts()}
    icit = {t["id"]: t for t in icit_texts()}
    reg = {(mt["text_no"], mt["side"]): it["id"] for p, mt, it in matched_pairs()}
    seq = {tuple(json.loads(k)): v["icit"] for k, v in
           json.load(open(ROOT / "experiments/consensus_corpus/out/seq_links.json")).items()}
    out = {}
    for site in SITES:
        m_seal = [k for k, t in m77.items() if SITE.get(t["site"], t["site"]) == site and t["object_type"] == "seal"]
        m_obj = {k[0] for k in m_seal}
        i_seal = {i for i, t in icit.items() if t["site"] == site and (t["type"] or "").startswith("SEAL")}
        r = {k: reg[k] for k in m_seal if k in reg}
        s = {k: seq[k] for k in m_seal if k in seq and k not in reg}
        u = {**s, **r}
        icit_hit = Counter(u.values())
        to_seal = {k: v for k, v in u.items() if v in i_seal}
        out[site] = dict(
            m77_seal_objects=len(m_obj), m77_seal_sides=len(m_seal), icit_seal_records=len(i_seal),
            linked_register=len(r), linked_signs=len(s), linked_total=len(u),
            linked_objects=len({k[0] for k in u}),
            linked_to_icit_seal=len(to_seal), distinct_icit_records=len(set(u.values())),
            distinct_icit_seal_records=len(set(to_seal.values())),
            icit_records_shared_by_2plus_m77_sides=sum(1 for c in icit_hit.values() if c > 1))
    # the two suspect Chanhu-daro links named in the paper
    sus = {}
    allk = {**seq, **reg}
    for no in (6203, 6204, 6124):
        for k in [k for k in m77 if k[0] == no]:
            iid = allk.get(k)
            sus[f"{no}.{k[1]}"] = dict(m77_seq=" ".join(m77[k]["seq"]), icit=iid,
                                       how="register" if k in reg else "signs" if k in seq else None,
                                       icit_seq=" ".join(icit[iid]["seq"]) if iid in icit else None,
                                       icit_type=icit[iid]["type"] if iid in icit else None)
    out["suspect_links"] = sus
    json.dump(out, open(HERE / "overlap.json", "w"), indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
