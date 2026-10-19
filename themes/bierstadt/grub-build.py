#!/usr/bin/env python3
"""Build the Bierstadt GRUB theme for one room, to match the login screen.

    python3 -I grub-build.py dark|light PAINTING "CAPTION" OUT_DIR

The boot menu is the greeter's login card: the painting fills the screen, a
rounded card with a hairline frame and soft shadow hangs at 20% across, and
the wall label sits in the bottom-left corner as on the desktop. GRUB cannot
draw rounded corners, shadows or letter-spacing, so the card, the static text
and the wall label are painted into the background. GRUB draws only the menu,
the countdown and the selection pill on top.

Everything is laid out in 1920x1080 points and drawn at S pixels per point.
The laptop's firmware only offers the panel's native 3840x2160, so S is 2 and
GRUB runs at 4K: GRUB fonts are fixed bitmaps, so a 1080p theme stretched to
4K leaves the text half size. Positions are percentages, so the layout still
lines up if the firmware picks another mode.
"""
import os
import subprocess
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2                      # pixels per point; 2 for the 4K panel
W, H = 1920 * S, 1080 * S


def px(v):
    return round(v * S)


FONTS = os.path.expanduser("~/.local/share/fonts/bierstadt")
SERIF = os.path.join(FONTS, "SourceSerif4[opsz,wght].ttf")
MONO = os.path.join(FONTS, "IBMPlexMono-Regular.ttf")
MONO_MEDIUM = os.path.join(FONTS, "IBMPlexMono-Medium.ttf")
KITTY_MONO = os.path.join(FONTS, "DMMono-Regular.ttf")   # kitty's font_family
KITTY_MONO_MEDIUM = os.path.join(FONTS, "DMMono-Medium.ttf")

# The two rooms, from gtk-3.0/_palette.css and _roles.css
ROOMS = {
    "dark": dict(
        card="#191612", frame="#615950", rule="#4D463E", fg="#F2EDE4",
        dim="#9E958A", sel_bg="#F2EDE4", sel_fg="#191612",
        label_bg=(0x19, 0x16, 0x12, 217), label="#9E958A",
    ),
    "light": dict(
        card="#F2ECDF", frame="#AAA398", rule="#DDD4C1", fg="#3C332D",
        dim="#6F6560", sel_bg="#231A15", sel_fg="#F2ECDF",
        label_bg=(0xF2, 0xEC, 0xDF, 217), label="#6F6560",
    ),
}

# The card: centred at 20% across and halfway down, like the greeter's
# `position = 20%,center 50%,center`.
CARD_W, CARD_H = px(600), px(520)
CARD_X, CARD_Y = round(W * 0.20 - CARD_W / 2), (H - CARD_H) // 2
RADIUS = px(14)
PAD = px(44)

# Inside the card, top to bottom
KICKER_Y = CARD_Y + PAD
HEAD_Y = KICKER_Y + px(30)
RULE1_Y = HEAD_Y + px(62)
MENU_Y = RULE1_Y + px(22)
MENU_H = px(250)
RULE2_Y = CARD_Y + CARD_H - PAD - px(46)
FOOT_Y = RULE2_Y + px(22)
ITEM_H = px(44)


def font(path, size, weight=None):
    """`size` in points; the optical size stays at the point size."""
    f = ImageFont.truetype(path, px(size))
    if weight is not None:
        try:
            f.set_variation_by_axes([weight, min(size, 60)])  # wght, opsz
        except (OSError, ValueError):
            pass
    return f


def spaced(draw, xy, text, f, fill, tracking):
    """Text with letter-spacing, which neither GRUB nor PIL do on their own."""
    x, y = xy
    for ch in text:
        draw.text((x, y), ch, font=f, fill=fill)
        x += draw.textlength(ch, font=f) + tracking
    return x


def pct(v, total):
    """GRUB only reads whole percents, so the rest goes on as pixels ("5%+36")."""
    v = round(v)
    p = v * 100 // total
    rest = v - p * total // 100
    return f"{p}%+{rest}" if rest else f"{p}%"


def rounded(size, radius, fill):
    """A rounded rectangle drawn at 4x and shrunk, so the corners are smooth."""
    s = 4
    big = Image.new("RGBA", (size[0] * s, size[1] * s), (0, 0, 0, 0))
    ImageDraw.Draw(big).rounded_rectangle(
        (0, 0, size[0] * s - 1, size[1] * s - 1), radius * s, fill=fill)
    return big.resize(size, Image.LANCZOS)


def shadow(canvas, box, radius, blur, dy, alpha):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    x0, y0, x1, y1 = box
    ImageDraw.Draw(layer).rounded_rectangle((x0, y0 + dy, x1, y1 + dy), radius, fill=(0, 0, 0, alpha))
    return Image.alpha_composite(canvas, layer.filter(ImageFilter.GaussianBlur(blur)))


def background(room, painting, caption):
    c = ROOMS[room]
    img = Image.open(painting).convert("RGB")
    # Cover-crop to 16:9, then scale to the boot resolution
    iw, ih = img.size
    if iw / ih > W / H:
        nw = round(ih * W / H)
        img = img.crop(((iw - nw) // 2, 0, (iw - nw) // 2 + nw, ih))
    else:
        nh = round(iw * H / W)
        img = img.crop((0, (ih - nh) // 2, iw, (ih - nh) // 2 + nh))
    bg = img.resize((W, H), Image.LANCZOS).convert("RGBA")

    # Card: 0 2px 4px and 0 12px 32px shadows, a 1px frame, then the fill
    box = (CARD_X, CARD_Y, CARD_X + CARD_W, CARD_Y + CARD_H)
    bg = shadow(bg, box, RADIUS, px(2), px(2), 64)
    bg = shadow(bg, box, RADIUS, px(16), px(12), 102)
    bg.alpha_composite(rounded((CARD_W + 2 * S, CARD_H + 2 * S), RADIUS + S, c["frame"]), (CARD_X - S, CARD_Y - S))
    bg.alpha_composite(rounded((CARD_W, CARD_H), RADIUS, c["card"]), (CARD_X, CARD_Y))

    d = ImageDraw.Draw(bg)
    x = CARD_X + PAD
    d.text((x, KICKER_Y), os.uname().nodename.lower(), font=font(KITTY_MONO, 15), fill=c["dim"])
    d.text((x, HEAD_Y), "Choose a system", font=font(SERIF, 36, 500), fill=c["fg"])
    d.line((x, RULE1_Y, CARD_X + CARD_W - PAD, RULE1_Y), fill=c["rule"], width=S)
    d.line((x, RULE2_Y, CARD_X + CARD_W - PAD, RULE2_Y), fill=c["rule"], width=S)
    d.text((x, FOOT_Y + px(24)), "↑↓ choose   enter start   e edit   c console",
           font=font(MONO, 14), fill=c["dim"])

    # Wall label, as bierstadt-caption draws it (in points: the desktop runs at 2x)
    if caption:
        f = font(MONO_MEDIUM, 11)
        tw = sum(d.textlength(ch, font=f) + px(1.2) for ch in caption)
        pad, gap = px(18), px(32)
        lw, lh = round(tw + 2 * pad), px(11 + 4) + 2 * pad
        label = Image.new("RGBA", (lw, lh), c["label_bg"])
        bg.alpha_composite(label, (gap, H - gap - lh))
        spaced(d, (gap + pad, H - gap - lh + pad), caption, f, c["label"], px(1.2))

    return bg.convert("RGB")


def pill(path, color, w, h, r, radius=None):
    """The selection pill as GRUB's nine-slice: corners as _nw.._se, edges and centre stretched.
    `r` is the slice size and `radius` the corner rounding (`r` unless given)."""
    full = rounded((w, h), r if radius is None else radius, color)
    parts = {
        "nw": (0, 0, r, r), "n": (r, 0, w - r, r), "ne": (w - r, 0, w, r),
        "w": (0, r, r, h - r), "c": (r, r, w - r, h - r), "e": (w - r, r, w, h - r),
        "sw": (0, h - r, r, h), "s": (r, h - r, w - r, h), "se": (w - r, h - r, w, h),
    }
    for name, box in parts.items():
        full.crop(box).save(f"{path}_{name}.png")


def terminal_box(path, c):
    """The console and editor: a card like the menu's, floating over the boot
    menu. GRUB draws the slices outside the terminal, so each corner holds the
    shadow, the hairline frame and the padding. The text area itself is filled
    by gfxterm with kitty's background (06_bierstadt sets background_color)."""
    r = px(40)                 # slice size: shadow margin + padding
    m = px(16)                 # shadow margin; the card's edge sits r - m outside the text
    size = 3 * r
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    box = (m, m, size - m, size - m)
    img = shadow(img, box, RADIUS, px(6), px(4), 110)
    img.alpha_composite(rounded((size - 2 * m, size - 2 * m), RADIUS, c["frame"]), (m, m))
    img.alpha_composite(rounded((size - 2 * m - 2 * S, size - 2 * m - 2 * S), RADIUS - S, c["card"]), (m + S, m + S))
    parts = {
        "nw": (0, 0, r, r), "n": (r, 0, 2 * r, r), "ne": (2 * r, 0, size, r),
        "w": (0, r, r, 2 * r), "c": (r, r, 2 * r, 2 * r), "e": (2 * r, r, size, 2 * r),
        "sw": (0, 2 * r, r, size), "s": (r, 2 * r, 2 * r, size), "se": (2 * r, 2 * r, size, size),
    }
    for name, b in parts.items():
        img.crop(b).save(f"{path}_{name}.png")


def mkfont(out, src, size, name):
    """Build a .pf2 and return the name GRUB knows it by.

    grub-mkfont takes -n as the family only and stores "FAMILY STYLE PIXELS"
    (e.g. "Bierstadt DM Mono 18 Regular 36"). GRUB matches font names exactly
    and silently falls back to the last font loaded, so the theme has to use
    the stored name, read back from the file's NAME section.
    """
    subprocess.run(["grub-mkfont", "-s", str(size), "-n", name, "-o", out, src], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    with open(out, "rb") as fh:
        data = fh.read(4096)
    i = data.index(b"NAME") + 4
    n = int.from_bytes(data[i:i + 4], "big")
    return data[i + 4:i + 4 + n].rstrip(b"\0").decode()


def main():
    room, painting, caption, out = sys.argv[1:5]
    c = ROOMS[room]
    os.makedirs(out, exist_ok=True)
    # JPEG: a 4K PNG is ~10 MB and GRUB takes seconds to decode it
    background(room, painting, caption).save(os.path.join(out, "background.jpg"), quality=92)
    pill(os.path.join(out, "select"), c["sel_bg"], px(48), px(48), px(8))
    terminal_box(os.path.join(out, "terminal_box"), c)

    # GRUB fonts are bitmaps at a fixed pixel size; the names keep the point size.
    # The systems and the console/editor are in kitty's DM Mono, like the hostname.
    term = mkfont(os.path.join(out, "dm-mono-16.pf2"), KITTY_MONO, px(16), "Bierstadt DM Mono 16")
    item = mkfont(os.path.join(out, "dm-mono-18.pf2"), KITTY_MONO, px(18), "Bierstadt DM Mono 18")
    sel = mkfont(os.path.join(out, "dm-mono-medium-18.pf2"), KITTY_MONO_MEDIUM, px(18),
                 "Bierstadt DM Mono Medium 18")
    label = mkfont(os.path.join(out, "mono-14.pf2"), MONO, px(14), "Bierstadt Mono 14")

    inner_x, inner_w = CARD_X + PAD - px(14), CARD_W - 2 * PAD + px(28)
    theme = f"""# Bierstadt GRUB theme ({room} room). Generated by grub-build.py; edit that, not this.

title-text: ""
desktop-image: "background.jpg"
desktop-color: "{c['card']}"
terminal-font: "{term}"
terminal-box: "terminal_box_*.png"
terminal-left: "16%"
terminal-top: "14%"
terminal-width: "68%"
terminal-height: "72%"
terminal-border: "0"

+ boot_menu {{
  left = {pct(inner_x, W)}
  top = {pct(MENU_Y, H)}
  width = {pct(inner_w, W)}
  height = {pct(MENU_H, H)}
  item_font = "{item}"
  selected_item_font = "{sel}"
  item_color = "{c['fg']}"
  selected_item_color = "{c['sel_fg']}"
  selected_item_pixmap_style = "select_*.png"
  icon_width = 0
  icon_height = 0
  item_icon_space = 0
  item_height = {ITEM_H}
  item_padding = {px(14)}
  item_spacing = {px(4)}
  scrollbar = false
}}

+ label {{
  left = {pct(CARD_X + PAD, W)}
  top = {pct(FOOT_Y - px(2), H)}
  width = {pct(CARD_W - 2 * PAD, W)}
  align = "left"
  id = "__timeout__"
  text = "Starting in %d s"
  color = "{c['dim']}"
  font = "{label}"
}}
"""
    with open(os.path.join(out, "theme.txt"), "w", encoding="utf-8") as fh:
        fh.write(theme)


if __name__ == "__main__":
    main()
