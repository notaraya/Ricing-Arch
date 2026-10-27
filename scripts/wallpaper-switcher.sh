#!/usr/bin/env bash

set -Eeuo pipefail

WALLPAPER_DIR="$HOME/Wallpaper"
THEME_DIR="$HOME/.config/themes"
ROFI_THEME="$HOME/.config/rofi/theme.rasi"
BG_IMAGE="$THEME_DIR/bg.png"
COLOR_SCRIPT="$THEME_DIR/wallpaper_colors.py"

error() {
    echo "Error: $*" >&2
    notify-send "Wallpaper Switcher" "$*" 2>/dev/null || true
}

for cmd in rofi awww python3; do
    command -v "$cmd" >/dev/null 2>&1 || {
        error "Missing dependency: $cmd"
        exit 1
    }
done

[[ -d "$WALLPAPER_DIR" ]] || {
    error "Wallpaper directory not found"
    exit 1
}

[[ -f "$COLOR_SCRIPT" ]] || {
    error "wallpaper_colors.py not found"
    exit 1
}

mkdir -p "$THEME_DIR"

# Step 1: Choose category
CATEGORY=$(
    find "$WALLPAPER_DIR" -mindepth 1 -maxdepth 1 \
        -type d -printf '%f\n' |
        sort |
        rofi -dmenu -i \
            -p "Wallpaper Category" \
            -theme "$ROFI_THEME"
) || exit 0

[[ -n "$CATEGORY" ]] || exit 0

CATEGORY_DIR="$WALLPAPER_DIR/$CATEGORY"

[[ -d "$CATEGORY_DIR" && "$CATEGORY" != */* ]] || {
    error "Invalid wallpaper category"
    exit 1
}

# Step 2: Show wallpaper thumbnails in Rofi
IMAGE=$(
    while IFS= read -r file; do
        [[ -n "$file" ]] || continue

        # Rofi dmenu icon metadata: visible label + image path
        printf '%s\0icon\x1f%s\n' \
            "$file" "$CATEGORY_DIR/$file"
    done < <(
        find "$CATEGORY_DIR" -type f \
            \( -iname '*.png' -o -iname '*.jpg' \
            -o -iname '*.jpeg' -o -iname '*.webp' \
            -o -iname '*.bmp' \) \
            -printf '%P\n' |
            sort
    ) |
        rofi -dmenu -i \
            -p "Wallpaper: $CATEGORY" \
            -show-icons \
            -theme "$ROFI_THEME" \
            -theme-str 'element-icon { size: 100px; } listview { columns: 3; lines: 3; } element { orientation: vertical; }'
) || exit 0

[[ -n "$IMAGE" ]] || exit 0

SELECTED_IMAGE="$CATEGORY_DIR/$IMAGE"

[[ -f "$SELECTED_IMAGE" ]] || {
    error "Selected wallpaper not found: $IMAGE"
    exit 1
}

echo "Selected: $SELECTED_IMAGE"

# Step 3: Copy selected image
cp -- "$SELECTED_IMAGE" "$BG_IMAGE"

# Step 4: Generate palette and update themes.txt
(
    cd "$THEME_DIR"
    python3 wallpaper_colors.py bg.png -o themes.txt
) || {
    error "Wallpaper color generation failed"
    exit 1
}

# Step 5: Apply wallpaper with a random transition
awww img "$BG_IMAGE" \
    --transition-type random \
    --transition-duration 2 || {
    error "Could not apply wallpaper. Check awww-daemon."
    exit 1
}

notify-send "Wallpaper Switcher" \
    "Category: $CATEGORY\nWallpaper: $IMAGE" \
    2>/dev/null || true

echo "Wallpaper switched successfully!"
