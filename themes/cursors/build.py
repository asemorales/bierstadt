#!/usr/bin/env python3
"""Build the Bierstadt cursors from Bibata Modern.

    python3 -I themes/cursors/build.py

Debian's libXcursor skips ~/.local/share/icons, so each theme is also linked
into ~/.icons for kitty and xfwm4.
"""
import glob
import os
import shutil
import subprocess
import tempfile
import tomllib
import urllib.request

TAG = "v2.0.7"
CACHE = os.path.expanduser(f"~/.cache/bierstadt/bibata-{TAG}")
ICONS = os.path.expanduser("~/.local/share/icons")
DOT_ICONS = os.path.expanduser("~/.icons")
SIZES = [24, 32, 48, 64, 72, 96]
SRC = 256  # Bibata draws on a 256px canvas, and hotspots are in those units

# Bibata's placeholders: #00FF00 body, #0000FF outline, #FF0000 the watch face.
SPINNER = ("#32A0DA", "#F05024", "#FCB813", "#7EBA41")


def variant(body, outline, mid):
    return {"#00FF00": body, "#0000FF": outline, "#FF0000": outline,
            **dict(zip(SPINNER, (body, mid, body, mid)))}


VARIANTS = {
    "bierstadt-cursors-dark": variant("#E3D8C4", "#191612", "#9E958A"),
    "bierstadt-cursors": variant("#231A15", "#F2ECDF", "#6B6560"),
}


def fetch():
    if os.path.isdir(CACHE):
        return
    url = f"https://github.com/ful1e5/Bibata_Cursor/archive/refs/tags/{TAG}.tar.gz"
    data = urllib.request.urlopen(url).read()
    os.makedirs(os.path.dirname(CACHE), exist_ok=True)
    tmp = tempfile.mkdtemp(dir=os.path.dirname(CACHE))
    # Debian's Python 3.11.2 predates extractall(filter=), so let tar do it.
    subprocess.run(["tar", "xzf", "-", "-C", tmp, "--no-same-owner"], input=data, check=True)
    os.rename(os.path.join(tmp, os.listdir(tmp)[0]), CACHE)
    os.rmdir(tmp)


def render(svg, colours, png, size):
    text = open(svg, encoding="utf-8").read()
    for old, new in colours.items():
        text = text.replace(old, new).replace(old.lower(), new)
    subprocess.run(["rsvg-convert", "-w", str(size), "-h", str(size), "-o", png],
                   input=text.encode(), check=True)


def build(name, colours, config, svgs):
    out = os.path.join(ICONS, name)
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(os.path.join(out, "cursors"))
    fallback = config["cursors"].pop("fallback_settings")
    delay = fallback.get("x11_delay", 40)

    with tempfile.TemporaryDirectory() as work:
        for key, cur in config["cursors"].items():
            stem = cur["png"].removesuffix(".png")
            if "*" in stem:  # animated: a folder of numbered frames
                frames = sorted(glob.glob(os.path.join(svgs, stem.split("-*")[0], "*.svg")))
            else:
                frames = [os.path.join(svgs, stem + ".svg")]
            if not frames or not os.path.exists(frames[0]):
                continue
            hx = cur.get("x_hotspot", fallback["x_hotspot"])
            hy = cur.get("y_hotspot", fallback["y_hotspot"])
            lines = []
            for size in SIZES:
                for i, svg in enumerate(frames):
                    png = os.path.join(work, f"{key}-{size}-{i:02}.png")
                    render(svg, colours, png, size)
                    line = f"{size} {round(hx * size / SRC)} {round(hy * size / SRC)} {png}"
                    lines.append(line + (f" {delay}" if len(frames) > 1 else ""))
            cfg = os.path.join(work, key + ".cfg")
            open(cfg, "w").write("\n".join(lines) + "\n")
            target = cur["x11_name"]
            subprocess.run(["xcursorgen", cfg, os.path.join(out, "cursors", target)], check=True)
            for link in cur.get("x11_symlinks", []):
                path = os.path.join(out, "cursors", link)
                if not os.path.lexists(path):
                    os.symlink(target, path)

    with open(os.path.join(out, "index.theme"), "w") as f:
        f.write(f"[Icon Theme]\nName={name}\nComment=Bibata Modern in Bierstadt's ink and paper\n")
    os.makedirs(DOT_ICONS, exist_ok=True)
    link = os.path.join(DOT_ICONS, name)
    if os.path.islink(link):
        os.unlink(link)
    os.symlink(out, link)
    print(out)


def main():
    fetch()
    for name, colours in VARIANTS.items():
        with open(os.path.join(CACHE, "configs/normal/x.build.toml"), "rb") as f:
            config = tomllib.load(f)
        build(name, colours, config, os.path.join(CACHE, "svg/modern"))


if __name__ == "__main__":
    main()
