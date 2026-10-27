
from pathlib import Path
import random
import shutil
import subprocess
import sys

wallpaper_dir = Path("~/Wallpaper").expanduser()
themes_dir = Path("~/.config/themes").expanduser()
image_extensions = {".png", ".jpg", ".jpeg", ".webp", ".bmp"}

# Find wallpapers recursively.
images = [
    path
    for path in wallpaper_dir.rglob("*")
    if path.is_file() and path.suffix.lower() in image_extensions
]

if not images:
    sys.exit(f"No wallpaper images found in {wallpaper_dir}")

chosen = random.choice(images)
themes_dir.mkdir(parents=True, exist_ok=True)

# Copy the selected wallpaper.
shutil.copy2(chosen, themes_dir / "bg.png")

# Generate theme colors from the wallpaper.
# 1. Generate 11 colors and update themes.txt
# Generate and save the 11 colors.
subprocess.run(
    [
        "python3", "wallpaper_colors.py",
        "bg.png",
        "-o", "themes.txt",
    ],
    cwd=themes_dir,
    check=True,
)

# Apply the wallpaper with a random transition.
subprocess.run(
    [
        "awww", "img", str(themes_dir / "bg.png"),
        "--transition-type", "random",
        "--transition-duration", "2",
    ],
    check=True,
)

print(f"Wallpaper selected: {chosen}")
