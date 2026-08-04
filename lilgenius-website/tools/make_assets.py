#!/usr/bin/env python3
"""
Regenerates brand assets from logo_lib.py. Run: python3 tools/make_assets.py

The supplied logo was a JPG on a solid yellow square, which cannot sit on a
white header without a visible box. This rebuilds the same mark as clean SVG
(transparent, scalable) plus the favicon and social-share image. Geometry,
colours and letterforms all come from logo_lib.py so nothing can drift.
"""
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import logo_lib as L

IMG = os.path.join(ROOT, "assets", "img")
GAL = os.path.join(IMG, "gallery")
os.makedirs(GAL, exist_ok=True)

PALETTE = L.PALETTE
INK = L.INK


def cube(letter, colour, x, y, s, text_fill="#fff"):
    return L.cube(letter, colour, x, y, s)


def write(path, text):
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("  wrote", os.path.relpath(path, ROOT))


print("Brand assets:")
write(os.path.join(IMG, "logo.svg"), L.logo_svg())
write(os.path.join(IMG, "logo-mono.svg"), L.logo_svg(sub_fill="#F6EFDF", lil_fill="#B76ECB", lil_halo="#F6EFDF"))
write(
    os.path.join(IMG, "favicon.svg"),
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    '<rect width="64" height="64" rx="14" fill="#FCD94B"/>'
    + L.cube("G", "#E63329", 18, 14, 36)
    + "</svg>",
)

# ---------------------------------------------------------------- placeholders
SCENES = [
    ("classroom", "Classroom", "#3FB3DE"),
    ("art-corner", "Art corner", "#EE6A15"),
    ("reading-nook", "In-house library", "#3E9C37"),
    ("play-zone", "Indoor play zone", "#E63329"),
    ("outdoor", "Outdoor play area", "#3E9C37"),
    ("circle-time", "Circle time", "#7B2E8E"),
    ("sports-day", "Sports day", "#EE6A15"),
    ("festival", "Festival celebration", "#E63329"),
    ("daycare", "Daycare room", "#3FB3DE"),
    ("field-trip", "Field trip", "#2E3192"),
    ("graduation", "Graduation day", "#7B2E8E"),
    ("campus", "Our campus", "#2E3192"),
]


def placeholder(label, colour, i):
    """A tidy, on-brand stand-in until real photographs are supplied."""
    blocks = "".join(
        cube(ch, PALETTE[(i + k) % 6], 250 + k * 76, 250, 66)
        for k, ch in enumerate(["L", "G"])
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 600" role="img" aria-label="{label} photo placeholder">
<rect width="800" height="600" fill="#FFF8E6"/>
<circle cx="640" cy="110" r="120" fill="{colour}" opacity=".18"/>
<circle cx="120" cy="520" r="150" fill="#FCD94B" opacity=".45"/>
<path d="M0 470 Q200 400 400 460 T800 440 L800 600 L0 600Z" fill="{colour}" opacity=".22"/>
{blocks}
<text x="400" y="180" text-anchor="middle" font-family="Trebuchet MS, Verdana, sans-serif" font-weight="bold" font-size="46" fill="#241D14">{label}</text>
<text x="400" y="222" text-anchor="middle" font-family="Trebuchet MS, Verdana, sans-serif" font-size="24" fill="#5F5346">Replace with a real photo</text>
</svg>"""


print("Gallery placeholders:")
for i, (slug, label, colour) in enumerate(SCENES):
    write(os.path.join(GAL, slug + ".svg"), placeholder(label, colour, i))

write(os.path.join(IMG, "hero-photo.svg"), placeholder("Our children at work", "#7B2E8E", 2))
write(os.path.join(IMG, "about-photo.svg"), placeholder("Inside Li'l Genius", "#3FB3DE", 4))
write(os.path.join(IMG, "teacher.svg"),
      '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" role="img" aria-label="Staff photo placeholder">'
      '<rect width="400" height="400" fill="#FFF8E6"/><circle cx="200" cy="155" r="66" fill="#EAE2CE"/>'
      '<path d="M70 400c0-72 58-116 130-116s130 44 130 116z" fill="#EAE2CE"/>'
      '<text x="200" y="372" text-anchor="middle" font-family="Trebuchet MS, Verdana, sans-serif" font-size="20" fill="#5F5346">Add staff photo</text></svg>')

# ------------------------------------------------------------- raster fallback
try:
    from PIL import Image, ImageDraw, ImageFont

    def font(sz):
        for p in ("/usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"):
            if os.path.exists(p):
                return ImageFont.truetype(p, sz)
        return ImageFont.load_default()

    def draw_cube(dr, ch, col, x, y, s):
        d = int(s * L.DEPTH)
        dr.polygon([(x, y), (x - d, y - d), (x - d, y + s - d), (x, y + s)], fill=L.FACE_SIDE)
        dr.polygon([(x, y), (x - d, y - d), (x + s - d, y - d), (x + s, y)], fill=L.FACE_TOP)
        dr.rounded_rectangle([x, y, x + s, y + s], radius=int(s * .05), fill=col)
        f = font(int(s * .62))
        bb = dr.textbbox((0, 0), ch, font=f)
        dr.text((x + s / 2 - (bb[2] - bb[0]) / 2, y + s / 2 - (bb[3] - bb[1]) / 2 - bb[1]), ch, font=f, fill="#fff")

    # social share card
    im = Image.new("RGB", (1200, 630), "#FCD94B")
    dr = ImageDraw.Draw(im)
    dr.ellipse([-120, 430, 480, 900], fill="#FFF8E6")
    s = 96
    for i, ch in enumerate("GENIUS"):
        draw_cube(dr, ch, PALETTE[i], 210 + i * (s + int(s * L.DEPTH)), 150, s)
    f1, f2 = font(46), font(30)
    dr.text((600, 330), "Li'l Genius Pre-School", font=f1, fill=INK, anchor="mm")
    dr.text((600, 392), "Preschool & Daycare  |  Balewadi, Pune  |  Ages 2-6", font=f2, fill="#5F5346", anchor="mm")
    dr.text((600, 452), "\u201cDo it your own the best\u201d", font=f2, fill="#8A2B22", anchor="mm")
    im.save(os.path.join(IMG, "og-image.png"), optimize=True)
    print("  wrote assets/img/og-image.png")

    ic = Image.new("RGB", (180, 180), "#FCD94B")
    draw_cube(ImageDraw.Draw(ic), "G", "#E63329", 48, 42, 100)
    ic.save(os.path.join(IMG, "apple-touch-icon.png"), optimize=True)
    print("  wrote assets/img/apple-touch-icon.png")
except ImportError:
    print("  (Pillow not installed - skipped PNG generation)")

print("Done.")
