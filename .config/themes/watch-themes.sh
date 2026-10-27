
#!/usr/bin/env bash
set -u

THEME_DIR="$HOME/.config/themes"
PALETTE="$THEME_DIR/themes.txt"
GENERATOR="$THEME_DIR/apply-theme.py"
RELOAD="$HOME/.config/waybar/reload.sh"

while true; do
    inotifywait -q -e close_write,moved_to "$PALETTE" || {
        sleep 1
        continue
    }

    sleep 0.2

    if [[ -f "$PALETTE" ]]; then
        echo "Palette changed; regenerating themes..."

        if python3 "$GENERATOR"; then
            echo "Reloading Waybar..."
            "$RELOAD"
        else
            echo "Theme generation failed."
        fi
    fi
done
