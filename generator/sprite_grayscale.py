"""Grayscale the GSI sprite sheet (docs/decisions/0036) to match
bvmap-starlight's neutral, silver-gray palette (docs/decisions/0030) — the
119 GSI icons are the only genuinely multi-hue content in this style;
everything else is already R=G=B (docs/bvmap-starlight-cartographic-design.md
§4.1).

Reads sprite/std.png (an unmodified snapshot of GSI's sprite, fetched from
https://gsi-cyberjapan.github.io/optimal_bvmap/sprite/std.png — same role as
style/bvmap-dark.json), writes sprite/bvmap-starlight.png. The sprite JSON
(icon rects) is copied verbatim as sprite/bvmap-starlight.json: recoloring
pixels doesn't move or resize any icon, so the geometry is unchanged.

Two steps per pixel, alpha untouched:
1. Desaturate to luminosity (ITU-R BT.601 weights, matching PIL's .convert("L"))
2. Run the resulting gray value through cool_transform() — the same brighten
   + silver tint applied to every other token in starlight-input.yaml, so the
   icons pick up the identical "quality" as the rest of the style instead of
   a hand-picked gray.
"""
import json

import numpy as np
from PIL import Image

from cool_transform import cool_transform

SRC_PNG = "sprite/std.png"
SRC_JSON = "sprite/std.json"
OUT_PNG = "sprite/bvmap-starlight.png"
OUT_JSON = "sprite/bvmap-starlight.json"

# GSI's own std@2x.png/.json are byte-identical to std.png/.json (docs/decisions/0036
# — not a real high-DPI asset, just a duplicate under the @2x name). MapLibre still
# requests {sprite}@2x.* on a high-DPR display and fails the whole sprite load on a
# 404, so we mirror that duplicate rather than omitting it.
OUT_PNG_2X = "sprite/bvmap-starlight@2x.png"
OUT_JSON_2X = "sprite/bvmap-starlight@2x.json"


def grayscale_starlight(rgba: np.ndarray) -> np.ndarray:
    r, g, b, a = (rgba[..., i].astype(np.float64) for i in range(4))
    y = 0.299 * r + 0.587 * g + 0.114 * b

    v = y  # (y+y+y)/3 == y
    brighten = np.where(v < 100, 0.03, 0.09)
    y2 = y + (255 - y) * brighten

    r2 = np.clip(np.round(y2 - 2.2 * 0.6), 0, 255)
    g2 = np.clip(np.round(y2), 0, 255)
    b2 = np.clip(np.round(y2 + 2.2), 0, 255)

    out = np.stack([r2, g2, b2, a], axis=-1).astype(np.uint8)
    return out


if __name__ == "__main__":
    img = Image.open(SRC_PNG).convert("RGBA")
    arr = np.array(img)

    out_arr = grayscale_starlight(arr)

    # Sanity-check the vectorized path against cool_transform() itself on a
    # handful of sampled pixels, so a future edit to either can't silently
    # drift the two implementations apart. cool_transform() itself doesn't
    # clip (fine for hand-picked palette tokens, which never sit near 0/255)
    # — clip its output here too, matching the clip the vectorized path
    # applies for real image data (icon pixels do reach white/255).
    rng = np.random.default_rng(0)
    ys, xs = np.where(arr[:, :, 3] > 0)
    for i in rng.choice(len(ys), size=min(200, len(ys)), replace=False):
        y, x = ys[i], xs[i]
        r, g, b, a = arr[y, x]
        expected = tuple(
            min(255, max(0, c))
            for c in cool_transform(*(0.299 * r + 0.587 * g + 0.114 * b,) * 3)
        )
        got = tuple(int(c) for c in out_arr[y, x][:3])
        assert got == expected, (y, x, got, expected)

    Image.fromarray(out_arr).save(OUT_PNG)
    Image.fromarray(out_arr).save(OUT_PNG_2X)

    with open(SRC_JSON) as f:
        sprite_json = json.load(f)
    for out_path in (OUT_JSON, OUT_JSON_2X):
        with open(out_path, "w") as f:
            json.dump(sprite_json, f, ensure_ascii=False, indent=1)
            f.write("\n")

    print(f"Wrote {OUT_PNG}/{OUT_JSON} (+@2x duplicates) — {len(sprite_json)} icons, "
          f"geometry unchanged from sprite/std.json, pixels desaturated + "
          f"cool_transform-toned (200 random pixels verified against "
          f"cool_transform() directly).")
