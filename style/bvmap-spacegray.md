# bvmap-spacegray

`bvmap-dark.json`(stars.optgeo.org配信版、無加工)から派生した別スタイル。縦書き注記の棒音符(「ー」)が横倒しに見える問題([UNopenGIS/7#1012](https://github.com/UNopenGIS/7/issues/1012))に対応するため、縦書きレイヤー3件の`text-font`を`["Choonpu"]`に置き換えている。

## bvmap-darkとの違い

- 対象レイヤー: `bvmap-注記シンボルなし縦ソート順100以上`、`bvmap-注記角度付き線`、`bvmap-注記シンボルなし縦ソート順100未満`(いずれも`text-writing-mode: ["vertical"]`)
- 上記3レイヤーの`text-font`を、元の`match`式(`vt_code`により`NotoSerifJP-SemiBold`/`NotoSansJP-Regular`を出し分け)から`["Choonpu"]`単一指定に完全置換した
- 結果として、この3レイヤーでは主要地名(セリフ体太字)とその他(ゴシック体通常)の書体差が失われる。「ー」問題の解消と引き換えのトレードオフとして採用している

## 前提条件(必須): ページ側でのCSS設定

このスタイルは**ページ側に以下の`@font-face`宣言があることを前提**とする。無いままでは`Choonpu`フォントスタックがPBF・ローカルいずれでも解決できず、対象3レイヤーの描画結果は保証されない(フォールバックは検証済みではない)。

```css
@font-face {
  font-family: "Choonpu";
  src: local("Hiragino Mincho ProN"), local("Noto Serif CJK JP"), local("MS Mincho");
  font-feature-settings: "vert";
}
```

出典: [maplibre/maplibre-gl-js#5259 (comment)](https://github.com/maplibre/maplibre-gl-js/issues/5259#issuecomment-3510571607)

## 技術的な背景

- `bvmap-spacegray.json`はルートに`glyphs`(GSIのPBFグリフサーバー)を持つため、`text-font`配列はMapLibreのスタイル仕様上「複数フォント名を`,`で結合した単一フォントスタック名」として解釈される([style-spec #1068](https://github.com/maplibre/maplibre-style-spec/issues/1068))。`["Choonpu", "NotoSerifJP-SemiBold"]`のような並記は「Choonpuがダメなら次を試す」というカスケードにはならない。そのため既存フォントへのグレースフルフォールバックは採用せず、完全置換とした
- ローカルフォント解決には MapLibre GL JS **5.11.0以上**が必要([PR #4564](https://github.com/maplibre/maplibre-gl-js/pull/4564))
- `Choonpu`は「長音符」のローマ字表記。issue #1012の「棒音符」と同じ対象を指す
