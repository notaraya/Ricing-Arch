# Ricing-Arch

Arch Linux rice configuration repository.

Includes:
- QuickShell config
- Hyprland config
- Kitty terminal config
- MPD + rmpc config
- Vicinae config
- Greetd greeter config
- Wallpapers
- Helper scripts

## Structure
- `dotfiles/` - configuration files
- `wallpapers/` - wallpapers
- `scripts/` - helper scripts, including `install.sh`

## Usage
Run the installer:

```bash
./scripts/install.sh
```

It installs required packages, backs up existing configs, copies dotfiles, and installs wallpapers. Log out and back in to apply.

To sync the greeter with your current wallpaper/theme:

```bash
./scripts/sync-greeter.sh
```