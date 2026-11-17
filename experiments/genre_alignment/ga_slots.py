"""Slot annotation for seal legends.

Cuneiform (word level, lines kept) -> one slot label per word:
  SEAL_OF   kišib "seal of" (possessive head that opens the legend)
  OWNER     the owner's personal name
  TITLE     an office/profession (owner's or father's), incl. toponym/temple qualifiers
  KIN       kinship relator: dumu "son of", dumu-munus "daughter of", dam "wife of"
  FATHER    the father's (or husband's) name, the word(s) after KIN
  SERV      servitude relator: arad / arad2 / geme2 "servant of" (incl. arad2-zu "your servant")
  LORD      the deity or king served, or heading a presentation seal
  EPITHET   royal / divine epithets in a LORD block (lugal kal-ga, lugal uri5ki-ma ...)
  CONJ      u3 "and" (co-owners)

Indus (sign level) -> one slot per sign from the functional_reading parse (readings.csv, read only):
  OPEN (role O), CONN (C), NUM (S,T,U), FISH (F), NOUN (N), TITLE (I, and every non-closer sign
  inside a TITLE-BLOCK constituent), CLOSER (J), BFISH (B, bracketed-fish closer), POST (P).
Coarse Indus level merges NUM+FISH+NOUN -> CORE and BFISH -> CLOSER.
"""
import csv, json, re
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent

SEALOF = {"kiszib3", "kiszib", "{na4}kiszib3", "{na4}kiszib", "kunuk", "na4-kiszib", "{na4}kunuk"}
KIN = {"dumu", "dumu-munus", "dumu-me", "dumu-mi2", "dam", "mar", "ma-ar", "dumu-mesz"}
SERV = {"arad2", "arad", "arad2-zu", "arad-zu", "arad2-da-ni", "arad2-da-ni-ir", "arad2-su2", "arad2-su",
        "arad-su2", "arad-su", "geme2", "geme2-zu", "geme2-da-ni", "ir3", "ir11", "warad", "ir3-zu",
        "arad-da-ni", "arad2-ni", "geme2-ni", "arad-zu-ne"}
SERV_SUFFIXED = {w for w in SERV if "-" in w}            # 'your/his servant': no LORD follows
SERV_LINK = {"sza", "sza-at"}                              # Akkadian 'of' after arad/geme
CONJ = {"u3"}
EPI = {"lugal", "kal-ga", "uri5{ki}-ma", "an-ub-da", "limmu2-ba", "ub-da", "an", "da-num2", "dingir",
       "kalam-ma", "a-ga-de3{ki}", "ki-en-gi", "ki-uri", "nita", "nita-kal-ga", "lugal-kal-ga",
       "ar-ba-im", "ki-ib-ra-tim", "an-ub-da-limmu2-ba", "da-nu-um", "szar", "ma-tim", "lugal-a-ni",
       "an-na", "dumu-an-na", "sukkal", "zi", "e2-kur", "e2-babbar", "e2-babbar2", "dingir-ra-ni",
       "tab-ba", "an-ki", "ra-bi-um", "lugal-la-ni", "nin", "kalam", "lugal-e", "dumu-an", "sza3-ga"}
ROYAL = {"{d}szu-{d}suen", "{d}amar-{d}suen", "{d}i-bi2-{d}suen", "{d}szul-gi", "szul-gi", "ur-{d}namma",
         "ur-{d}nammu", "szar-ka3-li2-szar3-ri2", "{d}szar-ka3-li2-szar3-ri2", "{d}na-ra-am-{d}suen",
         "na-ra-am-{d}suen", "ha-am-mu-ra-pi2", "sa-am-su-i-lu-na", "am-mi-s,a-du-qa2", "am-mi-di-ta-na",
         "am-mi-di-ta-na-ke4", "a-bi-e-szu-uh", "zi-im-ri-li-im", "{d}ri-im-{d}suen", "{d}szu-i3-li2-szu",
         "{d}isz-bi-er3-ra", "{d}li-pi2-it-esz18-dar", "su-mu-la-el", "ib-bi-{d}suen", "{d}bur-{d}suen",
         "{d}i-din-{d}da-gan", "{d}isz-me-{d}da-gan", "{d}ur-{d}nin-urta", "ri-im-{d}suen",
         "{d}su-mu-el", "{d}gu-un-gu-nu-um", "ia-ah-du-li-im", "ia-as2-ma-ah-{d}iszkur", "szu-dur-ul",
         "ri-mu-usz", "ma-an-isz-ti-su", "lugal-uszumgal"}
SEED_TITLES = {"dub-sar", "ensi2", "ugula", "nu-banda3", "szabra", "sagi", "kuruszda", "lunga", "sipa", "gudu4",
               "dam-gar3", "aga3-us2", "muhaldim", "sukkal", "szusz3", "ra2-gaba", "szagina", "sa12-du5",
               "sanga", "lukur", "sza13-dub-ba", "agrig", "nu-banda3-gu4", "ma2-lah5", "gu-za-la2", "nimgir",
               "szandana", "dub-sar-mah", "kurusza", "aszgab", "nar", "isib", "ka-guru7", "um-mi-a", "gal",
               "gudu4-abzu", "masz2-szu-gid2-gid2", "sza3-tam", "i3-du8", "ensi", "nu-esz3", "abgal", "en"}
KI = re.compile(r"\{ki\}")
INDUS_COARSE = {"NUM": "CORE", "FISH": "CORE", "NOUN": "CORE", "BFISH": "CLOSER"}
ROLE2SLOT = {"O": "OPEN", "C": "CONN", "S": "NUM", "T": "NUM", "U": "NUM", "F": "FISH", "N": "NOUN",
             "I": "TITLE", "J": "CLOSER", "B": "BFISH", "P": "POST"}


def load_cun(group):
    return [json.loads(l) for l in open(HERE / f"data/seals_{group}.jsonl")]


def build_lexicons(groups=("ur3", "ob", "oakk", "oa")):
    """data-driven title and lord lexicons over all cuneiform seal corpora"""
    ds = Counter(); first = Counter(); after_kin = Counter(); after_serv = Counter()
    for g in groups:
        for r in load_cun(g):
            ws = [w for l in r["lines"] for w in l]
            for w in set(ws): ds[w] += 1
            first[ws[0]] += 1
            for a, b in zip(ws, ws[1:]):
                if a in KIN: after_kin[b] += 1
                if a in SERV or a in SERV_LINK: after_serv[b] += 1
    titles = set(SEED_TITLES)
    for w, n in ds.items():
        if n >= 3 and first[w] / n < 0.05 and after_kin[w] / n < 0.3 and after_serv[w] / n < 0.3 \
                and w not in KIN | SERV | SEALOF | CONJ | EPI | ROYAL | SERV_LINK and not w.startswith("{d}"):
            titles.add(w)
    lords = set(ROYAL) | {w for w, n in after_serv.items() if n >= 2 and w.startswith("{d}")}
    return titles, lords


def tag_cun(lines, titles, lords):
    """returns list of (word, slot) in reading order"""
    ws = [(w, li) for li, l in enumerate(lines) for w in l]
    out = []; state = "start"; i = 0
    while i < len(ws):
        w, li = ws[i]
        if i == 0:
            if w in SEALOF:
                out.append((w, "SEAL_OF")); state = "owner"; i += 1; continue
            if w in lords and not (len(ws) > 1 and (ws[1][0] in KIN or ws[1][0] in SERV)):
                out.append((w, "LORD")); state = "lordblock"; i += 1; continue
            out.append((w, "OWNER")); state = "afterowner"; i += 1; continue
        if w in SEALOF:
            out.append((w, "SEAL_OF")); state = "owner"
        elif w in KIN:
            out.append((w, "KIN")); state = "father"
        elif w in SERV:
            out.append((w, "SERV")); state = "serv_done" if w in SERV_SUFFIXED else "lord"
        elif w in SERV_LINK and state in ("lord",):
            out.append((w, "SERV"))
        elif w in CONJ:
            prev = out[-1][1] if out else ""
            out.append((w, "CONJ")); state = "lord" if prev in ("LORD", "EPITHET") else "owner"
        elif state == "owner":
            out.append((w, "OWNER")); state = "afterowner"
        elif state == "father":
            out.append((w, "FATHER")); state = "afterfather"
        elif state == "lord":
            out.append((w, "LORD")); state = "lordblock"
        elif state == "lordblock":
            # epithets until a new line that does not look like an epithet line -> owner name
            if (w in EPI or KI.search(w) or w in titles) and not (ws[i - 1][1] != li and w not in EPI and not KI.search(w)):
                out.append((w, "EPITHET"))
            elif ws[i - 1][1] == li:
                out.append((w, "EPITHET"))
            else:
                out.append((w, "OWNER")); state = "afterowner"
        elif w in titles or KI.search(w):
            out.append((w, "TITLE"))
        elif state in ("afterowner", "afterfather") and ws[i - 1][1] == li and out[-1][1] in ("OWNER", "FATHER"):
            out.append((w, out[-1][1]))          # multi-word name on the same line
        elif out and out[-1][1] == "TITLE":
            out.append((w, "TITLE"))             # title complement (e.g. nu-banda3 gu4 {d}szara2)
        elif state == "serv_done":
            out.append((w, "EPITHET"))
        else:
            out.append((w, "TITLE" if not w.startswith("{d}") else "EPITHET"))
        i += 1
    return out


def cun_corpus(group, titles=None, lords=None):
    if titles is None: titles, lords = build_lexicons()
    texts = []
    for r in load_cun(group):
        t = tag_cun(r["lines"], titles, lords)
        texts.append({"id": r["pid"], "toks": [w for w, _ in t], "slots": [s for _, s in t]})
    return texts


# ---------------------------------------------------------------- Indus
def _constituents(reading):
    return re.findall(r"\[([A-Z\-+()a-z ]+): ([^\]]*)\]", reading)


def indus_corpus(split=None, coarse=False, object_type="seal"):
    """distinct M77 seal texts (one per distinct sign sequence) with slot labels.
    split: None (all), 'dev' or 'heldout' (v2 split as written in readings.csv)."""
    seen = set(); texts = []
    for r in csv.DictReader(open(ROOT / "experiments/functional_reading/readings.csv")):
        if r["object_type"] != object_type: continue
        if split and r["split"] != split: continue
        if "#" in r["signs"]: continue
        toks, roles = [], []
        for t in r["parse_roles"].split():
            if "/" not in t: continue
            s, ro = t.split("/"); toks.append(s); roles.append(ro)
        if not toks: continue
        key = tuple(toks)
        if key in seen: continue
        seen.add(key)
        slots = [ROLE2SLOT[ro] for ro in roles]
        # signs inside a TITLE-BLOCK constituent (except its closer) are TITLE
        cons = _constituents(r["reading"]); k = 0
        for name, body in cons:
            sg = [x for x in re.split(r"[+ ]", body) if x.startswith("M") or x.startswith("OOV")]
            for j, x in enumerate(sg):
                if k + j < len(slots) and name.startswith("TITLE") and slots[k + j] != "CLOSER":
                    slots[k + j] = "TITLE"
            k += len(sg)
        if coarse: slots = [INDUS_COARSE.get(s, s) for s in slots]
        texts.append({"id": r["text_no"] + "/" + r["side"], "toks": toks, "slots": slots})
    return texts


if __name__ == "__main__":
    import random
    titles, lords = build_lexicons()
    print("titles", len(titles), "lords", len(lords))
    for g in ("ur3", "ob", "oakk", "oa"):
        T = cun_corpus(g, titles, lords)
        c = Counter(s for t in T for s in t["slots"])
        print(g, len(T), dict(c))
    random.seed(1)
    for g, n in (("ur3", 25), ("ob", 20)):
        T = cun_corpus(g, titles, lords)
        for t in random.sample(T, n):
            print(g, " ".join(f"{w}/{s}" for w, s in zip(t["toks"], t["slots"])))
    I = indus_corpus()
    print("indus seals distinct", len(I), dict(Counter(s for t in I for s in t["slots"])))
