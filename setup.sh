#!/bin/bash
# Needs: curl, imagemagick, python3-yaml, python3-pil, conky (for the caption),
# and the Suru++ Asprómauros icon theme.

set -euo pipefail

UA="bierstadt-desktop/1.0 (personal wallpaper script)"
FONTS="$HOME/.local/share/fonts/bierstadt"
PICTURES="$HOME/Pictures/bierstadt"

step() { printf '\n\033[1m%s\033[0m\n' "$1"; }

step "Fonts"
mkdir -p "$FONTS"
gf=https://github.com/google/fonts/raw/main/ofl
for f in "sourceserif4/SourceSerif4%5Bopsz,wght%5D.ttf" "sourceserif4/SourceSerif4-Italic%5Bopsz,wght%5D.ttf" \
         ibmplexmono/IBMPlexMono-Regular.ttf ibmplexmono/IBMPlexMono-Medium.ttf \
         ibmplexmono/IBMPlexMono-SemiBold.ttf ibmplexmono/IBMPlexMono-Italic.ttf \
         dmmono/DMMono-Regular.ttf dmmono/DMMono-Medium.ttf dmmono/DMMono-Italic.ttf; do
  name=$(basename "$f" | sed 's/%5B/[/; s/%5D/]/')
  [ -s "$FONTS/$name" ] || curl -fsSL -o "$FONTS/$name" "$gf/$f"
done
fc-cache -f "$HOME/.local/share/fonts" >/dev/null

step "Paintings"
mkdir -p "$PICTURES"
commons() {  # local-name "File:..."
  [ -s "$PICTURES/$1" ] && return
  local url
  url=$(curl -fsSG -A "$UA" https://commons.wikimedia.org/w/api.php \
    --data-urlencode "titles=$2" -d action=query -d prop=imageinfo -d iiprop=url -d format=json \
    | python3 -I -c 'import json,sys; d=json.load(sys.stdin); print(next(iter(d["query"]["pages"].values()))["imageinfo"][0]["url"].split("?")[0])')
  echo "  $1"
  curl -fsSL -A "$UA" -o "$PICTURES/$1" "$url"
}
commons monet-cliff-walk.jpg            "File:Claude Monet - Cliff Walk at Pourville - Google Art Project.jpg"
commons monsted-summer-stream.png       "File:Peder Mønsted - Sommerdag ved et åløb. Til højre græssende køer på marken - 1906.png"
commons polenov-moscow-courtyard.jpg    "File:Moscow Courtyard (Polenov, 1878) - Google Art Project.jpg"
commons kuindzhi-birch-grove.jpg        "File:0828Ha. Kuindzhi A.I. Birch Grove, 1879.jpg"
commons bierstadt-sierra-nevada.jpg     "File:Albert Bierstadt - Among the Sierra Nevada, California - Google Art Project.jpg"
commons bierstadt-landers-peak.jpg      "File:Albert Bierstadt - The Rocky Mountains, Lander's Peak.jpg"
commons bierstadt-valley-of-yosemite.jpg "File:Albert Bierstadt - Valley of the Yosemite - Google Art Project.jpg"
commons bierstadt-storm-rosalie.jpg     "File:Albert Bierstadt - A Storm in the Rocky Mountains, Mt. Rosalie - Google Art Project.jpg"
commons bierstadt-rocky-mountain-landscape.jpg "File:Albert Bierstadt - Rocky Mountain Landscape - Google Art Project.jpg"
commons church-twilight.jpg             "File:Frederic Edwin Church - Twilight in the Wilderness.jpg"
commons aivazovsky-ninth-wave.jpg       "File:Hovhannes Aivazovsky - The Ninth Wave - Google Art Project.jpg"
commons kuindzhi-moonlit-dnieper.jpg    "File:Arkhip Kuindzhi - Ночь на Днепре - Google Art Project.jpg"

step "Icons"
python3 -I "$HOME/.local/share/icons/bierstadt-icons-build.py"

step "Cursors"
python3 -I "$(dirname "$(readlink -f "$0")")/themes/cursors/build.py"

step "Xfce settings"
set_prop() {  # channel property type value
  xfconf-query -c "$1" -p "$2" -n -t "$3" -s "$4" 2>/dev/null || xfconf-query -c "$1" -p "$2" -s "$4"
}
set_ints() {  # channel property int...
  local c=$1 p=$2 a=(); shift 2
  for v in "$@"; do a+=(-t int -s "$v"); done
  xfconf-query -c "$c" -p "$p" -r 2>/dev/null || true
  xfconf-query -c "$c" -p "$p" -n "${a[@]}" --force-array
}

set_prop xsettings /Gtk/FontName string "Inter 10"
set_prop xsettings /Gtk/MonospaceFontName string "IBM Plex Mono 11"
set_prop xsettings /Xft/Antialias int 1
set_prop xsettings /Xft/Hinting int 1
set_prop xsettings /Xft/HintStyle string hintslight
set_prop xsettings /Xft/RGBA string rgb

set_prop xfwm4 /general/title_font string "Source Serif 4 Semi-Bold 10"
set_prop xfwm4 /general/title_alignment string center
set_prop xfwm4 /general/use_compositing bool true
set_prop xfwm4 /general/show_frame_shadow bool true
set_prop xfwm4 /general/shadow_opacity int 35
set_prop xfwm4 /general/shadow_delta_x int 0
set_prop xfwm4 /general/shadow_delta_y int 6
set_prop xfwm4 /general/shadow_delta_width int 0
set_prop xfwm4 /general/shadow_delta_height int 4
set_prop xfwm4 /general/workspace_count int 4
xfconf-query -c xfwm4 -p /general/workspace_names -r 2>/dev/null || true
xfconf-query -c xfwm4 -p /general/workspace_names -n -t string -s I -t string -s II -t string -s III -t string -s IV

set_prop xfce4-keyboard-shortcuts "/commands/custom/<Super>k" string kitty
set_prop xfce4-keyboard-shortcuts "/commands/custom/<Super>o" string obsidian

# The GTK theme styles the panel plugins by id, so keep these plugin ids.
P=xfce4-panel
xfconf-query -c $P -p /panels -r -R 2>/dev/null || true
xfconf-query -c $P -p /plugins -r -R 2>/dev/null || true
set_ints $P /panels 1
set_prop $P /panels/dark-mode bool false
set_prop $P /panels/panel-1/position string "p=6;x=0;y=0"
set_prop $P /panels/panel-1/position-locked bool true
set_prop $P /panels/panel-1/length double 100
set_prop $P /panels/panel-1/length-adjust bool false
set_prop $P /panels/panel-1/size int 40
set_prop $P /panels/panel-1/icon-size int 16
set_prop $P /panels/panel-1/mode int 0
set_prop $P /panels/panel-1/nrows int 1
set_prop $P /panels/panel-1/background-style int 0
set_ints $P /panels/panel-1/plugin-ids 1 7 2 11 30 8 15 17 20 21 6 14 23 3
for id_type in 1:applicationsmenu 7:separator 2:tasklist 11:separator 30:pager 8:separator \
               15:systray 17:notification-plugin 20:pulseaudio 21:power-manager-plugin \
               6:systemload 14:separator 23:clock 3:actions; do
  set_prop $P "/plugins/plugin-${id_type%%:*}" string "${id_type#*:}"
done
for id in 7 8 14; do set_prop $P /plugins/plugin-$id/style int 0; set_prop $P /plugins/plugin-$id/expand bool false; done
set_prop $P /plugins/plugin-11/style int 0
set_prop $P /plugins/plugin-11/expand bool true
set_prop $P /plugins/plugin-1/show-button-title bool true
set_prop $P /plugins/plugin-1/button-title string "MENU"
set_prop $P /plugins/plugin-1/button-icon string ""
set_prop $P /plugins/plugin-1/show-menu-icons bool false
set_prop $P /plugins/plugin-2/flat-buttons bool true
set_prop $P /plugins/plugin-2/show-labels bool false
set_prop $P /plugins/plugin-2/show-handle bool false
set_prop $P /plugins/plugin-30/miniature-view bool false
set_prop $P /plugins/plugin-30/rows int 1
set_prop $P /plugins/plugin-30/workspace-scrolling bool false
set_prop $P /plugins/plugin-15/icon-size int 16
set_prop $P /plugins/plugin-15/symbolic-icons bool true
set_prop $P /plugins/plugin-15/square-icons bool true
set_prop $P /plugins/plugin-23/mode int 2
set_prop $P /plugins/plugin-23/digital-layout int 3
set_prop $P /plugins/plugin-23/digital-time-font string "Source Serif 4 11"
set_prop $P /plugins/plugin-23/digital-time-format string '<span font_family="Source Serif 4" font_features="smcp, c2sc" letter_spacing="600">%a %d %b · %H:%M</span>'
set_prop $P /plugins/plugin-23/tooltip-format string "%A %d %B %Y"
xfce4-panel -r

step "Room"
bierstadt-mode data
bierstadt-mode "$(bierstadt-mode status)"
(xfwm4 --replace >/dev/null 2>&1 &)
echo
echo "Done. Switch rooms with: bierstadt-mode light | dark | toggle"
