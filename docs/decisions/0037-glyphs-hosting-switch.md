# 0037: `glyphs`をstars.optgeo.org自前配信へ切り替え

[HANDOVER.md](../../HANDOVER.md)に「未検証・未対応」として記録していた保留事項——`hfu/stars`が
glyphを自前配信するようになった件——を、`stars`セッションからの報告と`stars.optgeo.org/catalog`
での独立した裏取りを経て、`bvmap-starlight`側で実際に切り替えた。

## 裏取り(実データ、`stars`の主張を鵜呑みにせず確認)

`https://stars.optgeo.org/catalog`を直接取得し、以下を独立に確認した:

- `sprites`: `{"positron": {...}}`の1件のみ(`stars`の「スプライト1」の主張と一致)
- `fonts`: 12件登録済み(`stars`の主張と一致)、うち`Noto Sans JP Regular`
  ・`Noto Serif JP SemiBold`が実在し、GSI原本のグリフ範囲(それぞれ32〜200812、32〜195060)を
  ほぼ上回るカバレッジ
- `styles`: `bvmap-dark`/`positron`/`glup2030-zoning`/`std`/`vlcm`/`openstreetmap_jp_planet`/`vbm`
  の7件、`bvmap-starlight`はまだ無い
- URLパターン: `https://stars.optgeo.org/font/{fontstack}/{range}`(`.pbf`拡張子を付けると404、
  無しで200・`content-type: application/x-protobuf`)を`curl`で直接確認

## 変更

`starlight-input.yaml`に`hosting:`セクションを新設した(トップレベルのスタイルプロパティで、
`bvmap-dark.json`から継承せず上書きするもの。現状`glyphs`のみ、`sprite`は
[0036](0036-sprite-grayscale-raster-exception.md)のホスティング方法が決まるまで未設定):

```yaml
hosting:
  glyphs: "https://stars.optgeo.org/font/{fontstack}/{range}"
  font_names:
    "NotoSansJP-Regular": "Noto Sans JP Regular"
    "NotoSerifJP-SemiBold": "Noto Serif JP SemiBold"
```

- `categories.anno_text_font`(`starlight-input.yaml`)の値をGSI原文からstars表記へ変更
- `assemble.py`: `hosting.glyphs`/`hosting.sprite`をトップレベルの出力に上書き。加えて
  `hosting.font_names`が指定されていれば、**全123層**の`layout.text-font`を横断的に置換する
  (`load_input.py`の新設`remap_font_names()`)
- `load_input.py`の自己診断から`anno_text_font`を`STRUCTURAL_CHECKS`から外した(stars表記に
  変わったことで`bvmap-dark.json`とは意図的に不一致になるため、他の配色トークンと同じ「diverged
  as expected」扱いに変更)

## なぜ全層の置換が必要だったか

`categories.anno_text_font`が生成するのはAnno9層中7層(`SHARED_TEXT_FONT_LAYERS`)のみ。残り3層
(`bvmap-等高線数値部`・`bvmap-等深線数値部`・`bvmap-注記道路番号`)は`patches`または個別の
Anno処理で、`layout.text-font`がbvmap-dark.json原文のまま埋め込まれていた——`categories`だけ
書き換えても、この3層は変換前のGSI表記(`NotoSansJP-Regular`)のまま残ってしまう。

スタイルの`glyphs`はトップレベルのプロパティ1つであり、スタイル全体でどのフォント名がどのURL
から解決されるかを決める。**一部の層だけ新しいフォント名、残りが旧表記のままという状態は
成立しない**(旧表記はstars側に存在しないフォント名になり、その層だけ文字が表示されなくなる)。
そのため`categories`経由かどうかに関わらず、組み立て済みスタイル全体に対して横断的に
文字列置換をかける設計にした。

## 検証

ローカルの`examples/style-preview.html`で実際に`bvmap-starlight`を読み込み、ラベルが正しく
描画されることを確認。`performance.getEntriesByType('resource')`で実際のフェッチ先を確認し、
`https://stars.optgeo.org/font/Noto%20Sans%20JP%20Regular/0-255`へのリクエストが発生している
ことを確認した(コンソールエラー無し)。`generator/load_input.py`・`generator/assemble.py`の
自己診断はいずれもPASS。

## 現状

`sprite`はまだGSI原本のURLのまま(`hosting`に未設定)。[0036](0036-sprite-grayscale-raster-exception.md)
のホスティング方法が決まり次第、`hosting.sprite`を追加するだけで済む設計にしてある。

`hfu/stars`への実際のPR・本番反映の手続き(誰のリポジトリに何をどう置くか)は
[0036](0036-sprite-grayscale-raster-exception.md)の訂正セクションに記載の通り、藤村さんの
判断待ち。
