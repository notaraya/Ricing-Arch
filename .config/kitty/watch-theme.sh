#!/usr/bin/env bash
set -u

PALETTE="$HOME/.config/themes/themes.txt"
THEME="$HOME/.config/kitty/theme.conf"

reload_kitty() {
    kitty @ ls 2>/dev/null |
        grep -o '"KITTY_LISTEN_ON": "[^"]*"' |
        sed -E 's/.*"([^"]+)"$/\1/' |
        sort -u |
        while IFS= read -r socket; do
            [[ -n "$socket" ]] || continue
            kitty @ --to "$socket" set-colors --all "$THEME" || true
        done
}

while true; do
    inotifywait -q -e close_write,moved_to "$PALETTE" || {
        sleep 1
        continue
    }

    # Allow the shared watcher to regenerate theme.conf first.
    sleep 1
    reload_kitty
done
