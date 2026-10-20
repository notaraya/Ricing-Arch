#!/usr/bin/env python3
"""Extract a bright/saturated palette from a wallpaper and apply it as a theme.

Usage: wallpaper-theme.py <image>

Writes:
  ~/.config/kitty/wallpaper-theme.conf        (kitty picks it up via SIGUSR1)
  ~/.config/hypr/hyprland.lua                 (between WALL_THEME_START/END markers)

Prints shell assignments (HYPR_ACTIVE_BORDER / HYPR_INACTIVE_BORDER) so the
caller can apply them instantly with `hyprctl keyword`.
"""

import colorsys
import json
import os
import sys

KITTY_OUT = os.path.expanduser("~/.config/kitty/wallpaper-theme.conf")
LUA_CONF = os.path.expanduser("~/.config/hypr/hyprland.lua")
VICINAE_OUT = os.path.expanduser("~/.local/share/vicinae/themes/wallpaper.toml")
DMS_DIR = os.path.expanduser("~/.config/DankMaterialShell/themes/wallpaper")
DMS_OUT = os.path.join(DMS_DIR, "theme.json")

START_MARK = "-- WALL_THEME_START"
END_MARK = "-- WALL_THEME_END"


# ---------------------------------------------------------------- helpers

def clamp(x):
    return max(0.0, min(1.0, x))


def to_hsv(rgb):
    return colorsys.rgb_to_hsv(*rgb)


def hsv2(h, s, v):
    """h in degrees -> rgb 0..1"""
    return colorsys.hsv_to_rgb((h % 360) / 360.0, clamp(s), clamp(v))


def hexs(rgb):
    return "#%02x%02x%02x" % tuple(int(round(clamp(c) * 255)) for c in rgb)


def rgba(rgb, alpha="ee"):
    return "rgba(%02x%02x%02x%s)" % (
        int(round(clamp(rgb[0]) * 255)),
        int(round(clamp(rgb[1]) * 255)),
        int(round(clamp(rgb[2]) * 255)),
        alpha,
    )


def hue_dist(a, b):
    return abs(((a - b + 180) % 360) - 180)


# ---------------------------------------------------------------- sampling

def sample_pixels(path, size=200):
    import gi
    gi.require_version("GdkPixbuf", "2.0")
    from gi.repository import GdkPixbuf

    pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, size, size, True)
    w, h = pb.get_width(), pb.get_height()
    n, rs = pb.get_n_channels(), pb.get_rowstride()
    data = pb.get_pixels()

    pix = []
    for y in range(h):
        row = data[y * rs:y * rs + w * n]
        for x in range(w):
            i = x * n
            if n == 4 and row[i + 3] < 128:
                continue  # skip transparent pixels
            pix.append((row[i] / 255.0, row[i + 1] / 255.0, row[i + 2] / 255.0))
    return pix


def score(hsv_t):
    """Most saturated AND brightest wins."""
    _, s, v = hsv_t
    if v < 0.25:  # near-black pixels can never look good as accents
        return -1.0
    return s * v


# ANSI hue families: (center hue, fallback sat, fallback val)
FAMILIES = [
    (0, 0.60, 0.85),    # red
    (50, 0.60, 0.88),   # yellow
    (105, 0.50, 0.80),  # green
    (175, 0.50, 0.82),  # cyan
    (215, 0.55, 0.85),  # blue
    (290, 0.50, 0.85),  # magenta
]
FAMILY_TOL = 38


def family_color(center, fallback_s, fallback_v, cands, taken=()):
    """Best wallpaper color inside a hue family, brightened for terminal use."""
    best, best_score = None, 0.0
    for rgb, t in cands:
        if hue_dist(t[0], center) <= FAMILY_TOL and t[2] >= 0.30:
            # don't reuse a hue we already assigned to another family
            if any(hue_dist(t[0], h) < 25 for h in taken):
                continue
            if score(t) > best_score:
                best, best_score = rgb, score(t)
    if best is None or best_score < 0.12:
        return hsv2(center, fallback_s, fallback_v)
    h, s, v = to_hsv(best)
    return hsv2(h * 360.0, max(s, 0.45), max(v, 0.78))


def lighten(rgb, dv=0.14, sm=0.92):
    h, s, v = to_hsv(rgb)
    return hsv2(h * 360.0, s * sm, v + dv)


def darken(rgb, dv=0.30, sm=0.85):
    h, s, v = to_hsv(rgb)
    return hsv2(h * 360.0, s * sm, v - dv)


def build(path):
    pix = sample_pixels(path)
    if not pix:
        raise SystemExit("no opaque pixels in %s" % path)

    cands = []
    for rgb in pix:
        t = to_hsv(rgb)
        cands.append((rgb, (t[0] * 360.0, t[1], t[2])))

    # --- accents: most saturated + brightest, second one a different hue
    acc_rgb, acc_t = max(cands, key=lambda c: score(c[1]))
    acc_h, acc_s, acc_v = acc_t

    other = [c for c in cands if hue_dist(c[1][0], acc_h) >= 60]
    if other:
        acc2_rgb, acc2_t = max(other, key=lambda c: score(c[1]))
        if score(acc2_t) < 0.10:  # washed-out second hue: derive one instead
            acc2_rgb = hsv2(acc_h + 150, 0.55, 0.85)
    else:
        # monochrome wallpaper: derive a complementary second colour
        acc2_rgb = hsv2(acc_h + 150, 0.55, 0.85)
    acc2_h = to_hsv(acc2_rgb)[0] * 360.0

    # --- background: average of the dark pixels, kept dark & desaturated
    dark = [rgb for rgb, t in cands if t[2] <= 0.35] or [rgb for rgb, _ in cands]
    br = sum(c[0] for c in dark) / len(dark)
    bg_ = sum(c[1] for c in dark) / len(dark)
    bb = sum(c[2] for c in dark) / len(dark)
    bh, bs, bv = to_hsv((br, bg_, bb))
    bg = hsv2(bh * 360.0, min(bs, 0.30), clamp(max(bv, 0.08) - 0.02 if bv > 0.10 else 0.10))

    # --- foreground: brighten the wallpaper's light tones
    light = [rgb for rgb, t in cands if t[2] >= 0.72] or [acc2_rgb]
    lr = sum(c[0] for c in light) / len(light)
    lg = sum(c[1] for c in light) / len(light)
    lb = sum(c[2] for c in light) / len(light)
    lh, ls, lv = to_hsv((lr, lg, lb))
    fg = hsv2(lh * 360.0, min(ls, 0.22), max(lv, 0.93))

    # --- 16-colour ANSI palette from the wallpaper's hue families
    bases = []
    taken = []
    for c, s, v in FAMILIES:
        col = family_color(c, s, v, cands, taken)
        taken.append(to_hsv(col)[0] * 360.0)
        bases.append(col)
    brights = [lighten(b, dv=0.12, sm=0.95) for b in bases]
    c0 = hsv2(bh * 360.0, min(bs, 0.30), 0.12)
    c7 = hsv2(to_hsv(fg)[0] * 360.0, 0.14, 0.82)
    c8 = hsv2(acc_h, 0.12, 0.55)

    # --- derived theme colors
    active_a = hsv2(acc_h, max(acc_s, 0.45), max(acc_v, 0.70))
    active_b = hsv2(acc2_h, max(to_hsv(acc2_rgb)[1], 0.45), max(to_hsv(acc2_rgb)[2], 0.70))
    inactive = hsv2(bh * 360.0, min(bs + 0.05, 0.35), 0.45)
    tab_active_bg = darken(active_a, dv=0.15, sm=0.95)

    return {
        "acc": active_a, "acc2": active_b, "bg": bg, "fg": fg,
        "inactive": inactive, "tab_bg": tab_active_bg,
        "bases": bases, "brights": brights,
        "c0": c0, "c7": c7, "c8": c8,
    }


# ---------------------------------------------------------------- writers

def write_kitty(p):
    lines = [
        "# Auto-generated wallpaper theme — managed by ~/.config/hypr/random-wallpaper.sh",
        "# Do not edit by hand, it is rewritten every time the wallpaper changes.",
        "",
        "foreground %s" % hexs(p["fg"]),
        "background %s" % hexs(p["bg"]),
        "cursor %s" % hexs(p["acc"]),
        "cursor_text_color %s" % hexs(p["bg"]),
        "selection_foreground %s" % hexs(p["bg"]),
        "selection_background %s" % hexs(p["acc"]),
        "url_color %s" % hexs(p["acc2"]),
        "active_border_color %s" % hexs(p["acc"]),
        "active_tab_foreground %s" % hexs(p["bg"]),
        "active_tab_background %s" % hexs(p["tab_bg"]),
        "inactive_tab_foreground %s" % hexs(p["c7"]),
        "inactive_tab_background %s" % hexs(darken(p["bg"], dv=0.03, sm=1.0)),
        "",
        "color0 %s" % hexs(p["c0"]),
        "color8 %s" % hexs(p["c8"]),
    ]
    for i in range(6):
        lines.append("color%d %s" % (i + 1, hexs(p["bases"][i])))
        lines.append("color%d %s" % (i + 9, hexs(p["brights"][i])))
    lines += ["color7 %s" % hexs(p["c7"]), "color15 %s" % hexs(p["fg"]), ""]

    tmp = KITTY_OUT + ".tmp"
    with open(tmp, "w") as f:
        f.write("\n".join(lines))
    os.replace(tmp, KITTY_OUT)


def write_lua(p):
    try:
        with open(LUA_CONF) as f:
            src = f.read()
    except OSError as e:
        print("theme: cannot read hyprland.lua: %s" % e, file=sys.stderr)
        return
    if START_MARK not in src or END_MARK not in src:
        print("theme: WALL_THEME markers missing in hyprland.lua", file=sys.stderr)
        return

    head, rest = src.split(START_MARK, 1)
    _, tail = rest.split(END_MARK, 1)
    block = (
        "\n"
        "            active_border   = { colors = {\"%s\", \"%s\"}, angle = 45 },\n"
        "            inactive_border = \"%s\",\n"
        "            "
        % (rgba(p["acc"], "ee"), rgba(p["acc2"], "ee"), rgba(p["inactive"], "aa"))
    )
    tmp = LUA_CONF + ".tmp"
    with open(tmp, "w") as f:
        f.write(head + START_MARK + block + END_MARK + tail)
    os.replace(tmp, LUA_CONF)


def variant_of(rgb):
    """dark or light based on background brightness"""
    _, _, v = to_hsv(rgb)
    return "dark" if v < 0.50 else "light"


def write_vicinae(p):
    """Write a wallpaper-derived vicinae theme to ~/.local/share/vicinae/themes/wallpaper.toml"""
    variant = variant_of(p["bg"])
    bg = hexs(p["bg"])
    fg = hexs(p["fg"])
    acc = hexs(p["acc"])
    acc2 = hexs(p["acc2"])
    inactive = hexs(p["inactive"])
    sec_bg = hexs(darken(p["bg"], dv=0.06, sm=1.0))
    muted = hexs(p["c8"])
    bases = [hexs(b) for b in p["bases"]]
    red, yellow, green, cyan, blue, magenta = bases
    orange = hexs(darken(p["bases"][1], dv=0.10, sm=1.0))
    purple = hexs(darken(p["bases"][5], dv=0.10, sm=1.0))

    lines = [
        "[meta]",
        "name = \"Wallpaper\"",
        "description = \"Theme derived from the current wallpaper\"",
        "variant = \"%s\"" % variant,
        "",
        "[colors.core]",
        "background = \"%s\"" % bg,
        "foreground = \"%s\"" % fg,
        "secondary_background = \"%s\"" % sec_bg,
        "border = \"%s\"" % inactive,
        "accent = \"%s\"" % acc,
        "accent_foreground = \"%s\"" % bg,
        "",
        "[colors.main_window]",
        "border = \"%s\"" % inactive,
        "",
        "[colors.settings_window]",
        "border = \"%s\"" % inactive,
        "",
        "[colors.accents]",
        "blue = \"%s\"" % blue,
        "green = \"%s\"" % green,
        "magenta = \"%s\"" % magenta,
        "orange = \"%s\"" % orange,
        "red = \"%s\"" % red,
        "yellow = \"%s\"" % yellow,
        "cyan = \"%s\"" % cyan,
        "purple = \"%s\"" % purple,
        "",
        "[colors.shortcut]",
        "border = \"colors.core.border\"",
        "",
        "[colors.text]",
        "default = \"colors.core.foreground\"",
        "muted = \"%s\"" % muted,
        "danger = \"%s\"" % red,
        "success = \"%s\"" % green,
        "placeholder = \"%s\"" % muted,
        "selection = { background = \"%s\", foreground = \"%s\" }" % (acc, bg),
        "",
        "[colors.text.links]",
        "default = \"%s\"" % acc2,
        "visited = \"%s\"" % purple,
        "",
        "[colors.input]",
        "border = \"%s\"" % inactive,
        "border_focus = \"%s\"" % acc,
        "border_error = \"%s\"" % red,
        "",
        "[colors.button.primary]",
        "background = \"%s\"" % sec_bg,
        "foreground = \"%s\"" % fg,
        "hover = { background = \"%s\" }" % sec_bg,
        "focus = { outline = \"colors.core.accent\" }",
        "",
        "[colors.list.item.hover]",
        "foreground = \"%s\"" % fg,
        "secondary_foreground = \"%s\"" % fg,
        "",
        "[colors.list.item.selection]",
        "background = \"%s\"" % sec_bg,
        "foreground = \"%s\"" % fg,
        "secondary_background = \"%s\"" % sec_bg,
        "secondary_foreground = \"%s\"" % fg,
        "",
        "[colors.grid.item]",
        "background = \"%s\"" % sec_bg,
        "hover = { outline = \"%s\" }" % fg,
        "selection = { outline = \"%s\" }" % fg,
        "",
        "[colors.scrollbars]",
        "background = \"%s\"" % inactive,
        "",
        "[colors.loading]",
        "bar = \"%s\"" % acc,
        "spinner = \"%s\"" % fg,
        "",
    ]

    tmp = VICINAE_OUT + ".tmp"
    with open(tmp, "w") as f:
        f.write("\n".join(lines))
    os.replace(tmp, VICINAE_OUT)


def dms_lighten(rgb, dv=0.35, sm=1.05):
    """Brighten a color for the DMS light variant."""
    h, s, v = to_hsv(rgb)
    return hsv2(h * 360.0, min(s * sm, 1.0), clamp(min(v + dv, 1.0)))


def write_dms_theme(p):
    """Write a wallpaper-derived DMS custom theme to themes/wallpaper/theme.json.

    DMS loads this as a "custom" theme and auto-reloads when the file changes
    (Theme.qml: customThemeFileView watches changes when currentTheme === custom).
    """
    bg = hexs(p["bg"])
    fg = hexs(p["fg"])
    acc = hexs(p["acc"])
    acc2 = hexs(p["acc2"])
    inactive = hexs(p["inactive"])
    sec_bg = hexs(darken(p["bg"], dv=0.06, sm=1.0))
    sec_bg_hi = hexs(darken(p["bg"], dv=-0.10, sm=1.0))
    bases = [hexs(b) for b in p["bases"]]
    red, yellow, green, cyan, blue, magenta = bases

    def mode(dark=True):
        if dark:
            return {
                "primary": acc,
                "onPrimary": bg,
                "primaryContainer": hexs(lighten(p["acc"], dv=0.25, sm=1.0)),
                "onPrimaryContainer": bg,
                "secondary": acc2,
                "onSecondary": bg,
                "secondaryContainer": hexs(lighten(p["acc2"], dv=0.25, sm=1.0)),
                "onSecondaryContainer": bg,
                "tertiary": green,
                "onTertiary": bg,
                "surface": bg,
                "surfaceText": fg,
                "surfaceVariant": inactive,
                "onSurfaceVariant": fg,
                "surfaceTint": acc,
                "background": bg,
                "backgroundText": fg,
                "outline": inactive,
                "outlineVariant": inactive,
                "surfaceContainerLowest": hexs(darken(p["bg"], dv=0.12, sm=1.0)),
                "surfaceContainerLow": sec_bg,
                "surfaceContainer": sec_bg_hi,
                "surfaceContainerHigh": sec_bg_hi,
                "surfaceContainerHighest": hexs(darken(p["bg"], dv=-0.18, sm=1.0)),
                "error": red,
                "onError": bg,
                "errorContainer": hexs(darken(p["bases"][0], dv=0.25, sm=1.0)),
                "warning": yellow,
                "success": green,
                "info": blue,
            }
        # Light variant: same accent hues, brighter background/surfaces
        lbg_rgb = lighten(p["bg"], dv=0.62, sm=1.0)
        lfg_rgb = (0.14, 0.14, 0.14)
        lbg = hexs(lbg_rgb)
        lfg = hexs(lfg_rgb)
        return {
            "primary": hexs(lighten(p["acc"], dv=-0.10, sm=1.0)),
            "onPrimary": lbg,
            "primaryContainer": acc,
            "onPrimaryContainer": lbg,
            "secondary": hexs(lighten(p["acc2"], dv=-0.10, sm=1.0)),
            "onSecondary": lbg,
            "secondaryContainer": acc2,
            "onSecondaryContainer": lbg,
            "tertiary": green,
            "onTertiary": lbg,
            "surface": lbg,
            "surfaceText": lfg,
            "surfaceVariant": hexs(lighten(lbg_rgb, dv=-0.08, sm=1.0)),
            "onSurfaceVariant": lfg,
            "surfaceTint": hexs(lighten(p["acc"], dv=-0.10, sm=1.0)),
            "background": lbg,
            "backgroundText": lfg,
            "outline": hexs(lighten(p["inactive"], dv=-0.10, sm=1.0)),
            "outlineVariant": hexs(lighten(p["inactive"], dv=-0.10, sm=1.0)),
            "surfaceContainerLowest": lbg,
            "surfaceContainerLow": hexs(lighten(lbg_rgb, dv=-0.05, sm=1.0)),
            "surfaceContainer": sec_bg_hi,
            "surfaceContainerHigh": sec_bg_hi,
            "surfaceContainerHighest": hexs(lighten(lbg_rgb, dv=-0.22, sm=1.0)),
            "error": red,
            "onError": lbg,
            "errorContainer": hexs(darken(p["bases"][0], dv=0.25, sm=1.0)),
            "warning": yellow,
            "success": green,
            "info": blue,
        }

    theme = {
        "id": "wallpaper",
        "name": "Wallpaper",
        "description": "Theme derived from the current wallpaper",
        "dark": mode(dark=True),
        "light": mode(dark=False),
    }

    os.makedirs(DMS_DIR, exist_ok=True)
    tmp = DMS_OUT + ".tmp"
    with open(tmp, "w") as f:
        json.dump(theme, f, indent=2)
        f.write("\n")
    os.replace(tmp, DMS_OUT)


def main():
    if len(sys.argv) != 2:
        raise SystemExit("usage: wallpaper-theme.py <image>")
    try:
        p = build(sys.argv[1])
    except Exception as e:
        print("theme: failed to analyze %s: %s" % (sys.argv[1], e), file=sys.stderr)
        raise SystemExit(1)

    write_kitty(p)
    write_lua(p)
    write_vicinae(p)
    write_dms_theme(p)

    # shell vars for instant application
    print("HYPR_ACTIVE_BORDER='%s %s 45'" % (rgba(p["acc"], "ee"), rgba(p["acc2"], "ee")))
    print("HYPR_INACTIVE_BORDER='%s'" % rgba(p["inactive"], "aa"))
    print("VICINAE_THEME='wallpaper'")
    print("DMS_THEME='custom'")


if __name__ == "__main__":
    main()
