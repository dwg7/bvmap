# 0004: 縦書き棒音符(ー)ワークアラウンドは機能しない(調査終了)

## 結論

[0002](0002-bvmap-starlight-vertical-choonpu.md)で実装した`@font-face` + `text-font: ["Choonpu"]`という回避策([maplibre/maplibre-gl-js#5259 (comment)](https://github.com/maplibre/maplibre-gl-js/issues/5259#issuecomment-3510571607)に基づく)は、**MapLibre GL JSの現在のローカルグリフ描画パイプラインとは構造的に噛み合わず、機能しない**ことが実機検証で確認された。本リポジトリではこの方向性での対応を終了する。

## 検証結果(2026-09-19、3ブラウザエンジン)

| ブラウザ | `Choonpu`の`FontFace`状態 | 「ー」の見た目 |
|---|---|---|
| Chromium系サンドボックス(Claude Browser pane) | `error`(`local()`解決失敗、`NetworkError`) | 未修正 |
| Brave | 同上。コンソールに`Failed to load font "Choonpu,sans-serif": A network error occurred.`([util.ts:617](https://github.com/maplibre/maplibre-gl-js/blob/main/src/util/util.ts)相当)。Braveは`src:local()`のフィンガープリンティング対策を他のChromium系より積極的に実施している([brave/brave-browser#23432](https://github.com/brave/brave-browser/issues/23432)) | 未修正 |
| Safari(実機) | **`loaded`**(フォント自体は正常にロード成功。他の文字の書体が実際に変化することも目視確認) | **それでも未修正** |

Safariでフォントのロードに成功したにもかかわらず「ー」の字形が変わらなかったことが、根本原因の特定につながった。

## 根本原因

`maplibre-gl-js`の`src/render/glyph_manager.ts`(`_createTinySDF()`)を確認したところ、ローカルフォント描画は[`@mapbox/tiny-sdf`](https://github.com/mapbox/tiny-sdf)を介したCanvas 2Dの`fillText()`ベースで、1文字ずつ個別のオフスクリーンcanvasに描画している。`ctx.font`には`fontStyle fontWeight fontSize fontFamily`のみが渡され、**`font-feature-settings`をCanvas 2Dの描画に伝える経路がそもそも存在しない**。

これは既知のブラウザ実装上の制約と一致する: `@font-face`ディスクリプタとしてのみ書かれた`font-feature-settings`は、対応する実際のDOM要素(セレクタ)側にも同じ指定がない限り、多くのブラウザで反映されない([2012年のw3c www-fontメーリングリストでの議論](https://lists.w3.org/Archives/Public/www-font/2012OctDec/0004.html))。Canvas 2Dには描画対象となるDOM要素が存在しないため、この経路そのものが成立しない。

つまり:
- Chrome/Brave: `Choonpu`のロード自体が`local()`制限で失敗 → 汎用フォントへフォールバック → vertが効くはずがない
- Safari: `Choonpu`のロードは成功 → しかし`fillText`に`font-feature-settings`を渡す手段がないため、フォントは変わっても「ー」の字形(vert置換)自体は変わらない

## 正しい実装がどうあるべきか(参考、本リポジトリのスコープ外)

MapLibre GL JS本体でのネイティブ対応(PR [#8399](https://github.com/maplibre/maplibre-gl-js/pull/8399) / [#8488](https://github.com/maplibre/maplibre-gl-js/pull/8488) / [#8489](https://github.com/maplibre/maplibre-gl-js/pull/8489)、2026-09時点でいずれもopen、未マージ)を調査したところ、以下の設計であることが分かった:

1. 同じ文字を「vertオフ」「vertオン」の両方でラスタライズし、実際に異なる字形が得られた場合のみ採用する(ビットマップ比較による実証的な判定。ブラウザに「効いたか」を問い合わせる代わりに、結果を見て判定する)
2. グリフキャッシュ/アトラスのキーに「variant」次元を追加する内部的なデータ構造変更が前提([#8488](https://github.com/maplibre/maplibre-gl-js/pull/8488))
3. **`glyphs`(PBFサーバー方式)ではなく、新しい`font-faces`ルートプロパティ(実フォントファイルをスタイルに直接宣言する方式)を使うフォントにのみ適用される**

3点目が特に重要: 仮にこれらのPRがマージされても、`bvmap-dark`/`bvmap-starlight`が現在採用している`glyphs`(GSIのPBFグリフサーバー)+`text-font`という構成のままでは対象にならない。`font-faces`方式への移行が前提となる、userland(style.json単体)では完結しない話である。

## 今後の扱い

- 本リポジトリでは、縦書き棒音符問題への対応を**目標から外す**([0005](0005-goal-change-master-repo-and-starlight-polish.md)参照)
- MapLibre GL JS本体のネイティブ対応がマージされ、かつ`font-faces`方式への移行が現実的になった時点で、改めて着手を検討する
- 1ec5氏のコメント(元issue)へのフォローアップは、今回の技術的知見が他の利用者の助けになる可能性があるため、藤村さんの判断で別途検討
