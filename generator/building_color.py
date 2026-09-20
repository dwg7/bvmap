"""
Stage 1 generator (reproduction-first): building fill/outline color.

Unlike road color (generator/road_color.py, docs/decisions/0018), building
fill and outline turn out to be plain single-property vt_code matches —
the same shape category_table.py's compile_match_expression() already
proves against Anno text-color/text-font. This module is the third
independent confirmation of that one mechanism (docs/decisions/0010 §2).
"""
import json

from category_table import compile_match_expression

BUILDING_FILL_CATEGORIES = {
    "c3101": [3101],
    "c3102": [3102],
    "c3103": [3103],
    "c3111": [3111],
    "c3112": [3112],
}
BUILDING_FILL_VALUES = {
    "c3101": "rgba(233,233,233,1)",
    "c3102": "rgba(203,203,203,1)",
    "c3103": "rgba(152,152,152,1)",
    "c3111": "rgba(203,203,203,1)",
    "c3112": "rgba(203,203,203,1)",
    "default": "rgba(0,0,0,0)",
}

# Outline color is a single value for any matching building vt_code —
# docs/decisions/0010's "matched or not, no per-category variation" point.
# bvmap-dark.json still spells this as 5 separate match keys (not a
# combined list), so the category table keeps that shape to stay
# byte-exact — the *value* table is where "any -> same value" collapses.
BUILDING_OUTLINE_CATEGORIES = {
    "c3101": [3101],
    "c3102": [3102],
    "c3103": [3103],
    "c3111": [3111],
    "c3112": [3112],
}
BUILDING_OUTLINE_COLOR_VALUES = {
    "c3101": "rgba(164,164,164,1)",
    "c3102": "rgba(164,164,164,1)",
    "c3103": "rgba(164,164,164,1)",
    "c3111": "rgba(164,164,164,1)",
    "c3112": "rgba(164,164,164,1)",
    "default": "rgba(0,0,0,0)",
}
BUILDING_OUTLINE_WIDTH_VALUES = {
    "c3101": 1,
    "c3102": 1,
    "c3103": 1,
    "c3111": 1,
    "c3112": 1,
    "default": 0,
}


if __name__ == "__main__":
    with open("style/bvmap-dark.json") as f:
        style = json.load(f)
    by_id = {l["id"]: l for l in style["layers"]}

    checks = [
        ("fill-color", by_id["bvmap-建築物0"]["paint"]["fill-color"],
         compile_match_expression(BUILDING_FILL_CATEGORIES, BUILDING_FILL_VALUES)),
        ("outline line-color", by_id["bvmap-建築物の外周線0"]["paint"]["line-color"],
         compile_match_expression(BUILDING_OUTLINE_CATEGORIES, BUILDING_OUTLINE_COLOR_VALUES)),
        ("outline line-width", by_id["bvmap-建築物の外周線0"]["paint"]["line-width"],
         compile_match_expression(BUILDING_OUTLINE_CATEGORIES, BUILDING_OUTLINE_WIDTH_VALUES)),
    ]

    mismatches = [name for name, original, generated in checks
                  if json.dumps(original, sort_keys=True) != json.dumps(generated, sort_keys=True)]

    if not mismatches:
        print("STAGE 1 GATE: PASS — building fill-color, outline line-color, and outline "
              "line-width all reproduced exactly by compile_match_expression() unmodified — "
              "third confirmation of the flat vt_code-category compiler (docs/decisions/0009).")
    else:
        print(f"STAGE 1 GATE: FAIL — mismatches: {mismatches}")
