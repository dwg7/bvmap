"""
Stage 1 generator (reproduction-first): ZL4-10 low-zoom road overview color.

docs/decisions/0022: ZL4-10 hands off to the tier structure exactly at
zoom 11 (ZL4-10 layers: maxzoom 11; tier layers: minzoom 11), but its
road color tables are independently authored — not shareable with
road_color.py's tier tables (different bridge vt_code set, different
values for the same-named vt_rdctg categories, reversed branch nesting).

Building this module surfaced a further fact 0022 hadn't caught: the two
ZL4-10 road layers (国道/高速) don't even share ONE table between
themselves, unlike the tier structure's 色/色橋 pairing ([0018]). Each
gets its own compile function here. The structural difference has a
plausible reason: 道路中心線ZL4-10高速's filter already narrows to
vt_rdctg=="高速自動車国道等" (which always renders motorway-gray anyway),
so its color tables never re-check vt_motorway — the check is only
needed on 道路中心線ZL4-10国道, whose filtered vt_rdctg set could still
contain a motorway-flagged feature under a non-expressway category.
"""
import json

from road_color import _rgba, _with_alpha

BRIDGE_VT_CODES = [2704, 2714, 2724, 2734]  # wider than tier's [2704,2714] (0022)

WIDTH_RAMP = {
    (2721, 2722, 2723): 173,
    (2731, 2732, 2733): 255,  # NOTE: 255 here, vs tier's 200 for the same vt_code bucket
}

MOTORWAY_GRAY = 157

# bvmap-道路中心線ZL4-10国道 (filter: 主要道路/国道/都道府県道/市区町村道等).
KOKUDO_BRIDGE_TABLE = {
    ("国道", "主要道路"): 160,
    "都道府県道": 100,
    "市区町村道等": 100,
    "高速自動車国道等": 157,
    "その他": 100,
    "不明": 100,
}
KOKUDO_BRIDGE_DEFAULT = 100
KOKUDO_GENERAL_TABLE = {
    ("国道", "主要道路"): 160,
    "都道府県道": 226,
    "高速自動車国道等": 157,
}
KOKUDO_GENERAL_DEFAULT = 255

# bvmap-道路中心線ZL4-10高速 (filter: 高速自動車国道等 only). No
# vt_motorway check in either branch (see module docstring).
KOSOKU_BRIDGE_TABLE = {
    "国道": 160,
    "都道府県道": 226,
    "市区町村道等": 100,
    "高速自動車国道等": 157,
    "その他": 100,
    "不明": 100,
}
KOSOKU_BRIDGE_DEFAULT = 100
KOSOKU_GENERAL_TABLE = {
    "国道": 160,
    "都道府県道": 226,
    "市区町村道等": 255,
    "高速自動車国道等": 157,
    "その他": 255,
    "不明": 255,
}
KOSOKU_GENERAL_DEFAULT = 255


def _match_body(table, resolve):
    body = []
    for key, value in table.items():
        body.append(list(key) if isinstance(key, tuple) else key)
        body.append(resolve(value))
    return body


def _width_ramp_match(width_ramp, fallback):
    """Unlike tier road_color.py's width ramp (which is the *last*
    fallback after motorway/rdctg checks), ZL4-10's nesting is reversed
    (docs/decisions/0022): the width ramp is checked FIRST, falling back
    to the motorway/rdctg case/match (`fallback`) only on no match."""
    body = []
    for codes, color in width_ramp.items():
        body.append(list(codes))
        body.append(color)
    return ["match", ["get", "vt_code"], *body, fallback]


def compile_kokudo_color(
    bridge_vt_codes=None, motorway_color=None,
    bridge_table=None, bridge_default=None,
    general_table=None, general_default=None,
    width_ramp=None,
):
    """bvmap-道路中心線ZL4-10国道's line-color. Both branches check
    vt_motorway first (see module docstring)."""
    bridge_vt_codes = bridge_vt_codes or BRIDGE_VT_CODES
    motorway_color = motorway_color or _rgba(MOTORWAY_GRAY)
    bridge_table = bridge_table or {k: _rgba(v) for k, v in KOKUDO_BRIDGE_TABLE.items()}
    bridge_default = bridge_default or _rgba(KOKUDO_BRIDGE_DEFAULT)
    general_table = general_table or {k: _rgba(v) for k, v in KOKUDO_GENERAL_TABLE.items()}
    general_default = general_default or _rgba(KOKUDO_GENERAL_DEFAULT)
    width_ramp = width_ramp or {codes: _rgba(v) for codes, v in WIDTH_RAMP.items()}

    is_bridge = ["in", ["get", "vt_code"], ["literal", list(bridge_vt_codes)]]

    bridge_branch = [
        "case", ["==", ["get", "vt_motorway"], 1], _with_alpha(motorway_color, 0.5),
        ["match", ["get", "vt_rdctg"],
         *_match_body(bridge_table, lambda v: _with_alpha(v, 0.5)),
         _with_alpha(bridge_default, 0.5)],
    ]
    general_branch = [
        "case", ["==", ["get", "vt_motorway"], 1], motorway_color,
        ["match", ["get", "vt_rdctg"], *_match_body(general_table, lambda v: v), general_default],
    ]
    return ["case", is_bridge, bridge_branch, _width_ramp_match(width_ramp, general_branch)]


def compile_kousoku_color(
    bridge_vt_codes=None,
    bridge_table=None, bridge_default=None,
    general_table=None, general_default=None,
    width_ramp=None,
):
    """bvmap-道路中心線ZL4-10高速's line-color. No vt_motorway check in
    either branch (see module docstring)."""
    bridge_vt_codes = bridge_vt_codes or BRIDGE_VT_CODES
    bridge_table = bridge_table or {k: _rgba(v) for k, v in KOSOKU_BRIDGE_TABLE.items()}
    bridge_default = bridge_default or _rgba(KOSOKU_BRIDGE_DEFAULT)
    general_table = general_table or {k: _rgba(v) for k, v in KOSOKU_GENERAL_TABLE.items()}
    general_default = general_default or _rgba(KOSOKU_GENERAL_DEFAULT)
    width_ramp = width_ramp or {codes: _rgba(v) for codes, v in WIDTH_RAMP.items()}

    is_bridge = ["in", ["get", "vt_code"], ["literal", list(bridge_vt_codes)]]

    bridge_branch = ["match", ["get", "vt_rdctg"],
                      *_match_body(bridge_table, lambda v: _with_alpha(v, 0.5)),
                      _with_alpha(bridge_default, 0.5)]
    general_branch = ["match", ["get", "vt_rdctg"], *_match_body(general_table, lambda v: v), general_default]
    return ["case", is_bridge, bridge_branch, _width_ramp_match(width_ramp, general_branch)]


if __name__ == "__main__":
    with open("style/bvmap-dark.json") as f:
        style = json.load(f)
    by_id = {l["id"]: l for l in style["layers"]}

    checks = [
        ("bvmap-道路中心線ZL4-10国道", compile_kokudo_color()),
        ("bvmap-道路中心線ZL4-10高速", compile_kousoku_color()),
    ]

    mismatches = []
    for lid, generated in checks:
        original = by_id[lid]["paint"]["line-color"]
        if json.dumps(generated, sort_keys=True, ensure_ascii=False) != \
           json.dumps(original, sort_keys=True, ensure_ascii=False):
            mismatches.append(lid)

    if not mismatches:
        print(f"STAGE 1 GATE: PASS — ZL4-10's 2 independently-authored road-color "
              f"tables (docs/decisions/0022) both reproduced exactly.")
    else:
        print(f"STAGE 1 GATE: FAIL — mismatches: {mismatches}")
