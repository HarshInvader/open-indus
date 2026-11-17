import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import fetch
B = "http://ojs.uop.edu.pk/ancientpakistan/article/download"
idx = {a["art"]: a for a in json.load(open("experiments/open_journals/work/ap_index.json"))}
for art in sys.argv[1:]:
    a = idx[art]
    for g in a["galleys"]:
        p, s = fetch("ancientpakistan", f"{B}/{art}/{g}", f"ap_{art}_{g}.pdf")
        print(art, g, s, p, os.path.getsize(p) if p else 0, a["title"][:60])
