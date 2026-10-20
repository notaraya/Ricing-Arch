#!/bin/bash
# Random wallpaper for awww — triggered by mod + W
# Picks a random image from ~/Pictures/Wallpapers and a random transition
# Conditions: always use an animation, never repeat the same transition twice

WALLPAPER_DIR="$HOME/Pictures/Wallpaper"
LAST_TRANSITION_FILE="/tmp/awww-last-transition"

# Bail if the directory is missing
if [ ! -d "$WALLPAPER_DIR" ]; then
    echo "Wallpaper dir $WALLPAPER_DIR not found"
    exit 1
fi

# Pick a random image
IMAGE=$(find "$WALLPAPER_DIR" -type f \( -iname "*.png" -o -iname "*.jpg" -o -iname "*.jpeg" -o -iname "*.gif" -o -iname "*.webp" \) | shuf -n 1)

if [ -z "$IMAGE" ]; then
    echo "No images found in $WALLPAPER_DIR"
    exit 1
fi

# Pick a random transition — exclude "none" (instant, no animation)
TRANSITIONS=(simple fade left right top bottom wipe wave grow center any outer random)

# Remove the last used transition so we never repeat it twice in a row
if [ -f "$LAST_TRANSITION_FILE" ]; then
    LAST_TRANSITION=$(cat "$LAST_TRANSITION_FILE")
    FILTERED=()
    for t in "${TRANSITIONS[@]}"; do
        [ "$t" != "$LAST_TRANSITION" ] && FILTERED+=("$t")
    done
    TRANSITIONS=("${FILTERED[@]}")
fi

TRANSITION=${TRANSITIONS[$RANDOM % ${#TRANSITIONS[@]}]}

# Remember this transition for next time
echo "$TRANSITION" > "$LAST_TRANSITION_FILE"

# Apply wallpaper via awww (faster, smoother transition, always animated)
awww img "$IMAGE" --transition-type "$TRANSITION" --transition-step 160 --transition-fps 60

# --- Derive a theme from the wallpaper: Hyprland borders + kitty colours ---
# Extracts the most saturated/bright colours, rewrites kitty's
# wallpaper-theme.conf and the colours in hyprland.lua, generates a DMS
# bar custom theme + vicinae theme, then applies the borders immediately,
# tells kitty to reload its config, and switches vicinae + DMS bar themes.
if THEME_VARS=$(python3 "$HOME/.config/hypr/wallpaper-theme.py" "$IMAGE"); then
    eval "$THEME_VARS"

    hyprctl keyword general:col.active_border   "$HYPR_ACTIVE_BORDER"   >/dev/null
    hyprctl keyword general:col.inactive_border "$HYPR_INACTIVE_BORDER" >/dev/null

    # SIGUSR1 makes every kitty window reload its config (picks up the new palette)
    pkill -USR1 -x kitty

    # Vicinae: switch to the wallpaper-derived theme.
    # Non-fatal if the vicinae server isn't running yet.
    if [ -n "$VICINAE_THEME" ] && [ -f "$HOME/.local/share/vicinae/themes/${VICINAE_THEME}.toml" ]; then
        vicinae theme set "$VICINAE_THEME" >/dev/null 2>&1 || true
    fi

    # DMS bar: wallpaper-derived custom theme.
    # settings.json selects currentThemeName="custom" + customThemeFile pointing
    # at themes/wallpaper/theme.json, which wallpaper-theme.py just regenerated.
    # DMS auto-reloads that file via its file watcher when running the "custom"
    # theme — no CLI call needed.
    if [ -n "$DMS_THEME" ] && [ -f "$HOME/.config/DankMaterialShell/themes/wallpaper/theme.json" ]; then
        touch "$HOME/.config/DankMaterialShell/themes/wallpaper/theme.json" >/dev/null 2>&1 || true
    fi
else
    echo "Theme generation failed — keeping the previous theme" >&2
fi
