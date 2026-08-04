#!/usr/bin/env python3
"""
Builds preview.html - the whole site collapsed into ONE self-contained file.

Why: chat previews, email attachments and USB handovers render a single HTML
file in isolation, so relative links to assets/css/styles.css never resolve and
the page appears unstyled. This inlines the CSS, the JS and every image as a
data URI, and turns the page-to-page links into in-document navigation.

This file is for REVIEW ONLY. Deploy dist/ - it is faster, cacheable and
crawlable. preview.html is neither.

Usage: python3 build.py && python3 tools/make_preview.py
"""
import base64
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST = os.path.join(ROOT, "dist")

PAGES = [
    ("index", "Home"), ("about", "About"), ("programs", "Programs"),
    ("curriculum", "Curriculum"), ("facilities", "Facilities"), ("gallery", "Gallery"),
    ("admissions", "Admissions"), ("contact", "Contact"), ("teachers", "Our Team"),
    ("testimonials", "Parent Reviews"), ("faq", "FAQs"), ("blog", "Blog"),
    ("blog-choosing-a-preschool", "Choosing a preschool"),
    ("blog-settling-in", "Settling in"),
    ("blog-grade-1-readiness", "Grade 1 readiness"),
    ("enquiry", "Enquire"), ("thank-you", "Thank you"),
]
SLUGS = {slug for slug, _ in PAGES}


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def data_uri(rel_path):
    full = os.path.join(DIST, rel_path)
    if not os.path.exists(full):
        return rel_path
    mime = "image/svg+xml" if full.endswith(".svg") else "image/png"
    with open(full, "rb") as fh:
        return "data:%s;base64,%s" % (mime, base64.b64encode(fh.read()).decode())


def inline_images(html):
    def sub(m):
        attr, path = m.group(1), m.group(2)
        return '%s="%s"' % (attr, data_uri(path))
    return re.sub(r'(src|data-full)="(assets/img/[^"]+)"', sub, html)


def rewrite_links(html):
    def sub(m):
        target = m.group(1)
        slug = target[:-5]
        return 'href="#p-%s"' % slug if slug in SLUGS else m.group(0)
    return re.sub(r'href="([a-z0-9\-]+\.html)"', sub, html)


def section(tag, html):
    m = re.search(r"<%s[^>]*>(.*)</%s>" % (tag, tag), html, re.S)
    return m.group(1) if m else ""


index = read(os.path.join(DIST, "index.html"))

css = read(os.path.join(ROOT, "assets", "css", "styles.css"))
js = read(os.path.join(ROOT, "assets", "js", "main.js"))

# shell pieces, taken once from the home page
topbar = re.search(r'<div class="topbar">.*?</div>\s*</div>', index, re.S).group(0)
header = re.search(r"<header class=\"head\".*?</header>", index, re.S).group(0)
footer = re.search(r"<footer class=\"foot\">.*?</footer>", index, re.S).group(0)
wafloat = re.search(r'<a class="wa-float".*?</a>', index, re.S).group(0)
sprite = re.search(r'<svg style="display:none".*?</svg>', index, re.S).group(0)

bodies = []
for slug, label in PAGES:
    page = read(os.path.join(DIST, slug + ".html"))
    main = section("main", page)
    bodies.append(
        '<div class="pv-page" id="p-%s" data-label="%s" hidden>%s</div>' % (slug, label, main)
    )

doc = """<!DOCTYPE html>
<!--
  ============================================================================
  REVIEW COPY - DO NOT UPLOAD THIS FILE TO THE WEB SERVER.

  This is all 17 pages squashed into one file with the CSS, JavaScript and
  images inlined, so it can be opened or shared anywhere without its assets
  folder. It is for showing people the design, not for hosting.

  The real website is the dist/ folder. Upload that.
  Rebuild this file with:  python3 build.py && python3 tools/make_preview.py
  ============================================================================
-->
<html lang="en-IN" class="js">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Li'l Genius Pre-School - full site preview</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Grandstander:wght@600;800&family=Figtree:wght@400;500;600;800&display=swap">
<style>
__CSS__
.pv-page[hidden]{display:none}
</style>
</head>
<body>
<a class="skip" href="#main">Skip to main content</a>
__TOPBAR__
__HEADER__
<main id="main">
__BODIES__
</main>
__FOOTER__
__WAFLOAT__
__SPRITE__
<script>
/* in-document router: replaces the multi-page navigation for preview only */
(function(){
  var pages=[].slice.call(document.querySelectorAll(".pv-page"));
  function show(id){
    var target=document.getElementById(id)||pages[0];
    pages.forEach(function(p){p.hidden=(p!==target)});
    document.querySelectorAll(".nav a").forEach(function(a){
      var on=a.getAttribute("href")==="#"+target.id;
      a.classList.toggle("is-active",on);
      if(on){a.setAttribute("aria-current","page")}else{a.removeAttribute("aria-current")}
    });
    document.title=target.dataset.label+" | Li'l Genius Pre-School";
    window.scrollTo(0,0);
  }
  function fromHash(){show((location.hash||"#p-index").slice(1))}
  window.addEventListener("hashchange",fromHash);
  fromHash();
})();
__JS__
</script>
</body>
</html>
"""

for token, value in [
    ("__CSS__", css), ("__TOPBAR__", topbar), ("__HEADER__", header),
    ("__BODIES__", "\n".join(bodies)), ("__FOOTER__", footer),
    ("__WAFLOAT__", wafloat), ("__SPRITE__", sprite), ("__JS__", js),
]:
    doc = doc.replace(token, value)

doc = rewrite_links(doc)
doc = inline_images(doc)

out = os.path.join(ROOT, "preview.html")
with open(out, "w", encoding="utf-8") as fh:
    fh.write(doc)
print("Wrote preview.html (%.0f KB) - open it directly, no server needed."
      % (os.path.getsize(out) / 1024))
