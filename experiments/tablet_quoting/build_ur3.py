"""Extract sealed Ur III tablets (ORACC epsd2/admin/ur3) as sign sequences: legend lines vs body lines.
Run: .venv/bin/python -I experiments/tablet_quoting/build_ur3.py
Writes data/ur3_sealed.jsonl: {"p": P-number, "prov": provenience, "legends": [[signs]...], "body": [[signs] per line]}.
Inputs are parsed as data (JSON), never executed. Prints shape only.
"""
import json, re, zipfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
Z = ROOT / "experiments/meaning_classes_seal/raw/ur3.zip"
OUT = HERE / "data"; OUT.mkdir(exist_ok=True)


def signs_of(form):
    """'lu2-{d}szara2' -> ['lu2', 'd', 'szara2']; numbers kept as one sign; damage marks dropped."""
    f = re.sub(r"[\[\]#?!<>⸢⸣]", "", form)
    parts = re.split(r"[-.{}\s]+", f)
    return [p for p in parts if p and p != "x"]


def main():
    z = zipfile.ZipFile(Z)
    cat = json.loads(z.read("epsd2/admin/ur3/catalogue.json"))
    members = cat.get("members", cat)
    prov = {k: (v.get("provenience") or "?") for k, v in members.items()} if isinstance(members, dict) else {}
    out = []
    for nm in z.namelist():
        if "/corpusjson/" not in nm or not nm.endswith(".json"):
            continue
        s = z.read(nm)
        if b"seal" not in s:
            continue
        d = json.loads(s)
        lines = {}; order = []; cur = [None]

        def walk(x):
            if isinstance(x, dict):
                if x.get("node") == "d" and x.get("type") == "line-start":
                    cur[0] = x.get("label", "")
                    if cur[0] not in lines:
                        lines[cur[0]] = []; order.append(cur[0])
                elif x.get("node") == "l" and cur[0] is not None:
                    form = x.get("f", {}).get("form", "")
                    if form:
                        lines[cur[0]] += signs_of(form)
                for v in x.values():
                    walk(v)
            elif isinstance(x, list):
                for v in x:
                    walk(v)
        walk(d.get("cdl", []))
        leg = {}; body = []
        for lab in order:
            m = re.match(r"seal (\d+)", lab)
            if m:
                leg.setdefault(m.group(1), []).extend(lines[lab])
            elif lines[lab]:
                body.append(lines[lab])
        leg = [v for v in leg.values() if v]
        if leg and body:
            p = Path(nm).stem
            out.append(dict(p=p, prov=prov.get(p, "?"), legends=leg, body=body))
    with open(OUT / "ur3_sealed.jsonl", "w") as f:
        for r in out:
            f.write(json.dumps(r) + "\n")
    print(dict(sealed_tablets=len(out), prov=Counter(r["prov"] for r in out).most_common(8),
               mean_legend_signs=round(sum(len(l) for r in out for l in r["legends"]) / sum(len(r["legends"]) for r in out), 2),
               mean_body_signs=round(sum(len(x) for r in out for x in r["body"]) / len(out), 1)))


if __name__ == "__main__":
    main()
