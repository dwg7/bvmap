# 0002: bvmap-spacegray — 縦書き棒音符(ー)ワークアラウンド

## 問題

`bvmap-dark`スタイルで、縦書きの注記に棒音符(長音符、「ー」)が含まれる場合、横倒しに見える([UNopenGIS/7#1012](https://github.com/UNopenGIS/7/issues/1012))。原因はMapLibre GL JS本体がOpenTypeの`vert`/`vrtr`機能をまだネイティブサポートしていないこと(2026-09時点でPR [#8399](https://github.com/maplibre/maplibre-gl-js/pull/8399)/[#8488](https://github.com/maplibre/maplibre-gl-js/pull/8488)/[#8489](https://github.com/maplibre/maplibre-gl-js/pull/8489)がopen)。

## 回避策の出典

[maplibre/maplibre-gl-js#5259 (comment)](https://github.com/maplibre/maplibre-gl-js/issues/5259#issuecomment-3510571607)(1ec5氏、2025-11-10)。CSSの`@font-face`で`font-feature-settings: "vert"`を持つローカルフォントを宣言し、対象レイヤーの`text-font`をそのフォント名に切り替える方式。GL JS 5.11.0以上が前提([PR #4564](https://github.com/maplibre/maplibre-gl-js/pull/4564)で追加された、ローカルフォントレンダリング機能に依存)。

## 検討した実装方式と決定

1. **既存フォントへのカスケードフォールバック(`text-font: ["Choonpu", "NotoSerifJP-SemiBold"]`)は不採用**。`bvmap-dark.json`はルートに`glyphs`を持つため、MapLibreのstyle-spec仕様上、`text-font`配列は「,」で結合された単一フォントスタック名として解釈される([style-spec #1068](https://github.com/maplibre/maplibre-style-spec/issues/1068)、`maplibre-gl-js`のテストフィクスチャでも裏付け)。カスケード的なフォールバックにはならないため、この方式は成立しない
2. **filterによるレイヤー分岐(「ー」を含む地物だけ新レイヤーへ)は不採用**。実装コストに対して、今回は影響範囲をレイヤー全体に許容する判断とした
3. **採用**: 対象3レイヤー(`bvmap-注記シンボルなし縦ソート順100以上`、`bvmap-注記角度付き線`、`bvmap-注記シンボルなし縦ソート順100未満`)の`text-font`を`["Choonpu"]`に完全置換。元の`match`式が持っていた主要地名(`NotoSerifJP-SemiBold`)とその他(`NotoSansJP-Regular`)の書体差は、この3レイヤーに限り失われる

## なぜ`bvmap-dark`を直接書き換えず、`bvmap-spacegray`という別名にしたか

「stars.optgeo.orgに置いてある現行`bvmap-dark.json`の品質を下げないこと」を大前提とする。上記の完全置換はフォント差の喪失というトレードオフを伴い、かつページ側に`@font-face` CSSの追加設定を必須で要求する(未設定環境での挙動は保証されない、[style/bvmap-spacegray.md](../../style/bvmap-spacegray.md)参照)。これは`bvmap-dark`と無条件に互換な変更ではないため、`style/bvmap-dark.json`は無加工のまま保持し、パッチ適用版を`style/bvmap-spacegray.json`という独立した名前の次世代スタイルとして分離した。

`stars.optgeo.org`側で`bvmap-spacegray`をどう配信するか(新規style idとして追加するか等)は、運用影響が大きいため人(藤村さん)の判断に委ねる。
