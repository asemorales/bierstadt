#!/usr/bin/env python3
"""Build the bierstadt and bierstadt-dark icon themes from Suru++-Asprómauros.

Run again after changing a colour:

    python3 -I ~/.local/share/icons/bierstadt-icons-build.py
"""
import colorsys
import os
import re
import shutil
import subprocess

SRC = "/usr/share/icons/Suru++-Asprómauros"
DEST = os.path.expanduser("~/.local/share/icons")

PAPER, INK, NIGHT, NIGHT_SEL = "#F2ECDF", "#231A15", "#191612", "#E0D9CD"

# Colours the source uses for glyphs (ColorScheme-Text) and their highlight.
GLYPH = {"#c0caf5", "#ececec"}
HIGHLIGHT = {"#1ad6ab"}


def rgb(h):
    h = h.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def hexc(t):
    return "#%02X%02X%02X" % tuple(max(0, min(255, round(x))) for x in t)


def mix(a, b, t):
    a, b = rgb(a), rgb(b)
    return hexc(x + (y - x) * t for x, y in zip(a, b))


VARIANTS = {
    "bierstadt": dict(glyph=mix(PAPER, INK, 0.78), highlight=mix(PAPER, INK, 0.45),
                    dark=INK, light=PAPER),
    "bierstadt-dark": dict(glyph=NIGHT_SEL, highlight="#9E958A",
                         dark=NIGHT, light=NIGHT_SEL),
}


def remap(h, v, cache):
    key = h.lower()
    if len(key) == 4:
        key = "#" + "".join(c * 2 for c in key[1:])
    if key in cache:
        return cache[key]
    if key in GLYPH:
        out = v["glyph"]
    elif key in HIGHLIGHT:
        out = v["highlight"]
    elif key in ("#FFFCF6", "#000000"):
        out = h
    else:
        r, g, b = (x / 255 for x in rgb(key))
        _, light, _ = colorsys.rgb_to_hls(r, g, b)
        out = mix(v["dark"], v["light"], light)
    cache[key] = out
    return out


HEX = re.compile(r"#[0-9A-Fa-f]{6}\b|#[0-9A-Fa-f]{3}\b")


def build(name, v):
    out = os.path.join(DEST, name)
    if os.path.exists(out):
        shutil.rmtree(out)
    shutil.copytree(SRC, out, symlinks=True)
    cache = {}
    n = 0
    for root, _, files in os.walk(out):
        for f in files:
            p = os.path.join(root, f)
            if os.path.islink(p):
                target = os.readlink(p)
                if target.startswith(SRC):
                    os.unlink(p)
                    os.symlink(os.path.relpath(out + target[len(SRC):], root), p)
                continue
            if not f.endswith(".svg"):
                continue
            with open(p, encoding="utf-8", errors="surrogateescape") as fh:
                s = fh.read()
            s2 = HEX.sub(lambda m: remap(m.group(0), v, cache), s)
            if s2 != s:
                with open(p, "w", encoding="utf-8", errors="surrogateescape") as fh:
                    fh.write(s2)
                n += 1
    idx = os.path.join(out, "index.theme")
    with open(idx, encoding="utf-8") as fh:
        s = fh.read()
    s = re.sub(r"(?m)^Name=.*$", f"Name={name}", s, count=1)
    s = re.sub(r"(?m)^Comment=.*$",
               "Comment=Suru++ Asprómauros recoloured to the Bierstadt palette", s, count=1)
    with open(idx, "w", encoding="utf-8") as fh:
        fh.write(s)
    cache_file = os.path.join(out, "icon-theme.cache")
    if os.path.exists(cache_file):
        os.unlink(cache_file)
    subprocess.run(["gtk-update-icon-cache", "-f", "-q", out], check=False)
    print(f"built {out}: {n} files recoloured")


if __name__ == "__main__":
    for name, v in VARIANTS.items():
        build(name, v)
