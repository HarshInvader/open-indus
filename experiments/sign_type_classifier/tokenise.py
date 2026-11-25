"""sign_type_classifier tokenisers. The count gate and the study import these same functions.

Each loader returns a list of clean natural lines; each line is a list of (sign_id, role) pairs.
  sign_id : reading-free sign identity (Unicode glyph for cuneiform and Japanese; the
            sign-list name for Linear B, with case folded so a syllabogram used as a logogram
            keeps one ID). The study re-codes every sign_id to an opaque integer before any
            feature is built, so no feature can see a reading or a case convention.
  role    : SYL / LOGO / DET / NUM / MEAS, from edition markup only (never from statistics).
Damage rule: a line with any damage, restoration, query, illegible or unknown mark is dropped
WHOLE. Numerals: a group of one unit repeated n times is ONE token (sign_id = the group), one
token per place, as an Indus stroke group is one sign.
Run with python3 -I. No file is written by this module.
"""
import json
import re
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]


# ----------------------------------------------------------------- Indus (M77)
def indus_numeral_signs():
    """Stroke numerals: short, tall and chevron groups from the stroke list, minus M99
    (connective) and M100 (ambiguous), as in slot_function and numeral_class."""
    d = json.load(open(REPO / "sources/shaunmortal_indus/data/stroke_signs.json"))
    keys = set(d["short"]) | set(d["tall"]) | set(d["chevron"])
    return {"M" + k for k in keys} - {"M99", "M100"}


def indus_lines():
    """Distinct M77 object-side texts, split at line breaks and breaks; runs touching a break
    are kept as separate runs (the study's features never cross a '|' or '#')."""
    import sys
    sys.path.insert(0, str(REPO))
    from corpus.load import m77_texts, distinct, runs
    num = indus_numeral_signs()
    out = []
    for t in distinct(m77_texts()):
        for r in runs(t["seq"]):
            out.append([(s, "NUM" if s in num else "UNK") for s in r])
    return out


# ----------------------------------------------------------------- cuneiform (Oracc GDL)
DROP_BREAK = {"missing", "damaged"}


class _Bad(Exception):
    pass


def _gdl_tokens(g, ctx, out):
    """Append (utf8, role) for one GDL node. ctx = role inherited from a logo group or det."""
    if not isinstance(g, dict):
        return
    if g.get("break") in DROP_BREAK or g.get("queried") or g.get("gdl_em") \
            or g.get("gdl_supplied") or g.get("gdl_implied"):
        raise _Bad("damage")
    if "x" in g:
        raise _Bad("x:" + str(g["x"]))
    if g.get("v") in ("x", "n", "..."):
        raise _Bad("illegible")
    if "det" in g:
        for s in g.get("seq", []):
            _gdl_tokens(s, "DET", out)
        return
    if "gg" in g:
        if g["gg"] not in ("logo", "ligature"):
            raise _Bad("gg:" + g["gg"])
        for s in g.get("group", []):
            # inside a determinative the group stays DET (e.g. {LU2} written as a logo group)
            _gdl_tokens(s, ctx if ctx == "DET" else ("LOGO" if g["gg"] == "logo" else ctx), out)
        return
    if g.get("n") == "n":
        u = g.get("utf8") or ""
        if not u:
            raise _Bad("no_utf8")
        out.append((u, "NUM"))          # one token per numeral group, e.g. 3(dis)
        return
    if any(k in g for k in ("v", "s", "c", "q", "form")):
        u = g.get("utf8") or ""
        if not u:
            raise _Bad("no_utf8")
        if ctx:
            role = ctx
        elif g.get("role") == "logo" or "s" in g:
            role = "LOGO"
        elif "v" in g:
            role = "SYL"
        else:
            f = g.get("form") or g.get("c") or g.get("q") or ""
            role = "LOGO" if f[:1].isupper() or f[:1] == "|" else "SYL"
        out.append((u, role))
        return
    # punctuation, r (repeat counts inside a numeral), o (operators): no token


def oracc_lines(zpaths, lang_prefix="akk"):
    """Clean lines from Oracc corpusjson zips. A line is the run of lemmas between two
    line-start nodes. Lines with any lemma not in lang_prefix are dropped (a Sumerogram inside
    an Akkadian lemma is kept: it carries logolang, not a Sumerian lemma)."""
    lines, stats = [], {"lines_seen": 0, "lines_dropped": 0, "drop_reasons": {}}

    def flush(cur, bad):
        if cur is None:
            return
        stats["lines_seen"] += 1
        if bad or not cur:
            stats["lines_dropped"] += 1
            if bad:
                stats["drop_reasons"][bad] = stats["drop_reasons"].get(bad, 0) + 1
            return
        lines.append(cur)

    for zp in zpaths:
        z = zipfile.ZipFile(zp)
        for name in sorted(n for n in z.namelist() if "/corpusjson/" in n and n.endswith(".json")):
            try:
                doc = json.loads(z.read(name))
            except Exception:
                continue
            state = {"cur": None, "bad": None}

            def walk(n):
                if isinstance(n, list):
                    for v in n:
                        walk(v)
                    return
                if not isinstance(n, dict):
                    return
                if n.get("node") == "d" and n.get("type") == "line-start":
                    flush(state["cur"], state["bad"])
                    state["cur"], state["bad"] = [], None
                    return
                if n.get("node") == "l" and state["cur"] is not None:
                    f = n.get("f", {})
                    if not str(f.get("lang", "")).startswith(lang_prefix):
                        state["bad"] = state["bad"] or "lang"
                        return
                    if state["bad"]:
                        return
                    toks = []
                    try:
                        for g in f.get("gdl", []):
                            _gdl_tokens(g, None, toks)
                    except _Bad as e:
                        state["bad"] = str(e).split(":")[0]
                        return
                    state["cur"].extend(toks)
                    return
                for k in ("cdl",):
                    if k in n:
                        walk(n[k])

            walk(doc.get("cdl", []))
            flush(state["cur"], state["bad"])
    return lines, stats


# ----------------------------------------------------------------- Linear B (DAMOS)
LB_APPARATUS = {"v.↓", "v.→", "v.", "r.", "lat.", "supra", "sup.", "inf.", "vac.", "vacat",
                "sigillum", "α", "β", "γ", "δ", "ε", ",", "/", "//", "lat. inf.", "lat. sup."}
LB_DAMAGE = ("[", "]", "⟦", "⟧", "̣", "?", "mut.", "vest", "deest", "fragmentum",
             "reliqua", "pars", "sine", "regulis", "nihil", "]", "<", ">", "{", "}")
LB_MEAS = {"T", "V", "Z", "S", "M", "N", "P", "Q", "L"}
LB_SYL = re.compile(r"^(?:[a-z]{1,3}[0-9]?|\*\d{1,2})$")
LB_LOGO = re.compile(r"^(?:\*\d{3}[a-z]?|[A-Z][A-Z0-9]*(?:[:;+][A-Za-z0-9+;:]*)*)$")


def _lb_place_tokens(n):
    out, k = [], 0
    while n > 0:
        d = n % 10
        if d:
            out.append(("NUM_1e%d_x%d" % (k, d), "NUM"))
        n //= 10
        k += 1
    return out[::-1]


def linearb_lines(keep_underdot=False):
    """Clean tablet lines from DAMOS items. Lowercase hyphenated words and lowercase single
    signs are SYL (edition convention); uppercase tokens are LOGO; a single uppercase metric
    letter is MEAS; digits are NUM by place. An uppercase syllabogram (e.g. SA, NI) is LOGO in
    role but shares the sign_id of its lowercase form."""
    lines, stats = [], {"lines_seen": 0, "lines_dropped": 0, "drop_reasons": {}}
    path = REPO / "sources/paragorth_Indus-/other-scripts/linear-a/data/damos_items.jsonl"
    for raw in open(path, encoding="utf-8"):
        it = json.loads(raw)
        for l in (it.get("content") or "").split("\n"):
            ws = l.split()
            if ws and re.fullmatch(r"\.[0-9A-Za-z]+", ws[0]):
                ws = ws[1:]
            ws = [w for w in ws if w not in LB_APPARATUS]
            if not ws:
                continue
            stats["lines_seen"] += 1
            dmg = [m for m in LB_DAMAGE if not (keep_underdot and m == "\u0323")]
            if keep_underdot:
                l = l.replace("\u0323", "")
                ws = [w.replace("\u0323", "") for w in ws]
            if any(m in l for m in dmg):
                stats["lines_dropped"] += 1
                stats["drop_reasons"]["damage"] = stats["drop_reasons"].get("damage", 0) + 1
                continue
            toks, bad = [], None
            for w in ws:
                w = w.strip(",")
                if not w:
                    continue
                if re.fullmatch(r"\d+", w):
                    toks += _lb_place_tokens(int(w))
                elif "-" in w or LB_SYL.match(w):
                    parts = [p for p in w.split("-") if p]
                    if not all(LB_SYL.match(p) for p in parts):
                        bad = "syl_shape"; break
                    toks += [(p, "SYL") for p in parts]
                elif w in LB_MEAS:
                    toks.append((w, "MEAS"))
                elif LB_LOGO.match(w):
                    sid = w.lower() if LB_SYL.match(w.lower()) else w
                    if re.fullmatch(r"\*\d{1,2}", w):
                        sid = w
                    toks.append((sid, "LOGO"))
                else:
                    bad = "unknown_token"; break
            if bad:
                stats["lines_dropped"] += 1
                stats["drop_reasons"][bad] = stats["drop_reasons"].get(bad, 0) + 1
                continue
            lines.append(toks)
    return lines, stats


# ----------------------------------------------------------------- Japanese (Wikipedia)
def _ja_class(ch):
    o = ord(ch)
    if 0x3040 <= o <= 0x309F or 0x30A0 <= o <= 0x30FF:
        return "SYL"                      # hiragana, katakana, incl. the long-vowel mark
    if 0x4E00 <= o <= 0x9FFF or 0x3400 <= o <= 0x4DBF or ch == "々":
        return "LOGO"                     # kanji (kanji numerals included: disclosed)
    if ch.isdigit() and (ch.isascii() or 0xFF10 <= o <= 0xFF19):
        return "NUM"
    return None


def japanese_lines(ja_dir):
    """Runs of kana / kanji / digits between any other character. Section headings dropped.
    A digit run becomes place tokens like Linear B (one token per non-zero place)."""
    lines, stats = [], {"lines_seen": 0, "lines_dropped": 0, "drop_reasons": {}, "files": 0,
                        "revids": []}
    for f in sorted(Path(ja_dir).glob("a*.json")):
        d = json.load(open(f, encoding="utf-8"))
        p = list(d["query"]["pages"].values())[0]
        stats["files"] += 1
        stats["revids"].append([p.get("title"), (p.get("revisions") or [{}])[0].get("revid")])
        for para in p.get("extract", "").split("\n"):
            if para.startswith("="):
                continue
            cur, digits = [], ""

            def close_digits():
                nonlocal digits
                if digits:
                    n = int("".join(str(int(c)) for c in digits))
                    cur.extend(_lb_place_tokens(n) if n else [])
                    digits = ""

            for ch in para:
                c = _ja_class(ch)
                if c == "NUM":
                    digits += ch
                    continue
                close_digits()
                if c:
                    cur.append((ch, c))
                else:
                    if cur:
                        lines.append(cur); stats["lines_seen"] += 1
                    cur = []
            close_digits()
            if cur:
                lines.append(cur); stats["lines_seen"] += 1
    return lines, stats


# ----------------------------------------------------------------- Indus-shape draws
def indus_length_dist():
    """Lengths of distinct M77 runs (the same runs indus_lines returns)."""
    return [len(r) for r in indus_lines()]


def cut_to_indus_shape(lines, lengths, rng):
    """Cut each natural line, in order, into consecutive pieces whose lengths are sampled
    from the Indus length distribution; the last piece of a line is whatever is left. Pieces
    never cross a line end."""
    pieces = []
    for ln in lines:
        i = 0
        while i < len(ln):
            k = rng.choice(lengths)
            pieces.append(ln[i:i + k])
            i += k
    return pieces


def draws(pieces, rng, size=10000, max_draws=20):
    """Disjoint draws of about `size` tokens: shuffle pieces, then fill draws in order."""
    idx = list(range(len(pieces)))
    rng.shuffle(idx)
    out, cur, n = [], [], 0
    for i in idx:
        cur.append(pieces[i]); n += len(pieces[i])
        if n >= size:
            out.append(cur); cur, n = [], 0
            if len(out) == max_draws:
                break
    return out
