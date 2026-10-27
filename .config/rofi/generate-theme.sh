#!/usr/bin/env bash
set -euo pipefail

PALETTE="$HOME/.config/themes/themes.txt"
OUTPUT="$HOME/.config/rofi/theme.rasi"

# Extract hex colors in written order.
mapfile -t colors < <(
    grep -oE '#[[:xdigit:]]{6}([[:xdigit:]]{2})?' "$PALETTE"
)

if ((${#colors[@]} < 16)); then
    echo "Error: themes.txt must contain at least 16 hex colors." >&2
    exit 1
fi

# Bash arrays are zero-indexed.
c8="${colors[7]}"
c9="${colors[8]}"
c10="${colors[9]}"
c11="${colors[10]}"
c16="${colors[15]}"

mkdir -p "$(dirname "$OUTPUT")"

cat > "$OUTPUT" <<EOF
* {
    background:     ${c8};
    background-alt: ${c9};
    surface:        ${c10};
    selected:       ${c11};
    foreground:     ${c16};
    border-color:   ${c16};
    icon-theme:     "Papirus";
}

window {
    background-color: @background;
    border: 2px;
    border-color: @border-color;
    border-radius: 12px;
    padding: 16px;
}

mainbox {
    background-color: @background;
    spacing: 12px;
    children: [ inputbar, listview ];
}

inputbar {
    background-color: @background-alt;
    text-color: @foreground;
    border: 1px;
    border-color: @border-color;
    border-radius: 8px;
    padding: 10px;
    spacing: 8px;
    children: [ prompt, entry ];
}

prompt {
    background-color: transparent;
    text-color: @foreground;
}

entry {
    background-color: transparent;
    text-color: @foreground;
    placeholder-color: @foreground;
}


listview {
    background-color: @surface;
    border-radius: 8px;
    padding: 8px;
    spacing: 4px;
    columns: 1;
    lines: 8;
    fixed-height: false;
    scrollbar: false;
}



element {
    background-color: @surface;
    text-color: @foreground;
    border-radius: 6px;
    padding: 8px;
    spacing: 10px;
    orientation: horizontal;
}

element normal.normal {
    background-color: @surface;
    text-color: @foreground;
}

element selected.normal {
    background-color: @selected;
    text-color: @foreground;
    border: 1px;
    border-color: @border-color;
}

element-icon {
    size: 28px;
    cursor: pointer;
    background-color: transparent;
}

element-text {
    background-color: transparent;
    text-color: inherit;
    vertical-align: 0.5;
}


element-icon {
    background-color: transparent;
    size: 1.2em;
}
EOF

echo "Generated: $OUTPUT"