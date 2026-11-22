"""Step 1 of docs/decisions/0043: reproduce the dorayaki session's mechanical
night version (every rgb()/rgba() in style/bvmap-starlight.json, lightness
reversed). Output is a *prototype*, written outside style/ and gitignored.

    python3 experiments/nightsky/mechanical.py   (from the repo root)
"""
import json, sys, os
sys.path.insert(0, "generator")
from night_transform import transform_tree

with open("style/bvmap-starlight.json") as f:
    style = json.load(f)
stats = {}
out = transform_tree(style, stats)
out["name"] = "bvmap-nightsky (mechanical prototype)"
os.makedirs("experiments/nightsky/out", exist_ok=True)
with open("experiments/nightsky/out/mechanical.json", "w") as f:
    json.dump(out, f, ensure_ascii=False, indent=1)
print(f"{len(stats)} distinct color strings mapped")
