"""
Full 123-layer assembly, and the generator's only writer of
style/bvmap-starlight.json.

Originally the Stage 1 gate (docs/decisions/0009, 0019): combine every
mechanism proven so far into one 123-layer array and diff it against
style/bvmap-dark.json layer-by-layer, to prove the generated pieces
actually fit into the assembled whole, not just pass their own narrow
test. That reproduction-first phase is done (docs/decisions/0028), and
the literal-layer migration continues (docs/decisions/0032/0034/0035) —
every layer not yet generated from a categories/priority_chains table is
still addressed by id via a `patches` entry (base copy + why-literal
annotation, docs/decisions/0020), never by raw array position (see
LITERAL_ANNO_LAYERS below for the one still-literal exception).

Starting with docs/decisions/0029, this script also WRITES the assembled
style to style/bvmap-starlight.json on every run — the actual Starlight
color polish work happens by editing starlight-input.yaml's palette and
re-running this. Once the palette diverges from the reproduction
defaults, the assembled style is *expected* to differ from
style/bvmap-dark.json's content; only an id/order mismatch is still
treated as a hard structural failure (see __main__ below).
"""
import json

from tier_template import extract_templates, generate_tier_block, KNOWN_TIER4_ANOMALIES
from category_table import SHARED_TEXT_COLOR_LAYERS
from load_input import (
    load, build_categories, build_priority_chains, build_patches, build_standalone_layers,
    remap_font_names,
)

# 7 of the 9 Anno layers share the text-font water/coastal split — 2 more
# than share text-color (docs/decisions/0017's unresolved let-wrapped
# layers, bvmap-注記シンボル付きソート順100以上/100未満, still use the
# split for text-font even though their text-color isn't reproduced yet).
# Derived from SHARED_TEXT_COLOR_LAYERS (not hand-copied) so a future edit
# to that list propagates here automatically.
SHARED_TEXT_FONT_LAYERS = SHARED_TEXT_COLOR_LAYERS + [
    "bvmap-注記シンボル付きソート順100以上",
    "bvmap-注記シンボル付きソート順100未満",
]

# LITERAL_RANGES (position-indexed literal layers, docs/decisions/0009's
# original escape hatch) is retired as of docs/decisions/0035 — every
# layer that used to live there now has an explicit by-id patches entry
# in starlight-input.yaml instead, closing the position-based fragility
# docs/decisions/0020's review flagged (an upstream bvmap-dark.json
# reorder can no longer silently misassign a "literal" layer).

# bvmap-注記シンボル付き重なり is the only genuinely one-off Anno layer
# (a pure icon layer with no text-color at all — docs/decisions/0027).
# The other 3 that used to live here (道路番号, シンボル付きソート順
# 100以上/100未満) turned out to have real, reproducible color logic —
# see ANNO_TEXT_COLOR_SOURCES below.
LITERAL_ANNO_LAYERS = [
    "bvmap-注記シンボル付き重なり",
]

# Which categories.*/priority_chains.* expression drives each Anno
# layer's text-color (docs/decisions/0027) — everything not listed here
# and not in LITERAL_ANNO_LAYERS has no text-color property at all.
ANNO_TEXT_COLOR_SOURCES = {
    lid: ("categories", "anno_text_color") for lid in SHARED_TEXT_COLOR_LAYERS
}
ANNO_TEXT_COLOR_SOURCES["bvmap-注記道路番号"] = ("categories", "anno_road_number_color")
ANNO_TEXT_COLOR_SOURCES["bvmap-注記シンボル付きソート順100以上"] = ("chains", "anno_symbol_text_color_100_over")
ANNO_TEXT_COLOR_SOURCES["bvmap-注記シンボル付きソート順100未満"] = ("chains", "anno_symbol_text_color_100_under")


def build_tier_block(by_id, categories, chains):
    templates_tier0 = extract_templates(by_id, 0)
    templates_tier1 = extract_templates(by_id, 1)
    generated = generate_tier_block(templates_tier0, templates_tier1)

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
            # branch (docs/decisions/0016/0018) — road_color only
            # reproduces the 9 non-exceptional layers, so leave 色0 as
            # tier_template's own literal-per-tier extraction.
            layer["paint"]["line-color"] = chains["road_color"]
        elif lid.startswith("bvmap-建築物の外周線"):
            layer["paint"]["line-color"] = categories["building_outline_color"]
            layer["paint"]["line-width"] = categories["building_outline_width"]
        elif lid.startswith("bvmap-建築物"):
            layer["paint"]["fill-color"] = categories["building_fill"]

        out.append(layer)
    return out


def build_anno_block(anno_ids, by_id, categories, chains):
    text_font_generated = categories["anno_text_font"]
    sources = {"categories": categories, "chains": chains}

    out = []
    for lid in anno_ids:
        layer = json.loads(json.dumps(by_id[lid]))  # deep copy; we mutate paint/layout below
        if lid in ANNO_TEXT_COLOR_SOURCES:
            section, name = ANNO_TEXT_COLOR_SOURCES[lid]
            layer["paint"]["text-color"] = sources[section][name]
        if lid in SHARED_TEXT_FONT_LAYERS:
            layer["layout"]["text-font"] = text_font_generated
        out.append(layer)
    return out


if __name__ == "__main__":
    with open("style/bvmap-dark.json") as f:
        style = json.load(f)
    layers = style["layers"]
    by_id = {l["id"]: l for l in layers}

    config = load()
    categories = build_categories(config)
    chains = build_priority_chains(config, categories)
    patches, patched_ids = build_patches(config, by_id)
    standalone = build_standalone_layers(config, by_id, categories, chains)

    assembled_by_id = {}

    # YAML-driven patches (docs/decisions/0020) — every literal layer is
    # now addressed by id here (docs/decisions/0035 retired the old
    # position-indexed LITERAL_RANGES fallback entirely). Most patches
    # have a resolved color_overrides by now; a few (docs/decisions/0021's
    # still-uninvestigated 0008-annotated group) remain a base copy with
    # no override yet and stay literal until their own color pass.
    for lid, layer in patches.items():
        assembled_by_id[lid] = layer

    # engine: standalone layers (docs/decisions/0022) — real vt_code match
    # tables for layers outside the tier structure (bvmap-構造物面/構造物線).
    for lid, layer in standalone.items():
        assembled_by_id[lid] = layer

    for layer in build_tier_block(by_id, categories, chains):
        assembled_by_id[layer["id"]] = layer

    anno_ids = [l["id"] for l in layers if l["id"].startswith("bvmap-注記")]
    for layer in build_anno_block(anno_ids, by_id, categories, chains):
        assembled_by_id[layer["id"]] = layer

    assert len(assembled_by_id) == len(layers), (len(assembled_by_id), len(layers))

    assembled = [assembled_by_id[l["id"]] for l in layers]

    # id/order mismatches are always a real bug (assembled_by_id is keyed
    # by the *original* ids, so this should be structurally impossible —
    # kept as a hard check). Content differences from bvmap-dark.json are
    # no longer a failure: once starlight-input.yaml's palette diverges
    # from the reproduction defaults, generated layers are *supposed* to
    # differ (docs/decisions/0029).
    id_order_problems = []
    content_diffs = []
    for g, o in zip(assembled, layers):
        if g["id"] != o["id"]:
            id_order_problems.append((g["id"], o["id"]))
            continue
        if json.dumps(g, sort_keys=True, ensure_ascii=False) != \
           json.dumps(o, sort_keys=True, ensure_ascii=False):
            content_diffs.append(g["id"])

    # "literal" = no compiler/palette value actually drives this layer's
    # content yet. A patches entry with no applied color_overrides (e.g.
    # the 0008-annotated group awaiting its own color investigation) is
    # still literal in that sense, even though it's addressed by id in
    # the YAML like every other patches entry.
    literal_count = len(LITERAL_ANNO_LAYERS) + (len(patches) - len(patched_ids))

    if id_order_problems:
        print(f"STRUCTURAL FAIL: {len(id_order_problems)} layer(s) assembled out of order "
              f"or with a mismatched id — this should be impossible: {id_order_problems[:5]}")
    else:
        with open("style/bvmap-starlight.json") as f:
            current_starlight_name = json.load(f)["name"]

        output_style = dict(style)
        output_style["layers"] = assembled
        output_style["name"] = current_starlight_name

        # hosting: (docs/decisions/0036) overrides style-level properties that
        # bvmap-dark.json still points at GSI for. Omitted keys pass GSI's
        # original value through unchanged.
        hosting = config.get("hosting", {})
        for key in ("glyphs", "sprite"):
            if key in hosting:
                output_style[key] = hosting[key]

        # A style's glyphs endpoint is style-wide — if we're switching it,
        # every layer's layout.text-font literal has to resolve against the
        # new host, not just the ones categories.anno_text_font generates.
        font_names = hosting.get("font_names", {})
        if font_names:
            for layer in output_style["layers"]:
                tf = layer.get("layout", {}).get("text-font")
                if tf is not None:
                    layer["layout"]["text-font"] = remap_font_names(tf, font_names)

        with open("style/bvmap-starlight.json", "w") as f:
            json.dump(output_style, f, ensure_ascii=False, indent=1)
            f.write("\n")

        print(
            f"Wrote style/bvmap-starlight.json — {len(assembled)} layers, structurally sound "
            f"(ids/order match bvmap-dark.json). {literal_count} literal, "
            f"{len(assembled) - literal_count} generated/YAML-patched. "
            f"{len(content_diffs)} layer(s) differ in content from bvmap-dark.json "
            f"(expected once starlight-input.yaml's palette diverges from the reproduction "
            f"defaults; 0 is expected only before any intentional color change)."
        )
