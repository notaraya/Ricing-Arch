#!/usr/bin/env bash
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing rice dotfiles from $DIR"

# Create necessary directories
mkdir -p ~/.config ~/.local/bin ~/.local/share/fonts ~/.cache

# Copy .config
echo "Copying .config..."
cp -r "$DIR/.config/"* ~/.config/ 2>&1 | tail -2

# Copy wallpapers
if [ -d "$DIR/Wallpapers" ]; then
  echo "Copying wallpapers to ~/Wallpaper..."
  mkdir -p ~/Wallpaper
  cp -r "$DIR/Wallpapers/"* ~/Wallpaper/ 2>&1 | tail -2
fi

# Install fonts
if [ -d "$DIR/fonts" ]; then
  echo "Installing fonts..."
  cp -r "$DIR/fonts/"* ~/.local/share/fonts/ 2>&1 | tail -2
  fc-cache -fv >/dev/null 2>&1
fi

# Install scripts to ~/.local/bin
if [ -d "$DIR/scripts" ]; then
  echo "Installing scripts to ~/.local/bin..."
  cp "$DIR/scripts/"* ~/.local/bin/ 2>&1 | tail -2
  chmod +x ~/.local/bin/* 2>&1 | tail -1
fi

# SDDM theme (requires sudo)
if [ -d "$DIR/sddm/pixie" ]; then
  echo "SDDM theme found at $DIR/sddm/pixie"
  echo "To install SDDM theme (system-wide): sudo cp -r $DIR/sddm/pixie /usr/share/sddm/themes/"
  echo "Configure in /etc/sddm.conf.d/ with [Theme] Current=pixie"
fi

# Enable notification daemon service
if systemctl --user list-unit-files | grep -q notification-daemon; then
  systemctl --user enable --now notification-daemon.service 2>&1 | tail -2
fi

echo ""
echo "Installation complete!"
echo "Note: Some paths may need adjustment (browser, file manager, weather location in waybar)."
echo "Review .config/hypr/modules/binds.lua and .config/waybar/config.jsonc"
