"""
Stage 1 generator (reproduction-first): road vt_rdctg-driven line-color.

Investigates whether docs/decisions/0010's road-color table is reproducible
by the same flat "vt_code category -> match" compiler as
generator/category_table.py (Anno text-color/text-font) and building
fill/outline. Finding: it is NOT the same shape — see docs/decisions/0018.

This module builds the shared line-color expression (identical across
bvmap-道路中心線色{1,2,3,4} and bvmap-道路中心線色橋{0,1,2,3,4} — 9 of the
10 vt_rdctg-driven layers; tier 0's non-bridge 色0 layer carries one
additional zoom>=14 branch, already handled verbatim by
generator/tier_template.py's per-tier template extraction and out of
scope here) from named building blocks, to make the *structure* legible
rather than to replace tier_template.py's literal copy.
"""
import json

BRIDGE_VT_CODES = [2704, 2714]

# The vt_rdctg table used ONLY inside the bridge-vt_code branch (docs/
# decisions/0010's original table matches this one, not the general case
# below — see docs/decisions/0018 for the correction).
BRIDGE_RDCTG_TABLE = {
    "国道": 160,
    "都道府県道": 226,
    "市区町村道等": 100,
    "高速自動車国道等": 157,
    "その他": 100,
    "不明": 100,
}
BRIDGE_RDCTG_DEFAULT = 100

# The vt_rdctg table used in the general (non-bridge-vt_code) case. Only
# 3 of the 6 categories get an explicit gray; everything else (including
# 市区町村道等/その他/不明) falls through to a *width*-driven ramp, not a
# vt_rdctg-driven gray. This directly contradicts docs/decisions/0010's
# implication that 市区町村道等->gray(100)/その他->gray(100)/不明->gray(100)
# hold generally — they only hold inside the bridge branch.
GENERAL_RDCTG_TABLE = {
    "国道": 160,
    "都道府県道": 226,
    "高速自動車国道等": 157,
}

# The fallback width ramp for roads that match neither vt_motorway nor
# any of the 3 general-case vt_rdctg keys above.
WIDTH_RAMP = {
    (2721, 2722, 2723): 173,
    (2731, 2732, 2733): 200,
}
WIDTH_RAMP_DEFAULT = 255


def _rgba(gray, alpha=1):
    return f"rgba({gray},{gray},{gray},{alpha})"


def _bridge_branch(alpha):
    body = []
    for name, gray in BRIDGE_RDCTG_TABLE.items():
        body.append(name)
        body.append(_rgba(gray, alpha))
    rdctg_match = ["match", ["get", "vt_rdctg"], *body, _rgba(BRIDGE_RDCTG_DEFAULT, alpha)]
    return [
        "case",
        ["==", ["get", "vt_motorway"], 1],
        _rgba(157, alpha),
        rdctg_match,
    ]


def _width_ramp_match():
    body = []
    for codes, gray in WIDTH_RAMP.items():
        body.append(list(codes))
        body.append(_rgba(gray))
    return ["match", ["get", "vt_code"], *body, _rgba(WIDTH_RAMP_DEFAULT)]


def _general_branch(include_3m_exception):
    body = []
    for name, gray in GENERAL_RDCTG_TABLE.items():
        body.append(name)
        body.append(_rgba(gray))
    fallback = _width_ramp_match()
    if include_3m_exception:
        fallback = [
            "case",
            ["==", ["get", "vt_rnkwidth"], "3m-5.5m未満"],
            _rgba(173),
            fallback,
        ]
    rdctg_match = ["match", ["get", "vt_rdctg"], *body, fallback]
    return [
        "case",
        ["==", ["get", "vt_motorway"], 1],
        _rgba(157),
        rdctg_match,
    ]


def compile_road_color_step(include_3m_exception_below14=True):
    """Builds the ["step", ["zoom"], <below14>, 14, <from14>] expression
    shared by the 9 non-exceptional vt_rdctg-driven road-color layers."""
    is_bridge = ["in", ["get", "vt_code"], ["literal", BRIDGE_VT_CODES]]

    below14 = ["case", is_bridge, _bridge_branch(0.5), _general_branch(include_3m_exception_below14)]
    from14 = ["case", is_bridge, _bridge_branch(0.5), _general_branch(False)]

    return ["step", ["zoom"], below14, 14, from14]


if __name__ == "__main__":
    with open("style/bvmap-dark.json") as f:
        style = json.load(f)
    by_id = {l["id"]: l for l in style["layers"]}

    SHARED_LAYERS = [
        "bvmap-道路中心線色1", "bvmap-道路中心線色2", "bvmap-道路中心線色3", "bvmap-道路中心線色4",
        "bvmap-道路中心線色橋0", "bvmap-道路中心線色橋1", "bvmap-道路中心線色橋2",
        "bvmap-道路中心線色橋3", "bvmap-道路中心線色橋4",
    ]

    generated = compile_road_color_step()
    generated_json = json.dumps(generated, sort_keys=True, ensure_ascii=False)

    mismatches = []
    for lid in SHARED_LAYERS:
        original = by_id[lid]["paint"]["line-color"]
        original_json = json.dumps(original, sort_keys=True, ensure_ascii=False)
        if generated_json != original_json:
            mismatches.append(lid)

    if not mismatches:
        print(
            f"STAGE 1 GATE: PASS — road vt_rdctg-driven line-color reproduced exactly "
            f"across all {len(SHARED_LAYERS)} non-exceptional layers, from named "
            f"building blocks (bridge table / general table / width-ramp fallback), "
            f"NOT from the flat compile_match_expression() compiler (see docs/decisions/0018)."
        )
    else:
        print(f"STAGE 1 GATE: FAIL — mismatches: {mismatches}")
