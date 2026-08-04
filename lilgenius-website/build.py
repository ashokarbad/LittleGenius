#!/usr/bin/env python3
"""
Li'l Genius Pre-School - static site builder.

Why a builder instead of 15 hand-maintained HTML files:
  - Header, footer, nav, SEO tags and schema live in ONE place (templates/base.html)
  - School details live in ONE place (content/site.json)
  - Output is plain static HTML: no JS routing, no server, best possible SEO,
    hostable free on GitHub Pages / Netlify / Hostinger.

Usage:
    python3 build.py            # build into dist/
    python3 build.py --check    # build + warn about placeholder content
    python3 build.py --serve    # build + preview at http://localhost:8000
"""

import json
import os
import re
import shutil
import sys
from datetime import date

import logo_lib as L

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")

# ---------------------------------------------------------------- site config
with open(os.path.join(ROOT, "content", "site.json"), encoding="utf-8") as fh:
    SITE = json.load(fh)

# Navigation. (label, file, show_in_top_nav)
NAV = [
    ("Home", "index.html", True),
    ("About", "about.html", True),
    ("Programs", "programs.html", True),
    ("Curriculum", "curriculum.html", True),
    ("Facilities", "facilities.html", True),
    ("Gallery", "gallery.html", True),
    ("Admissions", "admissions.html", True),
    ("Contact", "contact.html", True),
    ("Our Team", "teachers.html", False),
    ("Parent Reviews", "testimonials.html", False),
    ("FAQs", "faq.html", False),
    ("Blog", "blog.html", False),
    ("Enquire", "enquiry.html", False),
]



# ------------------------------------------------------------------ utilities
def hero_lockup():
    """The full logo mark, animated, used as the hero artwork."""
    return L.lockup(animate=True)


def read_fragment(path):
    """Fragment format: JSON front-matter between --- lines, then HTML body."""
    with open(path, encoding="utf-8") as fh:
        raw = fh.read()
    if raw.startswith("---"):
        _, meta, body = raw.split("---", 2)
        return json.loads(meta), body.strip()
    return {}, raw.strip()


def nav_html(current):
    items = []
    for label, href, top in NAV:
        if not top:
            continue
        active = ' aria-current="page"' if href == current else ""
        cls = ' class="is-active"' if href == current else ""
        items.append(f'<li><a href="{href}"{cls}{active}>{label}</a></li>')
    return "\n          ".join(items)


def footer_links_html():
    items = []
    for label, href, _ in NAV:
        items.append(f'<li><a href="{href}">{label}</a></li>')
    return "\n            ".join(items)


def breadcrumb_html(title, href):
    if href == "index.html":
        return ""
    return (
        '<nav class="crumb" aria-label="Breadcrumb"><div class="wrap">'
        '<a href="index.html">Home</a><span aria-hidden="true">/</span>'
        f"<span>{title}</span></div></nav>"
    )


def render(template, mapping):
    for key, val in mapping.items():
        template = template.replace("{{" + key + "}}", str(val))
    return template


# ---------------------------------------------------------------------- build
def build():
    os.makedirs(DIST, exist_ok=True)

    with open(os.path.join(ROOT, "templates", "base.html"), encoding="utf-8") as fh:
        base = fh.read()

    # copy static assets
    dest_assets = os.path.join(DIST, "assets")
    if os.path.exists(dest_assets):
        shutil.rmtree(dest_assets)
    shutil.copytree(os.path.join(ROOT, "assets"), dest_assets)

    pages_dir = os.path.join(ROOT, "pages")
    built = []

    org_schema = {
        "@context": "https://schema.org",
        "@type": ["Preschool", "ChildCare", "LocalBusiness"],
        "name": SITE["legal_name"],
        "alternateName": SITE["name"],
        "slogan": SITE["tagline"],
        "foundingDate": SITE["established"],
        "url": SITE["base_url"],
        "logo": SITE["base_url"] + "/assets/img/logo.svg",
        "image": SITE["base_url"] + "/assets/img/og-image.png",
        "telephone": SITE["phone_e164"],
        "email": SITE["email"],
        "priceRange": "₹₹",
        "address": {
            "@type": "PostalAddress",
            "streetAddress": SITE["address_street"],
            "addressLocality": SITE["address_locality"],
            "addressRegion": SITE["address_region"],
            "postalCode": SITE["address_postal"],
            "addressCountry": SITE["address_country"],
        },
        "geo": {
            "@type": "GeoCoordinates",
            "latitude": SITE["geo_lat"],
            "longitude": SITE["geo_lng"],
        },
        "openingHours": SITE["hours_schema"],
        "hasMap": SITE["maps_link"],
        "sameAs": [SITE["instagram"], SITE["facebook"]],
        "areaServed": [
            {"@type": "Place", "name": n}
            for n in ["Balewadi", "Baner", "Pashan", "Wakad", "Aundh", "Sus Road", "Pune"]
        ],
    }

    for fname in sorted(os.listdir(pages_dir)):
        if not fname.endswith(".html"):
            continue
        meta, body = read_fragment(os.path.join(pages_dir, fname))
        out_name = meta.get("output", fname)
        title = meta.get("title", SITE["name"])
        desc = meta.get("description", "")
        heading = meta.get("heading", title)

        body = render(
            body,
            {
                "hero_blocks": hero_lockup(),
                "phone_display": SITE["phone_display"],
                "phone_e164": SITE["phone_e164"],
                "whatsapp": SITE["whatsapp"],
                "email": SITE["email"],
                "address_full": SITE["address_full"],
                "maps_link": SITE["maps_link"],
                "maps_embed": SITE["maps_embed"],
                "hours_text": SITE["hours_text"],
                "established": SITE["established"],
                "tagline": SITE["tagline"],
                "name": SITE["name"],
                "instagram": SITE["instagram"],
                "facebook": SITE["facebook"],
            },
        )

        extra = meta.get("schema")
        schema_blocks = [org_schema] if out_name == "index.html" else []
        if extra:
            schema_blocks.append(extra)
        schema_html = "\n".join(
            f'<script type="application/ld+json">{json.dumps(s, ensure_ascii=False)}</script>'
            for s in schema_blocks
        )

        canonical = f"{SITE['base_url']}/{'' if out_name == 'index.html' else out_name}"

        html = render(
            base,
            {
                "title": title,
                "description": desc,
                "canonical": canonical,
                "nav": nav_html(out_name),
                "footer_links": footer_links_html(),
                "breadcrumb": breadcrumb_html(heading, out_name),
                "body": body,
                "schema": schema_html,
                "year": date.today().year,
                "og_image": SITE["base_url"] + "/assets/img/og-image.png",
                "body_class": meta.get("body_class", ""),
                # site tokens available in template too
                "site_name": SITE["name"],
                "legal_name": SITE["legal_name"],
                "tagline": SITE["tagline"],
                "phone_display": SITE["phone_display"],
                "phone_e164": SITE["phone_e164"],
                "whatsapp": SITE["whatsapp"],
                "email": SITE["email"],
                "address_full": SITE["address_full"],
                "hours_text": SITE["hours_text"],
                "maps_link": SITE["maps_link"],
                "instagram": SITE["instagram"],
                "facebook": SITE["facebook"],
                "form_endpoint": SITE["form_endpoint"],
                "established": SITE["established"],
            },
        )

        with open(os.path.join(DIST, out_name), "w", encoding="utf-8") as fh:
            fh.write(html)
        built.append((out_name, meta.get("priority", "0.7"), body))

    # ------------------------------------------------------------- sitemap.xml
    today = date.today().isoformat()
    urls = []
    for name, prio, _ in built:
        if name in ("404.html", "thank-you.html"):
            continue
        loc = f"{SITE['base_url']}/{'' if name == 'index.html' else name}"
        urls.append(
            f"  <url><loc>{loc}</loc><lastmod>{today}</lastmod>"
            f"<changefreq>monthly</changefreq><priority>{prio}</priority></url>"
        )
    with open(os.path.join(DIST, "sitemap.xml"), "w", encoding="utf-8") as fh:
        fh.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
            + "\n".join(urls)
            + "\n</urlset>\n"
        )

    with open(os.path.join(DIST, "robots.txt"), "w", encoding="utf-8") as fh:
        fh.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE['base_url']}/sitemap.xml\n")

    # GitHub Pages: stop Jekyll from eating folders that start with underscore
    open(os.path.join(DIST, ".nojekyll"), "w").close()

    print(f"Built {len(built)} pages into dist/")

    if "--check" in sys.argv:
        print("\n--- Pre-launch checks ---")
        problems = 0
        for name, _, body in built:
            for marker in re.findall(r"SAMPLE[- ]CONTENT|PLACEHOLDER", body):
                problems += 1
                print(f"  ! {name}: contains {marker} - replace before going live")
        if not SITE["form_endpoint"]:
            print("  i Enquiry form will open WhatsApp (no email endpoint configured).")
        if SITE["email"].endswith("yahoo.com"):
            print("  ! Public email is a Yahoo address - a domain address looks far more credible.")
        if not problems:
            print("  OK: no placeholder markers left.")
    return built


if __name__ == "__main__":
    build()
    if "--serve" in sys.argv:
        import http.server
        import socketserver

        os.chdir(DIST)
        with socketserver.TCPServer(("", 8000), http.server.SimpleHTTPRequestHandler) as httpd:
            print("Preview at http://localhost:8000  (Ctrl+C to stop)")
            httpd.serve_forever()
