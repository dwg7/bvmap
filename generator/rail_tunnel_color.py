"""
Stage 1 generator (reproduction-first): rail tunnel main-body line-color.

docs/decisions/0025: bvmap-鉄道中心線地下トンネルククリ(casing)/本体(main)
share almost everything (line-opacity, and a vt_rtcode width-factor
match table byte-identical to tier's 鉄道中心線0 — see 0025) except
line-color and a small additive width constant (out of scope here,
color only).

ククリ's line-color is a plain 2-branch match — reproduced directly by
category_table.compile_match_expression() (see starlight-input.yaml's
categories.rail_tunnel_kukuri_color), no new code needed.

本体's line-color does NOT reduce to that flat shape: its non-subway
branch is itself a nested case on vt_sngldbl, not a plain value. This
module is that one small addition.
"""
import json


def compile_main_color(subway_color=None, station_color=None, default_color=None):
    subway_color = subway_color or "rgba(113,113,113,1)"
    station_color = station_color or "rgb(173,173,173)"
    default_color = default_color or "rgb(100,100,100)"
    return [
        "match", ["get", "vt_rtcode"],
        "地下鉄", subway_color,
        ["case", ["==", ["get", "vt_sngldbl"], "駅部分"], station_color, default_color],
    ]


if __name__ == "__main__":
    with open("style/bvmap-dark.json") as f:
        style = json.load(f)
    by_id = {l["id"]: l for l in style["layers"]}

    generated = compile_main_color()
    original = by_id["bvmap-鉄道中心線地下トンネル"]["paint"]["line-color"]

    if json.dumps(generated, sort_keys=True, ensure_ascii=False) == \
       json.dumps(original, sort_keys=True, ensure_ascii=False):
        print("STAGE 1 GATE: PASS — rail tunnel main-body line-color reproduced exactly "
              "(docs/decisions/0025), NOT a flat match — nested case on vt_sngldbl.")
    else:
        print("STAGE 1 GATE: FAIL")
