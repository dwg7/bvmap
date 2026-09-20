"""
Stage 1 generator: loads generator/starlight-input.yaml and turns it into
the same MapLibre expressions/layer objects that category_table.py,
road_color.py, and building_color.py's hardcoded Python constants used to
produce directly. docs/decisions/0020.

This is the code/YAML boundary discussed in the case conference: the
*shape* of each compiler (flat single-property match, priority-ordered
case chain) stays in the dedicated Python modules; this module only
resolves the YAML's *data* (palette references, category tables) and
calls those compilers with it.
"""
import json

import yaml

from category_table import compile_match_expression
from road_color import compile_road_color_step


def load(path="generator/starlight-input.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)


def resolve(token, palette):
    """Looks up a palette token; raises loudly if the YAML references one
    that doesn't exist, rather than silently falling back to the token
    string as a literal color."""
    if token not in palette:
        raise KeyError(f"unknown palette token: {token!r}")
    return palette[token]


def build_flat_match_expression(entry, palette):
    """categories.<name> (engine: flat_match) -> compile_match_expression()."""
    value_type = entry.get("value_type", "color")

    def resolve_value(v):
        if value_type == "font_literal":
            return ["literal", [v]]
        if value_type == "number":
            return v
        return resolve(v, palette)

    categories = {name: group["codes"] for name, group in entry["groups"].items()}
    values = {name: resolve_value(group["value"]) for name, group in entry["groups"].items()}
    values["default"] = resolve_value(entry["default"])
    return compile_match_expression(categories, values)


def build_road_color_expression(entry, palette):
    """priority_chains.road_color (engine: priority_case_chain) ->
    compile_road_color_step(). The case-chain *structure* lives in
    road_color.py; only the parameter values come from the YAML."""
    bridge_table = {k: resolve(v, palette) for k, v in entry["bridge_table"].items()}
    general_table = {k: resolve(v, palette) for k, v in entry["general_table"].items()}

    width_ramp = {}
    for key, value in entry["width_ramp"].items():
        codes = tuple(int(x.strip()) for x in key.split(","))
        width_ramp[codes] = resolve(value, palette)

    return compile_road_color_step(
        bridge_vt_codes=entry["bridge_vt_codes"],
        bridge_table=bridge_table,
        bridge_default=resolve(entry["bridge_default"], palette),
        general_table=general_table,
        motorway_color=resolve(entry["motorway_color"], palette),
        width_ramp=width_ramp,
        width_ramp_default=resolve(entry["width_ramp_default"], palette),
        narrow_exception_color=resolve(entry["narrow_exception_color"], palette),
    )


def build_categories(config):
    """Compiles every categories.* entry into its match expression, keyed
    by name (e.g. "building_fill" -> the compiled ["match", ...])."""
    palette = config["palette"]
    return {
        name: build_flat_match_expression(entry, palette)
        for name, entry in config.get("categories", {}).items()
    }


def build_priority_chains(config):
    palette = config["palette"]
    out = {}
    for name, entry in config.get("priority_chains", {}).items():
        if entry["engine"] == "priority_case_chain" and name == "road_color":
            out[name] = build_road_color_expression(entry, palette)
        else:
            raise NotImplementedError(f"unknown priority_chains engine for {name!r}")
    return out


def build_patches(config, by_id):
    """patches: <id> -> literal-copied layer from its base, with
    color_overrides applied as top-level paint-property assignments only.
    A property absent from the base layer is left untouched (not every
    patch's overrides apply to every base). A property that IS present
    but holds a MapLibre expression (e.g. background's step-based
    background-color) is not something this mechanism can safely
    overwrite with a flat value — that raises loudly instead of silently
    clobbering the expression or silently no-op'ing in a way that looks
    identical to "property doesn't apply here" (docs/decisions/0020's
    review found the old key-existence-only check couldn't tell the two
    apart)."""
    palette = config["palette"]
    out = {}
    for entry in config.get("patches", []):
        lid = entry["id"]
        base_layer = by_id[entry["base"]["layer"]]
        layer = json.loads(json.dumps(base_layer))  # deep copy — never mutate the loaded source

        for prop, token in entry.get("color_overrides", {}).items():
            paint = layer.get("paint", {})
            if prop not in paint:
                continue  # not a property on this layer at all; left as literal
            if isinstance(paint[prop], list):
                raise ValueError(
                    f"patch {lid!r}: color_overrides.{prop} targets a MapLibre expression "
                    f"(e.g. step/case), not a plain literal value — this patch mechanism "
                    f"only overrides literal top-level values; resolve the expression's "
                    f"own structure (e.g. which step of a step-expression) before patching it"
                )
            layer["paint"][prop] = resolve(token, palette)

        out[lid] = layer
    return out


if __name__ == "__main__":
    config = load()

    with open("style/bvmap-dark.json") as f:
        style = json.load(f)
    by_id = {l["id"]: l for l in style["layers"]}

    categories = build_categories(config)
    chains = build_priority_chains(config)
    patches = build_patches(config, by_id)

    checks = [
        ("building_fill", categories["building_fill"], by_id["bvmap-建築物0"]["paint"]["fill-color"]),
        ("building_outline_color", categories["building_outline_color"],
         by_id["bvmap-建築物の外周線0"]["paint"]["line-color"]),
        ("building_outline_width", categories["building_outline_width"],
         by_id["bvmap-建築物の外周線0"]["paint"]["line-width"]),
        ("anno_text_color", categories["anno_text_color"],
         by_id["bvmap-注記角度付き線"]["paint"]["text-color"]),
        ("anno_text_font", categories["anno_text_font"],
         by_id["bvmap-注記角度付き線"]["layout"]["text-font"]),
        ("road_color", chains["road_color"], by_id["bvmap-道路中心線色1"]["paint"]["line-color"]),
        ("patch bvmap-行政区画", patches["bvmap-行政区画"], by_id["bvmap-行政区画"]),
        ("patch bvmap-水域", patches["bvmap-水域"], by_id["bvmap-水域"]),
    ]

    mismatches = [name for name, generated, original in checks
                  if json.dumps(generated, sort_keys=True, ensure_ascii=False)
                  != json.dumps(original, sort_keys=True, ensure_ascii=False)]

    if not mismatches:
        print(f"STAGE 1 GATE: PASS — starlight-input.yaml reproduces all {len(checks)} "
              f"checked expressions/layers exactly, driven entirely from YAML data.")
    else:
        print(f"STAGE 1 GATE: FAIL — mismatches: {mismatches}")
