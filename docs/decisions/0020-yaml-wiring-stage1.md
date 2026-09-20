# 0020: YAML入力の配線(コード⇔YAML境界の実装)

[HANDOVER.md](../../HANDOVER.md)の次ステップとして、ケース・カンファレンスで議論した
「`generator/sample-starlight-input.yaml`(試作)を実際にPythonから読み込む」を実装。
`generator/starlight-input.yaml`(サンプルからリネーム、実データで拡充)、
`generator/load_input.py`(新規ローダー)。

## 結果

**PASS**。[0019](0019-stage1-final-assembly.md)の123レイヤー完全一致を保ったまま、色を持つ生成部分を**全てYAMLデータ駆動**に置き換えた:

- `categories.building_fill` / `building_outline_color` / `building_outline_width`(新設) / `anno_text_color` / `anno_text_font`
- `priority_chains.road_color`
- `patches`のうち`bvmap-行政区画`・`bvmap-水域`(2層、色だけpalette参照に差し替え済み)

`generator/assemble.py`はもう`category_table.py`・`building_color.py`の定数や`road_color.py`のモジュールレベル定数を直接importしていない——全て`load_input.py`経由でYAMLの`palette`セクションから解決される。

## 実装で確定した設計

### 「構造はコード、値はYAML」の境界線

`categories.*`(`flat_match`エンジン)は`category_table.compile_match_expression()`にそのまま流し込めた——値の対応表(`groups`)を渡すだけで、コンパイラのコードは一切変更不要だった。

`priority_chains.road_color`(`priority_case_chain`エンジン)は、[0018](0018-road-color-not-flat-category-compiler.md)で書いた`road_color.compile_road_color_step()`を、**ハードコードされたモジュール定数からパラメータ引数へ**リファクタリングする必要があった(`_rgba(gray, alpha)`という「グレー値+アルファ」の内部表現から、パレットが持つ「アルファ1のrgba文字列」を受け取り、アルファだけ書き換える`_with_alpha()`という新しいヘルパーへの変更を含む)。**構造(caseの入れ子・判定順序)は一切動かしていない**——動いたのは「値をどこから受け取るか」という関数のインターフェースだけ。これは0018で予告した「構造はコード、値はYAML」という区分の最初の実地検証であり、うまくいった。

### `value_type`という小さな拡張が必要だった

`flat_match`のvalues は最初「色(palette参照)」だけを想定していたが、実装を進めると2つの反例が出た:

- `anno_text_font`: 値はフォント名の文字列で、`compile_match_expression()`には`["literal", [name]]`という別の形に包んで渡す必要がある
- `building_outline_width`: 値は色ではなく単なる数値(1/0)

どちらも「パレット参照」という前提を素直に壊すため、`value_type: font_literal` / `value_type: number`というオプトインのタグをYAMLに追加した(デフォルトは`color`)。**これは、フラットな`match`コンパイラという1つの構造が、実は「色」「フォント名」「数値」という3つの異なる値の世界に対して使い回されている、という新しい事実**——実装するまで見えていなかった。

### patchesの`color_overrides`は「トップレベル1プロパティ=1値」のみ実装

[前回のディスカッション](../../generator/starlight-input.yaml)で予告した通り、`background`の`background-color`(step式の中に色が埋まっている)は今回も未実装のまま——`load_input.build_patches()`は、`color_overrides`のキーがレイヤーの`paint`直下に存在する場合だけ上書きし、存在しない場合(`mid_zoom_gray`のような概念的なキー)は静かにスキップする。ごまかさず、YAML側にも「未解決」の注釈をそのまま残した。

## 統合で見つかった追加の事実

- `road_color.py`のリファクタリング中、旧`_rgba(gray, alpha=1)`ヘルパーが「グレー値」という前提を持っていたため、パレットの「フルrgba文字列」をそのまま渡せなかった。`_with_alpha()`という正規表現ベースの新ヘルパー(`rgba(157,157,157,1)` → `rgba(157,157,157,0.5)`)を追加することで解決したが、**パレットの値の型(グレー整数 vs rgba文字列)が、コンパイラのインターフェース設計に直接影響する**という、地味だが今後も繰り返しそうな制約が可視化された
- 「3m-5.5m未満」の例外色(0018で発見した、幅員ランプの最初のバケットと偶然同じ173という値)は、YAMLでは`narrow_exception_color`という独立したフィールドとして明示した(暗黙にwidth_rampの値を再利用するコードにはしなかった——値が偶然一致しているだけで、意味的に同じものだとは限らないため)

## 未解決のまま残っていること

- `category_table.py`/`building_color.py`自身の`__main__`検証は、まだ独自のハードコードされた定数を使っている(YAMLの値と**内容としては同一だが、ファイル上は別々に存在**する)。両者がドリフトする可能性は理論上残るが、`assemble.py`は既にYAML側だけを見ているため、実害はStage 1の範囲では発生しない。将来、この重複を一本化するか、単体モジュールの検証もYAML駆動に寄せるかは、次の焼き鈍しの候補
- `background`のstep式パッチは未実装のまま(次のケース・カンファレンス候補)
