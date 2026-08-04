"""
Li'l Genius block mark - one definition, used by every asset and by the
animated hero, so the logo can never drift between places.

Geometry note: the mark is lit from the upper LEFT. The top face is offset
up-and-left (near-white) and the LEFT side face is visible (mid grey). Getting
this backwards - grey on the right - is the single most obvious way to make a
rebuilt logo look subtly wrong.

Letterforms are a rounded marker face. Because these SVGs are also used inside
<img>, webfonts cannot load, so the stack falls back to fonts that ship with
Windows and macOS and read closest to the original.
"""

PALETTE = ["#E63329", "#3E9C37", "#2E3192", "#3FB3DE", "#7B2E8E", "#EE6A15"]
PURPLE = "#7B2E8E"
INK = "#241D14"
FACE_TOP = "#F4F2ED"
FACE_SIDE = "#BFBBB2"
MARKER = "Comic Sans MS, Chalkboard SE, Trebuchet MS, Verdana, sans-serif"

DEPTH = 0.30  # side/top face depth as a fraction of the cube size


def cube(letter, colour, x, y, s, cls="", delay=None, depth=DEPTH):
    """One alphabet block: left face, top face, coloured front, white letter."""
    d = s * depth
    left = f"{x},{y} {x-d},{y-d} {x-d},{y+s-d} {x},{y+s}"
    top = f"{x},{y} {x-d},{y-d} {x+s-d},{y-d} {x+s},{y}"
    style = f' style="--delay:{delay}s"' if delay is not None else ""
    klass = f' class="{cls}"' if cls else ""
    return (
        f"<g{klass}{style}>"
        f'<polygon points="{left}" fill="{FACE_SIDE}"/>'
        f'<polygon points="{top}" fill="{FACE_TOP}"/>'
        f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="{s*0.05:.1f}" fill="{colour}"/>'
        f'<text x="{x+s/2:.1f}" y="{y+s*0.755:.1f}" text-anchor="middle" font-family="{MARKER}" '
        f'font-weight="bold" font-size="{s*0.7:.1f}" fill="#fff">{letter}</text>'
        "</g>"
    )


def balloons(cls=""):
    """Red and green balloons on strings, top left, as on the original mark."""
    k1 = f' class="{cls}"' if cls else ""
    k2 = f' class="{cls} {cls}-2"' if cls else ""
    return (
        f"<g{k1}>"
        '<ellipse cx="92" cy="46" rx="25" ry="30" fill="#E63329"/>'
        '<path d="M92 76l4 5-8 0z" fill="#E63329"/>'
        '<path d="M92 81c-6 14 8 20 3 34" stroke="#3F3A32" stroke-width="3" fill="none" stroke-linecap="round"/>'
        "</g>"
        f"<g{k2}>"
        '<ellipse cx="140" cy="78" rx="19" ry="23" fill="#3E9C37"/>'
        '<path d="M140 101l3 4-6 0z" fill="#3E9C37"/>'
        '<path d="M140 105c-5 10 5 14 1 24" stroke="#3F3A32" stroke-width="3" fill="none" stroke-linecap="round"/>'
        "</g>"
    )


def lil(cls="", fill=PURPLE, halo="#FFFFFF"):
    """The 'Li'l' script sitting above the first block."""
    k = f' class="{cls}"' if cls else ""
    return (
        f"<g{k}>"
        f'<text x="44" y="164" font-family="{MARKER}" font-weight="bold" font-size="104" '
        f'textLength="150" lengthAdjust="spacingAndGlyphs" fill="{fill}" stroke="{halo}" '
        f'stroke-width="11" paint-order="stroke" stroke-linejoin="round">Li&#8217;l</text>'
        f'<text x="44" y="164" font-family="{MARKER}" font-weight="bold" font-size="104" '
        f'textLength="150" lengthAdjust="spacingAndGlyphs" fill="{fill}">Li&#8217;l</text>'
        "</g>"
    )


def word(text="GENIUS", x0=112, y0=186, s=88, gap_ratio=0.30, cls="", animate=False):
    """The GENIUS block row. Gap equals the face depth so the grey faces tuck in."""
    gap = s * gap_ratio
    out = []
    for i, ch in enumerate(text):
        out.append(
            cube(
                ch,
                PALETTE[i % len(PALETTE)],
                x0 + i * (s + gap),
                y0,
                s,
                cls=cls,
                delay=round(0.9 + 0.11 * i, 2) if animate else None,
            )
        )
    return "".join(out)


def subtitle(cls="", fill=INK, y=336, cx=396, length=660):
    k = f' class="{cls}"' if cls else ""
    return (
        f'<text{k} x="{cx}" y="{y}" text-anchor="middle" font-family="{MARKER}" font-weight="bold" '
        f'font-size="46" textLength="{length}" lengthAdjust="spacingAndGlyphs" fill="{fill}">'
        "PRESCHOOL AND DAYCARE CENTRE</text>"
    )


VIEWBOX = "0 0 792 360"


def lockup(animate=False, sub_fill=INK, lil_fill=PURPLE, lil_halo="#FFFFFF"):
    """The complete mark. Same markup static or animated - only classes differ."""
    c = ("lg-balloon", "lg-lil", "lg-cube", "lg-sub") if animate else ("", "", "", "")
    return (
        balloons(c[0])
        + word(cls=c[2], animate=animate)
        + lil(c[1], fill=lil_fill, halo=lil_halo)
        + subtitle(c[3], fill=sub_fill)
    )


def logo_svg(sub_fill=INK, lil_fill=PURPLE, lil_halo="#FFFFFF"):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{VIEWBOX}" role="img" '
        "aria-label=\"Li'l Genius Preschool and Daycare Centre\">"
        + lockup(sub_fill=sub_fill, lil_fill=lil_fill, lil_halo=lil_halo)
        + "</svg>"
    )
