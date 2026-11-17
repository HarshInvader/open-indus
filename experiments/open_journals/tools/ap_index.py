"""Crawl Ancient Pakistan OJS archive -> issues -> article titles/links (HTML only)."""
import sys, re, json, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch import fetch
B = "http://ojs.uop.edu.pk/ancientpakistan"
issues = set()
for page in range(1, 6):
    url = B + "/issue/archive" + (f"/{page}" if page > 1 else "")
    p, s = fetch("ancientpakistan", url, f"archive_{page}.html")
    if not p: break
    h = open(p, encoding="utf-8", errors="replace").read()
    new = set(re.findall(r'/ancientpakistan/issue/view/(\w+)', h))
    if not new - issues and page > 1: break
    issues |= new
print("issues", sorted(issues))
arts = []
for i in sorted(issues):
    p, s = fetch("ancientpakistan", f"{B}/issue/view/{i}", f"issue_{i}.html")
    if not p: print("fail", i, s); continue
    h = open(p, encoding="utf-8", errors="replace").read()
    t = re.search(r'<title>\s*(.*?)\s*\|', h, re.S)
    for m in re.finditer(r'<h3 class="title">\s*<a[^>]*href="[^"]*/article/view/(\d+)"[^>]*>(.*?)</a>', h, re.S):
        title = re.sub(r'\s+', ' ', re.sub('<[^>]+>', '', m.group(2))).strip()
        # galley links after
        seg = h[m.end(): m.end() + 3000]
        g = re.findall(r'/article/view/%s/(\d+)' % m.group(1), seg)
        arts.append({"issue": i, "issue_title": t.group(1).strip() if t else "", "art": m.group(1), "title": title, "galleys": sorted(set(g))})
json.dump(arts, open("experiments/open_journals/work/ap_index.json", "w"), indent=1)
print(len(arts))
