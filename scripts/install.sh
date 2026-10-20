#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Install required packages for the Ricing-Arch dotfiles
sudo pacman -S --needed --noconfirm \
  hyprland \
  quickshell \
  kitty \
  mpd \
  rmpc \
  vicinae \
  greetd \
  dms-shell \
  awww \
  mpv \
  ffmpeg

# Backup and copy dotfiles
mkdir -p "$HOME/.config"
for cfg in "$REPO_DIR"/dotfiles/*; do
  name="$(basename "$cfg")"
  if [ -e "$HOME/.config/$name" ]; then
    mv "$HOME/.config/$name" "$HOME/.config/${name}.bak.$(date +%s)"
  fi
  cp -r "$cfg" "$HOME/.config/$name"
done

# Copy icons
mkdir -p "$HOME/.icons"
cp -r "$REPO_DIR"/icons/* "$HOME/.icons/" 2>/dev/null || true

# Ensure ~/.local/bin is on PATH
if ! grep -q 'export PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc" 2>/dev/null; then
  echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi
if [ -d "$REPO_DIR/scripts/tty-clock" ]; then
  (cd "$REPO_DIR/scripts/tty-clock" && make && install -D -m 755 tty-clock "$HOME/.local/bin/tty-clock")
fi

echo "Done. Log out and back in to apply."
