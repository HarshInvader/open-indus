#!/usr/bin/env python3
"""Regenerate docs/library/LIBRARY.md from docs/library/library.json.
Run: python3 -I docs/library/make_index.py"""
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOPICS = json.loads((HERE.parent.parent / "site" / "news.json").read_text())["topics"]


def cell(s):
    return str(s or "").replace("|", "/").replace("\n", " ")


def main():
    lib = json.loads((HERE / "library.json").read_text())
    rows = lib["entries"]
    by = collections.defaultdict(list)
    for e in rows:
        by[e["topic"]].append(e)
    depth = collections.Counter(e["read_depth"] for e in rows)
    rel = collections.Counter(e["relevance"] for e in rows)
    out = [
        "# Open Indus paper library",
        "",
        f"Generated from `library.json` (updated {lib['updated']}) by `make_index.py`. Do not edit by hand.",
        "",
        f"- **{len(rows)} papers**: {rel['core']} core, {rel['useful']} useful, {rel['context']} context.",
        f"- Read in full: {depth['full']}. Abstract only: {depth['abstract']}.",
        f"- Not verified (DOI or page not opened, or content from a search summary): {sum(not e['verified'] for e in rows)}.",
        "- Bears on the mismatch study: " + ", ".join(f"`{e['id']}`" for e in rows if "mismatch_study" in (e.get("touches") or [])) + ".",
        "",
        "Each entry in `library.json` has the full analysis: question, what they tried, method and data, key results, limits, ideas for us, and which of our studies it touches. The site renders it at `library.html`.",
        "",
    ]
    for key, label in TOPICS.items():
        es = by.get(key, [])
        if not es:
            continue
        out += [f"## {label} ({len(es)})", "", "| Paper | Year | Read | Relevance | Touches | Idea for us |", "|---|---|---|---|---|---|"]
        for e in es:
            link = f"https://doi.org/{e['doi']}" if e.get("doi") else e["url"]
            flag = "" if e["verified"] else " (unverified)"
            out.append(f"| [{cell(e['title'])}]({link}), {cell(e['authors'])}{flag} | {e['year']} | {e['read_depth']} | {e['relevance']} | "
                       f"{', '.join(e.get('touches') or [])} | {cell(e['ideas_for_us'])[:220]} |")
        out.append("")
    (HERE / "LIBRARY.md").write_text("\n".join(out))
    print("LIBRARY.md", len(rows))


if __name__ == "__main__":
    main()
