#!/usr/bin/env bash
set -u

PALETTE="$HOME/.config/themes/themes.txt"
GENERATOR="$HOME/.config/rofi/generate-theme.sh"

# Generate the theme immediately.
"$GENERATOR"

# Watch the directory so replacing themes.txt is detected too.
while inotifywait -q -e close_write,create,moved_to \
    "$(dirname "$PALETTE")"; do
    if [[ -f "$PALETTE" ]]; then
        "$GENERATOR"
    fi
done
