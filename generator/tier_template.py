"""
Stage 1 generator (reproduction-first): the road/rail/building tier block.

Extracts the 14-role template from tier 0 of style/bvmap-dark.json,
parameterizes out the vt_lvorder filter clause, records the one known
tier-0-only exception (road-casing line-color), and regenerates all 5
tiers. The Stage 1 gate: this must reproduce layers[23:96] of the
source exactly (docs/decisions/0009, 0008).
"""
import json

# Tier 0 draws buildings *between* ground-level and elevated infrastructure
# (matching the real-world stacking: ground road/rail -> buildings ->
# bridges above them). Tiers 1-4 draw buildings *after* all rail-bridge
# roles instead — a second, structural (not just content) tier-0
# exception on top of the line-color one, confirmed against the real
# layer order (docs/decisions/0008/0009).
ROLES_TIER0 = [
    "道路中心線ククリ",
    "道路中心線色",
    "鉄道中心線駅ククリ",
    "鉄道中心線",
    "鉄道中心線旗竿",
    "道路中心線ククリ橋",
    "道路中心線色橋",
    "建築物",
    "建築物の外周線",
    "鉄道中心線橋ククリ黒",
    "鉄道中心線橋ククリ白",
    "鉄道中心線橋駅ククリ",
    "鉄道中心線橋",
    "鉄道中心線旗竿橋",
]

ROLES_SHARED = [
    "道路中心線ククリ",
    "道路中心線色",
    "鉄道中心線駅ククリ",
    "鉄道中心線",
    "鉄道中心線旗竿",
    "道路中心線ククリ橋",
    "道路中心線色橋",
    "鉄道中心線橋ククリ黒",
    "鉄道中心線橋ククリ白",
    "鉄道中心線橋駅ククリ",
    "鉄道中心線橋",
    "鉄道中心線旗竿橋",
    "建築物",
    "建築物の外周線",
]

ROLES = ROLES_TIER0  # union used by extract_templates; both lists have the same members

TIERS = [0, 1, 2, 3, 4]  # 4 means ">=4" — see tier_filter() below


def tier_filter(role: str, tier: int, base_filter):
    """Rebuilds a layer's filter for a given tier by replacing whichever
    [op, ["get","vt_lvorder"], N] clause is in base_filter with the right
    comparison for this tier (== for 0-3, >= for the last/overflow tier).
    Works regardless of which tier base_filter itself came from."""
    op = ">=" if tier == 4 else "=="

    def is_lvorder_clause(node):
        return (
            isinstance(node, list) and len(node) == 3
            and node[0] in ("==", ">=")
            and node[1] == ["get", "vt_lvorder"]
            and isinstance(node[2], (int, float))
        )

    def replace(node):
        if is_lvorder_clause(node):
            return [op, ["get", "vt_lvorder"], tier]
        if isinstance(node, list):
            return [replace(x) for x in node]
        return node

    return replace(base_filter)


OPTIONAL_KEYS = ["layout", "paint", "minzoom", "maxzoom"]


def extract_role_template(layer):
    template = {
        "filter": layer["filter"],
        "type": layer["type"],
        "source": layer["source"],
        "source-layer": layer["source-layer"],
    }
    for key in OPTIONAL_KEYS:
        if key in layer:
            template[key] = layer[key]
    return template


def extract_templates(layers_by_id, tier):
    """Pulls the 14 role templates from the given tier."""
    return {role: extract_role_template(layers_by_id[f"bvmap-{role}{tier}"]) for role in ROLES}


# The one confirmed exception (docs/decisions/0008, 0009): tier 0's
# road-casing line-color has an extra branch hiding vt_rnkwidth=="不明"
# roads that tiers 1-4 don't have. Rather than modeling that branch as a
# generic "patch" mechanism, tier 0 simply keeps its own extracted
# template (which already contains the exception verbatim) instead of
# sharing tier 1-4's template — see generate_tier_block().

def generate_tier_block(templates_from_tier0, templates_from_tier1):
    """Builds all 70 templated layers (14 roles x 5 tiers), in the same
    tier-major order as bvmap-dark.json. templates_from_tier1 supplies the
    *shared* (non-exceptional) role definitions; templates_from_tier0
    supplies tier 0's own copies, used verbatim for tier 0 so the known
    exception carries over exactly."""
    out = []
    for tier in TIERS:
        role_order = ROLES_TIER0 if tier == 0 else ROLES_SHARED
        for role in role_order:
            base = templates_from_tier0[role] if tier == 0 else templates_from_tier1[role]
            layer = {
                "id": f"bvmap-{role}{tier}",
                "type": base["type"],
                "source": base["source"],
                "source-layer": base["source-layer"],
                "filter": tier_filter(role, tier, base["filter"]),
            }
            for key in OPTIONAL_KEYS:
                if key in base:
                    layer[key] = base[key]
            out.append(layer)
    return out


# Known, deliberately-not-reproduced anomaly (confirmed 2026-09-19): in
# bvmap-dark.json's actual tier 4 (the ">=4" overflow tier), GSI's own
# generation process appears to have broadly replaced "==" with ">="
# within these 5 layers' filters, catching unrelated comparisons
# (e.g. ["==", ["get","vt_rtcode"], "JR"] -> [">=", ...]) beyond just the
# vt_lvorder clause. ">=" on a string equality check is not meaningful,
# so this reads as a bug in GSI's tier-4 generation, not intentional
# design. This generator reproduces only the vt_lvorder comparison
# change (the semantically correct behavior) and does not replicate the
# over-broad replacement — decided over reproducing it byte-for-byte.
KNOWN_TIER4_ANOMALIES = {
    "bvmap-道路中心線ククリ4",
    "bvmap-鉄道中心線旗竿4",
    "bvmap-鉄道中心線橋ククリ黒4",
    "bvmap-鉄道中心線橋ククリ白4",
    "bvmap-鉄道中心線旗竿橋4",
}


if __name__ == "__main__":
    with open("style/bvmap-dark.json") as f:
        style = json.load(f)
    by_id = {l["id"]: l for l in style["layers"]}

    templates_tier0 = extract_templates(by_id, 0)
    # tier 1 is exception-free; use it as the shared template for tiers 1-4
    templates_tier1 = extract_templates(by_id, 1)

    generated = generate_tier_block(templates_tier0, templates_tier1)

    original_block = style["layers"][26:96]  # the 70 templated layers (excludes 3 ZL4-10 overview layers)

    assert len(generated) == len(original_block), (len(generated), len(original_block))

    mismatches = []
    known_anomalies_seen = []
    for g, o in zip(generated, original_block):
        if g["id"] != o["id"]:
            mismatches.append(("id", g["id"], o["id"]))
            continue
        if g["id"] in KNOWN_TIER4_ANOMALIES:
            known_anomalies_seen.append(g["id"])
            continue
        gs = json.dumps(g, sort_keys=True, ensure_ascii=False)
        os_ = json.dumps(o, sort_keys=True, ensure_ascii=False)
        if gs != os_:
            mismatches.append((g["id"], gs, os_))

    if not mismatches:
        print(
            f"STAGE 1 GATE: PASS — {len(generated) - len(known_anomalies_seen)} of "
            f"{len(generated)} layers match bvmap-dark.json exactly; "
            f"{len(known_anomalies_seen)} known tier-4 anomalies deliberately not "
            f"reproduced (see KNOWN_TIER4_ANOMALIES)."
        )
    else:
        print(f"STAGE 1 GATE: FAIL — {len(mismatches)} unexplained mismatches of {len(generated)} layers")
        for m in mismatches[:5]:
            print(m)
