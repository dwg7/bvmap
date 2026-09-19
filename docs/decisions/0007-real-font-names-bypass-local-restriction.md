# 0007: `text-font`に実フォント名を直接書けば`local()`の制限を回避できる(検証済み)

## 背景

[0004](0004-vertical-choonpu-workaround-does-not-work.md)で、`@font-face`の`src: local(...)`によるOS内蔵フォントのマッチングが、Chrome/Braveのフィンガープリンティング対策で信頼できないことを確認した。この制限は、ブラウザが`local()`を使った**明示的なプロービングAPI**(JSから「このフォントは存在するか」を個別に問い合わせられる仕組み)を対象にしたもので、Webページの通常のテキスト描画で使われる**素朴な`font-family`フォールバック解決**(問い合わせ結果をJSに返さない、成功/失敗を外から観測しにくい仕組み)までは制限していない。

## 検証した方法

`@font-face`を一切使わず、`text-font`に実在するプラットフォーム標準フォント名をそのまま並べる:

```json
"text-font": ["Hiragino Mincho ProN", "Yu Mincho", "MS Mincho", "Noto Serif CJK JP"]
```

## なぜ機能するか

`bvmap-dark.json`はルートに`glyphs`(GSIのPBFグリフサーバー)を持つため、[0002](0002-bvmap-starlight-vertical-choonpu.md)で確認した通り、`text-font`配列は結合されて単一のPBFフォントスタック名として要求される。GSIのサーバーには当然この名前のフォントスタックは存在せず404になり、MapLibre GL JS 5.11+はローカル描画(TinySDF)にフォールバックする([PR #4564](https://github.com/maplibre/maplibre-gl-js/pull/4564))。このフォールバック時、`glyph_manager.ts`の`_createTinySDF()`は結合されたスタック名を再び`,`で分割し、Canvas 2Dの`ctx.font`にプレーンなCSSフォントショートハンド文字列(`"... Hiragino Mincho ProN,Yu Mincho,MS Mincho,Noto Serif CJK JP,sans-serif"`)として渡す。これは`@font-face`の`local()`プロービングAPIを一切経由しない、Canvas 2Dの通常のフォント名解決であり、フィンガープリンティング対策の対象外と考えられる。

## 検証結果

- **macOS Brave(実機、2026-09-19)**: `@font-face`を宣言せずに上記`text-font`を指定したところ、`bvmap-dark`のデフォルト(ゴシック体、NotoSansJP-Regular)から明確に異なる明朝体(Hiragino Mincho ProNと見られる)に変化した。`document.fonts`の登録数は0(FontFace読み込みAPIを一切経由していないことの確認)
- 検証用ページ: `examples/realfont-test.html`

## この方法の限界

- **縦書き棒音符(ー)の問題は解決しない**。[0004](0004-vertical-choonpu-workaround-does-not-work.md)で確認した通り、根本原因はCanvas 2Dの`fillText()`に`font-feature-settings`(および真の縦書きシェーピング)を伝える経路が無いことであり、この方法は`@font-face`を回避しているだけで、Canvas経由という点は変わらないため、この限界は解消されない
- Windows・iOS・Androidでの検証はまだ済んでいない

## 意義

「Noto一辺倒から脱却し、各プラットフォームのベストなネイティブフォントを使う」という方向性([0005](0005-goal-change-master-repo-and-starlight-polish.md)のstarlight磨き上げの一部)が、信頼性の高い形で実現可能であることが分かった。Android(実質Notoのみ)を弱者と割り切り、Mac/Windowsはそれぞれのネイティブフォント(Hiragino/Yu)を優先するフォントスタックが技術的に成立する。
