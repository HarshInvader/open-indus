"""Shared touches for every site in the Open Citizen Science family, applied to built HTML.

add_og: Open Graph and Twitter card tags. Each page keeps its own <title> and description;
  all pages share the site's card image. Pages that already carry og:image are left alone.
add_parent_link: an "(o) Open Citizen Science" link at the right of a project's nav, before Contribute,
  set off by a thin divider; on phones it sits in the menu.

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
CRUMB_CSS = ("<style id=\"ocs-parent\">.site-nav .ocs-li{display:flex;align-items:center}"
             ".site-nav a.ocs-parent{display:inline-flex;align-items:center;gap:7px;color:inherit;text-decoration:none;opacity:.6;"
             "font-size:.88em;white-space:nowrap;transition:opacity .15s}"
             ".site-nav a.ocs-parent:hover,.site-nav a.ocs-parent:focus-visible{opacity:1}"
             ".ocs-parent svg{width:15px;height:15px;flex:none}"
             "@media (min-width:900px){.site-nav .ocs-li{margin-left:6px;padding-left:22px;border-left:1px solid color-mix(in srgb,currentColor 18%,transparent);height:22px}}</style>")
CRUMB = ('<li class="ocs-li"><a class="ocs-parent" href="' + PARENT_URL + '" title="This project is part of Open Citizen Science">'
         '<svg viewBox="0 0 32 32" aria-hidden="true" focusable="false"><circle cx="16" cy="16" r="12" fill="none" stroke="currentColor" stroke-width="2.6"/>'
         '<circle cx="16" cy="16" r="3.5" fill="currentColor"/></svg>Open Citizen Science</a></li>')


def add_parent_link(dist):
    """Add an "Open Citizen Science" link to the right of the project's nav, just before Contribute (in the menu on phones)."""
    for f in Path(dist).rglob("*.html"):
        t = f.read_text()
        if "ocs-parent" in t or '<li class="nav-cta">' not in t or "</head>" not in t:
            continue
        t = t.replace('<li class="nav-cta">', CRUMB + '<li class="nav-cta">', 1)
        f.write_text(t.replace("</head>", CRUMB_CSS + "</head>", 1))
