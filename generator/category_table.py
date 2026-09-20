"""
Stage 1 generator (reproduction-first): the vt_code category-table compiler.

Core primitive from docs/decisions/0009: given named categories (each a
set of vt_codes) and a property table (category name -> value), emit the
equivalent MapLibre `match` expression. One mechanism, reused for color,
font, and icon selection — because GSI's own bvmap-dark.json already
uses this exact idiom for all three (docs/decisions/0009, 0010).

This module proves the mechanism against the Anno text-color ramp
(docs/decisions/0008), which 5 of the 7 Anno-derived symbol layers share
verbatim.
"""
import json


def compile_match_expression(categories: dict, property_table: dict, property: str = "vt_code"):
    """categories: {name: [key, ...]} (usually vt_code ints, but any
    feature property's values work — e.g. vt_rtcode strings for
    docs/decisions/0024's ZL4-10 rail color)
    property_table: {name: value, ..., "default": value}
    Returns a MapLibre ["match", ["get", property], ...] expression.

    Category order matters (MapLibre evaluates match branches in order,
    though for vt_code this only matters if codes were to appear in more
    than one category, which shouldn't happen) — callers pass an
    ordered dict/list to control it.
    """
    body = []
    for name, codes in categories.items():
        if name not in property_table:
            continue
        key = codes[0] if len(codes) == 1 else list(codes)
        body.append(key)
        body.append(property_table[name])
    body.append(property_table["default"])
    return ["match", ["get", property], *body]


# The Anno text-color ramp (docs/decisions/0008), extracted from
# bvmap-dark.json's bvmap-注記角度付き線 layer. Category names are
# provisional/descriptive (not GSI-official) pending case 2's fuller
# YAML writeup — this module only proves the compiler mechanism.
ANNO_TEXT_COLOR_CATEGORIES = {
    "c521": [521],
    "c348": [348],
    "group_a": [411, 412, 413, 421, 422, 423, 431, 432, 441, 860, 2941, 2942, 2943, 2944, 2945],
    "group_b": [7372, 7711],
    "c7352": [7352],
    "group_c": [2901, 2903, 2904],
    "water_coastal": [321, 322, 341, 344, 345, 820, 840, 841],
    "c220": [220],
    "c312": [312],
    "group_d": [333, 346],
    "group_e": [
        511, 522, 523, 531, 532, 534, 611, 612, 613, 614, 615, 621, 623, 631, 632, 633, 634,
        641, 642, 651, 652, 653, 654, 661, 662, 671, 672, 673, 681, 720, 730, 870, 880, 881,
        882, 883, 884, 885, 886, 887, 888, 889, 890, 899, 999, 3201, 3202, 3203, 3204, 3205,
        3206, 3211, 3212, 3213, 3214, 3215, 3216, 3217, 3218, 3221, 3231, 3232, 3241, 3242,
        3243, 3244,
    ],
}

ANNO_TEXT_COLOR_VALUES = {
    "c521": "rgba(29,29,29,1)",
    "c348": "rgba(98,98,98,1)",
    "group_a": "rgba(70,70,70,1)",
    "group_b": "rgba(88,88,88,1)",
    "c7352": "rgba(161,161,161,1)",
    "group_c": "rgba(255,255,255,1)",
    "water_coastal": "rgba(68,68,68,1)",
    "c220": "rgba(80,80,80,1)",
    "c312": "rgba(42,42,42,1)",
    "group_d": "rgba(59,59,59,1)",
    "group_e": "rgba(50,50,50,1)",
    "default": "rgba(0,0,0,1)",
}

# The 5 layers confirmed (2026-09-19) to share this exact table verbatim.
SHARED_TEXT_COLOR_LAYERS = [
    "bvmap-注記シンボルなし縦ソート順100以上",
    "bvmap-注記シンボルなし横ソート順100以上",
    "bvmap-注記角度付き線",
    "bvmap-注記シンボルなし縦ソート順100未満",
    "bvmap-注記シンボルなし横ソート順100未満",
]


# The text-font water/coastal split (docs/decisions/0002, 0007, 0013).
# NOTE: this "water_coastal" grouping is *not* the same 11-vs-8-code set
# as text-color's water_coastal above (color leaves out 342/347/842 —
# coastal/beach codes — which fall through to its default black instead).
# Each property's categories are independent, even when they overlap
# substantially — recorded here as-is rather than forcing one shared
# category across properties that don't actually agree on membership.
ANNO_TEXT_FONT_CATEGORIES = {
    "water_coastal": [321, 322, 341, 342, 344, 345, 347, 820, 840, 841, 842],
}
ANNO_TEXT_FONT_VALUES = {
    "water_coastal": ["literal", ["NotoSerifJP-SemiBold"]],
    "default": ["literal", ["NotoSansJP-Regular"]],
}


if __name__ == "__main__":
    with open("style/bvmap-dark.json") as f:
        style = json.load(f)
    by_id = {l["id"]: l for l in style["layers"]}

    generated = compile_match_expression(ANNO_TEXT_COLOR_CATEGORIES, ANNO_TEXT_COLOR_VALUES)
    generated_json = json.dumps(generated, sort_keys=True, ensure_ascii=False)

    mismatches = []
    for lid in SHARED_TEXT_COLOR_LAYERS:
        original = by_id[lid]["paint"]["text-color"]
        original_json = json.dumps(original, sort_keys=True, ensure_ascii=False)
        if generated_json != original_json:
            mismatches.append(lid)

    font_generated = compile_match_expression(ANNO_TEXT_FONT_CATEGORIES, ANNO_TEXT_FONT_VALUES)
    font_original = by_id["bvmap-注記角度付き線"]["layout"]["text-font"]
    font_ok = json.dumps(font_generated, sort_keys=True) == json.dumps(font_original, sort_keys=True)

    if not mismatches and font_ok:
        print(f"STAGE 1 GATE: PASS — same compiler reproduces text-color exactly across "
              f"all {len(SHARED_TEXT_COLOR_LAYERS)} layers that share it, AND text-font's "
              f"water/coastal split, with independent per-property category tables.")
    else:
        print(f"STAGE 1 GATE: FAIL — text-color mismatches: {mismatches}, text-font ok: {font_ok}")
