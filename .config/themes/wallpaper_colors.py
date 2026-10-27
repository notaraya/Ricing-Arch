
#!/usr/bin/env python3

import argparse
import colorsys
import os
import subprocess
import sys
import tempfile
from collections import Counter
from pathlib import Path



try:
    from PIL import Image
except ImportError:
    sys.exit("Install Pillow first: pip install pillow")

THEMES_FILE = Path("~/.config/themes/themes.txt").expanduser()
DARK_LUMINANCE = 0.18
LIGHT_LUMINANCE = 0.62
DARK_THRESHOLD = 0.40

# Required output order.
FAMILIES = [
    ("red", 0),
    ("yellow", 60),
    ("green", 120),
    ("orange", 30),
    ("blue", 240),
    ("purple", 285),
    ("aqua", 180),
]


def luminance(rgb):
    def linear(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    r, g, b = (linear(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def hsv(rgb):
    h, s, v = colorsys.rgb_to_hsv(*(c / 255 for c in rgb))
    return h * 360, s, v


def hue_distance(a, b):
    d = abs(a - b) % 360
    return min(d, 360 - d)


def hex_color(rgb):
    return "#{:02X}{:02X}{:02X}".format(*rgb)


def extract_colors(image_path):
    with Image.open(image_path) as image:
        image = image.convert("RGB")
        image.thumbnail((512, 512))
        pixels = list(image.getdata())

    if not pixels:
        raise ValueError("The wallpaper contains no pixels.")

    dark_fraction = sum(
        luminance(pixel) < DARK_LUMINANCE for pixel in pixels
    ) / len(pixels)

    # Group similar pixels into color bins and calculate their average RGB.
    bins = Counter(
        (r >> 3, g >> 3, b >> 3) for r, g, b in pixels
    )
    sums = {}

    for rgb in pixels:
        key = tuple(c >> 3 for c in rgb)
        if key not in sums:
            sums[key] = [0, 0, 0, 0]
        sums[key][0] += 1
        for i, channel in enumerate(rgb, start=1):
            sums[key][i] += channel

    candidates = []
    for key, (count, r, g, b) in sums.items():
        rgb = (round(r / count), round(g / count), round(b / count))
        h, s, v = hsv(rgb)
        candidates.append({
            "rgb": rgb,
            "hex": hex_color(rgb),
            "h": h,
            "s": s,
            "v": v,
            "lum": luminance(rgb),
            "count": count,
        })

    return candidates, dark_fraction


def pick_separated(pool, count, used, score, min_distance=18):
    """Pick distinct image colors, spreading selections apart in RGB."""
    selected = []

    for candidate in sorted(pool, key=score):
        rgb = candidate["rgb"]

        if candidate["hex"] in used:
            continue

        if any(
            sum((a - b) ** 2 for a, b in zip(rgb, other)) ** 0.5
            < min_distance
            for other in selected
        ):
            continue

        selected.append(rgb)
        used.add(candidate["hex"])

        if len(selected) == count:
            break

    return selected
    def reload_waybar():
        subprocess.Popen(
            ["pkill", "-x", "waybar"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        subprocess.Popen(
            ["waybar"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )


def make_dark_shades(candidates, used, count=4):
    """Get four dark shades, synthesizing hue-matched shades if needed."""
    # Prefer the wallpaper's darker colors; favor colors with some saturation.
    dark_candidates = sorted(
        (
            c for c in candidates
            if c["lum"] < DARK_LUMINANCE and c["hex"] not in used
        ),
        key=lambda c: (c["lum"], -c["s"], -c["count"]),
    )

    shades = []
    for c in dark_candidates:
        if c["hex"] not in used:
            shades.append(c["rgb"])
            used.add(c["hex"])
        if len(shades) == count:
            break

    # Use the most saturated wallpaper color as the hue source for any
    # additional shades. Lowering HSV value keeps the hue while making it dark.
    if len(shades) < count:
        source = max(
            candidates,
            key=lambda c: (c["s"], c["count"]),
        )
        h, s, _ = hsv(source["rgb"])
        s = max(s, 0.35)

        for value in (0.30, 0.22, 0.15, 0.10, 0.07, 0.05):
            rgb = tuple(
                round(channel * 255)
                for channel in colorsys.hsv_to_rgb(h / 360, s, value)
            )
            color = hex_color(rgb)

            # Ensure the generated shade is dark and not an exact duplicate.
            if luminance(rgb) < DARK_LUMINANCE and color not in used:
                shades.append(rgb)
                used.add(color)

            if len(shades) == count:
                break

    if len(shades) < count:
        raise ValueError("Could not generate four unique dark shades.")

    # Output lightest to darkest.
    shades.sort(key=luminance, reverse=True)
    return shades


def generate_palette(image_path):
    candidates, dark_fraction = extract_colors(image_path)
    used = set()
    palette = []

    # Colors 1–7: real colors from the wallpaper, nearest target hue first.
    for name, target_hue in FAMILIES:
                # Prefer clear, vivid colors; relax the thresholds if needed.
        pool = [
            c for c in candidates
            if c["hex"] not in used
            and c["s"] >= 0.45
            and c["v"] >= 0.55
        ]

        if not pool:
            pool = [
                c for c in candidates
                if c["hex"] not in used
                and c["s"] >= 0.25
                and c["v"] >= 0.35
            ]

        if not pool:
            pool = [c for c in candidates if c["hex"] not in used]

        if not pool:
            raise ValueError("Not enough unique colors in the wallpaper.")

        best = min(
            pool,
            key=lambda c: (
                hue_distance(c["h"], target_hue),
                -c["s"],
                -c["v"],
                -c["count"],
            ),
        )


        palette.append(best["rgb"])
        used.add(best["hex"])
        # Reorder the first 7 colors: most saturated and bright first.
    palette.sort(
        key=lambda rgb: (
            hsv(rgb)[1] * hsv(rgb)[2],
            hsv(rgb)[1],
            hsv(rgb)[2],
        ),
        reverse=True,
    )

    # Colors 8–11: always dark. Synthesize hue-matched shades when needed.
    palette.extend(make_dark_shades(candidates, used))


    # Colors 8–11: always dark. Synthesize hue-matched shades when needed.
    palette.extend(make_dark_shades(candidates, used))

        # Color 12: use a bright, saturated image color as the hue source,
    # then make the result brighter and less saturated.
    bright_candidates = [
        c for c in candidates if c["v"] >= 0.50
    ]
    source = max(
        bright_candidates or candidates,
        key=lambda c: (c["s"] * c["v"], c["v"], c["count"]),
    )

    h, s, v = hsv(source["rgb"])
    rgb12 = tuple(
        round(channel * 255)
        for channel in colorsys.hsv_to_rgb(
            h / 360,
            s * 0.35,       # less saturated
            max(v, 0.90),   # bright
        )
    )
    palette.append(rgb12)


    return [hex_color(rgb) for rgb in palette], dark_fraction


def write_palette(colors, output):
    output = output.expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)

    fd, temp_name = tempfile.mkstemp(
        dir=output.parent, prefix=".themes-", suffix=".tmp"
    )

    try:
        with os.fdopen(fd, "w") as file:
            file.write("\n".join(colors) + "\n")
        os.replace(temp_name, output)
    except BaseException:
        if os.path.exists(temp_name):
            os.unlink(temp_name)
        raise


def main():
    parser = argparse.ArgumentParser(
        description="Generate an 11-color wallpaper palette."
    )
    parser.add_argument("image", help="Path to the wallpaper image")
    parser.add_argument(
        "-o", "--output",
        type=Path,
        default=THEMES_FILE,
        help="Output file (default: ~/.config/themes/themes.txt)",
    )
    parser.add_argument(
        "--no-reload",
        action="store_true",
        help="Do not reload Hyprland after writing the palette",
    )
    args = parser.parse_args()

    try:
        colors, dark_fraction = generate_palette(args.image)
        write_palette(colors, args.output)

        if args.output.expanduser().resolve() == THEMES_FILE.resolve():
            update_kitty_theme()
    except (OSError, ValueError) as error:
        sys.exit(f"Error: {error}")

    shade_mode = "dark" if dark_fraction >= DARK_THRESHOLD else "light"
    print(f"Wrote {len(colors)} colors to {args.output}")
    print(f"Dark pixels: {dark_fraction:.1%}; shade mode: {shade_mode}")

    for i, color in enumerate(colors, start=1):
        print(f"{i:2}. {color}")

    if not args.no_reload:
        result = subprocess.run(
            ["hyprctl", "reload"],
            capture_output=True,
            text=True,
        )
        if result.returncode:
            print(
                "Warning: palette saved, but Hyprland reload failed:",
                result.stderr.strip() or result.stdout.strip(),
            )



def update_kitty_theme():
    """Regenerate shared application themes from the current 16-color palette."""
    generator = Path("~/.config/themes/apply-theme.py").expanduser()
    try:
        result = subprocess.run(
            ["python3", str(generator)],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(
                "Warning: Shared theme generation failed:",
                result.stderr.strip() or result.stdout.strip(),
            )
            return

        print(result.stdout.strip())

        # Apply the generated colors to the running Kitty instance if reachable.
        kitty_dir = Path("~/.config/kitty").expanduser()
        result = subprocess.run(
            [
                "kitty", "@", "--to", "unix:/tmp/kitty-themes",
                "set-colors", "--all", str(kitty_dir / "theme.conf"),
            ],
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(
                "Note: Theme files were generated, but live Kitty refresh "
                "was unavailable:",
                result.stderr.strip() or result.stdout.strip(),
            )
    except OSError as error:
        print(f"Warning: Shared theme update failed: {error}")

def update_gtk_theme(colors):
    """Generate GTK 3 and GTK 4 CSS from the 16-color palette."""
    gtk3 = Path("~/.config/gtk-3.0/gtk.css").expanduser()
    gtk4 = Path("~/.config/gtk-4.0/gtk.css").expanduser()

    css = f"""
@define-color accent_color {colors[0]};
@define-color accent_bg_color {colors[2]};
@define-color accent_fg_color {colors[15]};

@define-color window_bg_color {colors[7]};
@define-color window_fg_color {colors[15]};
@define-color view_bg_color {colors[8]};
@define-color view_fg_color {colors[15]};

@define-color headerbar_bg_color {colors[9]};
@define-color headerbar_fg_color {colors[15]};

@define-color card_bg_color {colors[10]};
@define-color dialog_bg_color {colors[7]};
@define-color popover_bg_color {colors[9]};

@define-color theme_bg_color {colors[7]};
@define-color theme_fg_color {colors[15]};
@define-color theme_selected_bg_color {colors[2]};
@define-color theme_selected_fg_color {colors[15]};
"""

    for path in (gtk3, gtk4):
        path.parent.mkdir(parents=True, exist_ok=True)
        fd, temp_name = tempfile.mkstemp(
            dir=path.parent, prefix=".gtk-theme-", suffix=".tmp"
        )
        try:
            with os.fdopen(fd, "w") as file:
                file.write(css)
            os.replace(temp_name, path)
        except BaseException:
            if os.path.exists(temp_name):
                os.unlink(temp_name)
            raise

    print("GTK 3 and GTK 4 theme files updated.")

reload_script = Path.home() / ".config/waybar/reload.sh"

if __name__ == "__main__":
    main()
    update_kitty_theme()
    subprocess.run([str(reload_script)], check=True)
