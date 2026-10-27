# Ricing-Arch

My Arch Linux Hyprland rice - dotfiles with dynamic theming based on wallpaper colors.

## Overview

This rice uses Hyprland (Lua config) with a dynamic theming system that extracts colors from wallpapers and applies them across the system. Includes Waybar, Rofi, Kitty, notification daemon, and various utilities.

## Structure

```
Ricing-Arch/
├── .config/
│   ├── hypr/           # Hyprland config (Lua)
│   │   ├── hyprland.lua
│   │   ├── modules/    # Modular config (binds, window rules, look&feel, etc.)
│   │   └── floating_sizes.tsv
│   ├── waybar/         # Status bar config and styling
│   ├── rofi/           # App launcher with theme watching
│   ├── kitty/          # Terminal emulator config
│   ├── rmpc/           # MPD client config (not music files)
│   ├── themes/         # Theme system, wallpaper colors, scripts
│   └── systemd/user/   # Notification daemon service
├── Wallpapers/         # Wallpaper collections
├── fonts/              # JetBrainsMono Nerd Font
├── scripts/            # Utility scripts (tty-clock, pipes.sh, wallpaper-switcher, etc.)
├── sddm/               # SDDM theme (pixie)
└── README.md
```

## Components

- **Window Manager**: [Hyprland](https://hyprland.org/) (Lua configuration)
- **Bar**: [Waybar](https://github.com/Alexays/Waybar)
- **Launcher**: [Rofi](https://github.com/davatorium/rofi)
- **Terminal**: [Kitty](https://sw.kovidgoyal.net/kitty/)
- **Notifications**: notification-daemon (systemd user service)
- **Music Client**: [rmpc](https://mierak.github.io/rmpc/) (config only)
- **Wallpaper Manager**: awww + custom scripts
- **Display Manager**: SDDM (pixie theme)

## Keybindings

### General
| Keybind | Action |
| --- | --- |
| `SUPER + RETURN` | Open terminal (kitty) |
| `SUPER + Q` | Close window |
| `SUPER + L` | Lock/exit (hyprshutdown or exit) |
| `SUPER + E` | Open file manager (kitty -e spf) |
| `SUPER + SPACE` | Open app launcher (rofi) |
| `SUPER + B` | Open browser (helium-browser) |
| `SUPER + P` | Toggle pseudo tiling (dwindle) |
| `SUPER + J` | Toggle split (dwindle) |
| `SUPER + F` | Toggle fullscreen |

### Window Management
| Keybind | Action |
| --- | --- |
| `SUPER + A` | Toggle floating with remembered size per app class (persists in `floating_sizes.tsv`) |
| `SUPER + SHIFT + S` | Move window to special workspace "magic" |
| `SUPER + S` | Toggle special workspace "magic" (scratchpad) |
| `SUPER + left/right/up/down` | Focus window in direction |
| `SUPER + mouse:272 (LMB)` | Drag window (with SUPER) |
| `SUPER + mouse:273 (RMB)` | Resize window (with SUPER) |

### Workspaces
| Keybind | Action |
| --- | --- |
| `SUPER + [1-0]` | Switch to workspace 1-10 |
| `SUPER + ALT + [1-0]` | Move active window to workspace 1-10 |
| `SUPER + mouse_down` | Next workspace |
| `SUPER + mouse_up` | Previous workspace |

### Wallpaper & Screenshots
| Keybind | Action |
| --- | --- |
| `Print` | Screenshot region with satty (`hyprshot -m region --raw \| satty --filename -`) |
| `SUPER + W` | Wallpaper switcher (`~/.local/bin/wallpaper-switcher.sh`) |
| `SUPER + SHIFT + W` | Random wallpaper (`python3 ~/.config/themes/random_wallpaper.py`) |

### Media & Volume (Function Keys)
| Keybind | Action |
| --- | --- |
| `XF86AudioRaiseVolume` | Volume up 5% |
| `XF86AudioLowerVolume` | Volume down 5% |
| `XF86AudioMute` | Toggle mute |
| `XF86AudioMicMute` | Toggle mic mute |
| `XF86AudioPlay/Pause` | Play/pause (playerctl) |
| `XF86AudioNext` | Next track |
| `XF86AudioPrev` | Previous track |
| `XF86MonBrightnessUp` | Brightness up 5% |
| `XF86MonBrightnessDown` | Brightness down 5% |

## Window Rules

Configured in `.config/hypr/modules/window.lua`:

- **Maximize suppression**: All windows ignore maximize requests
- **XWayland drag fixes**: No focus on certain XWayland floating windows with no class/title
- **Hyprland-run**: Moves to `20 monitor_h-120` and floats
- **Floating window size memory**: Windows toggled floating with `SUPER+A` have their size remembered per class and restored on subsequent floating toggle
- **Layouts**: Dwindle (preserve split), Master, Scrolling (fullscreen on one column)

## Autostart

From `.config/hypr/modules/autostart.lua`:
- `awww-daemon` - Wallpaper daemon
- Rofi theme watcher
- Kitty theme watcher  
- Themes watcher (for dynamic theming)
- `wl-clip-persist` - Clipboard persistence
- `notification-daemon` (both via service and direct exec)
- `mpd` - Music Player Daemon
- `waybar` (delayed 2s)
- ChatGPT URL (legacy)

## Dynamic Theming System

The theme system reads colors from `~/.config/themes/themes.txt` (16 colors) and dynamically generates:

- **GTK 3/4 CSS** (`~/.config/gtk-3.0/hyprland-colors.css`, `~/.config/gtk-4.0/hyprland-colors.css`) - imported into existing gtk.css
- **Qt6ct color scheme** (`~/.config/qt6ct/colors/hyprland.conf`) and sets it in qt6ct.conf
- **Hyprland borders** - Uses accent colors from palette with gradient
- **System color scheme** - Sets `prefer-dark` via gsettings

Theme is only regenerated if palette checksum changes (cached in `~/.cache/hyprland-theme/`).

**Palette structure** (from `look_feel.lua`):
- Colors 1-7: Ranked accent colors
- Colors 8-11: Dark background shades (lightest to darkest)  
- Colors 12-15: Secondary dark shades
- Color 16: Brightest highlight/foreground

## Waybar Modules

- **Left**: Arch logo, workspaces, window title
- **Center**: Clock, weather (Jammu via Open-Meteo), MPD status
- **Right**: Tray, memory, network, bluetooth, pulseaudio, CPU, battery

Weather location is hardcoded to Jammu (lat=32.73, lon=74.87).

## Rofi Theme

Custom dark theme with orange/peach accent colors (`#FACBB5`), rounded corners, icon support.

## Kitty

Terminal with theme integration via watch scripts.

## rmpc

MPD client with custom layout - album art on left, queue on right with header. Vim-style keybindings. Tabs for Queue, Directories, Artists, Album Artists, Albums, Playlists, Search.

## Wallpapers

Organized in categories under `Wallpapers/`: abstract, animals, anime, catppuccin, city, e-ink, gaming, gruvbox, japan, landscape, minimal, nord, os, retro, space, synthwave, vaporwave, etc.

## Fonts

- JetBrainsMono Nerd Font (all weights/styles) - installed system-wide and included here

## Scripts Included

- `tty-clock` - Terminal clock
- `pipes.sh` / `pipesz` - Terminal pipes screensaver
- `wallpaper-switcher.sh` - Wallpaper switching utility

## Installation

1. Clone/copy this repo to your system
2. Symlink or copy `.config/*` to `~/.config/`
3. Copy `Wallpapers/` to your preferred location (update paths in scripts if needed)
4. Copy fonts to `~/.local/share/fonts/` and run `fc-cache -fv`
5. For SDDM theme, copy `sddm/pixie/` to `/usr/share/sddm/themes/` and configure in `/etc/sddm.conf.d/`
6. Enable notification-daemon service: `systemctl --user enable --now notification-daemon.service`
7. Ensure dependencies are installed: hyprland, waybar, rofi, kitty, awww, wl-clip-persist, notification-daemon, mpd, mpc, playerctl, brightnessctl, hyprshot, satty, python, pavucontrol, nmtui, bluetui, spf (superfile), helium-browser, jq/wget/curl as needed

## Notes

- Browser is set to `helium-browser` - change in `hypr/modules/binds.lua` if different
- File manager is `spf` (superfile) launched in kitty
- Weather is hardcoded to Jammu - update coordinates in waybar config
- The autostart has a ChatGPT URL that opens on start (line 21 in autostart.lua) - you may want to remove this
- rmpc config is included but requires MPD to be running
- Theme watching scripts require inotify-tools or similar
