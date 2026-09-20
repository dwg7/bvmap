# 0036: スプライトのグレースケール化、`hfu/stars`へのラスタ例外提案

[0014](0014-sprite-decisions.md)で「今回は着手しない」と保留した独自スプライト作成のうち、
最も軽い選択肢(既存GSIラスタの再配色、絵文字代替でもSDF再構築でもない)を実装した。
保留条件だった「フォント・色の方針が固まってから」は、[0030](0030-starlight-first-color-pass.md)/[0033](0033-new-token-policy.md)で満たされている。

## 実データで判明した食い違い

`hfu/stars`の`assets/sprites.json`を確認したところ、明記された方針は
「Sprites starsは`/sprite/{id}`で自前配信。Martinが起動時にSVGソースからスプライトシートを
構築する——誰かのレンダリング済みPNGをミラーするのではなく、アイコンのSVGソースをコピーする」
というものだった(フォントの自前ホスティングと同じ考え方)。実例の`positron`は、個々のSVG
アイコンをupstreamのコミットハッシュ+sha256で検証してpinしている。

GSIの119アイコンは個別SVGソースを持たず、結合済みラスタPNG1枚としてのみ公開されている
([0014](0014-sprite-decisions.md)で確認済み、ライセンスも未確認のまま)。「レンダリング済み
PNGはミラーしない」というhfu/starsの原則と真正面から食い違う。

**判断(藤村さんの判断)**: GSIアイコンはこの原則の**ラスタ例外**として扱い、グレースケール化
した単一PNGスプライトシートをそのまま静的ファイルとしてhfu/starsに置いてもらう。ベクター化
(`potrace`等でSVGへ変換→`positron`方式に合わせる)は、トレース品質の検証・ライセンス確認・
80アイコン分の作業量を考えると今回は見送り。

## 副産物の訂正: `std@2x.png`は実在しない

[0014](0014-sprite-decisions.md)は「`@2x`のpixelRatioバリアントが無く、高DPI環境でぼやける」
と記録していたが、実際に`std@2x.png`を取得すると**HTTP 200を返す**。ただし中身は`std.png`と
バイト単位で完全に同一(MD5一致)、`std@2x.json`も`std.json`と内容が同一(pixelRatio:1のまま)。
つまり「存在しない」は不正確で、正しくは「**URLは存在するが、実体は@1xの複製であり、真の高
解像度アセットではない**」。GSI側のプレースホルダーか意図的な措置かは不明。

この動作を壊さないよう、生成物側も`bvmap-starlight@2x.png`/`.json`を`bvmap-starlight.png`/
`.json`の単純な複製として用意した(MapLibreは端末のdevicePixelRatioに応じて`@2x`を要求し、
404だとスプライト全体の読み込みに失敗することをローカル検証で確認済み——低DPI版だけでは
不十分)。

## 実装

- **`generator/cool_transform.py`**: [0030](0030-starlight-first-color-pass.md)の
  `cool_transform()`を初めて実コードとして切り出した(これまでADR本文と
  [docs/bvmap-starlight-cartographic-design.md](../bvmap-starlight-cartographic-design.md)
  に式が書かれているだけで、パレットトークンの値は手計算で`starlight-input.yaml`に転記されて
  いた)。ドキュメントに書かれた4組の変換例(`gray_100`/`anno_29`/`gray_233`/`gray_161`)と
  完全一致することを確認済み。
- **`generator/sprite_grayscale.py`**: `sprite/std.png`(GSIオリジナルの無加工スナップショット、
  `style/bvmap-dark.json`と同じ役割)を読み、各ピクセルを (1) ITU-R BT.601加重で輝度に落とし、
  (2) `cool_transform()`に通す。アルファは無変更。`cool_transform()`自体はクリップしない(手
  選定したパレットトークンには無関係だが、白に近いアイコンのピクセルでは255を超える)ため、
  ベクトル化した経路では`[0,255]`にクリップし、`cool_transform()`を直接呼んだ結果も同じ範囲へ
  クリップした上でランダム200ピクセルを突き合わせて一致を検証している。
- 出力: `sprite/bvmap-starlight.png`/`.json`(+`@2x`複製)。アイコンの位置・サイズは変更して
  いないため、JSON(座標)は`std.json`と同一内容。

## 検証

ローカルの`examples/style-preview.html`相当の環境で、`style/bvmap-starlight.json`の`sprite`
フィールドだけを一時的にローカルの`sprite/bvmap-starlight`へ差し替えたスタイルを作り、ブラウザ
で実際に読み込んで確認した(検証用ファイルはコミットしていない):

- `map.hasImage('神社')`等でスプライトが実際に読み込まれたことを確認
- 実タイル上で、GSIオリジナル(`bvmap-dark`、青色の「田」記号等)と比較し、同じ地物が中立
  グレーで描画されることを確認。黒系のアイコン(卍の寺院記号等)は見た目上ほぼ変化しない
  (`cool_transform`の設計上、暗い値ほど変化を抑える非対称brightenのため)

## 現状と次

`style/bvmap-starlight.json`の`sprite`フィールドはまだGSIの元URLのままで、切り替えていない
——実際に`stars.optgeo.org`側でホストされ、最終URLが決まってから`assemble.py`側で配線する
([0006](0006-hfu-stars-is-already-master-repo.md)のPRに合わせて)。

- [ ] `hfu/stars`へ`sprite/bvmap-starlight.png`/`.json`(+`@2x`)を「ラスタ例外」として提案・PR
- [ ] ホスト後、`style/bvmap-starlight.json`の`sprite`を実URLに切り替え
- [ ] GSIアイコンのライセンス確認は[0014](0014-sprite-decisions.md)から引き続き未解決(グレー
      スケール化した派生物にも同じ問題が及ぶ)
- 未使用39個・`icon-size`固定値バグ([0014](0014-sprite-decisions.md))は今回もスコープ外のまま

## 訂正(2026-09-20、`stars`セッションからの報告、`/catalog`で自分でも裏取り済み)

「ラスタ例外」は不要だった。`stars`セッションが同日中に回避策を実装・検証済み: GSIの
`std.json`の座標で`std.png`から各アイコンを切り出し、**そのPNGをdata URIとしてSVGへ埋め込む**。
Martinはそのsvgからシートを焼くため、`assets/sprites.json`の「SVGソース+Martin焼成」方針を
崩さずに済む。resveがembedded rasterをそのまま描くため、焼いたシートは元のラスタとピクセル
単位で完全一致することを`stars`側で119/119検証済み(SDFフラグは0件、ラスタ埋め込みでも意味が
変わる箇所がないため)。`bvmap-starlight`側のグレースケール版(119アイコン・1024×1024・SDF0件・
`@2x`が`@1x`とバイト単位で同一)も同じ性質のため、同じ経路にそのまま乗る。

本番のMartin設定には現在`sprites: {"positron": {...}}`の1件のみ登録されている
(`https://stars.optgeo.org/catalog`で確認、フォント12・スタイル7も一致)。GSIアイコン
(`optimal-bvmap`)は配置済みで、Martin再起動の承認待ち。想定URLは
`https://stars.optgeo.org/sprite/bvmap-starlight`。

残る手続き論点: hfu/starsのスタイル受け入れ規約は「hfu/starsへのPR」が入口だが、今回は
「dwg7/bvmap側のファイルをstars側でコピーする」形になるため、この経路を使ってよいか
藤村さんに確認中([0037](0037-glyphs-hosting-switch.md)参照)。

## 訂正2(2026-09-20、「119/119完全一致」自体が誤りだった)

上の訂正で書いた「119/119ピクセル完全一致」は不正確だった。配信開始後、公開中の
`bvmap-starlight.png`を手元の`sprite/bvmap-starlight.png`(commit `1410d64`)とアイコンごとに
crop して自分で比較したところ、**アルファは119/119完全一致だったがRGBは117/119アイコンで
エッジ付近が最大±10〜30程度ずれていた**(このセッションで発見、`stars`へ報告)。

`stars`側が原因を特定して報告してきた: 検証に使っていた`ImageChops.difference(a,b).getbbox()`
が、Pillow 10以降`alpha_only=True`が既定のため、アルファさえ一致すればRGBの差を無視して`None`
を返す——「一致」の検査が実質アルファしか見ていなかった。測り直した結果は次の通り:
不透明画素は0件差、差は全て半透明のエッジ画素に限られる(グレースケール版は12,458半透明画素中
最大|dRGB|32)。原因はresvg/tiny-skiaが乗算済みアルファで処理し、PNG出力時に非乗算へ戻す際の
丸め。**画面に出る値(アルファ乗算後)での最大偏差は1/255未満**で、視覚的な影響は無視できる
水準——この判断のままPR([hfu/stars#12](https://github.com/hfu/stars/pull/12))を進めた。

`stars`側は`assets/sprites.json`の「完全一致」表記を削除し、実測のfidelity情報(アルファ差0・
不透明差0・半透明差の件数と最大値・乗算後の最大偏差)に置き換え済み(`assets/sprites.json`で
直接確認、commit `1410d64`のsha256まで正しく記録されている)。**教訓**: 「完全一致」のような
強い主張は、検証コードの既定値(この場合Pillowのバージョン差)まで込みで裏取りしないと、
ツール側の挙動を鵜呑みにしてしまう——アイコンごとのcropという素朴な独自検証が、既存の
自動チェックの穴を見つけた形になった。
