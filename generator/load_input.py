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
from zl410_road_color import compile_kokudo_color, compile_kousoku_color


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
    return compile_match_expression(categories, values, property=entry.get("property", "vt_code"))


def _parse_vt_code_table(table, palette):
    """{"code1,code2,...": token} -> {(code1,code2,...): resolved_value},
    for the vt_code-keyed width ramps shared by road_color and
    zl410_road_color."""
    out = {}
    for key, value in table.items():
        codes = tuple(int(x.strip()) for x in key.split(","))
        out[codes] = resolve(value, palette)
    return out


def _parse_rdctg_table(table, palette):
    """{"key" or "key1,key2": token} -> {key: resolved_value} or
    {(key1,key2): resolved_value} for a grouped vt_rdctg match key (e.g.
    ZL4-10 国道's ["国道","主要道路"] grouping, docs/decisions/0024)."""
    out = {}
    for key, value in table.items():
        parts = tuple(p.strip() for p in key.split(","))
        out[parts[0] if len(parts) == 1 else parts] = resolve(value, palette)
    return out


def build_road_color_expression(entry, palette):
    """priority_chains.road_color (engine: priority_case_chain) ->
    compile_road_color_step(). The case-chain *structure* lives in
    road_color.py; only the parameter values come from the YAML."""
    return compile_road_color_step(
        bridge_vt_codes=entry["bridge_vt_codes"],
        bridge_table=_parse_rdctg_table(entry["bridge_table"], palette),
        bridge_default=resolve(entry["bridge_default"], palette),
        general_table=_parse_rdctg_table(entry["general_table"], palette),
        motorway_color=resolve(entry["motorway_color"], palette),
        width_ramp=_parse_vt_code_table(entry["width_ramp"], palette),
        width_ramp_default=resolve(entry["width_ramp_default"], palette),
        narrow_exception_color=resolve(entry["narrow_exception_color"], palette),
    )


def build_zl410_kokudo_expression(entry, palette):
    """priority_chains.zl410_kokudo_road_color ->
    zl410_road_color.compile_kokudo_color() (docs/decisions/0024)."""
    return compile_kokudo_color(
        bridge_vt_codes=entry["bridge_vt_codes"],
        motorway_color=resolve(entry["motorway_color"], palette),
        bridge_table=_parse_rdctg_table(entry["bridge_table"], palette),
        bridge_default=resolve(entry["bridge_default"], palette),
        general_table=_parse_rdctg_table(entry["general_table"], palette),
        general_default=resolve(entry["general_default"], palette),
        width_ramp=_parse_vt_code_table(entry["width_ramp"], palette),
    )


def build_zl410_kosoku_expression(entry, palette):
    """priority_chains.zl410_kosoku_road_color ->
    zl410_road_color.compile_kousoku_color() (docs/decisions/0024)."""
    return compile_kousoku_color(
        bridge_vt_codes=entry["bridge_vt_codes"],
        bridge_table=_parse_rdctg_table(entry["bridge_table"], palette),
        bridge_default=resolve(entry["bridge_default"], palette),
        general_table=_parse_rdctg_table(entry["general_table"], palette),
        general_default=resolve(entry["general_default"], palette),
        width_ramp=_parse_vt_code_table(entry["width_ramp"], palette),
    )


def build_categories(config):
    """Compiles every categories.* entry into its match expression, keyed
    by name (e.g. "building_fill" -> the compiled ["match", ...])."""
    palette = config["palette"]
    return {
        name: build_flat_match_expression(entry, palette)
        for name, entry in config.get("categories", {}).items()
    }


PRIORITY_CHAIN_BUILDERS = {
    "road_color": build_road_color_expression,
    "zl410_kokudo_road_color": build_zl410_kokudo_expression,
    "zl410_kosoku_road_color": build_zl410_kosoku_expression,
}


def build_priority_chains(config):
    palette = config["palette"]
    out = {}
    for name, entry in config.get("priority_chains", {}).items():
        if entry["engine"] != "priority_case_chain":
            raise NotImplementedError(f"unknown priority_chains engine for {name!r}: {entry['engine']!r}")
        if name not in PRIORITY_CHAIN_BUILDERS:
            raise NotImplementedError(f"no builder registered for priority_chains.{name!r}")
        out[name] = PRIORITY_CHAIN_BUILDERS[name](entry, palette)
    return out


def resolve_from_ref(ref, categories, chains):
    """Resolves a {from: "categories.<name>"} or {from: "priority_chains.<name>"}
    reference (used in layers.*.paint entries) to the already-compiled
    expression it points at."""
    path = ref["from"]
    section, name = path.split(".", 1)
    if section == "categories":
        return categories[name]
    if section == "priority_chains":
        return chains[name]
    raise ValueError(f"unknown layers.*.paint reference: {path!r}")


def build_standalone_layers(config, by_id, categories, chains):
    """layers: entries with engine: standalone — a single layer outside
    the tier structure, addressed by id, whose paint properties are
    replaced with already-compiled categories/priority_chains
    expressions (docs/decisions/0022). Unlike engine: tier_template
    (still wired by hand in assemble.build_tier_block(), not read from
    this section generically — a known inconsistency, not yet worth the
    risk of refactoring already-verified tier wiring to fix), this
    engine IS driven directly from the YAML's layers: list."""
    out = {}
    for entry in config.get("layers", []):
        if entry.get("engine") != "standalone":
            continue
        lid = entry["id"]
        layer = json.loads(json.dumps(by_id[lid]))  # deep copy — never mutate the loaded source
        for prop, ref in entry.get("paint", {}).items():
            layer["paint"][prop] = resolve_from_ref(ref, categories, chains)
        out[lid] = layer
    return out


def apply_step_outputs(expr, tokens, palette):
    """Overrides a ["step", input, out0, stop1, out1, stop2, out2, ...]
    expression's literal outputs in place, keeping its own structure
    (input, stop positions) untouched — the same "structure stays in
    code/expression, values move to YAML" split used everywhere else in
    this generator (docs/decisions/0018/0020), extended to step
    expressions instead of just plain properties."""
    if not (isinstance(expr, list) and len(expr) >= 3 and expr[0] == "step"):
        raise ValueError(f"step_outputs given but base value isn't a step expression: {expr!r}")
    output_indices = list(range(2, len(expr), 2))
    if len(tokens) != len(output_indices):
        raise ValueError(
            f"step_outputs has {len(tokens)} values but the expression has "
            f"{len(output_indices)} outputs"
        )
    new_expr = list(expr)
    for idx, token in zip(output_indices, tokens):
        new_expr[idx] = resolve(token, palette)
    return new_expr


def build_patches(config, by_id):
    """patches: <id> -> literal-copied layer from its base, with
    color_overrides applied as top-level paint-property assignments only.
    A property absent from the base layer is left untouched (not every
    patch's overrides apply to every base). An override may be a plain
    palette token (property holds a literal value) or {step_outputs: [...]}
    (property holds a ["step", ...] expression — see apply_step_outputs()).
    Any other case where the property holds a MapLibre expression this
    mechanism doesn't know how to patch (e.g. a case/match/interpolate)
    raises loudly instead of silently clobbering it or silently no-op'ing
    in a way indistinguishable from "property doesn't apply here" (docs/
    decisions/0020's review found the old key-existence-only check
    couldn't tell the two apart)."""
    palette = config["palette"]
    out = {}
    patched_ids = set()  # ids where an override actually changed something,
                          # as opposed to a patch that's purely structural
                          # annotation (base copy + literal_reason, no
                          # color_overrides yet) — see assemble.py's
                          # literal_count, which needs this distinction.
    for entry in config.get("patches", []):
        lid = entry["id"]
        base_layer = by_id[entry["base"]["layer"]]
        layer = json.loads(json.dumps(base_layer))  # deep copy — never mutate the loaded source

        for prop, override in entry.get("color_overrides", {}).items():
            paint = layer.get("paint", {})
            if prop not in paint:
                continue  # not a property on this layer at all; left as literal
            if isinstance(override, dict) and "step_outputs" in override:
                layer["paint"][prop] = apply_step_outputs(paint[prop], override["step_outputs"], palette)
                patched_ids.add(lid)
            elif isinstance(paint[prop], list):
                raise ValueError(
                    f"patch {lid!r}: color_overrides.{prop} targets a MapLibre expression "
                    f"(e.g. step/case), not a plain literal value — this patch mechanism "
                    f"only overrides literal top-level values (or a step expression's "
                    f"outputs via {{step_outputs: [...]}}); resolve the expression's own "
                    f"structure before patching anything else"
                )
            else:
                layer["paint"][prop] = resolve(override, palette)
                patched_ids.add(lid)

        out[lid] = layer
    return out, patched_ids


if __name__ == "__main__":
    config = load()

    with open("style/bvmap-dark.json") as f:
        style = json.load(f)
    by_id = {l["id"]: l for l in style["layers"]}

    categories = build_categories(config)
    chains = build_priority_chains(config)
    patches, _patched_ids = build_patches(config, by_id)
    standalone = build_standalone_layers(config, by_id, categories, chains)

    checks = [
        ("building_fill", categories["building_fill"], by_id["bvmap-建築物0"]["paint"]["fill-color"]),
        ("building_outline_color", categories["building_outline_color"],
         by_id["bvmap-建築物の外周線0"]["paint"]["line-color"]),
        ("building_outline_width", categories["building_outline_width"],
         by_id["bvmap-建築物の外周線0"]["paint"]["line-width"]),
        ("structure_fill", categories["structure_fill"], by_id["bvmap-構造物面"]["paint"]["fill-color"]),
        ("structure_line", categories["structure_line"], by_id["bvmap-構造物線"]["paint"]["line-color"]),
        ("anno_text_color", categories["anno_text_color"],
         by_id["bvmap-注記角度付き線"]["paint"]["text-color"]),
        ("anno_text_font", categories["anno_text_font"],
         by_id["bvmap-注記角度付き線"]["layout"]["text-font"]),
        ("road_color", chains["road_color"], by_id["bvmap-道路中心線色1"]["paint"]["line-color"]),
        ("patch bvmap-行政区画", patches["bvmap-行政区画"], by_id["bvmap-行政区画"]),
        ("patch bvmap-水域", patches["bvmap-水域"], by_id["bvmap-水域"]),
        ("patch bvmap-構造物面の外周線", patches["bvmap-構造物面の外周線"], by_id["bvmap-構造物面の外周線"]),
        ("patch bvmap-等高線", patches["bvmap-等高線"], by_id["bvmap-等高線"]),
        ("patch bvmap-等深線", patches["bvmap-等深線"], by_id["bvmap-等深線"]),
        ("patch bvmap-等高線数値部", patches["bvmap-等高線数値部"], by_id["bvmap-等高線数値部"]),
        ("patch bvmap-等深線数値部", patches["bvmap-等深線数値部"], by_id["bvmap-等深線数値部"]),
        ("standalone bvmap-構造物面", standalone["bvmap-構造物面"], by_id["bvmap-構造物面"]),
        ("standalone bvmap-構造物線", standalone["bvmap-構造物線"], by_id["bvmap-構造物線"]),
        ("zl410_rail_color", categories["zl410_rail_color"],
         by_id["bvmap-鉄道中心線ZL4-10"]["paint"]["line-color"]),
        ("zl410_kokudo_road_color", chains["zl410_kokudo_road_color"],
         by_id["bvmap-道路中心線ZL4-10国道"]["paint"]["line-color"]),
        ("zl410_kosoku_road_color", chains["zl410_kosoku_road_color"],
         by_id["bvmap-道路中心線ZL4-10高速"]["paint"]["line-color"]),
        ("standalone bvmap-道路中心線ZL4-10国道", standalone["bvmap-道路中心線ZL4-10国道"],
         by_id["bvmap-道路中心線ZL4-10国道"]),
        ("standalone bvmap-道路中心線ZL4-10高速", standalone["bvmap-道路中心線ZL4-10高速"],
         by_id["bvmap-道路中心線ZL4-10高速"]),
        ("standalone bvmap-鉄道中心線ZL4-10", standalone["bvmap-鉄道中心線ZL4-10"],
         by_id["bvmap-鉄道中心線ZL4-10"]),
    ]

    mismatches = [name for name, generated, original in checks
                  if json.dumps(generated, sort_keys=True, ensure_ascii=False)
                  != json.dumps(original, sort_keys=True, ensure_ascii=False)]

    if not mismatches:
        print(f"STAGE 1 GATE: PASS — starlight-input.yaml reproduces all {len(checks)} "
              f"checked expressions/layers exactly, driven entirely from YAML data.")
    else:
        print(f"STAGE 1 GATE: FAIL — mismatches: {mismatches}")
