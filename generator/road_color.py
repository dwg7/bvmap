"""
Stage 1 generator (reproduction-first): road vt_rdctg-driven line-color.

Investigates whether docs/decisions/0010's road-color table is reproducible
by the same flat "vt_code category -> match" compiler as
generator/category_table.py (Anno text-color/text-font) and building
fill/outline. Finding: it is NOT the same shape — see docs/decisions/0018.

compile_road_color_step() takes every gray value as an explicit rgba-string
parameter (defaulting to the module-level constants below, which are the
values actually observed in bvmap-dark.json) so generator/load_input.py can
drive it from starlight-input.yaml's palette instead — see docs/decisions/0020.

This module builds the shared line-color expression (identical across
bvmap-道路中心線色{1,2,3,4} and bvmap-道路中心線色橋{0,1,2,3,4} — 9 of the
10 vt_rdctg-driven layers; tier 0's non-bridge 色0 layer carries one
additional zoom>=14 branch, already handled verbatim by
generator/tier_template.py's per-tier template extraction and out of
scope here).
"""
import json
import re

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

MOTORWAY_GRAY = 157

# The fallback width ramp for roads that match neither vt_motorway nor
# any of the 3 general-case vt_rdctg keys above.
WIDTH_RAMP = {
    (2721, 2722, 2723): 173,
    (2731, 2732, 2733): 200,
}
WIDTH_RAMP_DEFAULT = 255

# zoom<14 only: roads that fall through vt_rdctg AND have vt_rnkwidth
# "3m-5.5m未満" get this gray before ever consulting the width ramp above —
# it happens to equal the width ramp's [2721,2722,2723] bucket (docs/
# decisions/0018), but is a separate branch, not derived from it.
NARROW_3M_5M_EXCEPTION_GRAY = 173


def _rgba(gray, alpha=1):
    return f"rgba({gray},{gray},{gray},{alpha})"


def _with_alpha(rgba, alpha):
    """Rewrites an rgba(...) string's alpha channel — used to derive the
    bridge branch's alpha=0.5 variant from a palette value that's
    normally alpha=1."""
    return re.sub(r",[^,]+\)$", f",{alpha})", rgba)


def _bridge_branch(alpha, bridge_table, bridge_default, motorway_color):
    body = []
    for name, color in bridge_table.items():
        body.append(name)
        body.append(_with_alpha(color, alpha))
    rdctg_match = ["match", ["get", "vt_rdctg"], *body, _with_alpha(bridge_default, alpha)]
    return [
        "case",
        ["==", ["get", "vt_motorway"], 1],
        _with_alpha(motorway_color, alpha),
        rdctg_match,
    ]


def _width_ramp_match(width_ramp, width_ramp_default):
    body = []
    for codes, color in width_ramp.items():
        body.append(list(codes))
        body.append(color)
    return ["match", ["get", "vt_code"], *body, width_ramp_default]


def _general_branch(include_3m_exception, general_table, motorway_color,
                     width_ramp, width_ramp_default, narrow_exception_color):
    body = []
    for name, color in general_table.items():
        body.append(name)
        body.append(color)
    fallback = _width_ramp_match(width_ramp, width_ramp_default)
    if include_3m_exception:
        fallback = [
            "case",
            ["==", ["get", "vt_rnkwidth"], "3m-5.5m未満"],
            narrow_exception_color,
            fallback,
        ]
    rdctg_match = ["match", ["get", "vt_rdctg"], *body, fallback]
    return [
        "case",
        ["==", ["get", "vt_motorway"], 1],
        motorway_color,
        rdctg_match,
    ]


def compile_road_color_step(
    bridge_vt_codes=None,
    bridge_table=None,
    bridge_default=None,
    general_table=None,
    motorway_color=None,
    width_ramp=None,
    width_ramp_default=None,
    narrow_exception_color=None,
    include_3m_exception_below14=True,
):
    """Builds the ["step", ["zoom"], <below14>, 14, <from14>] expression
    shared by the 9 non-exceptional vt_rdctg-driven road-color layers.
    Every color parameter is an rgba(...) string at alpha=1; the bridge
    branch derives its alpha=0.5 variant internally. Defaults reproduce
    bvmap-dark.json exactly (docs/decisions/0018); callers (e.g.
    generator/load_input.py) pass resolved palette values to repoint the
    same structure at different colors."""
    bridge_vt_codes = bridge_vt_codes or BRIDGE_VT_CODES
    bridge_table = bridge_table or {k: _rgba(v) for k, v in BRIDGE_RDCTG_TABLE.items()}
    bridge_default = bridge_default or _rgba(BRIDGE_RDCTG_DEFAULT)
    general_table = general_table or {k: _rgba(v) for k, v in GENERAL_RDCTG_TABLE.items()}
    motorway_color = motorway_color or _rgba(MOTORWAY_GRAY)
    width_ramp = width_ramp or {codes: _rgba(v) for codes, v in WIDTH_RAMP.items()}
    width_ramp_default = width_ramp_default or _rgba(WIDTH_RAMP_DEFAULT)
    narrow_exception_color = narrow_exception_color or _rgba(NARROW_3M_5M_EXCEPTION_GRAY)

    is_bridge = ["in", ["get", "vt_code"], ["literal", list(bridge_vt_codes)]]

    below14 = [
        "case", is_bridge,
        _bridge_branch(0.5, bridge_table, bridge_default, motorway_color),
        _general_branch(include_3m_exception_below14, general_table, motorway_color,
                         width_ramp, width_ramp_default, narrow_exception_color),
    ]
    from14 = [
        "case", is_bridge,
        _bridge_branch(0.5, bridge_table, bridge_default, motorway_color),
        _general_branch(False, general_table, motorway_color,
                         width_ramp, width_ramp_default, narrow_exception_color),
    ]

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
