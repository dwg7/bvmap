"""Light-on-dark sprite for bvmap-nightsky (docs/decisions/0043), the inverse
counterpart of sprite_grayscale.py (0036). Reads the unmodified GSI sprite
(sprite/std.png), writes sprite/bvmap-nightsky.png (+ json, + the @2x duplicates
MapLibre asks for on high-DPR displays — same reason as 0036).

Per pixel, alpha untouched: desaturate to luminosity (same BT.601 weights as
sprite_grayscale.py), then run the gray through night_transform.reverse_lightness
— the same function the nightsky palette is derived from, so an icon pixel that
was as dark as a given text color becomes as light as that text color's night
value. Dark glyphs -> light, white icon halos/fills -> the dark ground.

    python3 generator/sprite_nightsky.py     (from the repo root)
"""
import json

import numpy as np
from PIL import Image

from night_transform import DARK, LIGHT

SRC_PNG, SRC_JSON = "sprite/std.png", "sprite/std.json"
OUTS = [("sprite/bvmap-nightsky.png", "sprite/bvmap-nightsky.json"),
        ("sprite/bvmap-nightsky@2x.png", "sprite/bvmap-nightsky@2x.json")]


def nightsky_sprite(rgba: np.ndarray) -> np.ndarray:
    r, g, b, a = (rgba[..., i].astype(np.float64) for i in range(4))
    y = 0.299 * r + 0.587 * g + 0.114 * b
    t = y / 255.0
    chans = [np.clip(np.round(d + (1 - t) * (l - d)), 0, 255) for d, l in zip(DARK, LIGHT)]
    return np.stack(chans + [a], axis=-1).astype(np.uint8)


if __name__ == "__main__":
    arr = np.array(Image.open(SRC_PNG).convert("RGBA"))
    out = nightsky_sprite(arr)
    with open(SRC_JSON) as f:
        sprite_json = json.load(f)
    for png, js in OUTS:
        Image.fromarray(out).save(png)
        with open(js, "w") as f:
            json.dump(sprite_json, f, ensure_ascii=False, indent=1)
            f.write("\n")
    print(f"Wrote {OUTS[0][0]} (+json, +@2x) — {len(sprite_json)} icons, geometry unchanged.")
