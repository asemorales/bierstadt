#!/bin/bash

set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

do_link() {
  src="$1"
  target="$2"
  mkdir -p "$(dirname "$target")"
  if [ -L "$target" ] && [ "$(readlink "$target")" = "$src" ]; then
    return
  elif [ -L "$target" ]; then
    echo -e "\033[1;36mUPDATED:\033[0m  $target"
    ln -sfn "$src" "$target"
  elif [ ! -e "$target" ]; then
    echo -e "\033[1;32mCREATED:\033[0m  $target"
    ln -s "$src" "$target"
  elif [ -f "$target" ] && cmp -s "$src" "$target"; then
    echo -e "\033[1;33mREPLACED:\033[0m $target"
    ln -sf "$src" "$target"
  else
    echo -e "\033[1;31mSKIPPED:\033[0m  $target"
  fi
}

mozilla_profile() {
  awk -F= '/^\[Install/ { s = 1; next } /^\[/ { s = 0 } s && $1 == "Default" { print $2; exit }' \
    "$1/profiles.ini" 2>/dev/null || true
}

link_config() { do_link "$REPO/config/$1" "$HOME/.config/$1"; }
link_theme()  { do_link "$REPO/themes/$1" "$HOME/.themes/$1"; }
link_local()  { do_link "$REPO/local/$1" "$HOME/.local/$1"; }

link_mozilla() {
  local profile
  profile="$(mozilla_profile "$2")"
  [ -n "$profile" ] || return 0
  do_link "$REPO/$1/$3" "$2/$profile/$3"
}

link_config autostart/bierstadt-bar.desktop
link_config autostart/bierstadt-caption.desktop
link_config bierstadt/wall.yml
link_config btop/themes
link_config eww
link_config kitty/bierstadt-dark.conf
link_config kitty/bierstadt-light.conf
link_config nvim/colors/bierstadt.lua
link_config yazi/theme.toml
link_config yazi/flavors/bierstadt-dark.yazi
link_config yazi/flavors/bierstadt-light.yazi

link_theme bierstadt
link_theme bierstadt-dark

for f in "$REPO"/local/bin/bierstadt-*; do
  link_local "bin/$(basename "$f")"
done
link_local share/icons/bierstadt-icons-build.py

link_mozilla firefox "$HOME/.mozilla/firefox" user.js
link_mozilla firefox "$HOME/.mozilla/firefox" chrome/userChrome.css
link_mozilla thunderbird "$HOME/.thunderbird" user.js
link_mozilla thunderbird "$HOME/.thunderbird" chrome/userChrome.css
link_mozilla thunderbird "$HOME/.thunderbird" chrome/userContent.css
