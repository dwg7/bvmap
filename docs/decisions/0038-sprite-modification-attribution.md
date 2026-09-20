# 0038: スプライト改変の出典表示

`stars`セッションからの指摘(2026-09-20、hfu/stars側のPRレビュー観点)を受けて対応した。

## 背景

国土地理院コンテンツ利用規約2.0(CC BY 4.0相当)は改変を認めるが、出典の明示に加えて
**改変した旨の表示**を求める。[0036](0036-sprite-grayscale-raster-exception.md)で
GSIのスプライト(119アイコン)をグレースケール化しており、この表示義務が生じていた。
`hfu/stars`側は`assets/sprites.json`のマニフェストに改変者(dwg7/bvmap)を記録済みだが、
スタイル側(`style/bvmap-starlight.json`)にも同趣旨の記載が必要という指摘だった。

## 変更

`starlight-input.yaml`の`hosting:`セクションに`source_attribution`を追加し、
`assemble.py`が`sources.bvmap.attribution`を上書きするようにした:

```
国土地理院最適化ベクトルタイル。スプライトアイコンは国土地理院最適化ベクトルタイルの
原本を改変(グレースケール化)して使用。改変者: dwg7/bvmap。国土地理院コンテンツ利用規約
に基づく。
```

タイル自体は無改変のため出典のみ、スプライトアイコンは改変した旨を明記——両者を区別して
1つの文字列にまとめた(MapLibreの style spec にはsprite専用のattributionフィールドが無く、
実際にAttributionControlへ表示されるのは`sources.*.attribution`のため)。

`output_style["sources"]`は`bvmap-dark.json`から読み込んだ辞書への参照(浅いコピー)なので、
そのまま書き換えると読み込み元を汚染する([0019](0019-stage1-final-assembly.md)で踏んだ
罠と同型)。ディープコピーしてから上書きするようにした。

## 検証

`generator/assemble.py`・`generator/load_input.py`とも自己診断PASS。
`style/bvmap-dark.json`の`sources.bvmap.attribution`が無改変のまま
(`"国土地理院最適化ベクトルタイル"`)であることを確認済み。
