"""Lightness-reversal color transform used by the second palette `nightsky`
(docs/decisions/0043). Same role as cool_transform.py for Starlight (0030):
a pure function that the palette is *derived* from, kept as code so the
derivation is reproducible instead of living only in prose.

    t   = (r+g+b)/765            # lightness of the (near-neutral) source gray, 0 black .. 1 white
    out = DARK + (1-t)*(LIGHT-DARK)   # white -> DARK (green-tinted ground), black -> LIGHT

alpha is kept as-is. DARK/LIGHT come from the dorayaki proposal
(documents/dark-basemap.md there): DARK #2f3a30 is chosen to sit next to the
mean splat color rgb(68,71,67); LIGHT #eaedea is the text/line end.

Two roles use this module:
  - experiments/nightsky/mechanical.py: the *whole-style* mechanical
    version (every rgb()/rgba() string in the published starlight style),
    kept as the baseline the real second palette is compared against.
  - generator/assemble.py (variant nightsky): the fallback for any color
    string that is still a literal inside a layer (not a palette token).
"""
import re

DARK = (0x2F, 0x3A, 0x30)
LIGHT = (0xEA, 0xED, 0xEA)

_COLOR_RE = re.compile(r"^rgba?\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*(?:,\s*([\d.]+)\s*)?\)$")


def reverse_lightness(r, g, b, dark=DARK, light=LIGHT):
    t = (r + g + b) / 765.0
    return tuple(round(d + (1 - t) * (l - d)) for d, l in zip(dark, light))


def transform_color_string(s, dark=DARK, light=LIGHT):
    """'rgba(r,g,b,a)' / 'rgb(r,g,b)' -> same form, reversed lightness, alpha kept.
    Returns None when s is not such a string."""
    m = _COLOR_RE.match(s)
    if not m:
        return None
    if m.group(4) is not None and float(m.group(4)) == 0:
        return s  # fully transparent: the RGB is never seen; keep "rgba(0,0,0,0)" as is
    r, g, b = (float(m.group(i)) for i in (1, 2, 3))
    nr, ng, nb = reverse_lightness(r, g, b, dark, light)
    if m.group(4) is None:
        return f"rgb({nr},{ng},{nb})"
    return f"rgba({nr},{ng},{nb},{m.group(4)})"


def transform_tree(node, stats=None, dark=DARK, light=LIGHT):
    """Recursively maps every color string inside a JSON tree."""
    if isinstance(node, str):
        out = transform_color_string(node, dark, light)
        if out is None:
            return node
        if stats is not None:
            stats[node] = out
        return out
    if isinstance(node, list):
        return [transform_tree(x, stats, dark, light) for x in node]
    if isinstance(node, dict):
        return {k: transform_tree(v, stats, dark, light) for k, v in node.items()}
    return node


if __name__ == "__main__":
    # Prints where variants.nightsky.palette deviates from the pure formula
    # applied to the base palette = the hand-tuned tokens (docs/decisions/0043).
    import yaml
    with open("generator/starlight-input.yaml") as f:
        cfg = yaml.safe_load(f)
    night = cfg["variants"]["nightsky"]["palette"]
    for tok, base in cfg["palette"].items():
        formula = transform_color_string(base)
        mark = "hand-tuned" if night[tok] != formula else "formula"
        print(f"{tok:15s} {base:22s} -> {night[tok]:22s} [{mark}" + (f", formula says {formula}]" if mark != "formula" else "]"))
