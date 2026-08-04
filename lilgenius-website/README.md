# Li'l Genius Pre-School — website

A static, SEO-first website for Li'l Genius Preschool and Daycare Centre, Balewadi, Pune.
No frameworks, no build dependencies, no server required. Total page weight is under 500 KB
for the entire site.

```
content/site.json      All school details — edit here, not in the HTML
logo_lib.py            The block mark: geometry, palette, letterforms. One
                       definition shared by the logo files, the favicon, the
                       social image and the animated hero, so it cannot drift.
pages/*.html           One content fragment per page (JSON front-matter + HTML body)
templates/base.html    Head, SEO tags, header, nav, footer — shared by every page
assets/css/styles.css  Whole design system, one file
assets/js/main.js      Menu, scroll reveals, lightbox, enquiry form
tools/make_assets.py   Regenerates logo.svg, favicon, OG image, placeholders
build.py               Assembles everything into dist/
dist/                  ← upload this folder. Nothing else.
```

## Build

```bash
python3 build.py            # writes dist/
python3 build.py --check    # build + list placeholder content still to be replaced
python3 build.py --serve    # build + preview on http://localhost:8000
```

Python 3.8+ only. No pip installs (Pillow is optional, and only for the social-share PNG).

## Editing

**Phone, address, email, hours, social links, Maps link** → `content/site.json`, then rebuild.
They update everywhere at once, including the structured data Google reads.

**Page text** → the matching file in `pages/`. The block at the top between `---` lines sets
the browser title, the meta description and the sitemap priority; everything below it is
ordinary HTML.

**The logo** → `logo_lib.py`, then `python3 tools/make_assets.py`. It regenerates
`logo.svg`, the dark-background variant, the favicon, the touch icon and the social
share image together, and the animated hero picks up the change on the next build.

**Photos** → drop real files into `assets/img/gallery/` using the existing file names
(`classroom.svg` → `classroom.jpg`, and update the two references in `pages/gallery.html`).
Aim for roughly 1200×900, JPG or WebP, under 250 KB each.

**A new page** → copy any file in `pages/`, change the front-matter, add it to the `NAV`
list in `build.py`. Sitemap, nav, breadcrumbs and footer links update themselves.

## Enquiry form

Two modes, set by `form_endpoint` in `content/site.json`:

- **Blank (default)** — the form opens WhatsApp with the parent's details pre-filled. Works
  on free static hosting with no backend at all. The parent has to press send in WhatsApp.
- **A Formspree / Web3Forms endpoint URL** — the form posts in the background and the
  enquiry arrives by email. Free tiers are enough for a preschool's volume. Recommended
  once the site is live, since it captures enquiries even if the parent abandons WhatsApp.

## Deploying

Upload the **contents of `dist/`** to the web root. Any of these work:

- **GitHub Pages** — push `dist/` to a repo, enable Pages. Free, includes HTTPS.
- **Netlify / Cloudflare Pages** — drag the `dist/` folder onto the dashboard. Free.
- **Hostinger / GoDaddy shared hosting** — upload `dist/` into `public_html` over FTP.

Set `base_url` in `content/site.json` to the real domain before the final build, otherwise
`canonical`, `sitemap.xml` and the social-share image will point at the wrong address.

## Before it goes live — checklist

1. **Buy a domain.** The board outside the school currently advertises `www.genius.in`,
   which is not this school's website. Every parent who types it in is being sent elsewhere.
   Register something like `lilgeniuspreschool.com` and repaint the boards.
2. **Move off the Yahoo email.** `lilgeniuspreschool@yahoo.com` works, but
   `admissions@yourdomain.com` reads as an established school. Comes free with most hosting.
3. **Replace every placeholder.** Run `python3 build.py --check`. The testimonials and staff
   profiles are intentionally blank — see the warnings below.
4. **Add real photographs**, with written parental consent for any identifiable child.
5. **Fill in the fees** on `pages/programs.html`, or delete the notice box if you would
   rather not publish them.
6. **Claim your Google Business Profile.** For a neighbourhood preschool this drives more
   admissions than the website itself. The website's job is to make the profile convert.
7. **Submit `sitemap.xml`** in Google Search Console.

## Two things deliberately left blank

**Testimonials.** Inventing parent quotes would breach the Consumer Protection
(E-Commerce) Rules 2020 and ASCI's code on misleading advertising, and parents spot
fabricated reviews immediately. Collect three or four real quotes over WhatsApp, get
permission to publish with a first name and class, and paste them into
`pages/testimonials.html` and `pages/index.html`.

**Staff names and qualifications.** Same reasoning. Publish only what each staff member
has agreed to, in `pages/teachers.html`.

## Accessibility and performance notes

- Works fully with JavaScript disabled; JS only adds the menu drawer, reveals and lightbox.
- Keyboard navigable throughout, with visible focus rings and a skip link.
- `prefers-reduced-motion` is respected — all animation stops.
- Fonts load asynchronously; nothing blocks the first paint.
- Images are lazy-loaded below the fold and carry width/height to prevent layout shift.
- Structured data: `Preschool` / `LocalBusiness` on the home page, `FAQPage` on the FAQ
  page, `BlogPosting` on articles.
