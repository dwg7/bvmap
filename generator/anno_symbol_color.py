"""
Stage 1 generator (reproduction-first): Anno symbol-attached text-color.

docs/decisions/0017/0027: bvmap-注記シンボル付きソート順100以上/100未満
share the exact same darkness ramp as the other 5 Anno layers
(category_table.py's ANNO_TEXT_COLOR_CATEGORIES/VALUES — verified
byte-identical in 0027), wrapped in a zoom-14 step that makes a small,
per-layer set of vt_codes transparent below/at zoom 14 instead of using
the ramp's color. The same "zoom-14 sparse exception" shape as 0008's
text-size finding, just for a different property.

This module only adds the wrapping; the ramp itself is reused verbatim
(passed in already-compiled) rather than rebuilt here.
"""
import json

TRANSPARENT = "rgba(0,0,0,0)"


def _hide_match(vt_codes, fallback):
    """["match", ["get","vt_code"], <codes>, transparent, fallback] — or
    just `fallback` if there's nothing to hide in this zoom band."""
    if not vt_codes:
        return fallback
    key = vt_codes[0] if len(vt_codes) == 1 else list(vt_codes)
    return ["match", ["get", "vt_code"], key, TRANSPARENT, fallback]


def compile_symbol_text_color(base_color_expr, hide_below_zoom14, hide_at_and_above_zoom14):
    """base_color_expr: the compiled Anno text-color ramp (category_table.
    compile_match_expression() output for ANNO_TEXT_COLOR_CATEGORIES/
    VALUES) to reuse verbatim, not rebuild. hide_below_zoom14 /
    hide_at_and_above_zoom14: vt_code lists made transparent in that zoom
    band instead of the ramp's color."""
    var_color = ["var", "color"]
    return [
        "let", "color", base_color_expr,
        ["step", ["zoom"],
         _hide_match(hide_below_zoom14, var_color),
         14,
         _hide_match(hide_at_and_above_zoom14, var_color)],
    ]


if __name__ == "__main__":
    from category_table import ANNO_TEXT_COLOR_CATEGORIES, ANNO_TEXT_COLOR_VALUES, compile_match_expression

    with open("style/bvmap-dark.json") as f:
        style = json.load(f)
    by_id = {l["id"]: l for l in style["layers"]}

    base = compile_match_expression(ANNO_TEXT_COLOR_CATEGORIES, ANNO_TEXT_COLOR_VALUES)

    checks = [
        ("bvmap-注記シンボル付きソート順100以上",
         compile_symbol_text_color(base, [661, 662], [3201, 3204, 3215, 3216, 3217, 3218, 3243])),
        ("bvmap-注記シンボル付きソート順100未満",
         compile_symbol_text_color(base, [631, 632, 633, 6368, 6376], [3212, 3213, 3214])),
    ]

    mismatches = []
    for lid, generated in checks:
        original = by_id[lid]["paint"]["text-color"]
        if json.dumps(generated, sort_keys=True, ensure_ascii=False) != \
           json.dumps(original, sort_keys=True, ensure_ascii=False):
            mismatches.append(lid)

    if not mismatches:
        print("STAGE 1 GATE: PASS — Anno symbol-attached text-color (0017's "
              "let-wrapped mystery, resolved in 0027) reproduced exactly for both layers.")
    else:
        print(f"STAGE 1 GATE: FAIL — mismatches: {mismatches}")
