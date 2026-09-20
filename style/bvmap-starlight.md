# bvmap-starlight

`bvmap-dark.json`(stars.optgeo.org配信版)を基点に、配色をStarlight(低彩度・明るめ・銀灰色寄り)の方向へ磨き上げるスタイル。命名の経緯は[docs/decisions/0003](../docs/decisions/0003-bvmap-starlight-naming.md)を参照。

## 現在の状態

`generator/assemble.py`が`generator/starlight-input.yaml`から生成する(手動編集しない、[docs/decisions/0029](../docs/decisions/0029-assemble-writes-starlight-json.md))。2026-09-20時点で123層中108層が生成/YAMLパッチ駆動、55層が`bvmap-dark.json`と内容差分あり(意図した配色変更、構造は同一)。設計の詳細は[docs/bvmap-starlight-cartographic-design.md](../docs/bvmap-starlight-cartographic-design.md)を参照。

## 経緯

当初このファイルは、縦書き注記の棒音符(「ー」)問題([UNopenGIS/7#1012](https://github.com/UNopenGIS/7/issues/1012))への回避策([maplibre/maplibre-gl-js#5259 (comment)](https://github.com/maplibre/maplibre-gl-js/issues/5259#issuecomment-3510571607)、`text-font: ["Choonpu"]`への置換)を実装する場として使っていた。実機検証の結果、この回避策はMapLibre GL JSの現在の描画パイプラインでは機能しないことが判明したため撤去した(経緯: [docs/decisions/0004](../docs/decisions/0004-vertical-choonpu-workaround-does-not-work.md))。

本リポジトリの目標は[docs/decisions/0005](../docs/decisions/0005-goal-change-master-repo-and-starlight-polish.md)の通り変更されており、`bvmap-starlight`は現在「配色磨き上げ」専用のファイルとして再出発している。
