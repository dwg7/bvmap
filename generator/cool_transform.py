"""Starlight's color transform (docs/decisions/0030): brighten + a faint
cool/silver tint. Originally run by hand once to derive starlight-input.yaml's
palette tokens from bvmap-dark's raw values (the formula lived only in 0030's
prose and docs/bvmap-starlight-cartographic-design.md's synced copy). Promoted
to real code here so sprite_grayscale.py (docs/decisions/0036) can apply the
exact same transform per-pixel instead of hand-copying the formula again.
"""


def cool_transform(r, g, b, cool=2.2):
    v = (r + g + b) / 3
    brighten = 0.03 if v < 100 else 0.09  # dark values (Anno's importance ramp) stay subtle
    r2 = r + (255 - r) * brighten
    g2 = g + (255 - g) * brighten
    b2 = b + (255 - b) * brighten
    b2 += cool          # shift toward blue (silver-gray)
    r2 -= cool * 0.6    # pull back red
    return (round(r2), round(g2), round(b2))
