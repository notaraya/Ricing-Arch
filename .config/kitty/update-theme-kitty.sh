#!/usr/bin/env bash
set -euo pipefail

python3 "$HOME/.config/themes/apply-theme.py"

# Discover the active Kitty instance's listening socket.
kitty @ ls 2>/dev/null |
    grep -o '"KITTY_LISTEN_ON": "[^"]*"' |
    sed -E 's/.*"([^"]+)"$/\1/' |
    sort -u |
    while IFS= read -r socket; do
        [[ -n "$socket" ]] || continue
        kitty @ --to "$socket" set-colors --all \
            "$HOME/.config/kitty/theme.conf" || true
    done
