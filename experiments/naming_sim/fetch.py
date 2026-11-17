"""Download real onomastica (open data) into experiments/naming_sim/raw/<source>/.

Polite MediaWiki API client (1 request / ~2 s, backoff on 429). Raw responses are stored as-is (untrusted);
parsing happens in names.py, which reads them only as text/JSON.

Sources
  wiktionary/<Category>.json : {title: wikitext} for given-name categories (Old English, Old Norse, Old High
                               German, Ancient Greek, Egyptian, Tamil, Sanskrit). Etymology templates give the
                               element segmentation (e.g. {{affix|ang|æþel|ræd}}).
  wikipedia/<page>.json      : wikitext of list pages (Sangam poets), category member titles (Lakota people).
Run: .venv/bin/python experiments/naming_sim/fetch.py [wiktionary|wikipedia|all]
"""
import json, sys, time, urllib.parse, urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / "raw"
UA = "IndusNamingSim/0.1 (academic research) python-urllib"
DELAY = 2.0


def get(base, params, tries=8):
    params = dict(params, format="json", formatversion="2", maxlag="5")
    url = base + "?" + urllib.parse.urlencode(params)
    wait = 10
    for _ in range(tries):
        time.sleep(DELAY)
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=60) as r:
                txt = r.read().decode("utf-8")
            return json.loads(txt)
        except Exception as e:  # 429 / maxlag / network
            print("  retry", type(e).__name__, str(e)[:80], "wait", wait, flush=True)
            time.sleep(wait); wait = min(wait * 2, 300)
    raise RuntimeError(url)


def category_members(base, cat, ns=0):
    out, cont = [], {}
    while True:
        d = get(base, dict(action="query", list="categorymembers", cmtitle="Category:" + cat, cmlimit="500",
                           cmnamespace=str(ns), **cont))
        out += [m["title"] for m in d["query"]["categorymembers"]]
        if "continue" not in d:
            return out
        cont = {"cmcontinue": d["continue"]["cmcontinue"]}


def wikitexts(base, titles):
    out = {}
    for k in range(0, len(titles), 50):
        d = get(base, dict(action="query", prop="revisions", rvprop="content", rvslots="main",
                           titles="|".join(titles[k:k + 50])))
        for p in d["query"]["pages"]:
            if "revisions" in p:
                out[p["title"]] = p["revisions"][0]["slots"]["main"]["content"]
        print(f"  {len(out)}/{len(titles)}", flush=True)
    return out


WKT = "https://en.wiktionary.org/w/api.php"
WKP = "https://en.wikipedia.org/w/api.php"
WKT_CATS = ["Old_English_male_given_names", "Old_English_female_given_names", "Old_Norse_male_given_names",
            "Old_Norse_female_given_names", "Old_High_German_male_given_names", "Old_High_German_female_given_names",
            "Ancient_Greek_male_given_names", "Egyptian_male_given_names", "Egyptian_female_given_names",
            "Tamil_male_given_names", "Sanskrit_male_given_names"]
WKP_CATS = ["Lakota_people", "Lakota_leaders", "Oglala_people", "Hunkpapa_people", "Brulé_people",
            "Miniconjou_people", "Sicangu_people", "Cheyenne_people", "Crow_people", "Blackfoot_people",
            "Dakota_people", "Assiniboine_people", "Kiowa_people", "Arapaho_people", "Nez_Perce_people"]
WKP_PAGES = ["List_of_Sangam_poets", "Sangam_literature", "Eight_Deer_Jaguar_Claw", "Codex_Zouche-Nuttall"]


def run_wiktionary():
    d = RAW / "wiktionary"; d.mkdir(parents=True, exist_ok=True)
    for c in WKT_CATS:
        f = d / f"{c}.json"
        if f.exists():
            continue
        print(c, flush=True)
        t = category_members(WKT, c)
        f.write_text(json.dumps(wikitexts(WKT, t), ensure_ascii=False))


def run_wikipedia():
    d = RAW / "wikipedia"; d.mkdir(parents=True, exist_ok=True)
    f = d / "native_american_categories.json"
    if not f.exists():
        out = {}
        for c in WKP_CATS:
            print(c, flush=True)
            try:
                out[c] = category_members(WKP, c)
            except Exception as e:
                print("  fail", e)
        f.write_text(json.dumps(out, ensure_ascii=False))
    f = d / "pages.json"
    if not f.exists():
        f.write_text(json.dumps(wikitexts(WKP, WKP_PAGES), ensure_ascii=False))


if __name__ == "__main__":
    w = sys.argv[1] if len(sys.argv) > 1 else "all"
    if w in ("wiktionary", "all"):
        run_wiktionary()
    if w in ("wikipedia", "all"):
        run_wikipedia()
