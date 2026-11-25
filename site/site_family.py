"""Shared touches for every site in the Open Citizen Science family, applied to built HTML.

add_og: Open Graph and Twitter card tags. Each page keeps its own <title> and description;
  all pages share the site's card image. Pages that already carry og:image are left alone.
add_parent_link: a breadcrumb in front of a project's logo, "(o) Open Citizen Science / <project>".
  On tablets only the ring mark and the slash show; on phones it is hidden (the footer links home).

A copy of open-citizen-science/tools/site_family.py, used by build.py;
keep the two in step.
"""
import html, re
from pathlib import Path


def add_og(dist, base_url, image_url, site_name, size=(2400, 1260)):
    dist, base_url = Path(dist), base_url.rstrip("/")
    for f in dist.rglob("*.html"):
        t = f.read_text()
        if 'property="og:image"' in t or "</head>" not in t:
            continue
        m = re.search(r"<title>(.*?)</title>", t, re.S)
        title = html.unescape(m.group(1).strip()) if m else site_name
        m = re.search(r'<meta name="description" content="([^"]*)"', t)
        desc = html.unescape(m.group(1)) if m else ""
        rel = f.relative_to(dist).as_posix()
        path = "" if rel == "index.html" else rel[:-len("index.html")] if rel.endswith("/index.html") else rel[:-5]
        a = lambda s: html.escape(s, quote=True)
        tags = (f'<meta property="og:type" content="website"><meta property="og:site_name" content="{a(site_name)}">'
                f'<meta property="og:title" content="{a(title)}">'
                + (f'<meta property="og:description" content="{a(desc)}">' if desc else "")
                + f'<meta property="og:url" content="{a(base_url + "/" + path)}">'
                f'<meta property="og:image" content="{a(image_url)}"><meta property="og:image:width" content="{size[0]}">'
                f'<meta property="og:image:height" content="{size[1]}"><meta property="og:image:alt" content="{a(site_name)}: {a(title)}">'
                f'<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{a(image_url)}">')
        f.write_text(t.replace("</head>", tags + "</head>", 1))


PARENT_URL = "https://opencitizenscience.org/"
CRUMB_CSS = ("<style id=\"ocs-crumb\">.ocs-crumbs{display:flex;align-items:center;gap:12px;min-width:0;margin-right:auto}"
             ".ocs-parent{display:inline-flex;align-items:center;gap:7px;color:inherit;text-decoration:none;opacity:.62;"
             "font-size:14.5px;font-weight:500;letter-spacing:-.005em;white-space:nowrap;transition:opacity .15s}"
             ".ocs-parent:hover,.ocs-parent:focus-visible{opacity:1}"
             ".ocs-parent svg{width:18px;height:18px;flex:none}"
             ".ocs-sep{opacity:.3;font-size:22px;font-weight:300;line-height:1;margin-top:-2px}"
             "@media (max-width:899px){.ocs-parent span{display:none}.ocs-crumbs{gap:9px}}"
             "@media (max-width:559px){.ocs-parent,.ocs-sep{display:none}}</style>")
CRUMB = ('<div class="ocs-crumbs"><a class="ocs-parent" href="' + PARENT_URL + '" title="Part of Open Citizen Science">'
         '<svg viewBox="0 0 32 32" aria-hidden="true" focusable="false"><circle cx="16" cy="16" r="12" fill="none" stroke="currentColor" stroke-width="2.6"/>'
         '<circle cx="16" cy="16" r="3.5" fill="currentColor"/></svg><span>Open Citizen Science</span></a>'
         '<span class="ocs-sep" aria-hidden="true">/</span>')


def add_parent_link(dist):
    """Wrap the header's <a class="brand" ...>...</a> in the breadcrumb, on every page of a built project site."""
    for f in Path(dist).rglob("*.html"):
        t = f.read_text()
        if "ocs-crumbs" in t or '<a class="brand"' not in t or "</head>" not in t:
            continue
        i = t.index('<a class="brand"')
        j = t.index("</a>", i) + 4
        t = t[:i] + CRUMB + t[i:j] + "</div>" + t[j:]
        f.write_text(t.replace("</head>", CRUMB_CSS + "</head>", 1))
