"""
Stage 1 generator (reproduction-first): full 123-layer assembly.

The final Stage 1 gate (docs/decisions/0009, HANDOVER.md item 4): combine
every mechanism proven so far into one 123-layer array and diff it against
style/bvmap-dark.json layer-by-layer. This is an *integration* test, not
just a copy — wherever a compiler has been proven (tier_template,
category_table, road_color, building_color), this module actively
substitutes its generated output in place of a literal copy, so a
mismatch here means the compiler's output doesn't actually fit into the
assembled whole, not just that the compiler passed its own narrow test.

Layers this module does NOT yet generate (48 of 123) are carried over
verbatim from style/bvmap-dark.json. That is the "literal" bucket
discussed in the case conference (docs/decisions/0009's escape hatch) —
see LITERAL_RANGES below for exactly which ones and why.
"""
import json

from tier_template import (
    extract_templates, generate_tier_block, KNOWN_TIER4_ANOMALIES, TIERS, ROLES_TIER0, ROLES_SHARED,
)
from category_table import (
    compile_match_expression,
    ANNO_TEXT_COLOR_CATEGORIES, ANNO_TEXT_COLOR_VALUES, SHARED_TEXT_COLOR_LAYERS,
    ANNO_TEXT_FONT_CATEGORIES, ANNO_TEXT_FONT_VALUES,
)
from road_color import compile_road_color_step
from building_color import (
    BUILDING_FILL_CATEGORIES, BUILDING_FILL_VALUES,
    BUILDING_OUTLINE_CATEGORIES, BUILDING_OUTLINE_COLOR_VALUES, BUILDING_OUTLINE_WIDTH_VALUES,
)

# 7 of the 9 Anno layers share the text-font water/coastal split — 2 more
# than share text-color (docs/decisions/0017's unresolved let-wrapped
# layers, bvmap-注記シンボル付きソート順100以上/100未満, still use the
# split for text-font even though their text-color isn't reproduced yet).
SHARED_TEXT_FONT_LAYERS = SHARED_TEXT_COLOR_LAYERS + [
    "bvmap-注記シンボル付きソート順100以上",
    "bvmap-注記シンボル付きソート順100未満",
]

# Layers carried over verbatim, with the reason grouped by range (docs/
# decisions/0009's escape hatch). None of these have a compiler yet;
# each is a candidate for its own case-conference slot later.
LITERAL_RANGES = {
    "background/AdmArea/WA/terrain/hydrography/boundaries/contours (layers 0-22)":
        [l for l in range(0, 23)],
    "ZL4-10 low-zoom overview (layers 23-25, excluded from the tier block by design)":
        [23, 24, 25],
    "post-tier individual layers (dashed roads, tunnels, structures, power lines, etc., 96-113)":
        list(range(96, 114)),
}

# The 2 let-wrapped symbol-attached Anno layers (docs/decisions/0017's
# unresolved section) plus the 2 Anno layers with no shared pattern at
# all (シンボル付き重なり, 道路番号) — 4 of the 9 Anno layers, literal.
LITERAL_ANNO_LAYERS = [
    "bvmap-注記シンボル付き重なり",
    "bvmap-注記道路番号",
    "bvmap-注記シンボル付きソート順100以上",
    "bvmap-注記シンボル付きソート順100未満",
]


def build_tier_block(by_id):
    templates_tier0 = extract_templates(by_id, 0)
    templates_tier1 = extract_templates(by_id, 1)
    generated = generate_tier_block(templates_tier0, templates_tier1)

    road_color_generated = compile_road_color_step()
    building_fill_generated = compile_match_expression(BUILDING_FILL_CATEGORIES, BUILDING_FILL_VALUES)
    building_outline_color_generated = compile_match_expression(
        BUILDING_OUTLINE_CATEGORIES, BUILDING_OUTLINE_COLOR_VALUES)
    building_outline_width_generated = compile_match_expression(
        BUILDING_OUTLINE_CATEGORIES, BUILDING_OUTLINE_WIDTH_VALUES)

    out = []
    for template_layer in generated:
        lid = template_layer["id"]
        if lid in KNOWN_TIER4_ANOMALIES:
            # GSI's own tier-4 generation bug (docs/decisions/0016) —
            # deliberately not reproduced; carry the original verbatim.
            out.append(by_id[lid])
            continue

        # generate_tier_block() copies "paint" by reference from the
        # extracted per-tier template (itself a reference into by_id, i.e.
        # into the loaded style/bvmap-dark.json). Deep-copy before
        # mutating below, or we'd corrupt the ground truth we diff against.
        layer = json.loads(json.dumps(template_layer))

        if lid.startswith("bvmap-道路中心線色") and lid != "bvmap-道路中心線色0":
            # tier 0's plain (non-bridge) 色0 keeps its own extra zoom>=14
            # branch (docs/decisions/0016/0018) — road_color.py only
            # reproduces the 9 non-exceptional layers, so leave 色0 as
            # tier_template's own literal-per-tier extraction.
            layer["paint"]["line-color"] = road_color_generated
        elif lid.startswith("bvmap-建築物の外周線"):
            layer["paint"]["line-color"] = building_outline_color_generated
            layer["paint"]["line-width"] = building_outline_width_generated
        elif lid.startswith("bvmap-建築物"):
            layer["paint"]["fill-color"] = building_fill_generated

        out.append(layer)
    return out


def build_anno_block(anno_ids, by_id):
    text_color_generated = compile_match_expression(ANNO_TEXT_COLOR_CATEGORIES, ANNO_TEXT_COLOR_VALUES)
    text_font_generated = compile_match_expression(ANNO_TEXT_FONT_CATEGORIES, ANNO_TEXT_FONT_VALUES)

    out = []
    for lid in anno_ids:
        layer = json.loads(json.dumps(by_id[lid]))  # deep copy; we mutate paint/layout below
        if lid not in LITERAL_ANNO_LAYERS:
            layer["paint"]["text-color"] = text_color_generated
        if lid in SHARED_TEXT_FONT_LAYERS:
            layer["layout"]["text-font"] = text_font_generated
        out.append(layer)
    return out


if __name__ == "__main__":
    with open("style/bvmap-dark.json") as f:
        style = json.load(f)
    layers = style["layers"]
    by_id = {l["id"]: l for l in layers}

    assembled_by_id = {}

    for _, indices in LITERAL_RANGES.items():
        for i in indices:
            assembled_by_id[layers[i]["id"]] = layers[i]

    for layer in build_tier_block(by_id):
        assembled_by_id[layer["id"]] = layer

    anno_ids = [l["id"] for l in layers if l["id"].startswith("bvmap-注記")]
    for layer in build_anno_block(anno_ids, by_id):
        assembled_by_id[layer["id"]] = layer

    assert len(assembled_by_id) == len(layers), (len(assembled_by_id), len(layers))

    assembled = [assembled_by_id[l["id"]] for l in layers]

    mismatches = []
    for g, o in zip(assembled, layers):
        if g["id"] != o["id"]:
            mismatches.append(("id-order", g["id"], o["id"]))
            continue
        gs = json.dumps(g, sort_keys=True, ensure_ascii=False)
        os_ = json.dumps(o, sort_keys=True, ensure_ascii=False)
        if gs != os_:
            mismatches.append((g["id"], gs[:200], os_[:200]))

    literal_count = sum(len(v) for v in LITERAL_RANGES.values()) + len(LITERAL_ANNO_LAYERS)
    if not mismatches:
        print(
            f"STAGE 1 FINAL GATE: PASS — all {len(assembled)} layers reproduced exactly. "
            f"{literal_count} literal (not yet decomposed), "
            f"{len(assembled) - literal_count} generated (tier structure / category tables / "
            f"road priority chain / building tables)."
        )
    else:
        print(f"STAGE 1 FINAL GATE: FAIL — {len(mismatches)} mismatches of {len(assembled)} layers")
        for m in mismatches[:8]:
            print(m)
