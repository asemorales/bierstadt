#!/usr/bin/env python3
"""Draw the bierstadt and bierstadt-dark xfwm4 decorations.

xfwm4 does not scale its pixmaps, and this screen runs at 2x, so every size
below is in device pixels (logical size x 2). Run again after changing a colour:

    python3 ~/.themes/bierstadt/xfwm4-build.py
"""
import os
from PIL import Image, ImageDraw

S = 2                 # device pixels per logical pixel
TITLE_H = 26 * S      # flat title bar
BORDER = 1 * S        # side and bottom hairline
RADIUS = 10 * S       # top corners
CORNER_W = max(RADIUS, BORDER)  # width of the top-left/right pieces
BTN_W = 18 * S
GLYPH = 4 * S         # half-size of each button glyph
LINE = 1 * S          # glyph stroke

def _palette():
    import re
    here = os.path.dirname(os.path.abspath(__file__))
    css = open(os.path.join(here, "gtk-3.0", "_palette.css"), encoding="utf-8").read()
    return {k: v.upper() for k, v in re.findall(r"@define-color\s+(\w+)\s+(#[0-9A-Fa-f]{6})", css)}


_P = _palette()
PAPER, LINEN, STONE, MUTED = _P["paper"], _P["linen"], _P["stone"], _P["muted"]
INK = _P["ink"]
NIGHT, NIGHT_PANEL, NIGHT_HOVER = _P["night"], _P["night_panel"], _P["night_hover"]
NIGHT_RULE, NIGHT_FRAME, NIGHT_MID = _P["night_rule"], _P["night_frame"], _P["night_mid"]
NIGHT_DIM, NIGHT_TEXT = _P["night_dim"], _P["night_text"]


def rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(a, b, t):
    """t of b over a, returned as an opaque hex (themerc only takes hex)."""
    a, b = rgb(a), rgb(b)
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))


VARIANTS = {
    "bierstadt": dict(
        active=mix(PAPER, STONE, 0.35),          # only slightly darker than inactive
        inactive=PAPER,
        line=STONE,
        border=mix(PAPER, INK, 0.35),            # a hairline frame round the window
        text_active=INK,
        text_inactive=mix(PAPER, INK, 0.60),
        glyph_active=mix(PAPER, INK, 0.62),
        glyph_inactive=MUTED,
        glyph_hover=INK,
        hover=mix(mix(PAPER, STONE, 0.35), INK, 0.07),
        pressed=mix(mix(PAPER, STONE, 0.35), INK, 0.13),
    ),
    "bierstadt-dark": dict(                         # gwern.net's dark greys
        active=NIGHT,
        inactive="#1F1B17",                      # only slightly lighter than active
        line=NIGHT_RULE,
        border=NIGHT_FRAME,
        text_active=NIGHT_TEXT,
        text_inactive=NIGHT_DIM,
        glyph_active=NIGHT_DIM,
        glyph_inactive=NIGHT_FRAME,
        glyph_hover=NIGHT_TEXT,
        hover=NIGHT_HOVER,
        pressed=mix(NIGHT_HOVER, NIGHT_MID, 0.3),
    ),
}


def title_piece(bg, line, w=8, top=None):
    im = Image.new("RGBA", (w, TITLE_H), bg)
    d = ImageDraw.Draw(im)
    d.rectangle([0, TITLE_H - S, w, TITLE_H], fill=line)
    if top:
        d.rectangle([0, 0, w, BORDER - 1], fill=top)
    return im


def corner(bg, line, border, side):
    """Rounded top corner with a hairline down the outer edge."""
    big = 4  # supersample for a smooth curve
    w, h, r = CORNER_W * big, TITLE_H * big, RADIUS * big
    mask = Image.new("L", (w * 2, h), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, w * 2 - 1, h + r], r, fill=255)
    mask = mask.crop((0, 0, w, h)).resize((CORNER_W, TITLE_H), Image.LANCZOS)
    im = Image.new("RGBA", (CORNER_W, TITLE_H), bg)
    d = ImageDraw.Draw(im)
    d.rectangle([0, TITLE_H - S, CORNER_W, TITLE_H], fill=line)
    # outer hairline below the curve, matching the side border
    d.rectangle([0, RADIUS, BORDER - 1, TITLE_H], fill=border)
    d.rectangle([0, 0, CORNER_W, BORDER - 1], fill=border)
    if RADIUS:
        im.putalpha(mask)
    return im if side == "left" else im.transpose(Image.FLIP_LEFT_RIGHT)


def solid(w, h, color):
    return Image.new("RGBA", (w, h), color)


def glyph(kind, color, d, cx, cy):
    g = GLYPH
    if kind == "close":
        d.line([cx - g, cy - g, cx + g, cy + g], fill=color, width=LINE)
        d.line([cx - g, cy + g, cx + g, cy - g], fill=color, width=LINE)
    elif kind == "hide":
        d.line([cx - g, cy + g // 2, cx + g, cy + g // 2], fill=color, width=LINE)
    elif kind == "maximize":
        d.rectangle([cx - g, cy - g, cx + g, cy + g], outline=color, width=LINE)
    elif kind == "maximize-toggled":
        o = S
        d.rectangle([cx - g + o, cy - g, cx + g, cy + g - o], outline=color, width=LINE)
        d.rectangle([cx - g, cy - g + o * 2, cx + g - o * 2, cy + g], outline=color, width=LINE)
    elif kind in ("menu", "shade", "shade-toggled", "stick", "stick-toggled"):
        r = S + S // 2
        offs = {"menu": [-g, 0, g], "shade": [0], "shade-toggled": [0],
                "stick": [0], "stick-toggled": [0]}[kind]
        for ox in offs:
            box = [cx + ox - r, cy - r, cx + ox + r, cy + r]
            if kind.endswith("toggled"):
                d.ellipse(box, fill=color)
            else:
                d.ellipse(box, outline=color, width=LINE)


def button(kind, bg, line, glyph_color, hover_fill=None, top=None):
    im = title_piece(bg, line, BTN_W, top)
    d = ImageDraw.Draw(im)
    cx, cy = BTN_W // 2, (TITLE_H - S) // 2
    if hover_fill:
        r = 9 * S
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=hover_fill)
    glyph(kind, glyph_color, d, cx, cy)
    return im


def build(name, c):
    out = os.path.expanduser(f"~/.themes/{name}/xfwm4")
    os.makedirs(out, exist_ok=True)
    for state, bg in (("active", c["active"]), ("inactive", c["inactive"])):
        for i in range(1, 6):
            title_piece(bg, c["line"], top=c["border"]).save(f"{out}/title-{i}-{state}.png")
        corner(bg, c["line"], c["border"], "left").save(f"{out}/top-left-{state}.png")
        corner(bg, c["line"], c["border"], "right").save(f"{out}/top-right-{state}.png")
        solid(BORDER, 8, c["border"]).save(f"{out}/left-{state}.png")
        solid(BORDER, 8, c["border"]).save(f"{out}/right-{state}.png")
        solid(8, BORDER, c["border"]).save(f"{out}/bottom-{state}.png")
        solid(BORDER, BORDER, c["border"]).save(f"{out}/bottom-left-{state}.png")
        solid(BORDER, BORDER, c["border"]).save(f"{out}/bottom-right-{state}.png")

    kinds = ["close", "hide", "maximize", "maximize-toggled", "menu",
             "shade", "shade-toggled", "stick", "stick-toggled"]
    for k in kinds:
        a = c["active"]
        button(k, a, c["line"], c["glyph_active"], top=c["border"]).save(f"{out}/{k}-active.png")
        button(k, c["inactive"], c["line"], c["glyph_inactive"], top=c["border"]).save(f"{out}/{k}-inactive.png")
        button(k, a, c["line"], c["glyph_hover"], c["hover"], top=c["border"]).save(f"{out}/{k}-prelight.png")
        button(k, a, c["line"], c["glyph_hover"], c["pressed"], top=c["border"]).save(f"{out}/{k}-pressed.png")

    with open(f"{out}/themerc", "w") as f:
        f.write(f"""# {name} xfwm4 theme. Generated by ~/.themes/bierstadt/xfwm4-build.py
active_text_color={c['text_active']}
inactive_text_color={c['text_inactive']}
title_shadow_active=false
title_shadow_inactive=false
title_horizontal_offset={4 * S}
title_vertical_offset_active=0
title_vertical_offset_inactive=0
full_width_title=true
show_app_icon=false
button_offset={2 * S}
button_spacing=0
maximized_offset=0
shadow_delta_x=0
shadow_delta_y=-{1 * S}
shadow_delta_width=0
shadow_delta_height=0
shadow_opacity=20
""")
    print("built", out)


if __name__ == "__main__":
    for n, c in VARIANTS.items():
        build(n, c)
